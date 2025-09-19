# script/utils/simple_auth.py
import streamlit as st
import sqlite3
import hashlib
import secrets
import datetime
import time
import logging
from typing import Optional, Dict, Any, Tuple, Callable

# 配置日志
import os
import logging

# 根据环境设置日志级别
if os.environ.get('STREAMLIT_ENV') == 'production':
    logging.basicConfig(level=logging.WARNING)  # 生产环境只显示警告和错误
else:
    logging.basicConfig(level=logging.INFO)     # 开发环境显示详细信息

logger = logging.getLogger(__name__)

class SimpleAuthManager:
    """简化的用户认证管理器（支持并发访问）"""
    
    def __init__(self, db_path='simple_users.db'):
        self.db_path = db_path
        self.max_retries = 3
        self.retry_delay = 0.01  # 10ms
        self._init_db()
    
    def _safe_database_operation(self, operation: Callable, max_retries: int = None) -> Any:
        """安全的数据库操作，带重试机制"""
        retries = max_retries or self.max_retries
        
        for attempt in range(retries):
            try:
                start_time = time.time()
                result = operation()
                duration = time.time() - start_time
                
                # 记录慢查询
                if duration > 1.0:
                    logger.warning(f"慢查询检测: 耗时 {duration:.2f}s")
                
                return result
                
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)  # 指数退避
                    logger.info(f"数据库锁定，{wait_time:.3f}s后重试 (尝试 {attempt + 1}/{retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"数据库操作失败: {e}")
                    raise e
            except Exception as e:
                logger.error(f"数据库操作异常: {e}")
                raise e
        
        raise sqlite3.OperationalError("数据库操作重试次数超限")
    
    def _init_db(self):
        """初始化数据库（支持并发优化）"""
        def init_operation():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 启用WAL模式，提高并发性能
            cursor.execute('PRAGMA journal_mode=WAL')
            
            # 设置超时时间
            cursor.execute('PRAGMA busy_timeout=30000')  # 30秒
            
            # 启用外键约束
            cursor.execute('PRAGMA foreign_keys=ON')
            
            # 创建用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    plan TEXT DEFAULT 'free',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 检查是否需要添加salt列（数据库迁移）
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'salt' not in columns:
                # 添加salt列
                cursor.execute('ALTER TABLE users ADD COLUMN salt TEXT DEFAULT ""')
                # 为现有用户生成随机盐值
                cursor.execute('SELECT id FROM users WHERE salt = "" OR salt IS NULL')
                users_without_salt = cursor.fetchall()
                
                for user_id in users_without_salt:
                    random_salt = secrets.token_hex(32)
                    cursor.execute('UPDATE users SET salt = ? WHERE id = ?', (random_salt, user_id[0]))
            
            # 创建使用记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usage_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    feature TEXT NOT NULL,
                    count INTEGER DEFAULT 1,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # 创建索引提高查询性能
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_username ON users(username)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_email ON users(email)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON usage_logs(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON usage_logs(timestamp)')
            
            conn.commit()
            conn.close()
            return True
        
        # 使用安全操作包装初始化
        self._safe_database_operation(init_operation)
        logger.info("数据库初始化完成（WAL模式已启用）")
    
    def _hash_password(self, password: str) -> Tuple[str, str]:
        """安全的密码哈希（带盐值）"""
        # 生成随机盐值
        salt = secrets.token_hex(32)  # 64字符的随机盐值
        
        # 使用PBKDF2进行哈希（100,000次迭代）
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 迭代次数
        ).hex()
        
        return password_hash, salt
    
    def _verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """验证密码"""
        # 使用相同的盐值和迭代次数计算哈希
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        
        return password_hash == stored_hash
    
    def register_user(self, username: str, password: str, email: str) -> bool:
        """注册用户（支持并发访问）"""
        def register_operation():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash, salt = self._hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, salt, email)
                VALUES (?, ?, ?, ?)
            ''', (username, password_hash, salt, email))
            
            conn.commit()
            conn.close()
            return True
        
        try:
            self._safe_database_operation(register_operation)
            logger.info(f"用户注册成功: {username}")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"用户注册失败: {username} (用户名或邮箱已存在)")
            return False
        except Exception as e:
            logger.error(f"用户注册异常: {username} - {e}")
            return False
    
    def login_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """用户登录（支持并发访问）"""
        def login_operation():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取用户的盐值和哈希值
            cursor.execute('''
                SELECT id, username, email, plan, password_hash, salt FROM users
                WHERE username = ?
            ''', (username,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                user_id, db_username, email, plan, stored_hash, salt = result
                
                # 验证密码
                if self._verify_password(password, stored_hash, salt):
                    return {
                        'id': user_id,
                        'username': db_username,
                        'email': email,
                        'plan': plan
                    }
            return None
        
        try:
            user = self._safe_database_operation(login_operation)
            if user:
                logger.info(f"用户登录成功: {username}")
            else:
                logger.warning(f"用户登录失败: {username} (用户名或密码错误)")
            return user
        except Exception as e:
            logger.error(f"用户登录异常: {username} - {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """根据用户名获取用户信息（支持并发访问）"""
        def get_user_operation():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, email, plan FROM users
                WHERE username = ?
            ''', (username,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'id': result[0],
                    'username': result[1],
                    'email': result[2],
                    'plan': result[3]
                }
            return None
        
        try:
            return self._safe_database_operation(get_user_operation)
        except Exception as e:
            logger.error(f"获取用户信息异常: {username} - {e}")
            return None
    
    def can_user_process_files(self, user_id: int, file_count: int = 1) -> bool:
        """检查用户是否可以处理文件"""
        def check_permission_operation():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取用户计划
            cursor.execute('SELECT plan FROM users WHERE id = ?', (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return False
            
            user_plan = result[0]
            
            # 获取用户计划限制
            limits = self.get_plan_limits(user_plan)
            
            # 获取本月使用量
            current_month = datetime.datetime.now().strftime('%Y-%m')
            usage = self.get_user_usage(user_id, 'pdf_conversion', current_month)
            
            return usage + file_count <= limits['max_files']
        
        try:
            return self._safe_database_operation(check_permission_operation)
        except Exception as e:
            logger.error(f"检查用户权限异常: 用户{user_id} - {e}")
            return False
    
    def log_usage(self, user_id: int, feature: str, count: int = 1):
        """记录使用量（支持并发访问）"""
        def log_usage_operation():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO usage_logs (user_id, feature, count)
                VALUES (?, ?, ?)
            ''', (user_id, feature, count))
            
            conn.commit()
            conn.close()
            return True
        
        try:
            self._safe_database_operation(log_usage_operation)
            logger.info(f"记录使用量: 用户{user_id}, 功能{feature}, 数量{count}")
        except Exception as e:
            logger.error(f"记录使用量异常: 用户{user_id} - {e}")
    
    def get_user_usage(self, user_id: int, feature: str = 'pdf_conversion', month: str = None) -> int:
        """获取用户使用量（支持并发访问）"""
        def get_usage_operation():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if month:
                cursor.execute('''
                    SELECT SUM(count) FROM usage_logs
                    WHERE user_id = ? AND feature = ? 
                    AND strftime('%Y-%m', timestamp) = ?
                ''', (user_id, feature, month))
            else:
                cursor.execute('''
                    SELECT SUM(count) FROM usage_logs
                    WHERE user_id = ? AND feature = ?
                ''', (user_id, feature))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result[0] else 0
        
        try:
            usage = self._safe_database_operation(get_usage_operation)
            return usage
        except Exception as e:
            logger.error(f"获取用户使用量异常: 用户{user_id} - {e}")
            return 0
    
    def get_plan_limits(self, plan: str) -> Dict[str, int]:
        """获取计划限制"""
        limits = {
            'free': {'max_files': 5},
            'pro': {'max_files': 50},
            'enterprise': {'max_files': 200},
            'unlimited': {'max_files': 999999}  # 无限使用
        }
        return limits.get(plan, limits['free'])
    
    def get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        def stats_operation():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取用户数量
            cursor.execute('SELECT COUNT(*) FROM users')
            user_count = cursor.fetchone()[0]
            
            # 获取使用记录数量
            cursor.execute('SELECT COUNT(*) FROM usage_logs')
            log_count = cursor.fetchone()[0]
            
            # 获取数据库文件大小
            import os
            file_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            
            # 获取WAL文件信息
            wal_file = self.db_path + '-wal'
            wal_size = os.path.getsize(wal_file) if os.path.exists(wal_file) else 0
            
            conn.close()
            
            return {
                'user_count': user_count,
                'log_count': log_count,
                'db_size_bytes': file_size,
                'wal_size_bytes': wal_size,
                'db_size_mb': round(file_size / 1024 / 1024, 2),
                'wal_size_mb': round(wal_size / 1024 / 1024, 2)
            }
        
        try:
            return self._safe_database_operation(stats_operation)
        except Exception as e:
            logger.error(f"获取数据库统计信息异常: {e}")
            return {
                'user_count': 0,
                'log_count': 0,
                'db_size_bytes': 0,
                'wal_size_bytes': 0,
                'db_size_mb': 0,
                'wal_size_mb': 0
            }
