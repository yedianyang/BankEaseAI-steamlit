# api/routes/files.py
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from typing import List
from api.models.schemas import FileProcessRequest, FileProcessResponse, APIResponse
from api.middleware.auth import get_current_user
from api.services.file_service import FileService
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

router = APIRouter()
file_service = FileService()

@router.post("/upload", response_model=APIResponse)
async def upload_files(
    files: List[UploadFile] = File(...),
    current_user = Depends(get_current_user)
):
    """上传文件"""
    try:
        # 检查用户权限
        if not file_service.check_user_permissions(current_user["id"], len(files)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="超出月度使用限制，请升级订阅计划"
            )
        
        # 处理文件上传
        result = await file_service.upload_files(files, current_user["id"])
        
        return APIResponse(
            success=True,
            message=f"成功上传 {len(files)} 个文件",
            data=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}"
        )

@router.post("/process", response_model=FileProcessResponse)
async def process_files(
    request: FileProcessRequest,
    current_user = Depends(get_current_user)
):
    """处理PDF文件"""
    try:
        # 检查用户权限
        if not file_service.check_user_permissions(current_user["id"], len(request.file_names)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="超出月度使用限制，请升级订阅计划"
            )
        
        # 处理文件
        result = await file_service.process_files(
            request.file_names,
            request.file_contents,
            current_user["id"]
        )
        
        return FileProcessResponse(
            success=True,
            processed_files=result["processed_files"],
            download_url=result.get("download_url")
        )
        
    except Exception as e:
        return FileProcessResponse(
            success=False,
            processed_files=[],
            error=f"文件处理失败: {str(e)}"
        )

@router.get("/download/{file_id}")
async def download_file(
    file_id: str,
    current_user = Depends(get_current_user)
):
    """下载处理后的文件"""
    try:
        file_data = await file_service.get_download_file(file_id, current_user["id"])
        return file_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文件不存在: {str(e)}"
        )

@router.get("/status/{task_id}")
async def get_processing_status(
    task_id: str,
    current_user = Depends(get_current_user)
):
    """获取文件处理状态"""
    try:
        status_info = await file_service.get_processing_status(task_id, current_user["id"])
        return APIResponse(
            success=True,
            message="获取状态成功",
            data=status_info
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务不存在: {str(e)}"
        )
