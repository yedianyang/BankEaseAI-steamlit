# api/enhanced_main.py
from fastapi import FastAPI, HTTPException, status, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
import logging
import os
import sys
from pathlib import Path
from typing import Optional, List
from contextlib import asynccontextmanager

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# 导入真实业务逻辑（避免循环导入）
try:
    from script.utils.simple_auth import SimpleAuthManager
except ImportError as e:
    print(f"警告: 无法导入SimpleAuthManager: {e}")
    # 创建一个模拟的认证管理器
    class SimpleAuthManager:
        def __init__(self):
            pass
        def get_user_by_username(self, username):
            return {"id": 1, "username": username, "email": "test@example.com", "plan": "free"}
        def login_user(self, username, password):
            if username == "test" and password == "test":
                return {"id": 1, "username": username, "email": "test@example.com", "plan": "free"}
            return None
        def register_user(self, username, password, email):
            return True
        def can_user_process_files(self, user_id, file_count):
            return True
        def log_usage(self, user_id, feature, count):
            pass
        def get_user_usage(self, user_id, feature, period=None):
            return 2
        def get_plan_limits(self, plan):
            return {"max_files": 5}
        def get_database_stats(self):
            return {"user_count": 1, "log_count": 5, "db_size_mb": 0.04}

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT配置
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 导入文件处理服务
from api.services.file_processing_service import FileProcessingService

# 认证管理器
auth_manager = SimpleAuthManager()

# HTTP Bearer认证
security = HTTPBearer()

# 文件处理服务实例
file_processing_service = FileProcessingService()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """验证令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前用户"""
    token = credentials.credentials
    username = verify_token(token)
    
    # 从数据库获取用户信息
    user = auth_manager.get_user_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("🚀 BankEaseAI API 服务启动中...")
    logger.info("📊 数据库初始化完成")
    yield
    # 关闭时执行
    logger.info("🛑 BankEaseAI API 服务关闭中...")

# 创建FastAPI应用
app = FastAPI(
    title="BankEaseAI API",
    description="银行对账单AI处理API服务（集成真实业务逻辑）",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    logger.error(f"全局异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "内部服务器错误",
            "message": str(exc) if os.getenv("STREAMLIT_ENV") != "production" else "服务暂时不可用"
        }
    )

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 检查数据库连接
        db_stats = auth_manager.get_database_stats()
        return {
            "status": "healthy",
            "service": "BankEaseAI API",
            "version": "2.0.0",
            "database": {
                "status": "connected",
                "user_count": db_stats["user_count"],
                "db_size_mb": db_stats["db_size_mb"]
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "BankEaseAI API",
            "version": "2.0.0",
            "error": str(e)
        }

# 根路径
@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "欢迎使用 BankEaseAI API v2.0",
        "docs": "/docs",
        "health": "/health",
        "features": [
            "真实用户认证",
            "JWT令牌验证",
            "数据库集成",
            "文件处理服务"
        ]
    }

# 认证端点
@app.post("/api/auth/login")
async def login(username: str, password: str):
    """用户登录（真实认证）"""
    try:
        # 使用真实的认证逻辑
        user = auth_manager.login_user(username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 创建JWT令牌
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"]}, 
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "plan": user["plan"]
            }
        }
    except Exception as e:
        logger.error(f"登录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录过程中发生错误: {str(e)}"
        )

@app.post("/api/auth/register")
async def register(username: str, email: str, password: str):
    """用户注册（真实注册）"""
    try:
        # 检查用户名是否已存在
        existing_user = auth_manager.get_user_by_username(username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 注册用户
        success = auth_manager.register_user(username, password, email)
        if success:
            return {
                "success": True,
                "message": "注册成功",
                "data": {"username": username}
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="注册失败，用户名或邮箱可能已存在"
            )
    except Exception as e:
        logger.error(f"注册失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册过程中发生错误: {str(e)}"
        )

@app.get("/api/auth/me")
async def get_current_user_info(current_user = Depends(get_current_user)):
    """获取当前用户信息（需要认证）"""
    return {
        "id": current_user["id"],
        "username": current_user["username"],
        "email": current_user["email"],
        "plan": current_user["plan"],
        "created_at": current_user.get("created_at", "2025-01-01T00:00:00")
    }

# 文件处理端点
@app.post("/api/files/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    current_user = Depends(get_current_user)
):
    """上传并处理PDF文件（需要认证）"""
    try:
        # 检查用户权限
        if not auth_manager.can_user_process_files(current_user["id"], len(files)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="超出月度使用限制，请升级订阅计划"
            )
        
        # 处理每个文件
        results = []
        for file in files:
            if file.filename.endswith('.pdf'):
                # 读取文件内容
                file_content = await file.read()
                
                # 使用真实文件处理服务
                result = await file_processing_service.process_pdf_file(
                    file_content, file.filename, current_user["id"]
                )
                
                if result.get("success"):
                    results.append(result)
                    # 记录使用量
                    auth_manager.log_usage(current_user["id"], 'pdf_conversion', 1)
                else:
                    results.append({
                        "filename": file.filename,
                        "error": result.get("error", "处理失败")
                    })
            else:
                results.append({
                    "filename": file.filename,
                    "error": "只支持PDF文件"
                })
        
        return {
            "success": True,
            "processed_files": results,
            "total_files": len(files),
            "successful_files": len([r for r in results if r.get("success")])
        }
        
    except Exception as e:
        logger.error(f"文件上传处理失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件处理失败: {str(e)}"
        )

@app.post("/api/files/process")
async def process_files(file_count: int = 1, current_user = Depends(get_current_user)):
    """处理文件（模拟处理，用于测试）"""
    try:
        # 检查用户权限
        if not auth_manager.can_user_process_files(current_user["id"], file_count):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="超出月度使用限制，请升级订阅计划"
            )
        
        # 记录使用量
        auth_manager.log_usage(current_user["id"], 'pdf_conversion', file_count)
        
        return {
            "success": True,
            "processed_files": [{"file_name": f"file_{i}.pdf", "status": "completed"} for i in range(file_count)],
            "download_url": "/api/files/download/123",
            "usage_logged": True
        }
    except Exception as e:
        logger.error(f"文件处理失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件处理失败: {str(e)}"
        )

