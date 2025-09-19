# api/services/file_service.py
import asyncio
import uuid
from typing import List, Dict, Any
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from script.utils.simple_auth import SimpleAuthManager
from script.controllers.bank_controller import BankStatementController

class FileService:
    """文件处理服务"""
    
    def __init__(self):
        self.auth_manager = SimpleAuthManager()
        self.controller = BankStatementController()
        self.processing_tasks = {}  # 存储处理任务状态
    
    def check_user_permissions(self, user_id: int, file_count: int) -> bool:
        """检查用户权限"""
        return self.auth_manager.can_user_process_files(user_id, file_count)
    
    async def upload_files(self, files: List, user_id: int) -> Dict[str, Any]:
        """上传文件"""
        uploaded_files = []
        
        for file in files:
            file_id = str(uuid.uuid4())
            file_data = {
                "file_id": file_id,
                "file_name": file.filename,
                "file_size": len(await file.read()),
                "user_id": user_id,
                "status": "uploaded"
            }
            uploaded_files.append(file_data)
        
        return {
            "uploaded_files": uploaded_files,
            "total_files": len(files)
        }
    
    async def process_files(
        self, 
        file_names: List[str], 
        file_contents: List[str], 
        user_id: int
    ) -> Dict[str, Any]:
        """处理文件"""
        try:
            # 创建处理任务
            task_id = str(uuid.uuid4())
            self.processing_tasks[task_id] = {
                "status": "processing",
                "progress": 0,
                "user_id": user_id
            }
            
            # 模拟文件处理（实际应该调用controller）
            processed_files = []
            for i, (name, content) in enumerate(zip(file_names, file_contents)):
                # 更新进度
                self.processing_tasks[task_id]["progress"] = (i + 1) / len(file_names) * 100
                
                # 处理文件（这里简化处理）
                processed_file = {
                    "file_name": name,
                    "processed_content": f"处理后的内容: {content[:100]}...",
                    "status": "completed"
                }
                processed_files.append(processed_file)
            
            # 记录使用量
            self.auth_manager.log_usage(user_id, 'pdf_conversion', len(file_names))
            
            # 更新任务状态
            self.processing_tasks[task_id]["status"] = "completed"
            
            return {
                "processed_files": processed_files,
                "task_id": task_id,
                "download_url": f"/api/files/download/{task_id}"
            }
            
        except Exception as e:
            if task_id in self.processing_tasks:
                self.processing_tasks[task_id]["status"] = "failed"
                self.processing_tasks[task_id]["error"] = str(e)
            raise e
    
    async def get_download_file(self, file_id: str, user_id: int):
        """获取下载文件"""
        # 这里应该实现文件下载逻辑
        return {
            "file_id": file_id,
            "download_url": f"/download/{file_id}",
            "expires_at": "2025-12-31T23:59:59"
        }
    
    async def get_processing_status(self, task_id: str, user_id: int) -> Dict[str, Any]:
        """获取处理状态"""
        if task_id not in self.processing_tasks:
            raise ValueError("任务不存在")
        
        task = self.processing_tasks[task_id]
        if task["user_id"] != user_id:
            raise ValueError("无权访问此任务")
        
        return {
            "task_id": task_id,
            "status": task["status"],
            "progress": task.get("progress", 0),
            "error": task.get("error")
        }
