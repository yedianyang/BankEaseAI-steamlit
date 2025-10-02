"""iCost export template."""

from typing import Dict, List, Any
import pandas as pd
from datetime import datetime

from .base import ExportTemplate


class ICostTemplate(ExportTemplate):
    """Export template for iCost accounting software.

    iCost format requirements:
    - Date format: YYYYMMDD (e.g., 20250115)
    - Debit/Credit separated columns
    - Specific column names in Chinese
    """

    template_name = "iCost"
    template_code = "icost"
    description = "iCost会计软件导出格式"
    supported_formats = ["csv", "excel"]

    def transform(self, transactions: List[Dict[str, Any]]) -> pd.DataFrame:
        """Transform to iCost format.

        Args:
            transactions: Standardized transaction list

        Returns:
            DataFrame in iCost format
        """
        self.validate_data(transactions)

        data = []
        for trans in transactions:
            # Parse date
            date_val = trans["date"]
            if isinstance(date_val, datetime):
                date_str = date_val.strftime("%Y%m%d")
            elif isinstance(date_val, str):
                # Try to parse and reformat
                try:
                    dt = datetime.strptime(date_val, "%Y-%m-%d")
                    date_str = dt.strftime("%Y%m%d")
                except:
                    date_str = date_val.replace("-", "")
            else:
                date_str = ""

            # Calculate debit/credit
            amount = float(trans["amount"])
            debit = abs(amount) if amount < 0 else 0.00
            credit = amount if amount > 0 else 0.00

            # Balance
            balance = float(trans.get("balance", 0.0))

            data.append({
                "日期": date_str,
                "摘要": trans["description"],
                "借方": f"{debit:.2f}",
                "贷方": f"{credit:.2f}",
                "余额": f"{balance:.2f}"
            })

        return pd.DataFrame(data)

    def get_column_mapping(self) -> Dict[str, str]:
        """Get iCost column mapping.

        Returns:
            Column name mapping
        """
        return {
            "date": "日期",
            "description": "摘要",
            "debit": "借方",
            "credit": "贷方",
            "balance": "余额"
        }