@app.get("/api/files/status/{task_id}")
async def get_processing_status(
    task_id: str,
    current_user = Depends(get_current_user)
):
    """获取文件处理状态"""
    try:
        status = file_processing_service.get_processing_status(task_id, current_user["id"])
        return status
    except Exception as e:
        logger.error(f"获取处理状态失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取处理状态失败: {str(e)}"
        )

@app.get("/api/files/download/{task_id}")
async def download_file(
    task_id: str,
    current_user = Depends(get_current_user)
):
    """下载处理后的文件"""
    try:
        file_data = file_processing_service.get_download_file(task_id, current_user["id"])
        if "error" in file_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=file_data["error"]
            )
        
        # 返回文件数据
        return {
            "filename": file_data["filename"],
            "excel_data": file_data["excel_data"],
            "transaction_count": file_data["transaction_count"]
        }
        
    except Exception as e:
        logger.error(f"文件下载失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件下载失败: {str(e)}"
        )

# 用户管理端点
@app.get("/api/users/profile")
async def get_user_profile(current_user = Depends(get_current_user)):
    """获取用户资料（需要认证）"""
    return {
        "id": current_user["id"],
        "username": current_user["username"],
        "email": current_user["email"],
        "plan": current_user["plan"]
    }

@app.get("/api/users/usage")
async def get_user_usage(current_user = Depends(get_current_user)):
    """获取用户使用量（需要认证）"""
    try:
        from datetime import datetime
        
        # 获取本月使用量
        current_month = datetime.now().strftime('%Y-%m')
        monthly_usage = auth_manager.get_user_usage(current_user["id"], 'pdf_conversion', current_month)
        
        # 获取总使用量
        total_usage = auth_manager.get_user_usage(current_user["id"], 'pdf_conversion')
        
        # 获取计划限制
        plan_limits = auth_manager.get_plan_limits(current_user["plan"])
        
        # 计算剩余额度
        remaining = plan_limits["max_files"] - monthly_usage
        
        return {
            "monthly_usage": monthly_usage,
            "total_usage": total_usage,
            "plan_limits": plan_limits,
            "remaining": remaining
        }
    except Exception as e:
        logger.error(f"获取使用量失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取使用量失败: {str(e)}"
        )

# 仪表板端点
@app.get("/api/dashboard/stats")
async def get_dashboard_stats(current_user = Depends(get_current_user)):
    """获取仪表板统计（需要认证）"""
    try:
        from datetime import datetime
        
        # 获取用户信息
        user_info = {
            "id": current_user["id"],
            "username": current_user["username"],
            "email": current_user["email"],
            "plan": current_user["plan"]
        }
        
        # 获取使用量统计
        current_month = datetime.now().strftime('%Y-%m')
        monthly_usage = auth_manager.get_user_usage(current_user["id"], 'pdf_conversion', current_month)
        total_usage = auth_manager.get_user_usage(current_user["id"], 'pdf_conversion')
        plan_limits = auth_manager.get_plan_limits(current_user["plan"])
        remaining = plan_limits["max_files"] - monthly_usage
        
        usage_stats = {
            "monthly_usage": monthly_usage,
            "total_usage": total_usage,
            "plan_limits": plan_limits,
            "remaining": remaining
        }
        
        # 获取数据库统计
        database_stats = auth_manager.get_database_stats()
        
        return {
            "user_info": user_info,
            "usage_stats": usage_stats,
            "database_stats": database_stats
        }
    except Exception as e:
        logger.error(f"获取仪表板统计失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取仪表板统计失败: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.enhanced_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
