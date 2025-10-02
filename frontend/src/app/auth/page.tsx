'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import Button from '@/components/Button';
import Input from '@/components/Input';
import { Banknote, Eye, EyeOff, ArrowLeft } from 'lucide-react';

type AuthMode = 'login' | 'register';

export default function AuthPage() {
  const [mode, setMode] = useState<AuthMode>('login');
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const { login, register } = useAuth();
  const router = useRouter();

  // 客户端渲染完成后处理URL参数
  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }
    // 使用window.location.search获取URL参数
    const urlParams = new URLSearchParams(window.location.search);
    const modeParam = urlParams.get('mode');
    if (modeParam === 'register') {
      setMode('register');
    } else if (modeParam === 'login') {
      setMode('login');
    } else {
      setMode('login');
    }
  }, []);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.username) {
      newErrors.username = '用户名不能为空';
    } else if (formData.username.length < 3) {
      newErrors.username = '用户名至少3个字符';
    }

    if (mode === 'register') {
      if (!formData.email) {
        newErrors.email = '邮箱不能为空';
      } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
        newErrors.email = '邮箱格式不正确';
      }

      if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = '两次输入的密码不一致';
      }
    }

    if (!formData.password) {
      newErrors.password = '密码不能为空';
    } else if (formData.password.length < 6) {
      newErrors.password = '密码至少6个字符';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      let success = false;

      if (mode === 'login') {
        success = await login(formData.username, formData.password);
      } else {
        success = await register(formData.username, formData.email, formData.password);
        if (success) {
          success = await login(formData.username, formData.password);
        }
      }

      if (success) {
        router.push('/dashboard');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, [field]: e.target.value }));
    // 清除对应字段的错误
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const switchMode = () => {
    const newMode = mode === 'login' ? 'register' : 'login';
    setMode(newMode);
    setErrors({});
    setFormData({
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
    });
    
    // 更新URL参数
    const newUrl = newMode === 'register' ? '/auth?mode=register' : '/auth?mode=login';
    window.history.replaceState({}, '', newUrl);
  };

  const handleGoogleAuth = () => {
    // TODO: 实现Google OAuth登录
    console.log('Google OAuth login');
  };


  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-white py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* 返回按钮 */}
        <div className="flex items-center">
          <button
            onClick={() => router.push('/')}
            className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="h-4 w-4 mr-1" />
            返回首页
          </button>
        </div>

        <div className="text-center">
          <Banknote className="mx-auto h-12 w-12 text-primary-600" />
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            {mode === 'login' ? '登录到 BankEase AI' : '注册 BankEase AI'}
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            {mode === 'login' ? '欢迎回来' : '创建您的账户开始使用'}
          </p>
          {/* 模式指示器 */}
          <div className="mt-4 inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
            {mode === 'login' ? '🔐 登录模式' : '📝 注册模式'}
          </div>
          
          {/* 临时测试按钮 */}
          <div className="mt-2 space-x-2">
            <button
              type="button"
              onClick={() => setMode('login')}
              className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded"
            >
              测试登录模式
            </button>
            <button
              type="button"
              onClick={() => setMode('register')}
              className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded"
            >
              测试注册模式
            </button>
          </div>
        </div>
        
        {/* OAuth 登录区域 */}
        <div className="space-y-4">
          <Button
            type="button"
            variant="outline"
            className="w-full"
            onClick={handleGoogleAuth}
          >
            <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            使用 Google 登录
          </Button>
          
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">或</span>
            </div>
          </div>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <Input
              label="用户名"
              type="text"
              value={formData.username}
              onChange={handleChange('username')}
              placeholder="请输入用户名"
              error={errors.username}
              required
            />
            
            {mode === 'register' && (
              <Input
                label="邮箱"
                type="email"
                value={formData.email}
                onChange={handleChange('email')}
                placeholder="请输入邮箱"
                error={errors.email}
                required
              />
            )}
            
            <div className="relative">
              <Input
                label="密码"
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={handleChange('password')}
                placeholder="请输入密码"
                error={errors.password}
                helperText={mode === 'register' ? '至少6个字符' : ''}
                required
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? (
                  <EyeOff className="h-5 w-5 text-gray-400" />
                ) : (
                  <Eye className="h-5 w-5 text-gray-400" />
                )}
              </button>
            </div>

            {mode === 'register' && (
              <div className="relative">
                <Input
                  label="确认密码"
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={formData.confirmPassword}
                  onChange={handleChange('confirmPassword')}
                  placeholder="请再次输入密码"
                  error={errors.confirmPassword}
                  required
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  {showConfirmPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
            )}
          </div>

          <div>
            <Button
              type="submit"
              className="w-full"
              loading={isSubmitting}
            >
              {mode === 'login' ? '登录' : '注册'}
            </Button>
          </div>

          <div className="text-center">
            <p className="text-sm text-gray-600">
              {mode === 'login' ? '还没有账户？' : '已有账户？'}{' '}
              <button
                type="button"
                className="font-medium text-primary-600 hover:text-primary-500"
                onClick={switchMode}
              >
                {mode === 'login' ? '立即注册' : '立即登录'}
              </button>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
