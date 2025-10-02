"""Bank account management routes."""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List

from api.core.database import get_db
from api.core.dependencies import get_current_active_user
from api.core.models import User, BankAccount
from api.schemas import BankAccountCreate, BankAccountUpdate, BankAccountResponse

router = APIRouter()


@router.get("/", response_model=List[BankAccountResponse])
async def list_bank_accounts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of user's bank accounts.

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        List of bank accounts
    """
    accounts = db.query(BankAccount).filter(
        BankAccount.user_id == current_user.id
    ).order_by(BankAccount.is_primary.desc(), BankAccount.created_at.desc()).all()

    return accounts


@router.post("/", response_model=BankAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_bank_account(
    account_data: BankAccountCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new bank account.

    Args:
        account_data: Bank account data
        current_user: Authenticated user
        db: Database session

    Returns:
        Created bank account

    Raises:
        HTTPException: If account already exists
    """
    # Check if account already exists
    existing = db.query(BankAccount).filter(
        BankAccount.user_id == current_user.id,
        BankAccount.bank_code == account_data.bank_code,
        BankAccount.account_last4 == account_data.account_last4
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bank account already exists"
        )

    # Create account
    account = BankAccount(
        user_id=current_user.id,
        bank=account_data.bank,
        bank_code=account_data.bank_code,
        account_type=account_data.account_type,
        account_last4=account_data.account_last4,
        account_name=account_data.account_name,
        currency=account_data.currency,
        is_primary=account_data.is_primary,
        is_active=True
    )

    # If this is set as primary, unset others
    if account.is_primary:
        db.query(BankAccount).filter(
            BankAccount.user_id == current_user.id,
            BankAccount.is_primary == True
        ).update({"is_primary": False})

    db.add(account)
    db.commit()
    db.refresh(account)

    return account


@router.put("/{account_id}", response_model=BankAccountResponse)
async def update_bank_account(
    account_id: int,
    account_data: BankAccountUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update bank account details.

    Args:
        account_id: Account ID to update
        account_data: Updated account data
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated bank account

    Raises:
        HTTPException: If account not found
    """
    account = db.query(BankAccount).filter(
        BankAccount.id == account_id,
        BankAccount.user_id == current_user.id
    ).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank account not found"
        )

    # Update fields
    if account_data.account_name is not None:
        account.account_name = account_data.account_name

    if account_data.is_active is not None:
        account.is_active = account_data.is_active

    if account_data.is_primary is not None:
        if account_data.is_primary:
            # Unset other primary accounts
            db.query(BankAccount).filter(
                BankAccount.user_id == current_user.id,
                BankAccount.id != account_id,
                BankAccount.is_primary == True
            ).update({"is_primary": False})

        account.is_primary = account_data.is_primary

    db.commit()
    db.refresh(account)

    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bank_account(
    account_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a bank account.

    Args:
        account_id: Account ID to delete
        current_user: Authenticated user
        db: Database session

    Raises:
        HTTPException: If account not found
    """
    account = db.query(BankAccount).filter(
        BankAccount.id == account_id,
        BankAccount.user_id == current_user.id
    ).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank account not found"
        )

    db.delete(account)
    db.commit()


@router.get("/{account_id}", response_model=BankAccountResponse)
async def get_bank_account(
    account_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get bank account details.

    Args:
        account_id: Account ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Bank account details

    Raises:
        HTTPException: If account not found
    """
    account = db.query(BankAccount).filter(
        BankAccount.id == account_id,
        BankAccount.user_id == current_user.id
    ).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank account not found"
        )

    return account
