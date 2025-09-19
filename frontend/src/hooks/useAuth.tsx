'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { apiClient, User, AuthResponse } from '@/lib/api';
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
    try {
      const response = await apiClient.getCurrentUser();
      if (response.success && response.data) {
        setUser(response.data);
      } else {
        setUser(null);
      }
    } catch (error) {
      setUser(null);
    } finally {
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
      } else {
        toast.error(response.error || '登录失败');
        return false;
      }
    } catch (error) {
      toast.error('登录时发生错误');
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
        toast.success('注册成功！请使用新账户登录。');
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
