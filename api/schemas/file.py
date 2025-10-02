"""File processing schemas."""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class FileUploadResponse(BaseModel):
    """File upload response schema."""
    id: int
    filename: str
    file_size: int
    status: str
    bank: Optional[str]
    uploaded_at: datetime

    class Config:
        from_attributes = True


class FileProcessRequest(BaseModel):
    """File processing request schema."""
    file_id: int
    use_ai: bool = True
    export_template: str = "standard"


class TransactionResponse(BaseModel):
    """Transaction response schema."""
    id: int
    transaction_date: datetime
    description: str
    amount: float
    balance: Optional[float]
    category: Optional[str]

    class Config:
        from_attributes = True


class FileProcessResponse(BaseModel):
    """File processing result schema."""
    file_id: int
    status: str
    bank: str
    bank_code: str
    transaction_count: int
    transactions: List[TransactionResponse]
    metadata: Dict[str, Any]
    output_file_path: Optional[str]


class FileListResponse(BaseModel):
    """File list item schema."""
    id: int
    filename: str
    original_filename: str
    file_size: int
    status: str
    bank: Optional[str]
    transaction_count: int
    uploaded_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ExportRequest(BaseModel):
    """Export request schema."""
    file_id: int
    template: str = "standard"  # standard, icost, kingdee, yonyou
    format: str = "csv"  # csv, excel
