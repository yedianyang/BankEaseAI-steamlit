# api/services/file_processing_service.py
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import tempfile
import uuid
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# 导入真实的处理逻辑
from script.utils.pdf_processor import extract_text_from_pdf, clean_bank_statement_text
from script.utils.batch_processor import process_batches
from script.utils.ai_processor import AIProcessor

class FileProcessingService:
    """文件处理服务 - 集成真实的PDF处理逻辑"""
    
    def __init__(self):
        self.ai_processor = AIProcessor()
        self.batch_size = 150
        self.temp_dir = tempfile.gettempdir()
        self.processing_tasks = {}  # 存储处理任务状态
    
    async def process_pdf_file(self, file_content: bytes, filename: str, user_id: int) -> Dict[str, Any]:
        """处理单个PDF文件"""
        try:
            task_id = str(uuid.uuid4())
            self.processing_tasks[task_id] = {
                "status": "processing",
                "progress": 0,
                "user_id": user_id,
                "filename": filename,
                "start_time": datetime.now()
            }
            
            # 创建临时文件
            temp_file_path = os.path.join(self.temp_dir, f"{task_id}_{filename}")
            with open(temp_file_path, 'wb') as f:
                f.write(file_content)
            
            # 更新进度
            self.processing_tasks[task_id]["progress"] = 10
            
            # 1. 提取PDF文本
            pdf_text = extract_text_from_pdf(temp_file_path)
            if not pdf_text or not pdf_text.strip():
                self.processing_tasks[task_id]["status"] = "failed"
                self.processing_tasks[task_id]["error"] = "无法从PDF中提取文本"
                return {"error": "无法从PDF中提取文本"}
            
            self.processing_tasks[task_id]["progress"] = 30
            
            # 2. 清理文本
            cleaned_lines, transaction_count, bank_type, account_type = clean_bank_statement_text(pdf_text)
            if transaction_count == 0:
                self.processing_tasks[task_id]["status"] = "failed"
                self.processing_tasks[task_id]["error"] = "未找到有效的交易记录"
                return {"error": "未找到有效的交易记录"}
            
            self.processing_tasks[task_id]["progress"] = 50
            
            # 3. 批次处理
            batches = process_batches(cleaned_lines, self.batch_size)
            
            # 4. AI处理
            transaction_data = []
            total_processed_count = 0
            
            for i, batch in enumerate(batches):
                ai_response = self.ai_processor.process_text(
                    file_name=filename,
                    clean_lines=batch.get_text(),
                    model="gpt-4o",
                    temperature=0.3
                )
                
                if ai_response:
                    parsed_transactions, parsed_count = self._parse_ai_response(ai_response)
                    if parsed_transactions:
                        transaction_data.extend(parsed_transactions)
                        total_processed_count += parsed_count
                
                # 更新进度
                progress = 50 + (i + 1) / len(batches) * 40
                self.processing_tasks[task_id]["progress"] = min(progress, 90)
            
            self.processing_tasks[task_id]["progress"] = 95
            
            # 5. 保存为Excel
            excel_data = self._save_to_excel(transaction_data, filename, bank_type)
            
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            
            # 更新任务状态
            self.processing_tasks[task_id]["status"] = "completed"
            self.processing_tasks[task_id]["progress"] = 100
            self.processing_tasks[task_id]["result"] = {
                "filename": filename,
                "transaction_count": total_processed_count,
                "bank_type": bank_type,
                "account_type": account_type,
                "excel_data": excel_data
            }
            
            return {
                "success": True,
                "task_id": task_id,
                "filename": filename,
                "transaction_count": total_processed_count,
                "bank_type": bank_type,
                "account_type": account_type,
                "download_url": f"/api/files/download/{task_id}"
            }
            
        except Exception as e:
            # 清理临时文件
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            
            if task_id in self.processing_tasks:
                self.processing_tasks[task_id]["status"] = "failed"
                self.processing_tasks[task_id]["error"] = str(e)
            
            return {"error": f"文件处理失败: {str(e)}"}
    
    def _parse_ai_response(self, ai_response: str) -> tuple:
        """解析AI响应"""
        try:
            import json
            # 尝试解析JSON响应
            if ai_response.strip().startswith('{'):
                data = json.loads(ai_response)
                transactions = data.get('transactions', [])
                return transactions, len(transactions)
            else:
                # 如果不是JSON，尝试其他解析方式
                lines = ai_response.strip().split('\n')
                transactions = []
                for line in lines:
                    if line.strip():
                        # 简单的解析逻辑，实际应该根据AI响应格式调整
                        transactions.append({"raw": line.strip()})
                return transactions, len(transactions)
        except Exception as e:
            print(f"解析AI响应失败: {e}")
            return [], 0
    
    def _save_to_excel(self, transaction_data: List[Dict], filename: str, bank_type: str) -> Dict[str, Any]:
        """保存为Excel格式"""
        try:
            import pandas as pd
            from io import BytesIO
            import base64
            
            if not transaction_data:
                return {"error": "没有数据可保存"}
            
            # 创建DataFrame
            df = pd.DataFrame(transaction_data)
            
            # 保存到内存中的Excel文件
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Bank_Statement', index=False)
            
            # 获取Excel数据
            excel_data = output.getvalue()
            
            # 编码为base64
            excel_base64 = base64.b64encode(excel_data).decode('utf-8')
            
            return {
                "excel_base64": excel_base64,
                "filename": f"{os.path.splitext(filename)[0]}_processed.xlsx",
                "size": len(excel_data)
            }
            
        except Exception as e:
            return {"error": f"保存Excel失败: {str(e)}"}
    
    def get_processing_status(self, task_id: str, user_id: int) -> Dict[str, Any]:
        """获取处理状态"""
        if task_id not in self.processing_tasks:
            return {"error": "任务不存在"}
        
        task = self.processing_tasks[task_id]
        if task["user_id"] != user_id:
            return {"error": "无权访问此任务"}
        
        return {
            "task_id": task_id,
            "status": task["status"],
            "progress": task.get("progress", 0),
            "filename": task.get("filename", ""),
            "error": task.get("error"),
            "result": task.get("result")
        }
    
    def get_download_file(self, task_id: str, user_id: int) -> Dict[str, Any]:
        """获取下载文件"""
        if task_id not in self.processing_tasks:
            return {"error": "任务不存在"}
        
        task = self.processing_tasks[task_id]
        if task["user_id"] != user_id:
            return {"error": "无权访问此任务"}
        
        if task["status"] != "completed":
            return {"error": "任务未完成"}
        
        result = task.get("result", {})
        return {
            "filename": result.get("filename", ""),
            "excel_data": result.get("excel_data", {}),
            "transaction_count": result.get("transaction_count", 0)
        }
