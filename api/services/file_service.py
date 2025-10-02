"""File processing service layer."""

import os
import time
from typing import Optional, List, Dict, Any
from datetime import datetime
import pdfplumber
from sqlalchemy.orm import Session

from api.core.config import settings
from api.core.models import User, File, Transaction, BankAccount
from api.core.processors.registry import get_processor_registry


class FileService:
    """Service for file processing operations."""

    @staticmethod
    def save_uploaded_file(file_content: bytes, filename: str, user: User, db: Session) -> File:
        """Save uploaded file and create database record.

        Args:
            file_content: File binary content
            filename: Original filename
            user: User uploading the file
            db: Database session

        Returns:
            Created File object
        """
        # Generate unique filename
        timestamp = int(time.time())
        safe_filename = f"{user.id}_{timestamp}_{filename}"
        file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

        # Save file to disk
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Create database record
        file_record = File(
            user_id=user.id,
            filename=safe_filename,
            original_filename=filename,
            file_path=file_path,
            file_size=len(file_content),
            file_type="pdf",
            status="uploaded"
        )

        db.add(file_record)
        db.commit()
        db.refresh(file_record)

        return file_record

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text
        """
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    @staticmethod
    def process_file(file_id: int, user: User, db: Session, use_ai: bool = False) -> Dict[str, Any]:
        """Process uploaded file with bank processor.

        Args:
            file_id: File ID to process
            user: User who owns the file
            db: Database session
            use_ai: Whether to use AI for additional processing

        Returns:
            Processing result dict

        Raises:
            ValueError: If file not found or processing fails
        """
        start_time = time.time()

        # Get file record
        file_record = db.query(File).filter(
            File.id == file_id,
            File.user_id == user.id
        ).first()

        if not file_record:
            raise ValueError("File not found")

        if file_record.status == "processing":
            raise ValueError("File is already being processed")

        try:
            # Update status
            file_record.status = "processing"
            db.commit()

            # Extract text from PDF
            pdf_text = FileService.extract_text_from_pdf(file_record.file_path)

            # Get appropriate processor
            registry = get_processor_registry()
            processor = registry.get_processor(pdf_text)

            if not processor:
                raise ValueError("Could not detect bank type from statement")

            # Process with bank processor
            result = processor.process(pdf_text)

            # Update file record with bank info
            file_record.bank = result["bank"]
            file_record.bank_code = result["bank_code"]

            # Extract metadata
            metadata = result["metadata"]
            if metadata.get("statement_period"):
                file_record.statement_period_start = metadata["statement_period"].get("start")
                file_record.statement_period_end = metadata["statement_period"].get("end")

            # Find or create bank account
            bank_account = FileService._find_or_create_bank_account(
                user=user,
                bank=result["bank"],
                bank_code=result["bank_code"],
                account_type=metadata.get("account_type", "checking"),
                account_last4=metadata.get("account_number", "0000"),
                db=db
            )

            file_record.bank_account_id = bank_account.id

            # Save transactions
            transactions = []
            for trans_data in result["transactions"]:
                transaction = Transaction(
                    file_id=file_record.id,
                    bank_account_id=bank_account.id,
                    transaction_date=trans_data["date"],
                    description=trans_data["description"],
                    amount=trans_data["amount"],
                    balance=trans_data.get("balance", 0.0),
                    category=trans_data.get("category"),
                    ai_processed=use_ai
                )
                db.add(transaction)
                transactions.append(transaction)

            file_record.transaction_count = len(transactions)
            file_record.status = "completed"
            file_record.processed_at = datetime.utcnow()
            file_record.processing_time = time.time() - start_time

            db.commit()

            # Prepare response
            return {
                "file_id": file_record.id,
                "status": "completed",
                "bank": result["bank"],
                "bank_code": result["bank_code"],
                "transaction_count": len(transactions),
                "metadata": metadata,
                "processing_time": file_record.processing_time
            }

        except Exception as e:
            # Update status on error
            file_record.status = "failed"
            file_record.error_message = str(e)
            file_record.processing_time = time.time() - start_time
            db.commit()
            raise

    @staticmethod
    def _find_or_create_bank_account(
        user: User,
        bank: str,
        bank_code: str,
        account_type: str,
        account_last4: str,
        db: Session
    ) -> BankAccount:
        """Find existing or create new bank account.

        Args:
            user: User object
            bank: Bank name
            bank_code: Bank code
            account_type: Account type
            account_last4: Last 4 digits
            db: Database session

        Returns:
            BankAccount object
        """
        # Try to find existing account
        account = db.query(BankAccount).filter(
            BankAccount.user_id == user.id,
            BankAccount.bank_code == bank_code,
            BankAccount.account_last4 == account_last4
        ).first()

        if account:
            account.last_statement_date = datetime.utcnow()
            db.commit()
            return account

        # Create new account
        account = BankAccount(
            user_id=user.id,
            bank=bank,
            bank_code=bank_code,
            account_type=account_type,
            account_last4=account_last4,
            account_name=f"{bank} {account_type.title()} ****{account_last4}",
            is_active=True
        )

        db.add(account)
        db.commit()
        db.refresh(account)

        return account

    @staticmethod
    def get_user_files(user: User, db: Session, skip: int = 0, limit: int = 100) -> List[File]:
        """Get user's uploaded files.

        Args:
            user: User object
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of File objects
        """
        return db.query(File).filter(
            File.user_id == user.id
        ).order_by(File.uploaded_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_file_transactions(file_id: int, user: User, db: Session) -> List[Transaction]:
        """Get transactions for a file.

        Args:
            file_id: File ID
            user: User object
            db: Database session

        Returns:
            List of Transaction objects
        """
        file_record = db.query(File).filter(
            File.id == file_id,
            File.user_id == user.id
        ).first()

        if not file_record:
            raise ValueError("File not found")

        return db.query(Transaction).filter(
            Transaction.file_id == file_id
        ).order_by(Transaction.transaction_date).all()

    @staticmethod
    def delete_file(file_id: int, user: User, db: Session):
        """Delete file and associated data.

        Args:
            file_id: File ID
            user: User object
            db: Database session
        """
        file_record = db.query(File).filter(
            File.id == file_id,
            File.user_id == user.id
        ).first()

        if not file_record:
            raise ValueError("File not found")

        # Delete physical file
        if os.path.exists(file_record.file_path):
            os.remove(file_record.file_path)

        # Delete output file if exists
        if file_record.output_file_path and os.path.exists(file_record.output_file_path):
            os.remove(file_record.output_file_path)

        # Delete database record (cascade will handle transactions)
        db.delete(file_record)
        db.commit()
