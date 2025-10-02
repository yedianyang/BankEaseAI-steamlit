"""File processing routes - Refactored version."""

from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os

from api.core.database import get_db
from api.core.dependencies import get_current_active_user
from api.core.models import User
from api.schemas import (
    FileUploadResponse,
    FileProcessRequest,
    FileProcessResponse,
    FileListResponse,
    ExportRequest,
    TransactionResponse
)
from api.services.file_service import FileService
from api.services.export_service import ExportService

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload a PDF bank statement.

    Args:
        file: Uploaded PDF file
        current_user: Authenticated user
        db: Database session

    Returns:
        File upload details

    Raises:
        HTTPException: If upload fails
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )

    # Read file content
    content = await file.read()

    # Check file size
    if len(content) > 50 * 1024 * 1024:  # 50MB
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds 50MB limit"
        )

    try:
        file_record = FileService.save_uploaded_file(
            file_content=content,
            filename=file.filename,
            user=current_user,
            db=db
        )
        return file_record

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )


@router.post("/process", response_model=FileProcessResponse)
async def process_file(
    request: FileProcessRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process uploaded file to extract transactions.

    Args:
        request: Processing request
        current_user: Authenticated user
        db: Database session

    Returns:
        Processing results

    Raises:
        HTTPException: If processing fails
    """
    try:
        result = FileService.process_file(
            file_id=request.file_id,
            user=current_user,
            db=db,
            use_ai=request.use_ai
        )
        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing failed: {str(e)}"
        )


@router.get("/list", response_model=List[FileListResponse])
async def list_files(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of user's uploaded files.

    Args:
        skip: Number of records to skip
        limit: Maximum records to return
        current_user: Authenticated user
        db: Database session

    Returns:
        List of files
    """
    files = FileService.get_user_files(current_user, db, skip, limit)
    return files


@router.get("/{file_id}/transactions", response_model=List[TransactionResponse])
async def get_file_transactions(
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get transactions for a specific file.

    Args:
        file_id: File ID
        current_user: Authenticated user
        db: Database session

    Returns:
        List of transactions

    Raises:
        HTTPException: If file not found
    """
    try:
        transactions = FileService.get_file_transactions(file_id, current_user, db)
        return transactions

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/export")
async def export_file(
    request: ExportRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Export file transactions to specified format.

    Args:
        request: Export request
        current_user: Authenticated user
        db: Database session

    Returns:
        File download response

    Raises:
        HTTPException: If export fails
    """
    try:
        output_path = ExportService.export_file(
            file_id=request.file_id,
            user=current_user,
            db=db,
            template=request.template,
            output_format=request.format
        )

        if not os.path.exists(output_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exported file not found"
            )

        return FileResponse(
            path=output_path,
            filename=os.path.basename(output_path),
            media_type="application/octet-stream"
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}"
        )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a file and its associated data.

    Args:
        file_id: File ID to delete
        current_user: Authenticated user
        db: Database session

    Raises:
        HTTPException: If deletion fails
    """
    try:
        FileService.delete_file(file_id, current_user, db)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deletion failed: {str(e)}"
        )


@router.get("/templates")
async def list_export_templates():
    """List all available export templates.

    Returns:
        List of export template metadata
    """
    return ExportService.list_templates()
