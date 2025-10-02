"""American Express (Amex) credit card statement processor."""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from ..base import BankProcessor


class AmexProcessor(BankProcessor):
    """Processor for American Express credit card statements."""

    bank_name = "American Express"
    bank_code = "AMEX"
    supported_account_types = ["credit"]

    def detect(self, text: str) -> bool:
        """Detect if this is an American Express statement.

        Args:
            text: Raw PDF text

        Returns:
            True if this is an Amex statement
        """
        indicators = [
            "AMERICAN EXPRESS",
            "AMEX",
            "AmEx",
            "ACCOUNT ENDING"
        ]
        text_upper = text.upper()
        return any(indicator.upper() in text_upper for indicator in indicators)

    def clean_text(self, text: str) -> str:
        """Clean Amex statement text.

        Args:
            text: Raw text from PDF

        Returns:
            Cleaned text
        """
        lines = text.split('\n')
        cleaned_lines, _ = self._clean_amex_lines(lines)
        return '\n'.join(cleaned_lines)

    def extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract account metadata from Amex statement.

        Args:
            text: Cleaned text

        Returns:
            Metadata dict
        """
        lines = text.split('\n')
        metadata = {
            "account_number": None,
            "account_type": "credit",
            "statement_period": {},
            "opening_balance": 0.0,
            "closing_balance": 0.0
        }

        for line in lines:
            # Extract account last 5 digits (Amex uses 5)
            if "ACCOUNT ENDING" in line.upper():
                numbers = re.findall(r'\d{5}', line)
                if numbers:
                    metadata["account_number"] = numbers[-1]

            # Extract balances
            if "PREVIOUS BALANCE" in line.upper():
                balance_match = re.search(r'\$?([\d,]+\.\d{2})', line)
                if balance_match:
                    metadata["opening_balance"] = self.parse_amount(balance_match.group(1))

            if "NEW BALANCE" in line.upper():
                balance_match = re.search(r'\$?([\d,]+\.\d{2})', line)
                if balance_match:
                    metadata["closing_balance"] = self.parse_amount(balance_match.group(1))

        return metadata

    def extract_transactions(self, text: str) -> List[Dict[str, Any]]:
        """Extract transactions from Amex statement.

        Args:
            text: Cleaned text

        Returns:
            List of transaction dicts
        """
        lines = text.split('\n')
        _, transactions_text = self._clean_amex_lines(lines)

        transactions = []
        for trans_line in transactions_text:
            # Parse date (flexible format: MM/DD or MM/DD/YY or MM/DD/YYYY)
            date_match = re.search(r'\b(\d{1,2}/\d{1,2}(?:/\d{2,4})?)\b', trans_line)
            if not date_match:
                continue

            date_str = date_match.group(1)
            # Add current year if not present
            if '/' not in date_str[3:]:
                date_str += "/" + str(datetime.now().year)

            # Parse different date formats
            transaction_date = self.parse_date(
                date_str,
                ["%m/%d/%Y", "%m/%d/%y"]
            )

            # Parse amount (may have + or - prefix)
            amount_match = re.search(r'([-+]?\$?[\d,]+\.\d{2})', trans_line)
            if not amount_match:
                continue

            amount_str = amount_match.group(1)
            amount = self.parse_amount(amount_str)

            # Extract description
            description = trans_line.replace(date_match.group(0), '', 1)
            if amount_match:
                description = description.replace(amount_match.group(0), '', 1)
            description = description.strip()

            transactions.append({
                "date": transaction_date,
                "description": description,
                "amount": amount,
                "balance": 0.0,  # Credit card statements don't show running balance
                "category": None
            })

        return transactions

    def _clean_amex_lines(self, lines: List[str]) -> Tuple[List[str], List[str]]:
        """Internal method to clean Amex statement lines.

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
        current_transaction = None
        account_last_five = None
        is_transaction_detail = False

        remove_keywords = [
            "DATE",
            "DESCRIPTION",
            "AMOUNT",
            "BEGINNING BALANCE ON",
            "DEPOSITS AND OTHER ADDITIONS",
            "NEW CHARGES SUMMARY",
            "NEW CHARGES",
            "SUMMARY",
        ]

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Extract account last five (only once)
            if "ACCOUNT ENDING" in line.upper():
                if not any("=== American Express Credit Card(" in l for l in cleaned_lines):
                    numbers = re.findall(r'\d{5}', line)
                    if numbers:
                        account_last_five = numbers[-1]
                        cleaned_lines.append(f"\n=== American Express Credit Card({account_last_five}) ===")

            # Detect transaction detail section
            if any(keyword in line.upper() for keyword in [
                "FEES", "TOTAL PAYMENTS AND CREDITS", "DETAIL",
                "DETAIL *INDICATES POSTING DATE", "DETAIL CONTINUED"
            ]):
                is_transaction_detail = True
                continue

            if "TO RATE INTEREST RATE" in line.upper():
                is_transaction_detail = True
                continue

            # Detect end of transaction section
            if any(keyword in line.upper() for keyword in [
                "ABOUT TRAILING INTEREST", "CONTINUED ON REVERSE", "CONTINUED ON NEXT PAGE"
            ]):
                is_transaction_detail = False
                if current_transaction:
                    transaction_lines.append(current_transaction)
                    cleaned_lines.append(current_transaction)
                    transaction_count += 1
                    current_transaction = None
                continue

            # Process transactions
            if is_transaction_detail:
                # Skip keyword lines
                if any(keyword in line.upper() for keyword in remove_keywords):
                    continue

                # Match date and amount (flexible format)
                date_match = re.search(r'\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b', line)
                amount_match = re.search(r'[-+]?\$?[\d,]+(?:\.\d{2})', line)

                if date_match and amount_match:
                    if current_transaction:
                        transaction_lines.append(current_transaction)
                        cleaned_lines.append(current_transaction)
                        transaction_count += 1

                    # Invert amount (Amex shows debits as positive)
                    amount_str = amount_match.group()
                    clean_amount_str = amount_str.replace('$', '').replace(',', '')
                    inverted_amount = -float(clean_amount_str)
                    formatted_amount = f"+{inverted_amount:.2f}" if inverted_amount > 0 else f"{inverted_amount:.2f}"

                    # Replace original amount
                    line = line[:amount_match.start()] + formatted_amount + line[amount_match.end():]
                    current_transaction = line

                    # Handle interest rate transactions
                    if re.match(r'^(Purchases|Cash Advances)\b', line.strip()):
                        pattern = re.compile(
                            r'^(Purchases|Cash Advances)\s+'
                            r'(\d{1,2}/\d{1,2}(?:/\d{2,4})?)\s+'
                            r'([-+]?\d+(?:\.\d+)?%)\s+'
                            r'(?:\([^)]+\)\s+)?'
                            r'\$?([\d,]+\.\d{2})\s+'
                            r'\$?([\d,]+\.\d{2})'
                        )
                        match = pattern.match(current_transaction.strip())
                        if match:
                            txn_type = match.group(1)
                            date_str = match.group(2)
                            percent_val = match.group(3)
                            raw_amount = match.group(5).replace(',', '')
                            try:
                                amount_value = float(raw_amount)
                            except ValueError:
                                amount_value = 0.00
                            inverted_amount = -amount_value
                            formatted_amount = f"+{inverted_amount:.2f}" if inverted_amount > 0 else f"{inverted_amount:.2f}"
                            current_transaction = f"{date_str}  {txn_type} Interest Rate  {formatted_amount}"

        # Handle last transaction
        if current_transaction:
            transaction_lines.append(current_transaction)
            cleaned_lines.append(current_transaction)
            transaction_count += 1

        return cleaned_lines, transaction_lines
