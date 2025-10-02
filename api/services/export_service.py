"""Export service layer."""

import os
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from api.core.config import settings
from api.core.models import User, File, Transaction
from api.core.exporters.base import registry
from api.core.exporters.icost import ICostTemplate


class ExportService:
    """Service for exporting transaction data."""

    @staticmethod
    def _initialize_templates():
        """Initialize and register export templates."""
        # Register iCost template
        if not registry.get_template("icost"):
            registry.register(ICostTemplate())

    @staticmethod
    def export_file(
        file_id: int,
        user: User,
        db: Session,
        template: str = "standard",
        output_format: str = "csv"
    ) -> str:
        """Export file transactions to specified format.

        Args:
            file_id: File ID
            user: User object
            db: Database session
            template: Export template code (standard, icost, etc.)
            output_format: Output format (csv, excel)

        Returns:
            Path to exported file

        Raises:
            ValueError: If file not found or template invalid
        """
        # Initialize templates
        ExportService._initialize_templates()

        # Get file record
        file_record = db.query(File).filter(
            File.id == file_id,
            File.user_id == user.id
        ).first()

        if not file_record:
            raise ValueError("File not found")

        if file_record.status != "completed":
            raise ValueError("File has not been processed yet")

        # Get transactions
        transactions = db.query(Transaction).filter(
            Transaction.file_id == file_id
        ).order_by(Transaction.transaction_date).all()

        if not transactions:
            raise ValueError("No transactions found")

        # Convert to dict format
        trans_dicts = []
        for trans in transactions:
            trans_dicts.append({
                "date": trans.transaction_date,
                "description": trans.description,
                "amount": trans.amount,
                "balance": trans.balance or 0.0,
                "category": trans.category,
                "bank": file_record.bank,
                "account_last4": file_record.bank_account.account_last4 if file_record.bank_account else ""
            })

        # Get export template
        export_template = registry.get_template(template)
        if not export_template:
            raise ValueError(f"Export template '{template}' not found")

        # Transform data
        df = export_template.transform(trans_dicts)

        # Generate output filename
        timestamp = file_record.processed_at.strftime("%Y%m%d_%H%M%S")
        output_filename = f"{file_record.bank_code}_{timestamp}_{template}.{output_format}"
        output_path = os.path.join(settings.OUTPUT_DIR, output_filename)

        # Export based on format
        if output_format == "csv":
            export_template.export_to_csv(df, output_path)
        elif output_format == "excel":
            output_path = output_path.replace(".excel", ".xlsx")
            export_template.export_to_excel(df, output_path)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

        # Update file record
        file_record.output_file_path = output_path
        file_record.output_format = output_format
        file_record.export_template = template
        db.commit()

        return output_path

    @staticmethod
    def list_templates() -> List[Dict[str, Any]]:
        """List all available export templates.

        Returns:
            List of template metadata
        """
        ExportService._initialize_templates()
        return registry.list_templates()
