#!/usr/bin/env python3
# test_api.py - API服务测试脚本

import requests
import json
import time

# API基础URL
BASE_URL = "http://localhost:8000"

def test_api_endpoints():
    """测试API端点"""
    print("🧪 开始测试 BankEaseAI API 服务...")
    print("=" * 50)
    
    # 测试健康检查
    print("1. 测试健康检查端点...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ 健康检查通过")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
    
    print()
    
    # 测试根路径
    print("2. 测试根路径...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ 根路径访问成功")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 根路径访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 根路径访问异常: {e}")
    
    print()
    
    # 测试用户登录
    print("3. 测试用户登录...")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", params={
            "username": "test",
            "password": "test"
        })
        if response.status_code == 200:
            print("✅ 用户登录成功")
            token_data = response.json()
            print(f"   令牌: {token_data['access_token']}")
            print(f"   类型: {token_data['token_type']}")
            print(f"   过期时间: {token_data['expires_in']}秒")
        else:
            print(f"❌ 用户登录失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 用户登录异常: {e}")
    
    print()
    
    # 测试用户注册
    print("4. 测试用户注册...")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", params={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword"
        })
        if response.status_code == 200:
            print("✅ 用户注册成功")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 用户注册失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 用户注册异常: {e}")
    
    print()
    
    # 测试文件处理
    print("5. 测试文件处理...")
    try:
        response = requests.post(f"{BASE_URL}/api/files/process", params={
            "file_count": 3
        })
        if response.status_code == 200:
            print("✅ 文件处理成功")
            result = response.json()
            print(f"   处理文件数: {len(result['processed_files'])}")
            print(f"   下载URL: {result['download_url']}")
        else:
            print(f"❌ 文件处理失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 文件处理异常: {e}")
    
    print()
    
    # 测试仪表板统计
    print("6. 测试仪表板统计...")
    try:
        response = requests.get(f"{BASE_URL}/api/dashboard/stats")
        if response.status_code == 200:
            print("✅ 仪表板统计获取成功")
            stats = response.json()
            print(f"   用户: {stats['user_info']['username']}")
            print(f"   计划: {stats['user_info']['plan']}")
            print(f"   本月使用: {stats['usage_stats']['monthly_usage']}")
            print(f"   剩余额度: {stats['usage_stats']['remaining']}")
        else:
            print(f"❌ 仪表板统计获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 仪表板统计获取异常: {e}")
    
    print()
    
    # 测试用户使用量
    print("7. 测试用户使用量...")
    try:
        response = requests.get(f"{BASE_URL}/api/users/usage")
        if response.status_code == 200:
            print("✅ 用户使用量获取成功")
            usage = response.json()
            print(f"   本月使用: {usage['monthly_usage']}")
            print(f"   总使用: {usage['total_usage']}")
            print(f"   计划限制: {usage['plan_limits']['max_files']}")
            print(f"   剩余: {usage['remaining']}")
        else:
            print(f"❌ 用户使用量获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 用户使用量获取异常: {e}")
    
    print()
    print("=" * 50)
    print("🎉 API服务测试完成！")
    print(f"📖 查看完整API文档: {BASE_URL}/docs")
    print(f"🔍 健康检查: {BASE_URL}/health")

if __name__ == "__main__":
    # 等待API服务启动
    print("⏳ 等待API服务启动...")
    time.sleep(2)
    
    # 运行测试
    test_api_endpoints()
