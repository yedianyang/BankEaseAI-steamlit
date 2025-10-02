'use client';

import React, { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import Button from '@/components/Button';
import Logo from '@/components/Logo';
import { Upload, File, X, CheckCircle, AlertCircle, ArrowLeft, FileText, Settings, BarChart3 } from 'lucide-react';
import toast from 'react-hot-toast';

interface UploadedFile {
  file: File;
  status: 'pending' | 'uploading' | 'success' | 'error';
  progress: number;
  error?: string;
}

export default function UploadPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);

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
      const newFiles = files.map(file => ({
        file,
        status: 'pending' as const,
        progress: 0,
      }));
      setUploadedFiles(prev => [...prev, ...newFiles]);
      toast.success(`已添加 ${files.length} 个文件`);
    } else {
      toast.error('请上传PDF文件');
    }
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []).filter(file =>
      file.type === 'application/pdf'
    );

    if (files.length > 0) {
      const newFiles = files.map(file => ({
        file,
        status: 'pending' as const,
        progress: 0,
      }));
      setUploadedFiles(prev => [...prev, ...newFiles]);
      toast.success(`已添加 ${files.length} 个文件`);
    } else {
      toast.error('请上传PDF文件');
    }
  }, []);

  const removeFile = useCallback((index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  }, []);

  const handleUpload = async () => {
    if (!isAuthenticated) {
      toast.error('请先登录');
      router.push('/auth');
      return;
    }

    if (uploadedFiles.length === 0) {
      toast.error('请先选择文件');
      return;
    }

    setIsUploading(true);

    // 模拟上传过程
    for (let i = 0; i < uploadedFiles.length; i++) {
      setUploadedFiles(prev =>
        prev.map((f, idx) =>
          idx === i ? { ...f, status: 'uploading' as const } : f
        )
      );

      // 模拟上传进度
      for (let progress = 0; progress <= 100; progress += 20) {
        await new Promise(resolve => setTimeout(resolve, 200));
        setUploadedFiles(prev =>
          prev.map((f, idx) =>
            idx === i ? { ...f, progress } : f
          )
        );
      }

      // 模拟上传结果（90%成功率）
      const success = Math.random() > 0.1;
      setUploadedFiles(prev =>
        prev.map((f, idx) =>
          idx === i
            ? {
                ...f,
                status: success ? 'success' : 'error',
                progress: 100,
                error: success ? undefined : '上传失败，请重试',
              }
            : f
        )
      );
    }

    setIsUploading(false);
    toast.success('所有文件处理完成');
  };

  const getStatusIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      case 'uploading':
        return (
          <div className="h-5 w-5 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
        );
      default:
        return <File className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusText = (status: UploadedFile['status']) => {
    switch (status) {
      case 'success':
        return '上传成功';
      case 'error':
        return '上传失败';
      case 'uploading':
        return '上传中...';
      default:
        return '等待上传';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航栏 */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Logo onClick={() => router.push('/')} />
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                {user?.username || '访客'}
              </span>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex gap-6">
          {/* 左侧边栏 */}
          <div className="w-64 flex-shrink-0">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 px-3">上传文件</h2>
              <nav className="space-y-2">
                <button
                  onClick={() => router.push('/dashboard')}
                  className="w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                >
                  <BarChart3 className="mr-3 h-5 w-5" />
                  返回仪表板
                </button>
                <button
                  className="w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors bg-primary-100 text-primary-700"
                >
                  <Upload className="mr-3 h-5 w-5" />
                  上传新文件
                </button>
                <button
                  onClick={() => router.push('/settings')}
                  className="w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                >
                  <Settings className="mr-3 h-5 w-5" />
                  设置
                </button>
              </nav>
            </div>
          </div>

          {/* 主内容区域 */}
          <div className="flex-1">
            {/* 上传区域 */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">选择文件</h2>

          {/* 拖拽上传区域 */}
          <div
            className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-colors ${
              isDragOver
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <div className="space-y-6">
              <div className="mx-auto w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center">
                <Upload className="h-10 w-10 text-primary-600" />
              </div>

              <div>
                <p className="text-xl font-medium text-gray-900 mb-2">
                  拖拽PDF文件到这里
                </p>
                <p className="text-gray-500">或点击下方按钮选择文件</p>
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
                  className="inline-flex items-center px-6 py-3 border border-gray-300 rounded-lg shadow-sm text-base font-medium text-gray-700 bg-white hover:bg-gray-50 cursor-pointer transition-colors"
                >
                  <File className="h-5 w-5 mr-2" />
                  选择PDF文件
                </label>
              </div>
            </div>
          </div>
        </div>

            {/* 文件列表 */}
            {uploadedFiles.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-lg font-medium text-gray-900">
                    已选择的文件 ({uploadedFiles.length})
                  </h3>
                  <Button
                    onClick={handleUpload}
                    disabled={isUploading || uploadedFiles.every(f => f.status === 'success')}
                  >
                    {isUploading ? '上传中...' : '开始上传'}
                  </Button>
                </div>

                <div className="space-y-4">
                  {uploadedFiles.map((uploadedFile, index) => (
                    <div
                      key={index}
                      className="flex items-start justify-between p-4 border border-gray-200 rounded-lg"
                    >
                      <div className="flex items-start space-x-4 flex-1">
                        <div className="mt-1">{getStatusIcon(uploadedFile.status)}</div>
                        <div className="flex-1 min-w-0">
                          <p className="text-base font-medium text-gray-900 truncate">
                            {uploadedFile.file.name}
                          </p>
                          <p className="text-sm text-gray-500">
                            {(uploadedFile.file.size / 1024 / 1024).toFixed(2)} MB
                          </p>
                          <p className="text-sm text-gray-600 mt-1">
                            {getStatusText(uploadedFile.status)}
                          </p>
                          {uploadedFile.error && (
                            <p className="text-sm text-red-600 mt-1">
                              {uploadedFile.error}
                            </p>
                          )}
                          {uploadedFile.status === 'uploading' && (
                            <div className="mt-2">
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div
                                  className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                                  style={{ width: `${uploadedFile.progress}%` }}
                                />
                              </div>
                              <p className="text-xs text-gray-500 mt-1">
                                {uploadedFile.progress}%
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                      <button
                        onClick={() => removeFile(index)}
                        disabled={uploadedFile.status === 'uploading'}
                        className="ml-4 text-gray-400 hover:text-red-500 transition-colors p-1 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <X className="h-5 w-5" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 提示信息 */}
            {uploadedFiles.length === 0 && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-800">
                  💡 提示：支持批量上传多个PDF文件，文件大小限制为10MB
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
