"""Dashboard routes - User statistics and overview."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from api.core.database import get_db
from api.core.dependencies import get_current_active_user
from api.core.models import User, File, Transaction, UsageLog

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics for current user.

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        Dashboard statistics including usage and database stats
    """
    # 获取用户的使用量限制
    tier_limits = {
        "free": 10,
        "basic": 100,
        "pro": 1000
    }
    max_files = tier_limits.get(current_user.tier.lower(), 10)

    # 计算剩余额度
    remaining = max_files - current_user.monthly_usage_count

    # 基础响应数据
    response = {
        "user_info": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "plan": current_user.tier
        },
        "usage_stats": {
            "monthly_usage": current_user.monthly_usage_count,
            "total_usage": current_user.total_usage_count,
            "plan_limits": {
                "max_files": max_files
            },
            "remaining": remaining
        }
    }

    # 仅管理员可以看到数据库统计信息
    if current_user.is_admin:
        user_count = db.query(func.count(User.id)).scalar() or 0
        log_count = db.query(func.count(UsageLog.id)).scalar() or 0
        # 数据库大小（SQLite）- 简单返回0，生产环境可以实际计算
        db_size_mb = 0.0

        response["database_stats"] = {
            "user_count": user_count,
            "log_count": log_count,
            "db_size_mb": db_size_mb
        }

    return response


@router.get("/files")
async def get_user_files(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = 10,
    offset: int = 0
):
    """Get user's uploaded files.

    Args:
        current_user: Authenticated user
        db: Database session
        limit: Number of files to return
        offset: Pagination offset

    Returns:
        List of user's files with metadata
    """
    files = db.query(File).filter(
        File.user_id == current_user.id
    ).order_by(
        File.created_at.desc()
    ).limit(limit).offset(offset).all()

    total = db.query(func.count(File.id)).filter(
        File.user_id == current_user.id
    ).scalar()

    return {
        "files": [
            {
                "id": f.id,
                "filename": f.filename,
                "file_size": f.file_size,
                "status": f.status,
                "created_at": f.created_at.isoformat() if f.created_at else None,
                "processed_at": f.processed_at.isoformat() if f.processed_at else None,
                "error_message": f.error_message,
                "bank": f.bank,
                "transaction_count": f.transaction_count
            }
            for f in files
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/transactions")
async def get_user_transactions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """Get user's transactions from processed files.

    Args:
        current_user: Authenticated user
        db: Database session
        limit: Number of transactions to return
        offset: Pagination offset

    Returns:
        List of user's transactions
    """
    # 获取用户的所有文件ID
    file_ids = db.query(File.id).filter(File.user_id == current_user.id).all()
    file_ids = [f[0] for f in file_ids]

    # 获取这些文件的交易记录
    transactions = db.query(Transaction).filter(
        Transaction.file_id.in_(file_ids)
    ).order_by(
        Transaction.date.desc()
    ).limit(limit).offset(offset).all()

    total = db.query(func.count(Transaction.id)).filter(
        Transaction.file_id.in_(file_ids)
    ).scalar()

    return {
        "transactions": [
            {
                "id": t.id,
                "date": t.date.isoformat() if t.date else None,
                "description": t.description,
                "amount": float(t.amount) if t.amount else 0.0,
                "balance": float(t.balance) if t.balance else 0.0,
                "category": t.category,
                "file_id": t.file_id
            }
            for t in transactions
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }
