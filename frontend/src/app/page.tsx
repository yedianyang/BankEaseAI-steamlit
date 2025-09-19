'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import Button from '@/components/Button';
import { Banknote, FileText, BarChart3, Shield } from 'lucide-react';

export default function HomePage() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();

  const features = [
    {
      icon: FileText,
      title: 'PDF智能解析',
      description: '使用AI技术自动识别和提取银行对账单中的交易信息',
    },
    {
      icon: BarChart3,
      title: '数据格式转换',
      description: '将PDF转换为Excel/CSV格式，便于进一步分析',
    },
    {
      icon: Shield,
      title: '安全可靠',
      description: '采用企业级安全标准，保护您的财务数据安全',
    },
  ];

  if (isAuthenticated) {
    router.push('/dashboard');
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-white">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Banknote className="h-8 w-8 text-primary-600" />
              <h1 className="ml-2 text-xl font-bold text-gray-900">
                BankEase AI
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                onClick={() => router.push('/login')}
              >
                登录
              </Button>
              <Button
                onClick={() => router.push('/register')}
              >
                注册
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            银行对账单
            <span className="text-primary-600"> AI 处理</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            使用先进的人工智能技术，快速将PDF银行对账单转换为Excel/CSV格式，
            让财务数据处理变得简单高效。
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              size="lg"
              onClick={() => router.push('/register')}
            >
              开始使用
            </Button>
            <Button
              variant="outline"
              size="lg"
              onClick={() => router.push('/login')}
            >
              已有账户
            </Button>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="bg-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              为什么选择 BankEase AI？
            </h2>
            <p className="text-lg text-gray-600">
              我们提供最先进的AI技术，让银行对账单处理变得简单高效
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-6">
                  <feature.icon className="h-8 w-8 text-primary-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-primary-600 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            准备开始了吗？
          </h2>
          <p className="text-xl text-primary-100 mb-8">
            立即注册，体验AI驱动的银行对账单处理服务
          </p>
          <Button
            size="lg"
            variant="secondary"
            onClick={() => router.push('/register')}
          >
            免费注册
          </Button>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="flex items-center justify-center mb-4">
            <Banknote className="h-6 w-6 text-primary-400" />
            <span className="ml-2 text-lg font-semibold">BankEase AI</span>
          </div>
          <p className="text-gray-400">
            © 2024 BankEase AI. 让银行对账单处理变得简单高效。
          </p>
        </div>
      </footer>
    </div>
  );
}