'use client';

import React, { useEffect, useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { apiClient, DashboardStats } from '@/lib/api';
import { BarChart3, FileText, Users, Database } from 'lucide-react';
import LoadingSpinner from '@/components/LoadingSpinner';

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await apiClient.getDashboardStats();
        if (response.success && response.data) {
          setStats(response.data);
        }
      } catch (error) {
        console.error('获取统计数据失败:', error);
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
    <div className="space-y-6">
      {/* 欢迎信息 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900">
          欢迎回来, {user_info.username}!
        </h1>
        <p className="text-gray-600 mt-2">
          这是您的个人仪表板，可以查看使用情况和账户信息。
        </p>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
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

        <div className="bg-white rounded-lg shadow p-6">
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

        <div className="bg-white rounded-lg shadow p-6">
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

        <div className="bg-white rounded-lg shadow p-6">
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
      <div className="bg-white rounded-lg shadow p-6">
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

      {/* 快速操作 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">快速操作</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <FileText className="h-8 w-8 text-primary-600 mx-auto mb-2" />
            <p className="font-medium text-gray-900">开始转换PDF</p>
            <p className="text-sm text-gray-600">上传银行对账单进行转换</p>
          </button>
          <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <BarChart3 className="h-8 w-8 text-primary-600 mx-auto mb-2" />
            <p className="font-medium text-gray-900">查看详细统计</p>
            <p className="text-sm text-gray-600">查看历史使用记录</p>
          </button>
        </div>
      </div>
    </div>
  );
}
