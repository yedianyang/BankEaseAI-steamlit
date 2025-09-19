# api/services/dashboard_service.py
from typing import Dict, Any
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from script.utils.simple_auth import SimpleAuthManager
from api.models.schemas import DashboardStats, UserResponse, UsageResponse

class DashboardService:
    """仪表板服务"""
    
    def __init__(self):
        self.auth_manager = SimpleAuthManager()
    
    async def get_dashboard_stats(self, user_id: int) -> DashboardStats:
        """获取仪表板统计数据"""
        # 获取用户信息
        user = self.auth_manager.get_user_by_username("current_user")  # 简化处理
        user_info = UserResponse(
            id=user_id,
            username=user["username"] if user else "unknown",
            email=user["email"] if user else "unknown@example.com",
            plan=user["plan"] if user else "free",
            created_at="2025-01-01T00:00:00"
        )
        
        # 获取使用量统计
        usage_stats = await self._get_usage_stats(user_id)
        
        # 获取数据库统计
        database_stats = self.auth_manager.get_database_stats()
        
        return DashboardStats(
            user_info=user_info,
            usage_stats=usage_stats,
            database_stats=database_stats
        )
    
    async def _get_usage_stats(self, user_id: int) -> UsageResponse:
        """获取使用量统计"""
        from datetime import datetime
        
        # 获取本月使用量
        current_month = datetime.now().strftime('%Y-%m')
        monthly_usage = self.auth_manager.get_user_usage(user_id, 'pdf_conversion', current_month)
        
        # 获取总使用量
        total_usage = self.auth_manager.get_user_usage(user_id, 'pdf_conversion')
        
        # 获取计划限制
        user = self.auth_manager.get_user_by_username("current_user")  # 简化处理
        plan_limits = self.auth_manager.get_plan_limits(user["plan"] if user else "free")
        
        # 计算剩余额度
        remaining = plan_limits["max_files"] - monthly_usage
        
        return UsageResponse(
            monthly_usage=monthly_usage,
            total_usage=total_usage,
            plan_limits=plan_limits,
            remaining=remaining
        )
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        return self.auth_manager.get_database_stats()
    
    async def get_recent_activity(self, user_id: int) -> Dict[str, Any]:
        """获取最近活动"""
        # 这里应该实现最近活动查询逻辑
        # 目前返回模拟数据
        return {
            "recent_files": [],
            "recent_logins": [],
            "activity_summary": {
                "total_files_processed": 0,
                "last_activity": "2025-01-01T00:00:00"
            }
        }
