"""
BankEaseAI API - Version 2.0
Refactored architecture with proper separation of concerns.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time

from api.core.config import settings
from api.core.database import db_manager, init_db
from api.routes import auth_v2, files_v2, bank_accounts, dashboard

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Bank statement processing and conversion API",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and measure response time."""
    start_time = time.time()

    # Process request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time

    # Log request details
    logger.info(
        f"{request.method} {request.url.path} "
        f"- {response.status_code} - {process_time:.3f}s"
    )

    # Add custom header
    response.headers["X-Process-Time"] = str(process_time)

    return response


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    # Initialize database
    logger.info("Initializing database...")
    init_db()

    # Test database connection
    if db_manager.test_connection():
        logger.info("Database connection successful")
    else:
        logger.error("Database connection failed!")

    # Ensure directories exist
    settings.ensure_directories()
    logger.info(f"Upload directory: {settings.UPLOAD_DIR}")
    logger.info(f"Output directory: {settings.OUTPUT_DIR}")

    # Initialize processors
    from api.core.processors.registry import get_processor_registry
    registry = get_processor_registry()
    banks = registry.list_supported_banks()
    logger.info(f"Loaded {len(banks)} bank processors:")
    for bank in banks:
        logger.info(f"  - {bank['bank_name']} ({bank['bank_code']})")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down application...")


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    db_healthy = db_manager.test_connection()

    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


# Include routers with proper prefixes
app.include_router(
    auth_v2.router,
    prefix="/api/auth",
    tags=["Authentication"]
)

app.include_router(
    files_v2.router,
    prefix="/api/files",
    tags=["Files"]
)

app.include_router(
    bank_accounts.router,
    prefix="/api/bank-accounts",
    tags=["Bank Accounts"]
)

app.include_router(
    dashboard.router,
    prefix="/api/dashboard",
    tags=["Dashboard"]
)


# Development server
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main_v2:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS if not settings.DEBUG else 1,
        log_level=settings.LOG_LEVEL.lower()
    )
