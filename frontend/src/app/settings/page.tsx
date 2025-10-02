'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import Button from '@/components/Button';
import Input from '@/components/Input';
import Logo from '@/components/Logo';
import { ArrowLeft, User, Mail, Lock, Bell, Shield, CreditCard, LogOut } from 'lucide-react';
import toast from 'react-hot-toast';

type SettingsTab = 'profile' | 'security' | 'notifications' | 'plan';

export default function SettingsPage() {
  const router = useRouter();
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState<SettingsTab>('profile');
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // 个人信息表单
  const [profileData, setProfileData] = useState({
    username: user?.username || '',
    email: user?.email || '',
  });

  // 密码修改表单
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  // 通知设置
  const [notificationSettings, setNotificationSettings] = useState({
    emailNotifications: true,
    uploadComplete: true,
    processingErrors: true,
    monthlyReport: false,
  });

  const handleProfileSave = async () => {
    setIsSaving(true);
    // 模拟保存
    await new Promise(resolve => setTimeout(resolve, 1000));
    toast.success('个人信息已更新');
    setIsSaving(false);
    setIsEditing(false);
  };

  const handlePasswordChange = async () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      toast.error('两次输入的密码不一致');
      return;
    }

    if (passwordData.newPassword.length < 6) {
      toast.error('密码至少6个字符');
      return;
    }

    setIsSaving(true);
    // 模拟保存
    await new Promise(resolve => setTimeout(resolve, 1000));
    toast.success('密码已修改');
    setIsSaving(false);
    setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
  };

  const handleNotificationSave = async () => {
    setIsSaving(true);
    // 模拟保存
    await new Promise(resolve => setTimeout(resolve, 1000));
    toast.success('通知设置已保存');
    setIsSaving(false);
  };

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  const tabs = [
    { id: 'profile' as const, label: '个人信息', icon: User },
    { id: 'security' as const, label: '安全设置', icon: Shield },
    { id: 'notifications' as const, label: '通知设置', icon: Bell },
    { id: 'plan' as const, label: '套餐管理', icon: CreditCard },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航栏 */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Logo onClick={() => router.push('/')} />
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">{user?.username || '访客'}</span>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-6">
          {/* 左侧导航 */}
          <div className="w-64 flex-shrink-0">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 px-3">设置</h2>
              <nav className="space-y-2">
                {tabs.map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                      activeTab === tab.id
                        ? 'bg-primary-100 text-primary-700'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`}
                  >
                    <tab.icon className="mr-3 h-5 w-5" />
                    {tab.label}
                  </button>
                ))}
                <hr className="my-4" />
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-md transition-colors"
                >
                  <LogOut className="mr-3 h-5 w-5" />
                  退出登录
                </button>
              </nav>
            </div>
          </div>

          {/* 右侧内容 */}
          <div className="flex-1">
            {/* 个人信息 */}
            {activeTab === 'profile' && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold text-gray-900">个人信息</h2>
                  {!isEditing && (
                    <Button variant="outline" onClick={() => setIsEditing(true)}>
                      编辑
                    </Button>
                  )}
                </div>

                <div className="space-y-4 max-w-md">
                  <Input
                    label="用户名"
                    type="text"
                    value={profileData.username}
                    onChange={e => setProfileData(prev => ({ ...prev, username: e.target.value }))}
                    disabled={!isEditing}
                  />
                  <Input
                    label="邮箱"
                    type="email"
                    value={profileData.email}
                    onChange={e => setProfileData(prev => ({ ...prev, email: e.target.value }))}
                    disabled={!isEditing}
                  />

                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">当前套餐</span>
                      <span className="text-sm font-semibold text-primary-600">
                        {user?.plan?.toUpperCase() || 'FREE'}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500">
                      升级套餐以获得更多功能和更高的使用限额
                    </p>
                  </div>

                  {isEditing && (
                    <div className="flex space-x-3 pt-4">
                      <Button onClick={handleProfileSave} loading={isSaving}>
                        保存修改
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => {
                          setIsEditing(false);
                          setProfileData({
                            username: user?.username || '',
                            email: user?.email || '',
                          });
                        }}
                      >
                        取消
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* 安全设置 */}
            {activeTab === 'security' && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-6">安全设置</h2>

                <div className="space-y-6 max-w-md">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">修改密码</h3>
                    <div className="space-y-4">
                      <Input
                        label="当前密码"
                        type="password"
                        value={passwordData.currentPassword}
                        onChange={e =>
                          setPasswordData(prev => ({ ...prev, currentPassword: e.target.value }))
                        }
                      />
                      <Input
                        label="新密码"
                        type="password"
                        value={passwordData.newPassword}
                        onChange={e =>
                          setPasswordData(prev => ({ ...prev, newPassword: e.target.value }))
                        }
                        helperText="至少6个字符"
                      />
                      <Input
                        label="确认新密码"
                        type="password"
                        value={passwordData.confirmPassword}
                        onChange={e =>
                          setPasswordData(prev => ({ ...prev, confirmPassword: e.target.value }))
                        }
                      />
                      <Button onClick={handlePasswordChange} loading={isSaving}>
                        修改密码
                      </Button>
                    </div>
                  </div>

                  <hr />

                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">登录设备</h3>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="text-sm text-gray-600">
                        当前设备：{navigator.userAgent.includes('Mac') ? 'macOS' : 'Unknown'}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        最后登录时间：{new Date().toLocaleString('zh-CN')}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* 通知设置 */}
            {activeTab === 'notifications' && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-6">通知设置</h2>

                <div className="space-y-4 max-w-md">
                  <div className="flex items-center justify-between py-3">
                    <div>
                      <p className="font-medium text-gray-900">邮件通知</p>
                      <p className="text-sm text-gray-500">接收系统邮件通知</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={notificationSettings.emailNotifications}
                        onChange={e =>
                          setNotificationSettings(prev => ({
                            ...prev,
                            emailNotifications: e.target.checked,
                          }))
                        }
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between py-3">
                    <div>
                      <p className="font-medium text-gray-900">上传完成通知</p>
                      <p className="text-sm text-gray-500">文件处理完成后通知</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={notificationSettings.uploadComplete}
                        onChange={e =>
                          setNotificationSettings(prev => ({
                            ...prev,
                            uploadComplete: e.target.checked,
                          }))
                        }
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between py-3">
                    <div>
                      <p className="font-medium text-gray-900">错误通知</p>
                      <p className="text-sm text-gray-500">处理失败时通知</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={notificationSettings.processingErrors}
                        onChange={e =>
                          setNotificationSettings(prev => ({
                            ...prev,
                            processingErrors: e.target.checked,
                          }))
                        }
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between py-3">
                    <div>
                      <p className="font-medium text-gray-900">月度报告</p>
                      <p className="text-sm text-gray-500">每月使用情况报告</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={notificationSettings.monthlyReport}
                        onChange={e =>
                          setNotificationSettings(prev => ({
                            ...prev,
                            monthlyReport: e.target.checked,
                          }))
                        }
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                    </label>
                  </div>

                  <div className="pt-4">
                    <Button onClick={handleNotificationSave} loading={isSaving}>
                      保存设置
                    </Button>
                  </div>
                </div>
              </div>
            )}

            {/* 套餐管理 */}
            {activeTab === 'plan' && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-6">套餐管理</h2>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* Free Plan */}
                  <div className="border border-gray-200 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Free</h3>
                    <p className="text-3xl font-bold text-gray-900 mb-4">
                      ¥0<span className="text-sm font-normal text-gray-500">/月</span>
                    </p>
                    <ul className="space-y-2 mb-6">
                      <li className="text-sm text-gray-600">• 每月10个文件</li>
                      <li className="text-sm text-gray-600">• 基础功能</li>
                      <li className="text-sm text-gray-600">• 邮件支持</li>
                    </ul>
                    <Button
                      variant="outline"
                      className="w-full"
                      disabled={user?.plan === 'free'}
                    >
                      {user?.plan === 'free' ? '当前套餐' : '降级'}
                    </Button>
                  </div>

                  {/* Pro Plan */}
                  <div className="border-2 border-primary-500 rounded-lg p-6 relative">
                    <div className="absolute top-0 right-0 bg-primary-500 text-white text-xs px-3 py-1 rounded-bl-lg">
                      推荐
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Pro</h3>
                    <p className="text-3xl font-bold text-gray-900 mb-4">
                      ¥99<span className="text-sm font-normal text-gray-500">/月</span>
                    </p>
                    <ul className="space-y-2 mb-6">
                      <li className="text-sm text-gray-600">• 每月100个文件</li>
                      <li className="text-sm text-gray-600">• 所有功能</li>
                      <li className="text-sm text-gray-600">• 优先支持</li>
                    </ul>
                    <Button className="w-full" disabled={user?.plan === 'pro'}>
                      {user?.plan === 'pro' ? '当前套餐' : '升级'}
                    </Button>
                  </div>

                  {/* Enterprise Plan */}
                  <div className="border border-gray-200 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Enterprise</h3>
                    <p className="text-3xl font-bold text-gray-900 mb-4">
                      自定义<span className="text-sm font-normal text-gray-500"></span>
                    </p>
                    <ul className="space-y-2 mb-6">
                      <li className="text-sm text-gray-600">• 无限文件</li>
                      <li className="text-sm text-gray-600">• 定制功能</li>
                      <li className="text-sm text-gray-600">• 专属支持</li>
                    </ul>
                    <Button
                      variant="outline"
                      className="w-full"
                      disabled={user?.plan === 'enterprise'}
                    >
                      {user?.plan === 'enterprise' ? '当前套餐' : '联系我们'}
                    </Button>
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
