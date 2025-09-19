#!/usr/bin/env python3
# test_frontend_api_integration.py - 测试前后端分离集成

import requests
import json
import time

# API基础URL
API_BASE_URL = "http://localhost:8000"
STREAMLIT_URL = "http://localhost:8501"

def test_api_backend():
    """测试API后端"""
    print("🔧 测试API后端...")
    
    # 测试健康检查
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API服务健康检查通过")
            health_data = response.json()
            print(f"   版本: {health_data['version']}")
            print(f"   数据库状态: {health_data['database']['status']}")
            print(f"   用户数: {health_data['database']['user_count']}")
        else:
            print(f"❌ API健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API服务不可用: {e}")
        return False
    
    # 测试用户登录
    try:
        response = requests.post(f"{API_BASE_URL}/api/auth/login", params={
            "username": "test",
            "password": "test"
        })
        if response.status_code == 200:
            print("✅ API用户登录测试通过")
            login_data = response.json()
            print(f"   令牌类型: {login_data['token_type']}")
            print(f"   用户: {login_data['user']['username']}")
            return login_data['access_token']
        else:
            print(f"❌ API用户登录失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ API登录测试异常: {e}")
        return None

def test_streamlit_frontend():
    """测试Streamlit前端"""
    print("\n🌐 测试Streamlit前端...")
    
    try:
        response = requests.get(STREAMLIT_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Streamlit前端可访问")
            print(f"   状态码: {response.status_code}")
            print(f"   内容类型: {response.headers.get('content-type', 'unknown')}")
            return True
        else:
            print(f"❌ Streamlit前端访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Streamlit前端不可用: {e}")
        return False

def test_api_frontend_integration(token):
    """测试API与前端集成"""
    print("\n🔗 测试API与前端集成...")
    
    if not token:
        print("❌ 无法测试集成 - 缺少认证令牌")
        return False
    
    # 测试需要认证的API端点
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        # 测试获取用户信息
        response = requests.get(f"{API_BASE_URL}/api/auth/me", headers=headers)
        if response.status_code == 200:
            print("✅ API认证端点测试通过")
            user_data = response.json()
            print(f"   用户: {user_data['username']}")
            print(f"   计划: {user_data['plan']}")
        else:
            print(f"❌ API认证端点测试失败: {response.status_code}")
            return False
        
        # 测试仪表板统计
        response = requests.get(f"{API_BASE_URL}/api/dashboard/stats", headers=headers)
        if response.status_code == 200:
            print("✅ API仪表板统计测试通过")
            stats_data = response.json()
            print(f"   本月使用: {stats_data['usage_stats']['monthly_usage']}")
            print(f"   剩余额度: {stats_data['usage_stats']['remaining']}")
        else:
            print(f"❌ API仪表板统计测试失败: {response.status_code}")
            return False
        
        # 测试文件处理权限
        response = requests.post(f"{API_BASE_URL}/api/files/process", 
                               params={"file_count": 1}, 
                               headers=headers)
        if response.status_code == 200:
            print("✅ API文件处理权限测试通过")
            process_data = response.json()
            print(f"   处理状态: {process_data['success']}")
        else:
            print(f"❌ API文件处理权限测试失败: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ API集成测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 开始测试前后端分离集成...")
    print("=" * 60)
    
    # 测试API后端
    token = test_api_backend()
    if not token:
        print("\n❌ API后端测试失败，无法继续")
        return
    
    # 测试Streamlit前端
    if not test_streamlit_frontend():
        print("\n❌ Streamlit前端测试失败")
        return
    
    # 测试API与前端集成
    if not test_api_frontend_integration(token):
        print("\n❌ API与前端集成测试失败")
        return
    
    print("\n" + "=" * 60)
    print("🎉 前后端分离集成测试完成！")
    print("\n📋 测试总结:")
    print("✅ API后端服务正常运行")
    print("✅ Streamlit前端服务正常运行")
    print("✅ API认证系统工作正常")
    print("✅ 前后端数据交互正常")
    print("\n🚀 现在可以:")
    print("1. 访问 http://localhost:8501 使用Streamlit前端")
    print("2. 访问 http://localhost:8000/docs 查看API文档")
    print("3. 在Streamlit中登录、查看仪表板、处理文件")
    print("4. 所有操作都通过API进行，实现真正的前后端分离")

if __name__ == "__main__":
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(3)
    
    # 运行测试
    main()
