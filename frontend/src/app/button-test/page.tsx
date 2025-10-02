'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import Button from '@/components/Button';

export default function ButtonTestPage() {
  const router = useRouter();

  const handleClick = () => {
    console.log('Button clicked!');
    alert('Button clicked! Navigating to /auth');
    router.push('/auth');
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg">
        <h1 className="text-2xl font-bold mb-6 text-center">按钮测试页面</h1>
        
        <div className="space-y-4">
          <Button onClick={handleClick}>
            测试按钮 - 跳转到认证页面
          </Button>
          
          <Button 
            variant="outline"
            onClick={() => {
              console.log('Direct navigation test');
              window.location.href = '/auth';
            }}
          >
            直接跳转测试 (window.location)
          </Button>
          
          <Button 
            variant="secondary"
            onClick={() => {
              console.log('Router push test');
              router.push('/auth');
            }}
          >
            Router.push 测试
          </Button>
        </div>
        
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            打开浏览器控制台查看点击事件
          </p>
        </div>
      </div>
    </div>
  );
}
