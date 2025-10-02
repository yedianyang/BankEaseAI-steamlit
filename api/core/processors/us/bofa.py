"""Bank of America (BOFA) statement processor."""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from ..base import BankProcessor


class BOFAProcessor(BankProcessor):
    """Processor for Bank of America statements."""

    bank_name = "Bank of America"
    bank_code = "BOFA"
    supported_account_types = ["savings", "checking"]

    def detect(self, text: str) -> bool:
        """Detect if this is a Bank of America statement.

        Args:
            text: Raw PDF text

        Returns:
            True if this is a BOFA statement
        """
        indicators = [
            "BANK OF AMERICA",
            "BofA",
            "Bank of America, N.A.",
            "ADVANTAGE SAVINGS"
        ]
        text_upper = text.upper()
        return any(indicator.upper() in text_upper for indicator in indicators)

    def clean_text(self, text: str) -> str:
        """Clean BOFA statement text.

        Removes headers, footers, and other noise specific to BOFA statements.

        Args:
            text: Raw text from PDF

        Returns:
            Cleaned text
        """
        lines = text.split('\n')
        cleaned_lines, _ = self._clean_bofa_lines(lines)
        return '\n'.join(cleaned_lines)

    def extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract account metadata from BOFA statement.

        Args:
            text: Cleaned text

        Returns:
            Metadata dict
        """
        lines = text.split('\n')
        metadata = {
            "account_number": None,
            "account_type": "savings",  # Default
            "statement_period": {},
            "opening_balance": 0.0,
            "closing_balance": 0.0
        }

        for line in lines:
            # Extract account last 4 digits
            if "Account number:" in line or "ACCOUNT NUMBER" in line.upper():
                numbers = re.findall(r'\d{4}', line)
                if numbers:
                    metadata["account_number"] = numbers[-1]

            # Extract account type
            if "ADVANTAGE SAVINGS" in line.upper():
                metadata["account_type"] = "savings"
            elif "CHECKING" in line.upper():
                metadata["account_type"] = "checking"

            # Extract balances
            if "Beginning balance on" in line:
                balance_match = re.search(r'\$?([\d,]+\.\d{2})', line)
                if balance_match:
                    metadata["opening_balance"] = self.parse_amount(balance_match.group(1))

            if "Ending balance on" in line:
                balance_match = re.search(r'\$?([\d,]+\.\d{2})', line)
                if balance_match:
                    metadata["closing_balance"] = self.parse_amount(balance_match.group(1))

        return metadata

    def extract_transactions(self, text: str) -> List[Dict[str, Any]]:
        """Extract transactions from BOFA statement.

        Args:
            text: Cleaned text

        Returns:
            List of transaction dicts
        """
        lines = text.split('\n')
        _, transactions_text = self._clean_bofa_lines(lines)

        transactions = []
        for trans_line in transactions_text:
            # Parse date
            date_match = re.search(r'(\d{2}/\d{2}/\d{2})', trans_line)
            if not date_match:
                continue

            date_str = date_match.group(1)
            transaction_date = self.parse_date(date_str, ["%m/%d/%y"])

            # Parse amount
            amount_match = re.search(r'[-]?\$?([\d,]+\.\d{2})', trans_line)
            if not amount_match:
                continue

            amount = self.parse_amount(amount_match.group(1))

            # Extract description (everything between date and amount)
            description = trans_line.replace(date_str, '', 1)
            if amount_match:
                description = description.replace(amount_match.group(0), '', 1)
            description = description.strip()

            transactions.append({
                "date": transaction_date,
                "description": description,
                "amount": amount,
                "balance": 0.0,  # BOFA statements don't always show running balance
                "category": None
            })

        return transactions

    def _clean_bofa_lines(self, lines: List[str]) -> Tuple[List[str], List[str]]:
        """Internal method to clean BOFA statement lines.

        This is the core processing logic extracted from script/utils/pdf_processor.py

        Args:
            lines: Raw lines from PDF

        Returns:
            Tuple of (cleaned_lines, transaction_lines)
        """
        cleaned_lines = []
        transaction_lines = []
        transaction_count = 0

        # State tracking
        is_transaction_detail = False
        current_transaction = None
        account_last_four = None

        remove_keywords = [
            "Date",
            "Description",
            "Amount",
            "Beginning balance on",
            "Deposits and other additions",
            "ATM and debit card subtractions",
            "Other subtractions",
            "Service fees",
            "Ending balance on",
            "Total deposits and other additions",
            "Total ATM and debit card subtractions",
            "Total other subtractions",
            "Total service fees"
        ]

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Extract account last four
            if "Account number:" in line:
                numbers = re.findall(r'\d{4}', line)
                if numbers:
                    account_last_four = numbers[-1]
                cleaned_lines.append(f"\n=== Bank of America Savings Account({account_last_four}) ===")

            # Detect transaction detail section
            if any(keyword in line for keyword in ["Deposits and other additions", "ATM and debit card subtractions", "Other subtractions"]):
                is_transaction_detail = True
                continue

            # Detect end of transaction section
            if "Total " in line or "Braille and Large Print Request" in line:
                is_transaction_detail = False
                if current_transaction:
                    transaction_lines.append(current_transaction)
                    cleaned_lines.append(current_transaction)
                    transaction_count += 1
                    current_transaction = None
                continue

            # Process transactions
            if is_transaction_detail:
                date_match = re.search(r'\d{2}/\d{2}/\d{2}', line)
                amount_match = re.search(r'[-]?\$?[\d,]+\.\d{2}', line)

                if date_match and amount_match:
                    if current_transaction:
                        transaction_lines.append(current_transaction)
                        cleaned_lines.append(current_transaction)
                        transaction_count += 1
                    current_transaction = line
                elif current_transaction and len(line.split()) > 3:
                    current_transaction += " " + line
                elif current_transaction:
                    transaction_lines.append(current_transaction)
                    cleaned_lines.append(current_transaction)
                    transaction_count += 1
                    current_transaction = None

        # Handle last transaction
        if current_transaction:
            transaction_lines.append(current_transaction)
            cleaned_lines.append(current_transaction)
            transaction_count += 1

        return cleaned_lines, transaction_lines
