# api/routes/dashboard.py
from fastapi import APIRouter, Depends
from api.models.schemas import DashboardStats, APIResponse
from api.middleware.auth import get_current_user
from api.services.dashboard_service import DashboardService
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

router = APIRouter()
dashboard_service = DashboardService()

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(current_user = Depends(get_current_user)):
    """获取仪表板统计数据"""
    try:
        stats = await dashboard_service.get_dashboard_stats(current_user["id"])
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取仪表板数据失败: {str(e)}"
        )

@router.get("/database-stats")
async def get_database_stats(current_user = Depends(get_current_user)):
    """获取数据库统计信息"""
    try:
        db_stats = await dashboard_service.get_database_stats()
        
        return APIResponse(
            success=True,
            message="获取数据库统计成功",
            data=db_stats
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取数据库统计失败: {str(e)}"
        )

@router.get("/recent-activity")
async def get_recent_activity(current_user = Depends(get_current_user)):
    """获取最近活动"""
    try:
        activity = await dashboard_service.get_recent_activity(current_user["id"])
        
        return APIResponse(
            success=True,
            message="获取最近活动成功",
            data=activity
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取最近活动失败: {str(e)}"
        )
