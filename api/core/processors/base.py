"""Base class for bank statement processors."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import re


class BankProcessor(ABC):
    """Abstract base class for bank statement processors.

    Each bank processor handles:
    1. Bank detection (is this PDF from our bank?)
    2. Text cleaning and extraction (90% of the work)
    3. Structured data extraction
    """

    bank_name: str = "UNKNOWN"
    bank_code: str = "UNKNOWN"
    supported_account_types: List[str] = []

    @abstractmethod
    def detect(self, text: str) -> bool:
        """Detect if this text is from this bank's statement.

        Args:
            text: Raw text extracted from PDF

        Returns:
            True if this processor can handle this statement
        """
        pass

    @abstractmethod
    def clean_text(self, text: str) -> str:
        """Clean and preprocess the raw text.

        This is the core value - removes 90% of noise specific to this bank.

        Args:
            text: Raw text from PDF

        Returns:
            Cleaned text ready for structured extraction
        """
        pass

    @abstractmethod
    def extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract account metadata from statement.

        Args:
            text: Cleaned text

        Returns:
            Dict containing:
                - account_number: str (last 4 digits)
                - account_type: str (checking, savings, credit)
                - statement_period: Dict[str, datetime]
                - opening_balance: float
                - closing_balance: float
        """
        pass

    @abstractmethod
    def extract_transactions(self, text: str) -> List[Dict[str, Any]]:
        """Extract transaction records from cleaned text.

        Args:
            text: Cleaned text

        Returns:
            List of transaction dicts, each containing:
                - date: datetime
                - description: str
                - amount: float (negative for debit, positive for credit)
                - balance: float
                - category: Optional[str]
        """
        pass

    def process(self, pdf_text: str) -> Dict[str, Any]:
        """Full processing pipeline.

        Args:
            pdf_text: Raw text from PDF

        Returns:
            Complete structured data including metadata and transactions
        """
        if not self.detect(pdf_text):
            raise ValueError(f"This statement is not from {self.bank_name}")

        cleaned_text = self.clean_text(pdf_text)
        metadata = self.extract_metadata(cleaned_text)
        transactions = self.extract_transactions(cleaned_text)

        return {
            "bank": self.bank_name,
            "bank_code": self.bank_code,
            "metadata": metadata,
            "transactions": transactions,
            "processed_at": datetime.utcnow().isoformat()
        }

    @staticmethod
    def parse_amount(amount_str: str) -> float:
        """Helper method to parse amount strings.

        Args:
            amount_str: String like "$1,234.56" or "(234.56)" for negative

        Returns:
            Float value (negative for debits in parentheses)
        """
        # Remove currency symbols and spaces
        cleaned = re.sub(r'[$,\s]', '', amount_str)

        # Check if it's negative (in parentheses)
        is_negative = cleaned.startswith('(') and cleaned.endswith(')')
        if is_negative:
            cleaned = cleaned[1:-1]

        try:
            value = float(cleaned)
            return -value if is_negative else value
        except ValueError:
            return 0.0

    @staticmethod
    def parse_date(date_str: str, formats: List[str] = None) -> Optional[datetime]:
        """Helper method to parse date strings.

        Args:
            date_str: Date string to parse
            formats: List of strptime format strings to try

        Returns:
            datetime object or None if parsing fails
        """
        if formats is None:
            formats = [
                "%m/%d/%Y",
                "%m/%d/%y",
                "%Y-%m-%d",
                "%b %d, %Y",
                "%B %d, %Y"
            ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue

        return None


class ProcessorRegistry:
    """Registry for all bank processors.

    Automatically detects which processor to use for a given statement.
    """

    def __init__(self):
        self._processors: List[BankProcessor] = []

    def register(self, processor: BankProcessor):
        """Register a bank processor.

        Args:
            processor: Instance of BankProcessor subclass
        """
        self._processors.append(processor)

    def get_processor(self, pdf_text: str) -> Optional[BankProcessor]:
        """Automatically detect and return the appropriate processor.

        Args:
            pdf_text: Raw text from PDF

        Returns:
            BankProcessor instance or None if no match found
        """
        for processor in self._processors:
            if processor.detect(pdf_text):
                return processor

        return None

    def list_supported_banks(self) -> List[Dict[str, str]]:
        """List all registered banks.

        Returns:
            List of dicts with bank_name and bank_code
        """
        return [
            {
                "bank_name": p.bank_name,
                "bank_code": p.bank_code,
                "account_types": p.supported_account_types
            }
            for p in self._processors
        ]


# Global registry instance
registry = ProcessorRegistry()
