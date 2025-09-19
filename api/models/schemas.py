# api/models/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# 用户相关模型
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    plan: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    plan: Optional[str] = None

# 认证相关模型
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None

# 文件处理相关模型
class FileProcessRequest(BaseModel):
    file_names: List[str]
    file_contents: List[str]

class FileProcessResponse(BaseModel):
    success: bool
    processed_files: List[Dict[str, Any]]
    download_url: Optional[str] = None
    error: Optional[str] = None

class FileUploadResponse(BaseModel):
    success: bool
    file_id: str
    file_name: str
    file_size: int
    upload_time: datetime

# 使用量相关模型
class UsageStats(BaseModel):
    user_id: int
    feature: str
    count: int
    timestamp: datetime

class UsageResponse(BaseModel):
    monthly_usage: int
    total_usage: int
    plan_limits: Dict[str, int]
    remaining: int

# 仪表板相关模型
class DashboardStats(BaseModel):
    user_info: UserResponse
    usage_stats: UsageResponse
    database_stats: Dict[str, Any]

# 通用响应模型
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None

# 错误响应模型
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
