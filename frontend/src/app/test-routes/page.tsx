'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Button from '@/components/Button';

export default function TestRoutesPage() {
  const router = useRouter();

  useEffect(() => {
    // 更新调试信息
    const updateDebugInfo = () => {
      const currentUrlEl = document.getElementById('current-url');
      const userAgentEl = document.getElementById('user-agent');
      const localStorageEl = document.getElementById('localstorage-info');

      if (currentUrlEl) currentUrlEl.textContent = window.location.href;
      if (userAgentEl) userAgentEl.textContent = window.navigator.userAgent;
      
      if (localStorageEl) {
        const demoUser = localStorage.getItem('demo_user');
        const accessToken = localStorage.getItem('access_token');
        localStorageEl.textContent = `demo_user: ${demoUser ? '存在' : '不存在'}, access_token: ${accessToken ? '存在' : '不存在'}`;
      }
    };

    updateDebugInfo();
  }, []);

  const testRoutes = [
    { path: '/', label: '主页' },
    { path: '/auth', label: '认证页面' },
    { path: '/auth?mode=login', label: '登录模式' },
    { path: '/auth?mode=register', label: '注册模式' },
    { path: '/dashboard', label: '仪表板' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">
          路由测试页面
        </h1>
        
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4">测试所有路由</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {testRoutes.map((route, index) => (
              <Button
                key={index}
                variant="outline"
                onClick={() => {
                  console.log(`Navigating to: ${route.path}`);
                  router.push(route.path);
                }}
                className="justify-start"
              >
                {route.label} ({route.path})
              </Button>
            ))}
          </div>
        </div>

        <div className="mt-8 bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4">调试信息</h2>
          <div className="space-y-2 text-sm">
            <p><strong>当前URL:</strong> <span id="current-url">加载中...</span></p>
            <p><strong>User Agent:</strong> <span id="user-agent">加载中...</span></p>
            <p><strong>LocalStorage:</strong> <span id="localstorage-info">加载中...</span></p>
          </div>
        </div>

        <div className="mt-8 text-center">
          <Button
            variant="ghost"
            onClick={() => router.push('/')}
          >
            返回主页
          </Button>
        </div>
      </div>
    </div>
  );
}
