"""Database models for BankEaseAI."""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

from .database import Base


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))

    # User tier and status
    tier = Column(String(20), default="free")  # free, basic, pro
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)

    # Usage tracking
    monthly_usage_count = Column(Integer, default=0)
    total_usage_count = Column(Integer, default=0)
    last_usage_reset = Column(DateTime, default=func.now())

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime)

    # Relationships
    bank_accounts = relationship("BankAccount", back_populates="user", cascade="all, delete-orphan")
    files = relationship("File", back_populates="user", cascade="all, delete-orphan")
    usage_logs = relationship("UsageLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', tier='{self.tier}')>"


class BankAccount(Base):
    """Bank account model for tracking user's bank accounts."""

    __tablename__ = "bank_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Bank information
    bank = Column(String(50), nullable=False)  # BOFA, Chase, Amex, etc.
    bank_code = Column(String(20), nullable=False, index=True)
    account_type = Column(String(50), nullable=False)  # checking, savings, credit

    # Account identification
    account_number = Column(String(255))  # Encrypted full account number
    account_last4 = Column(String(4), nullable=False)  # Last 4 digits (plain text)
    account_name = Column(String(100))  # User-defined alias (e.g., "Primary Checking")

    # Account details
    currency = Column(String(10), default="USD")

    # Status
    is_active = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    last_statement_date = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="bank_accounts")
    files = relationship("File", back_populates="bank_account")
    transactions = relationship("Transaction", back_populates="bank_account", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<BankAccount(id={self.id}, bank='{self.bank}', last4='****{self.account_last4}')>"


class File(Base):
    """Uploaded file model."""

    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    bank_account_id = Column(Integer, ForeignKey("bank_accounts.id"), index=True)

    # File information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    file_type = Column(String(50), default="pdf")

    # Processing information
    status = Column(String(50), default="uploaded")  # uploaded, processing, completed, failed
    bank = Column(String(50))  # Detected bank
    bank_code = Column(String(20))

    # Statement metadata
    statement_period_start = Column(DateTime)
    statement_period_end = Column(DateTime)
    transaction_count = Column(Integer, default=0)

    # Processing results
    output_file_path = Column(String(512))
    output_format = Column(String(20))  # csv, excel
    export_template = Column(String(50))  # standard, icost, kingdee, yonyou

    # Error tracking
    error_message = Column(Text)
    processing_time = Column(Float)  # in seconds

    # Timestamps
    uploaded_at = Column(DateTime, default=func.now(), nullable=False)
    processed_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="files")
    bank_account = relationship("BankAccount", back_populates="files")
    transactions = relationship("Transaction", back_populates="file", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<File(id={self.id}, filename='{self.filename}', status='{self.status}')>"


class Transaction(Base):
    """Transaction record model."""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False, index=True)
    bank_account_id = Column(Integer, ForeignKey("bank_accounts.id"), index=True)

    # Transaction details
    transaction_date = Column(DateTime, nullable=False, index=True)
    post_date = Column(DateTime)
    description = Column(Text, nullable=False)
    amount = Column(Float, nullable=False)  # Negative for debit, positive for credit
    balance = Column(Float)

    # Categorization
    category = Column(String(100))
    merchant = Column(String(255))

    # Transaction type
    transaction_type = Column(String(50))  # debit, credit, fee, interest, etc.

    # AI processing
    ai_processed = Column(Boolean, default=False)
    ai_category = Column(String(100))
    ai_confidence = Column(Float)

    # Metadata
    raw_text = Column(Text)  # Original text from PDF
    extra_data = Column(JSON)  # Additional data

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    file = relationship("File", back_populates="transactions")
    bank_account = relationship("BankAccount", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction(id={self.id}, date={self.transaction_date}, amount={self.amount})>"


class UsageLog(Base):
    """Usage log model for tracking API usage."""

    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Action tracking
    action = Column(String(100), nullable=False)  # upload, process, export, etc.
    endpoint = Column(String(255))
    method = Column(String(10))  # GET, POST, etc.

    # Request details
    file_size = Column(Integer)
    processing_time = Column(Float)

    # AI usage
    ai_provider = Column(String(50))
    ai_model = Column(String(100))
    tokens_used = Column(Integer)
    estimated_cost = Column(Float)

    # Result
    status = Column(String(50))  # success, failed, error
    error_message = Column(Text)

    # Client information
    ip_address = Column(String(50))
    user_agent = Column(String(255))

    # Timestamp
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="usage_logs")

    def __repr__(self):
        return f"<UsageLog(id={self.id}, user_id={self.user_id}, action='{self.action}')>"
