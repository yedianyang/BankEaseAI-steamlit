# api/simple_main.py
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from contextlib import asynccontextmanager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("🚀 BankEaseAI API 服务启动中...")
    yield
    # 关闭时执行
    logger.info("🛑 BankEaseAI API 服务关闭中...")

# 创建FastAPI应用
app = FastAPI(
    title="BankEaseAI API",
    description="银行对账单AI处理API服务",
    version="1.0.0",
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
    return {
        "status": "healthy",
        "service": "BankEaseAI API",
        "version": "1.0.0"
    }

# 根路径
@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "欢迎使用 BankEaseAI API",
        "docs": "/docs",
        "health": "/health"
    }

# 简单的认证端点
@app.post("/api/auth/login")
async def login(username: str, password: str):
    """用户登录"""
    # 这里应该实现真实的认证逻辑
    if username == "test" and password == "test":
        return {
            "access_token": "fake-jwt-token",
            "token_type": "bearer",
            "expires_in": 3600
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

@app.post("/api/auth/register")
async def register(username: str, email: str, password: str):
    """用户注册"""
    # 这里应该实现真实的注册逻辑
    return {
        "success": True,
        "message": "注册成功",
        "data": {"username": username}
    }

@app.get("/api/auth/me")
async def get_current_user():
    """获取当前用户信息"""
    return {
        "id": 1,
        "username": "test",
        "email": "test@example.com",
        "plan": "free"
    }

# 文件处理端点
@app.post("/api/files/process")
async def process_files(file_count: int = 1):
    """处理文件"""
    return {
        "success": True,
        "processed_files": [{"file_name": f"file_{i}.pdf", "status": "completed"} for i in range(file_count)],
        "download_url": "/api/files/download/123"
    }

@app.get("/api/files/download/{file_id}")
async def download_file(file_id: str):
    """下载文件"""
    return {
        "file_id": file_id,
        "download_url": f"/download/{file_id}",
        "expires_at": "2025-12-31T23:59:59"
    }

# 用户管理端点
@app.get("/api/users/profile")
async def get_user_profile():
    """获取用户资料"""
    return {
        "id": 1,
        "username": "test",
        "email": "test@example.com",
        "plan": "free"
    }

@app.get("/api/users/usage")
async def get_user_usage():
    """获取用户使用量"""
    return {
        "monthly_usage": 2,
        "total_usage": 5,
        "plan_limits": {"max_files": 5},
        "remaining": 3
    }

# 仪表板端点
@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """获取仪表板统计"""
    return {
        "user_info": {
            "id": 1,
            "username": "test",
            "email": "test@example.com",
            "plan": "free"
        },
        "usage_stats": {
            "monthly_usage": 2,
            "total_usage": 5,
            "plan_limits": {"max_files": 5},
            "remaining": 3
        },
        "database_stats": {
            "user_count": 1,
            "log_count": 5,
            "db_size_mb": 0.04
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.simple_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
