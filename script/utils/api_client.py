# script/utils/api_client.py
import requests
import streamlit as st
import json
from typing import Optional, Dict, Any
import logging

# 配置日志
logger = logging.getLogger(__name__)

class APIClient:
    """API客户端 - 用于Streamlit前端调用后端API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _get_auth_header(self) -> Optional[Dict[str, str]]:
        """获取认证头"""
        token = st.session_state.get('api_token')
        if token:
            return {'Authorization': f'Bearer {token}'}
        return None
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """处理API响应"""
        try:
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                # 认证失败，清除token
                if 'api_token' in st.session_state:
                    del st.session_state.api_token
                if 'logged_in' in st.session_state:
                    del st.session_state.logged_in
                if 'user' in st.session_state:
                    del st.session_state.user
                st.error("登录已过期，请重新登录")
                return {"error": "认证失败"}
            else:
                error_msg = f"API请求失败: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = error_data.get('detail', error_msg)
                except:
                    pass
                st.error(error_msg)
                return {"error": error_msg}
        except Exception as e:
            logger.error(f"处理API响应异常: {e}")
            st.error(f"API调用异常: {str(e)}")
            return {"error": str(e)}
    
    # 认证相关API
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """用户登录"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                params={"username": username, "password": password}
            )
            result = self._handle_response(response)
            
            if "access_token" in result:
                # 保存token和用户信息
                st.session_state.api_token = result["access_token"]
                st.session_state.logged_in = True
                st.session_state.user = result["user"]
                logger.info(f"用户 {username} 登录成功")
            
            return result
        except Exception as e:
            logger.error(f"登录API调用异常: {e}")
            st.error(f"登录失败: {str(e)}")
            return {"error": str(e)}
    
    def register(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """用户注册"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/register",
                params={"username": username, "email": email, "password": password}
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"注册API调用异常: {e}")
            st.error(f"注册失败: {str(e)}")
            return {"error": str(e)}
    
    def get_current_user(self) -> Dict[str, Any]:
        """获取当前用户信息"""
        try:
            headers = self._get_auth_header()
            if not headers:
                return {"error": "未登录"}
            
            response = self.session.get(
                f"{self.base_url}/api/auth/me",
                headers=headers
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"获取用户信息API调用异常: {e}")
            return {"error": str(e)}
    
    def logout(self):
        """用户登出"""
        try:
            headers = self._get_auth_header()
            if headers:
                self.session.post(
                    f"{self.base_url}/api/auth/logout",
                    headers=headers
                )
        except Exception as e:
            logger.error(f"登出API调用异常: {e}")
        finally:
            # 清除本地状态
            for key in ['api_token', 'logged_in', 'user']:
                if key in st.session_state:
                    del st.session_state[key]
    
    # 文件处理相关API
    def process_files(self, file_count: int = 1) -> Dict[str, Any]:
        """处理文件"""
        try:
            headers = self._get_auth_header()
            if not headers:
                return {"error": "未登录"}
            
            response = self.session.post(
                f"{self.base_url}/api/files/process",
                params={"file_count": file_count},
                headers=headers
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"文件处理API调用异常: {e}")
            return {"error": str(e)}
    
    # 用户管理相关API
    def get_user_profile(self) -> Dict[str, Any]:
        """获取用户资料"""
        try:
            headers = self._get_auth_header()
            if not headers:
                return {"error": "未登录"}
            
            response = self.session.get(
                f"{self.base_url}/api/users/profile",
                headers=headers
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"获取用户资料API调用异常: {e}")
            return {"error": str(e)}
    
    def get_user_usage(self) -> Dict[str, Any]:
        """获取用户使用量"""
        try:
            headers = self._get_auth_header()
            if not headers:
                return {"error": "未登录"}
            
            response = self.session.get(
                f"{self.base_url}/api/users/usage",
                headers=headers
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"获取使用量API调用异常: {e}")
            return {"error": str(e)}
    
    # 仪表板相关API
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """获取仪表板统计"""
        try:
            headers = self._get_auth_header()
            if not headers:
                return {"error": "未登录"}
            
            response = self.session.get(
                f"{self.base_url}/api/dashboard/stats",
                headers=headers
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"获取仪表板统计API调用异常: {e}")
            return {"error": str(e)}
    
    def check_api_health(self) -> bool:
        """检查API服务健康状态"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"API健康检查失败: {e}")
            return False

# 全局API客户端实例
@st.cache_resource
def get_api_client() -> APIClient:
    """获取API客户端实例"""
    return APIClient()
