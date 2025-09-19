# api/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from contextlib import asynccontextmanager

# 导入路由
from api.routes import auth, files, users, dashboard

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

# 添加受信任主机中间件
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # 生产环境应该限制具体主机
)

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
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

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(files.router, prefix="/api/files", tags=["文件处理"])
app.include_router(users.router, prefix="/api/users", tags=["用户管理"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["仪表板"])

# 根路径
@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "欢迎使用 BankEaseAI API",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
