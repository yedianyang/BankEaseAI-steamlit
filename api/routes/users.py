# api/routes/users.py
from fastapi import APIRouter, HTTPException, status, Depends
from api.models.schemas import UserResponse, UserUpdate, UsageResponse, APIResponse
from api.middleware.auth import get_current_user
from api.services.user_service import UserService
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

router = APIRouter()
user_service = UserService()

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user = Depends(get_current_user)):
    """获取用户资料"""
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
        plan=current_user["plan"],
        created_at=current_user.get("created_at", "2025-01-01T00:00:00")
    )

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user = Depends(get_current_user)
):
    """更新用户资料"""
    try:
        updated_user = await user_service.update_user_profile(
            current_user["id"], 
            user_update
        )
        
        return UserResponse(
            id=updated_user["id"],
            username=updated_user["username"],
            email=updated_user["email"],
            plan=updated_user["plan"],
            created_at=updated_user.get("created_at", "2025-01-01T00:00:00")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户资料失败: {str(e)}"
        )

@router.get("/usage", response_model=UsageResponse)
async def get_user_usage(current_user = Depends(get_current_user)):
    """获取用户使用量"""
    try:
        usage_data = await user_service.get_user_usage(current_user["id"])
        
        return UsageResponse(
            monthly_usage=usage_data["monthly_usage"],
            total_usage=usage_data["total_usage"],
            plan_limits=usage_data["plan_limits"],
            remaining=usage_data["remaining"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取使用量失败: {str(e)}"
        )

@router.get("/permissions")
async def check_user_permissions(
    file_count: int = 1,
    current_user = Depends(get_current_user)
):
    """检查用户权限"""
    try:
        can_process = await user_service.check_user_permissions(
            current_user["id"], 
            file_count
        )
        
        return APIResponse(
            success=True,
            message="权限检查完成",
            data={
                "can_process": can_process,
                "file_count": file_count,
                "user_plan": current_user["plan"]
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"权限检查失败: {str(e)}"
        )

@router.delete("/account")
async def delete_account(current_user = Depends(get_current_user)):
    """删除用户账户"""
    try:
        success = await user_service.delete_user_account(current_user["id"])
        
        if success:
            return APIResponse(
                success=True,
                message="账户删除成功"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="账户删除失败"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除账户失败: {str(e)}"
        )
