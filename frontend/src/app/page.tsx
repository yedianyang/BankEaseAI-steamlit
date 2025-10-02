'use client';

import React, { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import Button from '@/components/Button';
import Logo from '@/components/Logo';
import { Banknote, FileText, BarChart3, Shield, Upload, File, LogIn, LayoutDashboard, Lock, CheckCircle } from 'lucide-react';

export default function HomePage() {
  const { isAuthenticated, isLoading, user } = useAuth();
  const router = useRouter();
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);

  // 调试信息
  console.log('HomePage - isAuthenticated:', isAuthenticated, 'isLoading:', isLoading);

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

  // 处理文件拖拽
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files).filter(file => 
      file.type === 'application/pdf'
    );
    
    if (files.length > 0) {
      setUploadedFiles(prev => [...prev, ...files]);
    }
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []).filter(file => 
      file.type === 'application/pdf'
    );
    
    if (files.length > 0) {
      setUploadedFiles(prev => [...prev, ...files]);
    }
  }, []);

  const removeFile = useCallback((index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  }, []);

  const handleUpload = useCallback(() => {
    if (!isAuthenticated) {
      // 保存文件信息到localStorage，登录后恢复
      const fileNames = uploadedFiles.map(f => f.name);
      if (typeof window !== 'undefined') {
        localStorage.setItem('pending_files', JSON.stringify(fileNames));
      }
      router.push('/auth');
      return;
    }

    // 已登录用户：跳转到上传页面
    router.push('/upload');
  }, [isAuthenticated, uploadedFiles, router]);

  // 如果正在加载，显示加载状态
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white/95 backdrop-blur-sm shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Logo />
            <div className="flex items-center space-x-2">
              {isAuthenticated ? (
                <>
                  <span className="text-base text-gray-600">
                    欢迎回来
                  </span>
                  <button
                    onClick={() => router.push('/dashboard')}
                    className="text-base font-semibold text-blue-600 hover:text-blue-700 hover:underline transition-colors"
                  >
                    {user?.username}
                  </button>
                </>
              ) : (
                <Button
                  onClick={() => router.push('/auth')}
                >
                  <LogIn className="h-4 w-4 mr-2" />
                  登录 / 注册
                </Button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Upload Section */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <div className="inline-flex items-center px-4 py-2 bg-blue-50 border border-blue-200 rounded-full mb-6">
            <Shield className="h-4 w-4 text-blue-600 mr-2" />
            <span className="text-sm font-medium text-blue-700">企业级安全加密</span>
          </div>

          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6 leading-tight">
            银行对账单
            <span className="text-blue-600"> AI 处理</span>
          </h1>
          <p className="text-xl text-gray-600 mb-6 max-w-3xl mx-auto leading-relaxed">
            使用先进的人工智能技术，快速将PDF银行对账单转换为Excel/CSV格式，
            <br />
            让财务数据处理变得简单高效。
          </p>

          {/* 信任指标 */}
          <div className="flex items-center justify-center gap-8 mb-8 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <Lock className="h-4 w-4 text-green-600" />
              <span>数据加密传输</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <span>处理后自动删除</span>
            </div>
            <div className="flex items-center gap-2">
              <Shield className="h-4 w-4 text-green-600" />
              <span>隐私保护认证</span>
            </div>
          </div>

          <p className="text-base text-gray-500">
            拖拽PDF文件到下方区域，或点击选择文件开始转换
          </p>
        </div>

        {/* 拖拽上传区域 */}
        <div
          className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 bg-white shadow-sm ${
            isDragOver
              ? 'border-blue-500 bg-blue-50 shadow-lg scale-[1.02]'
              : 'border-gray-300 hover:border-blue-400 hover:shadow-md'
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {/* 安全标识 */}
          <div className="absolute top-4 right-4 flex items-center gap-2 px-3 py-1.5 bg-green-50 border border-green-200 rounded-full">
            <Lock className="h-3.5 w-3.5 text-green-600" />
            <span className="text-xs font-medium text-green-700">安全加密</span>
          </div>

          <div className="space-y-6">
            <div className="mx-auto w-24 h-24 bg-gradient-to-br from-blue-100 to-blue-50 rounded-full flex items-center justify-center shadow-inner">
              <Upload className="h-12 w-12 text-blue-600" />
            </div>

            <div>
              <p className="text-xl font-semibold text-gray-900 mb-2">
                拖拽PDF文件到这里
              </p>
              <p className="text-gray-600">
                或点击下方按钮选择文件
              </p>
            </div>

            <div>
              <input
                type="file"
                id="file-upload"
                className="hidden"
                multiple
                accept=".pdf"
                onChange={handleFileSelect}
              />
              <label
                htmlFor="file-upload"
                className="inline-flex items-center px-8 py-3.5 border-2 border-blue-600 rounded-lg shadow-sm text-base font-semibold text-blue-600 bg-white hover:bg-blue-50 cursor-pointer transition-all duration-200 hover:shadow-md"
              >
                <File className="h-5 w-5 mr-2" />
                选择PDF文件
              </label>
              <p className="mt-3 text-xs text-gray-500">
                支持多个文件，单个文件最大 10MB
              </p>
            </div>
          </div>
        </div>

        {/* 已选择的文件列表 */}
        {uploadedFiles.length > 0 && (
          <div className="mt-8">
            <h3 className="text-xl font-medium text-gray-900 mb-6 text-center">
              已选择的文件 ({uploadedFiles.length})
            </h3>
            <div className="space-y-3">
              {uploadedFiles.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg shadow-sm"
                >
                  <div className="flex items-center">
                    <File className="h-6 w-6 text-red-500 mr-4" />
                    <div>
                      <p className="text-base font-medium text-gray-900">
                        {file.name}
                      </p>
                      <p className="text-sm text-gray-500">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => removeFile(index)}
                    className="text-gray-400 hover:text-red-500 transition-colors p-1"
                  >
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>

            <div className="mt-8 flex justify-center">
              <Button
                size="lg"
                onClick={handleUpload}
                disabled={uploadedFiles.length === 0}
                className="px-8 py-4 text-lg"
              >
                {isAuthenticated ? (
                  <>
                    <Upload className="h-5 w-5 mr-2" />
                    前往上传页面 ({uploadedFiles.length} 个文件)
                  </>
                ) : (
                  <>
                    <LogIn className="h-5 w-5 mr-2" />
                    登录后上传 ({uploadedFiles.length} 个文件)
                  </>
                )}
              </Button>
            </div>
            {!isAuthenticated && uploadedFiles.length > 0 && (
              <p className="text-center text-sm text-gray-500 mt-4">
                💡 登录后将保留您选择的文件
              </p>
            )}
          </div>
        )}
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
            onClick={() => {
              console.log('CTA button clicked - navigating to /auth');
              router.push('/auth');
            }}
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