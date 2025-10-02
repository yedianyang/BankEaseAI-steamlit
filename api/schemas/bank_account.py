"""Bank account schemas."""

from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


class BankAccountCreate(BaseModel):
    """Bank account creation schema."""
    bank: str
    bank_code: str
    account_type: str  # checking, savings, credit
    account_last4: str
    account_name: Optional[str] = None
    currency: str = "USD"
    is_primary: bool = False

    @validator('account_last4')
    def validate_last4(cls, v):
        if not v.isdigit() or len(v) != 4:
            raise ValueError('account_last4 must be exactly 4 digits')
        return v


class BankAccountUpdate(BaseModel):
    """Bank account update schema."""
    account_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_primary: Optional[bool] = None


class BankAccountResponse(BaseModel):
    """Bank account response schema."""
    id: int
    bank: str
    bank_code: str
    account_type: str
    account_last4: str
    account_name: Optional[str]
    currency: str
    is_active: bool
    is_primary: bool
    created_at: datetime
    last_statement_date: Optional[datetime]

    class Config:
        from_attributes = True
