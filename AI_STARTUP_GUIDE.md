# BankEaseAI 启动指南

## 项目概述
BankEaseAI是一个现代化的银行对账单AI处理应用，采用React + Next.js + FastAPI架构。

## 技术栈
- **前端**: React + Next.js + TypeScript
- **后端**: FastAPI + Python + SQLite
- **部署**: Vercel (前端) + Railway/Heroku (后端)

## 启动方式

### 现代化前端（推荐）
```bash
# 安装前端依赖
cd frontend && npm install

# 开发环境
npm run dev

# 生产环境
npm run build && npm start
```

### 后端API服务
```bash
# 启动API服务
./start_api.sh
```

### 传统UI（Streamlit）
```bash
# 启动传统UI
./start_production.sh
```

### 完整系统（推荐）
```bash
# 终端1：启动后端
./start_api.sh

# 终端2：启动前端
cd frontend && npm run dev
```

## 环境变量

### 前端环境变量
- `NEXT_PUBLIC_API_URL`: API服务地址（默认：http://localhost:8000）
- `NODE_ENV`: 环境模式（development/production）

### 后端环境变量
- `OPENAI_API_KEY`: OpenAI API密钥（必需）
- `JWT_SECRET_KEY`: JWT密钥
- `DATABASE_URL`: 数据库连接
- `ANTHROPIC_API_KEY`: Anthropic API密钥（可选）

## 项目结构
```
BankEaseAI-steamlit/
├── frontend/                 # React + Next.js 前端
│   ├── pages/               # 页面组件
│   ├── components/          # UI组件
│   ├── lib/                 # 工具函数
│   └── styles/              # 样式文件
├── api/                     # FastAPI 后端
│   ├── main.py             # API主文件
│   ├── routes/             # 路由
│   ├── services/           # 服务层
│   └── models/             # 数据模型
├── script/                  # 传统Streamlit UI（保留）
│   ├── main.py             # Streamlit入口
│   ├── controllers/        # 控制器
│   ├── utils/              # 工具函数
│   └── views/              # 视图组件
└── simple_users.db         # SQLite数据库
```

## 功能特性
- ✅ 现代化响应式UI
- ✅ 用户认证系统（JWT）
- ✅ PDF银行对账单解析
- ✅ AI智能文本处理
- ✅ 数据格式转换（Excel/CSV）
- ✅ 使用量限制和权限控制
- ✅ 移动端支持
- ✅ SSR/SSG支持

## 数据库
- **类型**: SQLite
- **文件**: `simple_users.db`
- **特性**: WAL模式，支持并发访问
- **安全**: PBKDF2+盐值密码哈希

## 访问地址
- **现代化前端**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **传统UI**: http://localhost:8501

## AI助手启动指南
当用户打开这个项目时，AI应该：

1. **检查环境**: 确认Node.js和Python环境
2. **安装依赖**: 
   - Python: `pip install -r requirements.txt`
   - Node.js: `cd frontend && npm install`
3. **启动服务**: 根据用户需求选择启动方式
4. **环境选择**: 开发或生产环境
5. **访问应用**: 提供相应的访问URL

## 开发工作流
- **前端开发**: React + Next.js + TypeScript
- **后端开发**: FastAPI + Python + SQLite
- **API优先**: 所有业务逻辑在后端实现
- **现代化UI**: 响应式设计、移动端支持
- **部署**: Vercel (前端) + Railway/Heroku (后端)

## 常见问题
- **端口冲突**: 使用 `lsof -ti:3000 | xargs kill -9` 清理端口
- **依赖问题**: 确保虚拟环境和Node.js环境正确
- **API连接**: 检查前后端服务是否都启动
- **数据库问题**: 删除 `simple_users.db` 重新初始化