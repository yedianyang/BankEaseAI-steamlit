'use client';

import React, { ReactNode } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import {
  BarChart3,
  FileText,
  Upload,
  TrendingUp,
  User,
  Shield,
  Bell,
  CreditCard,
  LogOut
} from 'lucide-react';
import Logo from './Logo';
import Button from './Button';
import { useAuth } from '@/hooks/useAuth';

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { logout } = useAuth();

  const navigationGroups = [
    {
      title: '仪表板',
      items: [
        {
          name: '概览',
          icon: BarChart3,
          path: '/dashboard',
          active: pathname === '/dashboard'
        }
      ]
    },
    {
      title: '操作',
      items: [
        {
          name: '上传文件',
          icon: Upload,
          path: '/upload',
          active: pathname === '/upload'
        },
        {
          name: '文件管理',
          icon: FileText,
          path: '/dashboard/files',
          active: pathname === '/dashboard/files'
        },
        {
          name: '数据分析',
          icon: TrendingUp,
          path: '/dashboard/analytics',
          active: pathname === '/dashboard/analytics'
        }
      ]
    },
    {
      title: '设置',
      items: [
        {
          name: '个人信息',
          icon: User,
          path: '/dashboard/profile',
          active: pathname === '/dashboard/profile'
        },
        {
          name: '安全设置',
          icon: Shield,
          path: '/dashboard/security',
          active: pathname === '/dashboard/security'
        },
        {
          name: '通知设置',
          icon: Bell,
          path: '/dashboard/notifications',
          active: pathname === '/dashboard/notifications'
        },
        {
          name: '套餐管理',
          icon: CreditCard,
          path: '/dashboard/plan',
          active: pathname === '/dashboard/plan'
        },
        {
          name: '退出登录',
          icon: LogOut,
          path: '/logout',
          active: false,
          isAction: true
        }
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航栏 */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* 左侧：Logo */}
            <Logo onClick={() => router.push('/')} />

            {/* 右侧：快捷操作按钮 */}
            <div className="flex items-center space-x-3">
              <Button
                variant="outline"
                size="sm"
                onClick={() => router.push('/upload')}
              >
                <Upload className="h-4 w-4 mr-2" />
                上传文件
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex gap-6">
          {/* 全局侧边栏 - 所有页面通用 */}
          <aside className="w-64 flex-shrink-0">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sticky top-6">
              <nav className="space-y-6">
                {navigationGroups.map((group, groupIndex) => (
                  <div key={groupIndex}>
                    {/* 分组标题 */}
                    <div className="px-3 mb-2">
                      <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        {group.title}
                      </h3>
                    </div>
                    {/* 分组菜单项 */}
                    <div className="space-y-1">
                      {group.items.map((item: any) => {
                        const Icon = item.icon;
                        const isLogout = item.path === '/logout';

                        return (
                          <button
                            key={item.path}
                            onClick={() => {
                              if (isLogout) {
                                logout();
                                router.push('/');
                              } else {
                                router.push(item.path);
                              }
                            }}
                            className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                              isLogout
                                ? 'text-red-600 hover:bg-red-50'
                                : item.active
                                ? 'bg-primary-100 text-primary-700'
                                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                            }`}
                          >
                            <Icon className="mr-3 h-5 w-5" />
                            {item.name}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </nav>
            </div>
          </aside>

          {/* 主内容区域 */}
          <main className="flex-1">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}
