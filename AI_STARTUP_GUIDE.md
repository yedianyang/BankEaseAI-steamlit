# BankEaseAI 项目配置

## 项目信息
- **项目名称**: BankEaseAI - Streamlit Web App
- **项目类型**: Python Streamlit 应用
- **主要功能**: 银行对账单AI处理，PDF转Excel/CSV
- **技术栈**: Python, Streamlit, SQLite, OpenAI GPT-4

## 启动方式

### 开发环境启动
```bash
# 激活虚拟环境
source bankeaseai/bin/activate

# 启动应用（显示详细日志）
python -m streamlit run script/main.py
```

### 生产环境启动
```bash
# 激活虚拟环境
source bankeaseai/bin/activate

# 设置生产环境变量（隐藏调试日志）
export STREAMLIT_ENV=production

# 启动应用
python -m streamlit run script/main.py
```

### 使用启动脚本
```bash
# 生产环境启动脚本
./start_production.sh
```

## 环境变量

### 开发环境
- `STREAMLIT_ENV=development` (默认)
- 显示详细日志（INFO级别）

### 生产环境
- `STREAMLIT_ENV=production`
- 只显示警告和错误（WARNING级别）

### 必需的环境变量
- `OPENAI_API_KEY`: OpenAI API密钥
- `ANTHROPIC_API_KEY`: Anthropic API密钥（可选）
- `OUTPUT_DIR`: 输出目录（默认：/tmp）

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
├── start_production.sh      # 生产环境启动脚本
└── .streamlit/             # Streamlit配置
```

## 功能特性
- ✅ 用户认证系统（注册/登录）
- ✅ 弹窗式登录界面
- ✅ PDF银行对账单解析
- ✅ AI智能文本处理
- ✅ 数据格式转换（Excel/CSV）
- ✅ 使用量限制和权限控制
- ✅ 生产级错误处理
- ✅ 并发访问支持

## 数据库
- **类型**: SQLite
- **文件**: `simple_users.db`
- **特性**: WAL模式，支持并发访问
- **安全**: PBKDF2+盐值密码哈希

## 部署信息
- **本地访问**: http://localhost:8501
- **网络访问**: http://10.0.0.156:8501
- **外部访问**: http://204.188.233.66:8501

## AI助手启动指南
当用户打开这个项目时，AI应该：

1. **检查虚拟环境**: 确认 `bankeaseai` 虚拟环境存在
2. **安装依赖**: 运行 `pip install -r requirements.txt`
3. **启动应用**: 使用上述启动命令
4. **环境选择**: 根据用户需求选择开发或生产环境
5. **访问应用**: 提供访问URL

## 常见问题
- **端口冲突**: 使用 `lsof -ti:8501 | xargs kill -9` 清理端口
- **依赖问题**: 确保虚拟环境已激活
- **API密钥**: 检查环境变量设置
- **数据库问题**: 删除 `simple_users.db` 重新初始化
