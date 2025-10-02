"""Chase Bank statement processor."""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from ..base import BankProcessor


class ChaseProcessor(BankProcessor):
    """Processor for Chase Bank statements (checking and savings)."""

    bank_name = "Chase Bank"
    bank_code = "CHASE"
    supported_account_types = ["checking", "savings"]

    def detect(self, text: str) -> bool:
        """Detect if this is a Chase Bank statement.

        Args:
            text: Raw PDF text

        Returns:
            True if this is a Chase statement
        """
        indicators = [
            "CHASE",
            "JPMorgan Chase",
            "Chase Bank",
            "CHASE TOTAL CHECKING",
            "CHASE SAVINGS"
        ]
        text_upper = text.upper()
        return any(indicator.upper() in text_upper for indicator in indicators)

    def clean_text(self, text: str) -> str:
        """Clean Chase statement text.

        Args:
            text: Raw text from PDF

        Returns:
            Cleaned text
        """
        lines = text.split('\n')
        cleaned_lines, _ = self._clean_chase_lines(lines)
        return '\n'.join(cleaned_lines)

    def extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract account metadata from Chase statement.

        Args:
            text: Cleaned text

        Returns:
            Metadata dict
        """
        lines = text.split('\n')
        metadata = {
            "account_number": None,
            "account_type": "checking",  # Default
            "statement_period": {},
            "opening_balance": 0.0,
            "closing_balance": 0.0
        }

        for line in lines:
            # Extract account last 4 digits
            if "CHASE TOTAL CHECKING" in line.upper():
                match = re.search(r'(\d{4})\b', line)
                if match:
                    metadata["account_number"] = match.group(1)
                    metadata["account_type"] = "checking"
            elif "CHASE SAVINGS" in line.upper():
                match = re.search(r'(\d{4})\b', line)
                if match:
                    metadata["account_number"] = match.group(1)
                    metadata["account_type"] = "savings"

            # Extract balances
            if "BEGINNING BALANCE" in line.upper():
                balance_match = re.search(r'\$?([\d,]+\.\d{2})', line)
                if balance_match:
                    metadata["opening_balance"] = self.parse_amount(balance_match.group(1))

            if "ENDING BALANCE" in line.upper():
                balance_match = re.search(r'\$?([\d,]+\.\d{2})', line)
                if balance_match:
                    metadata["closing_balance"] = self.parse_amount(balance_match.group(1))

        return metadata

    def extract_transactions(self, text: str) -> List[Dict[str, Any]]:
        """Extract transactions from Chase statement.

        Args:
            text: Cleaned text

        Returns:
            List of transaction dicts
        """
        lines = text.split('\n')
        _, transactions_text = self._clean_chase_lines(lines)

        transactions = []
        for trans_line in transactions_text:
            # Parse date (MM/DD format)
            date_match = re.search(r'(\d{2}/\d{2})', trans_line)
            if not date_match:
                continue

            # Add current year to date
            date_str = date_match.group(1) + "/" + str(datetime.now().year)
            transaction_date = self.parse_date(date_str, ["%m/%d/%Y"])

            # Parse amount
            amount_match = re.search(r'[-]?\$?([\d,]+\.\d{2})', trans_line)
            if not amount_match:
                continue

            amount = self.parse_amount(amount_match.group(1))

            # Extract description
            description = trans_line.replace(date_match.group(0), '', 1)
            if amount_match:
                description = description.replace(amount_match.group(0), '', 1)
            description = description.strip()

            transactions.append({
                "date": transaction_date,
                "description": description,
                "amount": amount,
                "balance": 0.0,
                "category": None
            })

        return transactions

    def _clean_chase_lines(self, lines: List[str]) -> Tuple[List[str], List[str]]:
        """Internal method to clean Chase statement lines.

        Extracted from script/utils/pdf_processor.py

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
        checking_account_last_four = None
        savings_account_last_four = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Extract checking account last four
            if "CHASE TOTAL CHECKING" in line.upper():
                match = re.search(r'(\d{4})\b', line)
                if match:
                    checking_account_last_four = match.group(1)

            # Extract savings account last four
            elif "CHASE SAVINGS" in line.upper():
                match = re.search(r'(\d{4})\b', line)
                if match:
                    savings_account_last_four = match.group(1)

            # Detect account type sections
            if "CHECKING SUMMARY" in line.upper():
                if checking_account_last_four:
                    cleaned_lines.append(f"\n=== Chase Checking Account({checking_account_last_four}) ===")
                else:
                    cleaned_lines.append(f"\n=== Chase Checking Account ===")
                continue
            elif "SAVINGS SUMMARY" in line.upper():
                if savings_account_last_four:
                    cleaned_lines.append(f"\n=== Chase Savings Account({savings_account_last_four}) ===")
                else:
                    cleaned_lines.append(f"\n=== Chase Savings Account ===")
                continue

            # Skip balance lines
            if "BEGINNING BALANCE" in line.upper() or "ENDING BALANCE" in line.upper():
                continue

            # Stop at disclosure markers
            if "*start*dre portrait disclosure message area" in line.lower():
                break

            # Detect transaction detail section
            if "TRANSACTION DETAIL" in line.upper():
                is_transaction_detail = True
                continue

            # Process transactions
            if is_transaction_detail:
                # Stop at overdraft markers
                if "*start*post overdraft and returned" in line.lower():
                    break

                # Process transaction markers
                if "*end*transac" in line.lower():
                    # Could add marker replacement logic here
                    pass

                # Match date and amount
                date_match = re.search(r'\d{2}/\d{2}', line)
                amount_match = re.search(r'[-]?\$?[\d,]+\.\d{2}', line)

                if date_match and amount_match:
                    if current_transaction:
                        transaction_lines.append(current_transaction)
                        cleaned_lines.append(current_transaction)
                        transaction_count += 1

                    current_transaction = line
                elif current_transaction and len(line.split()) > 2:
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
