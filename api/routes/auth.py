# api/routes/auth.py
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from api.models.schemas import UserCreate, UserLogin, UserResponse, Token, APIResponse
# 暂时注释掉导入，避免循环依赖
# from api.middleware.auth import authenticate_user, create_access_token, get_current_user
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from script.utils.simple_auth import SimpleAuthManager

router = APIRouter()
auth_manager = SimpleAuthManager()

# JWT配置
ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.post("/register", response_model=APIResponse)
async def register(user_data: UserCreate):
    """用户注册"""
    try:
        # 检查用户名是否已存在
        existing_user = auth_manager.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 注册用户
        success = auth_manager.register_user(
            user_data.username,
            user_data.password,
            user_data.email
        )
        
        if success:
            return APIResponse(
                success=True,
                message="注册成功",
                data={"username": user_data.username}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="注册失败，用户名或邮箱可能已存在"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册过程中发生错误: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """用户登录"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
        plan=current_user["plan"],
        created_at=current_user.get("created_at", "2025-01-01T00:00:00")
    )

@router.post("/logout", response_model=APIResponse)
async def logout(current_user = Depends(get_current_user)):
    """用户登出"""
    # 在实际应用中，这里可以将token加入黑名单
    return APIResponse(
        success=True,
        message="登出成功"
    )
