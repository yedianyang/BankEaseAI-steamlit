"""Authentication routes - Refactored version."""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.core.dependencies import get_current_active_user
from api.core.models import User
from api.schemas import UserCreate, UserLogin, UserResponse, Token
from api.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        Created user details

    Raises:
        HTTPException: If registration fails
    """
    try:
        user = AuthService.register_user(
            db=db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        return user

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """User login with username and password.

    Args:
        form_data: OAuth2 form data with username and password
        db: Database session

    Returns:
        Access token and user details

    Raises:
        HTTPException: If authentication fails
    """
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    AuthService.update_last_login(db, user)

    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = AuthService.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information.

    Args:
        current_user: Authenticated user from token

    Returns:
        Current user details
    """
    return current_user


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """User logout.

    In a production system, you would add the token to a blacklist here.

    Args:
        current_user: Authenticated user

    Returns:
        Success message
    """
    return {"message": "Successfully logged out"}
