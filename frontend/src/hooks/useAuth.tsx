'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { apiClient, User } from '@/lib/api';
import toast from 'react-hot-toast';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  register: (username: string, email: string, password: string) => Promise<boolean>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user;

  // 检查认证状态
  const checkAuth = async () => {
    console.log('checkAuth started');

    // 确保在客户端环境
    if (typeof window === 'undefined') {
      console.log('Server side, skipping auth check');
      setIsLoading(false);
      return;
    }

    try {
      // 检查localStorage中的模拟用户数据
      const demoUser = localStorage.getItem('demo_user');
      if (demoUser) {
        console.log('Found demo user data');
        const userData = JSON.parse(demoUser);
        setUser(userData);
        return;
      }

      // 检查是否有token，如果没有token就直接设置为未认证
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.log('No token found, setting user to null');
        setUser(null);
        return;
      }

      console.log('Token found, attempting API call');
      // 如果有token，尝试API调用（带超时）
      const timeoutPromise = new Promise<any>((_, reject) =>
        setTimeout(() => reject(new Error('Timeout')), 2000)
      );

      const apiPromise = apiClient.getCurrentUser();

      const response = await Promise.race([apiPromise, timeoutPromise]);

      if (response && response.success && response.data) {
        console.log('API call successful');
        setUser(response.data);
      } else {
        console.log('API call failed or no data');
        setUser(null);
      }
    } catch (error) {
      console.log('Auth check error:', error);
      // 如果API调用失败，清除token并设置为未认证
      localStorage.removeItem('access_token');
      setUser(null);
    } finally {
      console.log('Auth check completed, setting loading to false');
      setIsLoading(false);
    }
  };

  // 登录
  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      setIsLoading(true);
      const response = await apiClient.login(username, password);

      if (response.success && response.data) {
        setUser(response.data.user);
        toast.success(`欢迎回来, ${response.data.user.username}!`);
        return true;
      }

      toast.error(response.error || '登录失败');
      setUser(null);
      return false;
    } catch (error) {
      toast.error('登录时发生错误');
      setUser(null);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // 注册
  const register = async (username: string, email: string, password: string): Promise<boolean> => {
    try {
      setIsLoading(true);
      const response = await apiClient.register(username, email, password);
      
      if (response.success) {
        toast.success('注册成功！');
        return true;
      } else {
        toast.error(response.error || '注册失败');
        return false;
      }
    } catch (error) {
      toast.error('注册时发生错误');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // 登出
  const logout = () => {
    apiClient.logout();
    setUser(null);
    toast.success('已成功退出登录');
  };

  // 初始化时检查认证状态
  useEffect(() => {
    checkAuth();
  }, []);

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    checkAuth,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
