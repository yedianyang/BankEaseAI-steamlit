'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { apiClient, DashboardStats } from '@/lib/api';
import {
  BarChart3,
  FileText,
  Users,
  Database,
  Upload,
  Download,
  Settings,
  Clock,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Activity,
  Home,
  Banknote
} from 'lucide-react';
import LoadingSpinner from '@/components/LoadingSpinner';
import Button from '@/components/Button';
import Logo from '@/components/Logo';

export default function DashboardPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'files' | 'analytics'>('overview');

  // 模拟最近文件数据
  const recentFiles = [
    {
      id: 1,
      name: '银行对账单_2024年1月.pdf',
      status: 'completed',
      uploadedAt: '2024-01-15 14:30',
      size: '2.3 MB',
      downloadUrl: '#'
    },
    {
      id: 2,
      name: '银行对账单_2024年2月.pdf',
      status: 'processing',
      uploadedAt: '2024-01-16 09:15',
      size: '1.8 MB',
      downloadUrl: null
    },
    {
      id: 3,
      name: '银行对账单_2024年3月.pdf',
      status: 'failed',
      uploadedAt: '2024-01-17 16:45',
      size: '3.1 MB',
      downloadUrl: null
    }
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'processing':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return '已完成';
      case 'processing':
        return '处理中';
      case 'failed':
        return '处理失败';
      default:
        return '未知';
    }
  };

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await apiClient.getDashboardStats();
        if (response.success && response.data) {
          setStats(response.data);
        } else {
          setStats(null);
        }
      } catch (error) {
        console.error('获取统计数据失败:', error);
        setStats(null);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!stats) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">无法加载统计数据</p>
      </div>
    );
  }

  const { user_info, usage_stats, database_stats } = stats;
  const progressPercentage = (usage_stats.monthly_usage / usage_stats.plan_limits.max_files) * 100;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航栏 */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* 左侧：Logo */}
            <Logo onClick={() => router.push('/')} />

            {/* 右侧：操作按钮 */}
            <div className="flex items-center space-x-3">
              <Button
                variant="outline"
                size="sm"
                onClick={() => router.push('/upload')}
              >
                <Upload className="h-4 w-4 mr-2" />
                上传文件
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => router.push('/settings')}
              >
                <Settings className="h-4 w-4 mr-2" />
                设置
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex gap-6">
          {/* 左侧边栏 */}
          <div className="w-64 flex-shrink-0">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 px-3">仪表板</h2>
              <nav className="space-y-2">
                <button
                  onClick={() => setActiveTab('overview')}
                  className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    activeTab === 'overview'
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <BarChart3 className="mr-3 h-5 w-5" />
                  概览
                </button>
                <button
                  onClick={() => router.push('/upload')}
                  className="w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                >
                  <FileText className="mr-3 h-5 w-5" />
                  开始转换PDF
                </button>
                <button
                  onClick={() => setActiveTab('files')}
                  className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    activeTab === 'files'
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <FileText className="mr-3 h-5 w-5" />
                  文件管理
                </button>
                <button
                  onClick={() => setActiveTab('analytics')}
                  className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    activeTab === 'analytics'
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <TrendingUp className="mr-3 h-5 w-5" />
                  数据分析
                </button>
              </nav>
            </div>
          </div>

          {/* 主内容区域 */}
          <div className="flex-1">
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* 欢迎信息 */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h2 className="text-2xl font-bold text-gray-900">
                    欢迎回来, {user_info.username}!
                  </h2>
                  <p className="text-gray-600 mt-2">
                    这是您的个人仪表板，可以查看使用情况和账户信息。
                  </p>
                </div>

                {/* 统计卡片 */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <div className="flex items-center">
                      <div className="p-2 bg-primary-100 rounded-lg">
                        <BarChart3 className="h-6 w-6 text-primary-600" />
                      </div>
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">当前计划</p>
                        <p className="text-2xl font-semibold text-gray-900">
                          {user_info.plan.toUpperCase()}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <div className="flex items-center">
                      <div className="p-2 bg-green-100 rounded-lg">
                        <FileText className="h-6 w-6 text-green-600" />
                      </div>
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">本月已处理</p>
                        <p className="text-2xl font-semibold text-gray-900">
                          {usage_stats.monthly_usage}/{usage_stats.plan_limits.max_files}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <div className="flex items-center">
                      <div className="p-2 bg-blue-100 rounded-lg">
                        <Users className="h-6 w-6 text-blue-600" />
                      </div>
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">剩余额度</p>
                        <p className="text-2xl font-semibold text-gray-900">
                          {usage_stats.remaining}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <div className="flex items-center">
                      <div className="p-2 bg-purple-100 rounded-lg">
                        <Database className="h-6 w-6 text-purple-600" />
                      </div>
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">总用户数</p>
                        <p className="text-2xl font-semibold text-gray-900">
                          {database_stats.user_count}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* 使用进度 */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">使用进度</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">本月使用量</span>
                      <span className="font-medium">
                        {usage_stats.monthly_usage} / {usage_stats.plan_limits.max_files} 文件
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-300 ${
                          progressPercentage >= 80
                            ? 'bg-red-500'
                            : progressPercentage >= 50
                            ? 'bg-yellow-500'
                            : 'bg-green-500'
                        }`}
                        style={{ width: `${Math.min(progressPercentage, 100)}%` }}
                      />
                    </div>
                    {progressPercentage >= 80 && (
                      <p className="text-sm text-red-600">
                        ⚠️ 使用量接近限制，请考虑升级计划
                      </p>
                    )}
                  </div>
                </div>

                {/* 历史转换文件 */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <div className="flex justify-between items-center mb-6">
                    <h3 className="text-lg font-medium text-gray-900">历史转换文件</h3>
                    <Button variant="outline" size="sm" onClick={() => setActiveTab('files')}>
                      查看全部
                    </Button>
                  </div>
                  <div className="space-y-4">
                    {recentFiles.slice(0, 3).map((file) => (
                      <div
                        key={file.id}
                        className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                      >
                        <div className="flex items-center space-x-4">
                          <FileText className="h-8 w-8 text-red-500" />
                          <div>
                            <p className="font-medium text-gray-900">{file.name}</p>
                            <div className="flex items-center space-x-4 text-sm text-gray-500">
                              <span>{file.uploadedAt}</span>
                              <span>{file.size}</span>
                              <div className="flex items-center space-x-1">
                                {getStatusIcon(file.status)}
                                <span>{getStatusText(file.status)}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          {file.downloadUrl && (
                            <Button variant="outline" size="sm">
                              <Download className="h-4 w-4 mr-1" />
                              下载
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'files' && (
              <div className="space-y-6">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-semibold text-gray-900">文件管理</h2>
                    <Button onClick={() => router.push('/upload')}>
                      <Upload className="h-4 w-4 mr-2" />
                      上传新文件
                    </Button>
                  </div>

                  <div className="space-y-4">
                    {recentFiles.map((file) => (
                      <div
                        key={file.id}
                        className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                      >
                        <div className="flex items-center space-x-4">
                          <FileText className="h-8 w-8 text-red-500" />
                          <div>
                            <p className="font-medium text-gray-900">{file.name}</p>
                            <div className="flex items-center space-x-4 text-sm text-gray-500">
                              <span>{file.uploadedAt}</span>
                              <span>{file.size}</span>
                              <div className="flex items-center space-x-1">
                                {getStatusIcon(file.status)}
                                <span>{getStatusText(file.status)}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          {file.downloadUrl && (
                            <Button variant="outline" size="sm">
                              <Download className="h-4 w-4 mr-1" />
                              下载
                            </Button>
                          )}
                          <Button variant="ghost" size="sm">
                            详情
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'analytics' && (
              <div className="space-y-6">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-6">数据分析</h2>
                  <div className="text-center py-12">
                    <TrendingUp className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">数据分析功能即将推出</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
