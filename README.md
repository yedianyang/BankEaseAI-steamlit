# BankEaseAI - 银行对账单AI处理应用

BankEaseAI是一个现代化的银行对账单AI处理应用，支持Web界面和API服务，可以将PDF银行对账单转换为iCost格式。

## 🚀 快速启动

### 方式1：Web应用（Streamlit）
```bash
# 开发环境
source bankeaseai/bin/activate && python -m streamlit run script/main.py

# 生产环境
./start_production.sh
```
**访问地址**: http://localhost:8501

### 方式2：API服务（FastAPI）
```bash
# 启动API服务
./start_api.sh
```
**API文档**: http://localhost:8000/docs  
**健康检查**: http://localhost:8000/health

### 方式3：同时运行（推荐）
```bash
# 终端1：启动API服务
./start_api.sh

# 终端2：启动Web应用
./start_production.sh
```

## 功能特性

### 🎯 核心功能
- 📄 PDF银行对账单解析
- 🤖 AI智能文本处理（GPT-4o）
- 📊 数据格式转换（Excel/CSV）
- 🔐 用户认证系统
- 📈 使用量统计和权限控制

### 🏗️ 架构特性
- 🌐 **双模式部署**：Web应用 + API服务
- 🔄 **前后端分离**：支持多种前端技术栈
- 🛡️ **安全认证**：JWT令牌 + PBKDF2密码哈希
- 📊 **实时监控**：健康检查和状态监控
- 🚀 **高性能**：异步处理和并发支持

## 本地运行

### 1. 克隆项目
```bash
git clone https://github.com/yourusername/BankEaseAI-steamlit.git
cd BankEaseAI-steamlit
```

### 2. 创建虚拟环境
```bash
python3 -m venv bankeaseai
source bankeaseai/bin/activate  # macOS/Linux
# 或
bankeaseai\Scripts\activate  # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 运行应用
```bash
streamlit run script/main.py
```

## 🚀 生产环境部署

### 环境变量配置

在生产环境中，设置以下环境变量：

```bash
# 生产环境模式（隐藏调试日志）
export STREAMLIT_ENV=production

# 数据库路径
export DB_PATH=/var/lib/bankeaseai/users.db

# 输出目录
export OUTPUT_DIR=/tmp/bankeaseai

# API密钥
export OPENAI_API_KEY=your_openai_api_key
export ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 生产环境启动

使用生产环境启动脚本：

```bash
# 使用生产环境启动脚本
./start_production.sh

# 或手动设置环境变量
export STREAMLIT_ENV=production
source bankeaseai/bin/activate
python -m streamlit run script/main.py --server.port 8501 --server.address 0.0.0.0
```

### 日志级别

- **开发环境**：显示详细日志（INFO级别）
- **生产环境**：只显示警告和错误（WARNING级别）

### 安全特性

- **密码安全**：PBKDF2+盐值哈希
- **数据库安全**：WAL模式，支持并发访问
- **错误处理**：完善的异常处理和重试机制
- **日志安全**：生产环境隐藏敏感信息

## Streamlit Cloud 部署

### 1. 推送代码到GitHub
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. 在Streamlit Cloud部署
1. 访问 [share.streamlit.io](https://share.streamlit.io)
2. 点击 "New app"
3. 连接您的GitHub仓库
4. 设置应用配置：
   - **Main file path**: `script/main.py`
   - **Python version**: `3.8`

### 3. 配置环境变量
在Streamlit Cloud的Secrets管理中添加：
```
OPENAI_API_KEY = "your_openai_api_key"
ANTHROPIC_API_KEY = "your_anthropic_api_key"  # 可选
OUTPUT_DIR = "/tmp"
```

## 项目结构

```
BankEaseAI-steamlit/
├── script/
│   ├── main.py              # 主入口文件
│   ├── controllers/          # 控制器
│   ├── models/              # 数据模型
│   ├── utils/               # 工具函数
│   └── views/               # 视图组件
├── Assets/                  # 静态资源
├── requirements.txt         # 依赖列表
└── .streamlit/             # Streamlit配置
```

## 技术栈

- **Frontend**: Streamlit
- **AI**: OpenAI GPT-4, Anthropic Claude
- **PDF处理**: pdfplumber, pypdfium2
- **数据处理**: pandas, numpy
- **可视化**: plotly

## 许可证

MIT License
