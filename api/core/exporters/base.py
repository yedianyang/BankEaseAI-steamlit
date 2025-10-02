"""Base class for export templates."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import pandas as pd
from datetime import datetime


class ExportTemplate(ABC):
    """Abstract base class for export templates.

    Each template transforms standardized transaction data into
    a specific accounting software format (iCost, 金蝶, 用友, etc.)
    """

    template_name: str = "UNKNOWN"
    template_code: str = "UNKNOWN"
    description: str = ""
    supported_formats: List[str] = ["csv"]

    @abstractmethod
    def transform(self, transactions: List[Dict[str, Any]]) -> pd.DataFrame:
        """Transform standardized transactions to template format.

        Args:
            transactions: List of standardized transaction dicts, each containing:
                - date: datetime
                - description: str
                - amount: float (negative for debit, positive for credit)
                - balance: float
                - category: Optional[str]
                - bank: str
                - account_last4: str

        Returns:
            pandas DataFrame in template-specific format
        """
        pass

    @abstractmethod
    def get_column_mapping(self) -> Dict[str, str]:
        """Get column name mapping.

        Returns:
            Dict mapping standard field names to template column names
        """
        pass

    def validate_data(self, transactions: List[Dict[str, Any]]) -> bool:
        """Validate transaction data before transformation.

        Args:
            transactions: Transaction list to validate

        Returns:
            True if data is valid

        Raises:
            ValueError: If data is invalid
        """
        required_fields = ["date", "description", "amount", "balance"]

        for idx, trans in enumerate(transactions):
            for field in required_fields:
                if field not in trans:
                    raise ValueError(f"Transaction {idx} missing required field: {field}")

            # Validate data types
            if not isinstance(trans["date"], (datetime, str)):
                raise ValueError(f"Transaction {idx} has invalid date type")

            if not isinstance(trans["amount"], (int, float)):
                raise ValueError(f"Transaction {idx} has invalid amount type")

            if not isinstance(trans["balance"], (int, float)):
                raise ValueError(f"Transaction {idx} has invalid balance type")

        return True

    def export_to_csv(self, df: pd.DataFrame, file_path: str, encoding: str = "utf-8-sig"):
        """Export DataFrame to CSV file.

        Args:
            df: DataFrame to export
            file_path: Output file path
            encoding: File encoding (default: utf-8-sig for Excel compatibility)
        """
        df.to_csv(file_path, index=False, encoding=encoding)

    def export_to_excel(self, df: pd.DataFrame, file_path: str, sheet_name: str = "Transactions"):
        """Export DataFrame to Excel file.

        Args:
            df: DataFrame to export
            file_path: Output file path
            sheet_name: Excel sheet name
        """
        df.to_excel(file_path, index=False, sheet_name=sheet_name)

    def get_metadata(self) -> Dict[str, Any]:
        """Get template metadata.

        Returns:
            Dict containing template information
        """
        return {
            "template_name": self.template_name,
            "template_code": self.template_code,
            "description": self.description,
            "supported_formats": self.supported_formats,
            "column_mapping": self.get_column_mapping()
        }


class StandardTemplate(ExportTemplate):
    """Standard CSV export template.

    This is the default format - a unified CSV with all transaction data.
    """

    template_name = "Standard CSV"
    template_code = "standard"
    description = "Standard unified CSV format with all transaction details"
    supported_formats = ["csv", "excel"]

    def transform(self, transactions: List[Dict[str, Any]]) -> pd.DataFrame:
        """Transform to standard format.

        Args:
            transactions: Standardized transaction list

        Returns:
            DataFrame with standard columns
        """
        self.validate_data(transactions)

        data = []
        for trans in transactions:
            # Convert datetime to string if needed
            date_val = trans["date"]
            if isinstance(date_val, datetime):
                date_str = date_val.strftime("%Y-%m-%d")
            else:
                date_str = str(date_val)

            amount = float(trans["amount"])
            debit = abs(amount) if amount < 0 else 0.00
            credit = amount if amount > 0 else 0.00

            data.append({
                "Date": date_str,
                "Description": trans["description"],
                "Debit": f"{debit:.2f}",
                "Credit": f"{credit:.2f}",
                "Balance": f"{trans['balance']:.2f}",
                "Category": trans.get("category", ""),
                "Bank": trans.get("bank", ""),
                "Account": trans.get("account_last4", "")
            })

        return pd.DataFrame(data)

    def get_column_mapping(self) -> Dict[str, str]:
        """Get column mapping.

        Returns:
            Standard column names
        """
        return {
            "date": "Date",
            "description": "Description",
            "debit": "Debit",
            "credit": "Credit",
            "balance": "Balance",
            "category": "Category",
            "bank": "Bank",
            "account": "Account"
        }


class TemplateRegistry:
    """Registry for export templates.

    Manages all available export templates.
    """

    def __init__(self):
        self._templates: Dict[str, ExportTemplate] = {}

        # Register standard template by default
        self.register(StandardTemplate())

    def register(self, template: ExportTemplate):
        """Register an export template.

        Args:
            template: ExportTemplate instance
        """
        self._templates[template.template_code] = template

    def get_template(self, template_code: str) -> Optional[ExportTemplate]:
        """Get template by code.

        Args:
            template_code: Template code (e.g., 'icost', 'standard')

        Returns:
            ExportTemplate instance or None
        """
        return self._templates.get(template_code)

    def list_templates(self) -> List[Dict[str, Any]]:
        """List all registered templates.

        Returns:
            List of template metadata
        """
        return [template.get_metadata() for template in self._templates.values()]


# Global registry instance
registry = TemplateRegistry()
