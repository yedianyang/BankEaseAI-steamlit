# api/services/user_service.py
from typing import Dict, Any
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from script.utils.simple_auth import SimpleAuthManager
from api.models.schemas import UserUpdate

class UserService:
    """用户管理服务"""
    
    def __init__(self):
        self.auth_manager = SimpleAuthManager()
    
    async def update_user_profile(self, user_id: int, user_update: UserUpdate) -> Dict[str, Any]:
        """更新用户资料"""
        # 这里应该实现用户资料更新逻辑
        # 目前简化处理
        user = self.auth_manager.get_user_by_username("current_user")
        if user:
            return user
        else:
            raise ValueError("用户不存在")
    
    async def get_user_usage(self, user_id: int) -> Dict[str, Any]:
        """获取用户使用量"""
        # 获取本月使用量
        from datetime import datetime
        current_month = datetime.now().strftime('%Y-%m')
        monthly_usage = self.auth_manager.get_user_usage(user_id, 'pdf_conversion', current_month)
        
        # 获取总使用量
        total_usage = self.auth_manager.get_user_usage(user_id, 'pdf_conversion')
        
        # 获取计划限制
        user = self.auth_manager.get_user_by_username("current_user")  # 简化处理
        plan_limits = self.auth_manager.get_plan_limits(user["plan"] if user else "free")
        
        # 计算剩余额度
        remaining = plan_limits["max_files"] - monthly_usage
        
        return {
            "monthly_usage": monthly_usage,
            "total_usage": total_usage,
            "plan_limits": plan_limits,
            "remaining": remaining
        }
    
    async def check_user_permissions(self, user_id: int, file_count: int) -> bool:
        """检查用户权限"""
        return self.auth_manager.can_user_process_files(user_id, file_count)
    
    async def delete_user_account(self, user_id: int) -> bool:
        """删除用户账户"""
        # 这里应该实现用户账户删除逻辑
        # 目前简化处理
        return True
