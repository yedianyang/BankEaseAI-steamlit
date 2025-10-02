# BankEaseAI 开发文档

> **版本**: 2.0 (重构版本)
> **更新日期**: 2025-10-02
> **架构状态**: ✅ 完成重构 - 采用模块化、分层架构

## 项目概述
BankEaseAI 是一个智能银行对账单处理系统，通过 AI 技术将 PDF 银行对账单自动转换为标准化的 CSV/Excel 格式，并支持多种财务软件模板导出。

### 最新更新 (v2.0)
- ✅ 完成后端架构重构 - 采用分层设计 (Core → Services → Routes)
- ✅ 实现银行处理器模式 - 支持BOFA、Chase、Amex
- ✅ 新增银行账户管理功能 - 自动追踪账户尾号
- ✅ 创建导出模板系统 - 支持iCost等标准格式
- ✅ 规范化API接口 - RESTful设计 + Pydantic验证

## 技术栈
- **前端**: React 18 + Next.js 13 + TypeScript + Tailwind CSS
- **后端**: FastAPI + Python 3.8+ + SQLAlchemy + Pydantic
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **AI**: OpenAI GPT-4 / Anthropic Claude (可切换)
- **部署**: Vercel (前端) + Railway (后端)

## 快速开始

### 开发环境启动
```bash
# 一键启动前后端
./start_dev.sh

# 或分别启动
# 后端 (http://localhost:8000)
python3 api/main_v2.py

# 前端 (http://localhost:3000)
cd frontend && npm run dev
```

### API文档
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

---

## 核心业务流程

### 用户操作流程
```
1. 上传PDF银行对账单
   ↓
2. 系统自动识别银行类型（招商/工行/BOFA/Chase等）
   ↓
3. 银行特定预处理（清洗噪音，提取交易数据）
   ↓
4. AI智能解析（可选，用于增强处理）
   ↓
5. 生成标准化CSV并保存到数据库
   ↓
6. 用户选择导出模板（iCost/金蝶/用友/自定义）
   ↓
7. 下载模板格式的文件
```

### 数据处理流程
```
PDF文本（10,000字）
  ↓ [银行特定预处理]
标准化文本（1,000字，90%噪音已清除）
  ↓ [AI处理-可选]
结构化JSON数据
  ↓ [数据库存储]
标准CSV格式
  ↓ [模板转换]
iCost/金蝶/用友格式
```

---

## 新架构说明 (v2.0)

### 架构重构亮点

#### 1. 分层架构设计
```
┌─────────────────────────────────────────┐
│          API Layer (Routes)             │  ← FastAPI路由层
├─────────────────────────────────────────┤
│        Service Layer (Business)         │  ← 业务逻辑层
├─────────────────────────────────────────┤
│       Core Layer (Processors/AI)        │  ← 核心处理层
├─────────────────────────────────────────┤
│      Data Layer (Models/Database)       │  ← 数据访问层
└─────────────────────────────────────────┘
```

#### 2. 新增模块

**核心处理器 (api/core/processors/)**
- `BankProcessor` - 银行处理器基类，定义统一接口
- `BOFAProcessor` - Bank of America处理器
- `ChaseProcessor` - Chase Bank处理器
- `AmexProcessor` - American Express处理器
- `ProcessorRegistry` - 自动银行识别和处理器分发

**服务层 (api/services/)**
- `AuthService` - 认证服务 (JWT, 密码加密)
- `FileService` - 文件处理服务 (上传, 处理, 删除)
- `ExportService` - 导出服务 (模板转换)

**数据模型 (api/core/models.py)**
- `User` - 用户模型
- `BankAccount` - **新增** 银行账户模型 (追踪账户尾号)
- `File` - 文件模型
- `Transaction` - 交易记录模型
- `UsageLog` - 使用日志模型

**Pydantic Schemas (api/schemas/)**
- 所有API请求/响应都有类型验证
- 自动生成API文档

#### 3. 关键改进

**✅ 银行处理器模式**
```python
# 每个银行有独立的处理器类
class BOFAProcessor(BankProcessor):
    def detect(self, text: str) -> bool:
        # 检测是否是BOFA对账单
        return "BANK OF AMERICA" in text.upper()

    def clean_text(self, text: str) -> str:
        # BOFA特定的文本清洗逻辑 (去除90%噪音)
        pass

    def extract_transactions(self, text: str) -> List[Dict]:
        # 提取交易数据
        pass
```

**✅ 自动银行识别**
```python
# 系统自动检测银行类型并选择对应处理器
registry = ProcessorRegistry()
processor = registry.get_processor(pdf_text)  # 自动匹配
result = processor.process(pdf_text)
```

**✅ 导出模板系统**
```python
# iCost模板示例
class ICostTemplate(ExportTemplate):
    def transform(self, transactions: List[Dict]) -> pd.DataFrame:
        # 转换为iCost格式的CSV
        return df  # 日期(YYYYMMDD), 摘要, 借方, 贷方, 余额
```

**✅ 银行账户管理**
- 自动创建和关联银行账户
- 追踪账户后4位 (或5位 for Amex)
- 支持多账户管理

#### 4. API端点结构

**认证 (/api/auth)**
- `POST /register` - 用户注册
- `POST /login` - 用户登录
- `GET /me` - 获取当前用户
- `POST /logout` - 退出登录

**文件处理 (/api/files)**
- `POST /upload` - 上传PDF
- `POST /process` - 处理文件
- `GET /list` - 文件列表
- `GET /{file_id}/transactions` - 获取交易
- `POST /export` - 导出文件
- `DELETE /{file_id}` - 删除文件
- `GET /templates` - 导出模板列表

**银行账户 (/api/bank-accounts)**
- `GET /` - 账户列表
- `POST /` - 创建账户
- `PUT /{id}` - 更新账户
- `DELETE /{id}` - 删除账户
- `GET /{id}` - 获取账户详情

---

## 项目架构设计

### 完整目录结构
```
BankEaseAI/
│
├── api/                                 # FastAPI 后端
│   ├── main.py                         # 应用入口（简洁，只负责路由注册）
│   ├── config.py                       # 配置管理
│   ├── database.py                     # 数据库连接
│   │
│   ├── core/                           # 核心业务逻辑（框架无关）
│   │   │
│   │   ├── processors/                # 银行处理器（核心价值）
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # 处理器基类
│   │   │   ├── registry.py            # 处理器注册中心
│   │   │   │
│   │   │   ├── us/                    # 美国银行
│   │   │   │   ├── __init__.py
│   │   │   │   ├── bofa.py           # Bank of America
│   │   │   │   ├── chase.py          # Chase Bank
│   │   │   │   ├── chase_credit.py   # Chase Credit Card
│   │   │   │   └── amex.py           # American Express
│   │   │   │
│   │   │   └── cn/                    # 中国银行
│   │   │       ├── __init__.py
│   │   │       ├── cmb.py            # 招商银行
│   │   │       ├── icbc.py           # 工商银行
│   │   │       ├── ccb.py            # 建设银行
│   │   │       ├── abc.py            # 农业银行
│   │   │       └── boc.py            # 中国银行
│   │   │
│   │   ├── ai/                        # AI提供商（可替换）
│   │   │   ├── __init__.py
│   │   │   ├── base.py               # AI基类
│   │   │   ├── openai_provider.py    # ChatGPT
│   │   │   ├── anthropic_provider.py # Claude
│   │   │   ├── gemini_provider.py    # Google Gemini
│   │   │   └── config.py             # AI配置
│   │   │
│   │   ├── exporters/                 # 导出模板（可扩展）
│   │   │   ├── __init__.py
│   │   │   ├── base.py               # 导出器基类
│   │   │   ├── standard.py           # 标准CSV
│   │   │   ├── icost.py              # iCost模板
│   │   │   ├── kingdee.py            # 金蝶模板
│   │   │   ├── yonyou.py             # 用友模板
│   │   │   └── registry.py           # 模板注册中心
│   │   │
│   │   └── security.py                # 安全相关（JWT、密码加密）
│   │
│   ├── models/                        # 数据库模型（ORM）
│   │   ├── __init__.py
│   │   ├── base.py                   # Base模型
│   │   ├── user.py                   # 用户模型
│   │   ├── file.py                   # 文件模型
│   │   ├── transaction.py            # 交易记录模型
│   │   ├── export_template.py        # 导出模板模型
│   │   └── usage_log.py              # 使用记录模型
│   │
│   ├── schemas/                       # Pydantic验证模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── auth.py
│   │   ├── file.py
│   │   ├── transaction.py
│   │   └── export.py
│   │
│   ├── routes/                        # API路由
│   │   ├── __init__.py
│   │   ├── auth.py                   # POST /api/auth/login
│   │   ├── files.py                  # POST /api/files/upload
│   │   ├── transactions.py           # GET  /api/transactions
│   │   ├── export.py                 # POST /api/export/{template_id}
│   │   ├── templates.py              # GET  /api/templates
│   │   ├── dashboard.py              # GET  /api/dashboard/stats
│   │   └── users.py                  # GET  /api/users/profile
│   │
│   ├── services/                      # 业务服务层
│   │   ├── __init__.py
│   │   ├── auth_service.py           # 认证服务
│   │   ├── pdf_service.py            # PDF处理服务
│   │   ├── transaction_service.py    # 交易处理服务
│   │   ├── export_service.py         # 导出服务
│   │   ├── storage_service.py        # 文件存储服务
│   │   └── user_service.py           # 用户服务
│   │
│   ├── middleware/                    # 中间件
│   │   ├── __init__.py
│   │   ├── auth.py                   # 认证中间件
│   │   ├── error_handler.py          # 错误处理
│   │   └── logging.py                # 日志中间件
│   │
│   └── utils/                         # 工具函数
│       ├── __init__.py
│       ├── pdf_extractor.py          # PDF文本提取
│       ├── validators.py             # 数据验证
│       └── helpers.py                # 辅助函数
│
├── frontend/                          # Next.js 前端
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx              # 主页
│   │   │   ├── auth/                 # 认证
│   │   │   │   └── page.tsx
│   │   │   ├── dashboard/            # 仪表板
│   │   │   │   └── page.tsx
│   │   │   ├── upload/               # 上传
│   │   │   │   └── page.tsx
│   │   │   ├── transactions/         # 交易记录（新增）
│   │   │   │   └── page.tsx
│   │   │   ├── export/               # 导出页面（新增）
│   │   │   │   └── page.tsx
│   │   │   └── settings/             # 设置
│   │   │       └── page.tsx
│   │   │
│   │   ├── components/
│   │   │   ├── Logo.tsx
│   │   │   ├── FileUpload.tsx
│   │   │   ├── TransactionTable.tsx  # 交易记录表格
│   │   │   ├── TemplateSelector.tsx  # 模板选择器
│   │   │   ├── ExportPreview.tsx     # 导出预览
│   │   │   └── ProcessingStatus.tsx  # 处理状态
│   │   │
│   │   ├── hooks/
│   │   │   └── useAuth.tsx
│   │   │
│   │   └── lib/
│   │       ├── api.ts                # API客户端
│   │       └── types.ts              # 类型定义
│   │
│   └── package.json
│
├── storage/                           # 文件存储
│   ├── uploads/                      # 上传的PDF
│   ├── processed/                    # 处理后的标准CSV
│   └── exports/                      # 导出的模板文件
│
├── templates/                         # 模板示例文件（可选，用于文档参考）
│   ├── icost_sample.csv              # iCost格式示例
│   ├── kingdee_sample.csv            # 金蝶格式示例
│   └── yonyou_sample.csv             # 用友格式示例
│
├── alembic/                          # 数据库迁移
│   ├── versions/
│   └── env.py
│
├── tests/                            # 测试
│   ├── test_processors/              # 测试银行处理器
│   ├── test_exporters/               # 测试导出器
│   └── test_api/                     # 测试API
│
├── docs/                             # 文档
│   ├── API.md
│   ├── BANKS.md                     # 支持的银行
│   └── TEMPLATES.md                 # 模板说明
│
├── .env.example                     # 环境变量示例
├── requirements.txt                 # Python依赖
├── alembic.ini                      # 数据库迁移配置
└── README.md
```

---

## 核心模块设计

### 1. 银行处理器（核心价值）

**基类设计**:
```python
class BankProcessor(ABC):
    bank_name: str = "UNKNOWN"

    @abstractmethod
    def detect(self, text: str) -> bool:
        """检测是否是该银行"""
        pass

    @abstractmethod
    def clean_text(self, text: str) -> Dict:
        """清洗文本，返回标准化数据"""
        pass
```

**为什么重要？**
- 每个银行PDF格式完全不同（表格结构、字段顺序、日期格式）
- 预处理可清除90%噪音，降低AI成本
- 提高准确率从60%到95%

**示例：招商银行处理器**
```python
class CMBProcessor(BankProcessor):
    bank_name = "招商银行"

    def detect(self, text: str) -> bool:
        return "招商银行" in text or "CMB" in text

    def clean_text(self, text: str) -> Dict:
        # 1. 识别交易区域标记
        # 2. 提取日期、摘要、金额、余额
        # 3. 处理中文字符和特殊格式
        # 4. 返回标准化数据
        return {
            "bank": "招商银行",
            "transactions": [...],
            "metadata": {...}
        }
```

### 2. AI提供商（可替换）

**设计理念**：AI只是工具，可随时替换

```python
class AIProvider(ABC):
    @abstractmethod
    def extract_transactions(self, text: str) -> List[Dict]:
        pass

# 实现
class OpenAIProvider(AIProvider):
    def extract_transactions(self, text: str) -> List[Dict]:
        # 调用GPT-4处理
        pass

class AnthropicProvider(AIProvider):
    def extract_transactions(self, text: str) -> List[Dict]:
        # 调用Claude处理
        pass
```

**切换AI只需修改配置**:
```python
# .env
AI_PROVIDER=openai  # 或 anthropic / gemini
```

### 3. 导出模板系统

**设计理念**：Python代码实现的CSV转换器，不是配置文件

**标准化数据格式**（数据库存储）:
```python
{
  "date": "2025-01-15",           # YYYY-MM-DD
  "description": "超市购物",
  "amount": -150.00,               # 负数=支出，正数=收入
  "balance": 9850.00,
  "type": "debit"                  # debit=借方，credit=贷方
}
```

**导出器基类**:
```python
class ExportTemplate(ABC):
    template_id: str = "unknown"
    template_name: str = "未知模板"
    file_extension: str = "csv"

    @abstractmethod
    def transform(self, transactions: List[Dict]) -> pd.DataFrame:
        """转换为模板格式"""
        pass

    def export_csv(self, transactions: List[Dict]) -> str:
        df = self.transform(transactions)
        return df.to_csv(index=False, encoding='utf-8-sig')
```

**iCost CSV导出器**:
```python
class ICostTemplate(ExportTemplate):
    template_id = "icost"
    template_name = "iCost"

    def transform(self, transactions: List[Dict]) -> pd.DataFrame:
        data = []
        for trans in transactions:
            # 日期: 2025-01-15 → 20250115
            date_str = trans["date"].replace("-", "")

            # 借贷方分离
            amount = float(trans["amount"])
            debit = abs(amount) if amount < 0 else 0.00
            credit = amount if amount > 0 else 0.00

            data.append({
                "日期": date_str,
                "摘要": trans["description"],
                "借方": f"{debit:.2f}",
                "贷方": f"{credit:.2f}",
                "余额": f"{trans['balance']:.2f}"
            })
        return pd.DataFrame(data)
```

**金蝶CSV导出器**:
```python
class KingdeeTemplate(ExportTemplate):
    template_id = "kingdee"
    template_name = "金蝶"

    def transform(self, transactions: List[Dict]) -> pd.DataFrame:
        data = []
        for trans in transactions:
            amount = float(trans["amount"])
            direction = "贷" if amount > 0 else "借"

            data.append({
                "凭证日期": trans["date"],      # YYYY-MM-DD
                "摘要": trans["description"],
                "科目编码": "1002",
                "科目名称": "银行存款",
                "方向": direction,
                "金额": f"{abs(amount):.2f}"
            })
        return pd.DataFrame(data)
```

**用友CSV导出器**:
```python
class YonyouTemplate(ExportTemplate):
    template_id = "yonyou"
    template_name = "用友"

    def transform(self, transactions: List[Dict]) -> pd.DataFrame:
        data = []
        for trans in transactions:
            amount = float(trans["amount"])
            # 日期: 2025-01-15 → 2025/01/15
            date_str = trans["date"].replace("-", "/")
            # 借贷方向: 1=借，0=贷
            direction = 0 if amount > 0 else 1

            data.append({
                "制单日期": date_str,
                "凭证类型": "记",
                "摘要": trans["description"],
                "科目编码": "100201",
                "科目名称": "银行存款",
                "借贷方向": direction,
                "金额": f"{abs(amount):.2f}"
            })
        return pd.DataFrame(data)
```

**CSV格式对比**:

标准格式（数据库）:
```csv
date,description,amount,balance,type
2025-01-15,超市购物,-150.00,9850.00,debit
2025-01-16,工资收入,5000.00,14850.00,credit
```

iCost格式:
```csv
日期,摘要,借方,贷方,余额
20250115,超市购物,150.00,0.00,9850.00
20250116,工资收入,0.00,5000.00,14850.00
```

金蝶格式:
```csv
凭证日期,摘要,科目编码,科目名称,方向,金额
2025-01-15,超市购物,1002,银行存款,借,150.00
2025-01-16,工资收入,1002,银行存款,贷,5000.00
```

用友格式:
```csv
制单日期,凭证类型,摘要,科目编码,科目名称,借贷方向,金额
2025/01/15,记,超市购物,100201,银行存款,1,150.00
2025/01/16,记,工资收入,100201,银行存款,0,5000.00
```

---

## API 端点设计

### 认证相关
```
POST   /api/auth/register      # 用户注册
POST   /api/auth/login         # 用户登录
GET    /api/auth/me            # 获取当前用户
POST   /api/auth/logout        # 用户登出
```

### 文件处理
```
POST   /api/files/upload       # 上传PDF文件
GET    /api/files/{file_id}    # 获取文件详情
DELETE /api/files/{file_id}    # 删除文件
```

### 交易记录
```
GET    /api/transactions              # 获取交易列表
GET    /api/transactions/{id}         # 获取交易详情
POST   /api/transactions/batch        # 批量操作
```

### 导出功能
```
GET    /api/templates                 # 列出所有模板
GET    /api/templates/{template_id}   # 获取模板详情
POST   /api/export/{template_id}      # 使用模板导出
GET    /api/export/download/{file_id} # 下载导出文件
```

### 仪表板
```
GET    /api/dashboard/stats           # 获取统计数据
GET    /api/dashboard/recent-files    # 最近文件
```

---

## 数据库设计

### 核心表结构

**users** - 用户表
```sql
id              INTEGER PRIMARY KEY
username        VARCHAR(50) UNIQUE
email           VARCHAR(100) UNIQUE
hashed_password VARCHAR(255)
plan            VARCHAR(20)         -- free/pro/enterprise
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

**bank_accounts** - 银行账户表（新增）
```sql
id              INTEGER PRIMARY KEY
user_id         INTEGER FOREIGN KEY
bank            VARCHAR(50)         -- 银行名称（招商银行、工商银行等）
account_type    VARCHAR(50)         -- 账户类型（储蓄卡、信用卡、一卡通）
account_number  VARCHAR(100)        -- 完整账号（加密存储）
account_last4   VARCHAR(4)          -- 账户尾号（明文，用于显示）
account_name    VARCHAR(100)        -- 账户别名（如"工资卡"、"备用卡"）
currency        VARCHAR(10)         -- 币种（CNY、USD等）
is_active       BOOLEAN DEFAULT TRUE
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

**files** - 文件表
```sql
id              INTEGER PRIMARY KEY
user_id         INTEGER FOREIGN KEY
account_id      INTEGER FOREIGN KEY  -- 关联到 bank_accounts 表
filename        VARCHAR(255)
file_path       VARCHAR(500)
file_size       INTEGER
bank            VARCHAR(50)          -- 冗余字段，方便查询
account_last4   VARCHAR(4)           -- 冗余字段，账户尾号
statement_period VARCHAR(20)         -- 账单周期（2025-01）
status          VARCHAR(20)          -- processing/completed/failed
error_message   TEXT                 -- 错误信息（如果失败）
created_at      TIMESTAMP
```

**transactions** - 交易记录表
```sql
id              INTEGER PRIMARY KEY
user_id         INTEGER FOREIGN KEY
file_id         INTEGER FOREIGN KEY
account_id      INTEGER FOREIGN KEY  -- 关联到银行账户

-- 交易信息
date            DATE
description     TEXT
amount          DECIMAL(15,2)
balance         DECIMAL(15,2)
transaction_type VARCHAR(10)         -- debit/credit

-- 银行信息（冗余字段，提高查询性能）
bank            VARCHAR(50)
account_type    VARCHAR(50)
account_last4   VARCHAR(4)           -- 账户尾号

-- 分类信息（可选，用于未来扩展）
category        VARCHAR(50)          -- 消费分类（餐饮、交通、购物等）
merchant        VARCHAR(100)         -- 商户名称
tags            TEXT                 -- 标签（JSON数组）

-- 元数据
raw_data        TEXT                 -- JSON格式原始数据
created_at      TIMESTAMP
```

**usage_logs** - 使用记录表
```sql
id          INTEGER PRIMARY KEY
user_id     INTEGER FOREIGN KEY
feature     VARCHAR(50)             -- pdf_conversion/export/api_call
count       INTEGER
period      VARCHAR(20)             -- 2025-01
metadata    TEXT                    -- JSON格式额外信息
created_at  TIMESTAMP
```

---

## 环境配置

### 环境变量 (.env)
```bash
# 应用配置
PROJECT_NAME=BankEaseAI
VERSION=3.0.0
DEBUG=False

# 安全配置
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 数据库配置
DATABASE_URL=sqlite:///./bankeaseai.db
# 生产环境使用PostgreSQL
# DATABASE_URL=postgresql://user:password@localhost/bankeaseai

# CORS配置
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# AI配置
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
AI_PROVIDER=openai  # openai | anthropic | gemini

# 文件存储
UPLOAD_DIR=./storage/uploads
PROCESSED_DIR=./storage/processed
EXPORT_DIR=./storage/exports
MAX_FILE_SIZE=10485760  # 10MB
```

### 前端环境变量
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=BankEaseAI
```

---

## 启动方式

### 方式1: 开发环境（推荐）

#### **后端启动**
```bash
# 终端1 - 启动后端
# 激活虚拟环境
source bankeaseai/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行数据库迁移
alembic upgrade head

# 启动API服务
uvicorn api.main:app --reload --port 8000
```

#### **前端启动（HTTPS）**
```bash
# 终端2 - 首次使用需要生成HTTPS证书
./setup-https.sh

# 启动前端开发服务器（HTTPS）
cd frontend
npm install
npm run dev

# 或使用HTTP模式
npm run dev:http
```

**访问地址**:
- 前端（HTTPS）: https://localhost:3000 ✅
- 前端（HTTP）: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 方式2: HTTPS 证书配置

#### **自动配置（推荐）**
```bash
# 运行自动配置脚本
./setup-https.sh

# 脚本会自动:
# 1. 检查 mkcert 是否安装
# 2. 安装本地 CA
# 3. 生成 HTTPS 证书
# 4. 保存到 frontend/.cert/
```

#### **手动配置**
```bash
# 1. 安装 mkcert
# macOS
brew install mkcert
brew install nss  # 用于Firefox

# Ubuntu/Debian
sudo apt install libnss3-tools
wget -O mkcert https://github.com/FiloSottile/mkcert/releases/download/v1.4.4/mkcert-v1.4.4-linux-amd64
chmod +x mkcert
sudo mv mkcert /usr/local/bin/

# 2. 生成证书
cd frontend
mkdir -p .cert
mkcert -install
mkcert -key-file .cert/localhost-key.pem -cert-file .cert/localhost-cert.pem localhost 127.0.0.1 ::1

# 3. 启动服务
npm run dev  # 自动使用 HTTPS
```

#### **可用的启动命令**
```bash
npm run dev         # HTTPS模式（如有证书）/ HTTP模式（无证书）
npm run dev:http    # 强制 HTTP 模式
npm run dev:https   # 强制 HTTPS 模式（需要证书）
npm run build       # 构建生产版本
npm run start       # 生产环境启动（HTTPS）
npm run start:http  # 生产环境启动（HTTP）
```

### 方式3: 使用脚本启动

```bash
# 启动后端
./start_api.sh

# 启动前端（新终端）
./start_frontend.sh
```

### 方式4: Docker（生产环境）

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 方式5: 生产环境 HTTPS（Nginx + Let's Encrypt）

#### **Nginx 配置**
```nginx
# /etc/nginx/sites-available/bankeaseai
server {
    listen 80;
    server_name bankeaseai.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name bankeaseai.com;

    ssl_certificate /etc/letsencrypt/live/bankeaseai.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bankeaseai.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

#### **获取 Let's Encrypt 证书**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d bankeaseai.com
sudo certbot renew --dry-run  # 测试自动续期
```

---

## 开发工作流

### 添加新银行支持

1. **创建处理器文件**
```bash
# 中国银行示例
touch api/core/processors/cn/boc.py
```

2. **实现处理器类**
```python
# api/core/processors/cn/boc.py
from ..base import BankProcessor

class BOCProcessor(BankProcessor):
    bank_name = "中国银行"

    def detect(self, text: str) -> bool:
        return "中国银行" in text or "Bank of China" in text

    def clean_text(self, text: str) -> Dict:
        # 实现具体清洗逻辑
        pass
```

3. **注册处理器**
```python
# api/core/processors/registry.py
from .cn.boc import BOCProcessor

class ProcessorRegistry:
    def __init__(self):
        self.processors = [
            # ... 其他处理器
            BOCProcessor(),
        ]
```

### 添加新导出模板

1. **创建模板文件**
```bash
touch api/core/exporters/mysoft.py
```

2. **实现模板类**
```python
# api/core/exporters/mysoft.py
from .base import ExportTemplate

class MySoftTemplate(ExportTemplate):
    template_id = "mysoft"
    template_name = "MySoft财务软件"

    def transform(self, transactions: List[Dict]) -> pd.DataFrame:
        # 实现转换逻辑
        pass
```

3. **注册模板**
```python
# api/core/exporters/registry.py
from .mysoft import MySoftTemplate

templates = {
    "mysoft": MySoftTemplate(),
}
```

---

## 测试

### 运行测试
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_processors/test_cmb.py

# 覆盖率报告
pytest --cov=api tests/
```

### 测试示例
```python
# tests/test_processors/test_cmb.py
def test_cmb_detection():
    processor = CMBProcessor()
    text = "招商银行对账单..."
    assert processor.detect(text) == True

def test_cmb_cleaning():
    processor = CMBProcessor()
    result = processor.clean_text(sample_text)
    assert result["bank"] == "招商银行"
    assert len(result["transactions"]) > 0
```

---

## 部署

### Vercel (前端)
```bash
# 安装Vercel CLI
npm i -g vercel

# 部署
cd frontend
vercel --prod
```

### Railway (后端)
```bash
# 连接GitHub仓库
# 在Railway控制台设置环境变量
# 自动部署
```

### Docker部署
```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: ./api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://...

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://api:8000
```

---

## AI助手开发指南

当AI助手处理这个项目时，应该：

### 1. 项目启动检查
- 检查Node.js和Python环境
- 确认依赖是否安装
- 验证环境变量配置
- 检查数据库连接

### 2. 代码开发原则
- 遵循现有架构模式
- 新功能先添加到core层，再连接到routes
- 所有业务逻辑放在services层
- 使用类型注解和文档字符串

### 3. 银行处理器开发
- 先收集真实PDF样本
- 分析格式特点
- 编写清洗规则
- 充分测试

### 4. API开发规范
- 使用Pydantic验证输入
- 统一返回格式
- 完善错误处理
- 添加API文档

### 5. 前端开发规范
- 使用TypeScript类型
- 组件复用
- 统一样式风格
- 响应式设计

---

## 常见问题

### Q: 如何切换AI提供商？
A: 修改 `.env` 文件中的 `AI_PROVIDER` 变量：
```bash
AI_PROVIDER=anthropic  # 改为Claude
```

### Q: 如何添加新的导出模板？
A:
1. 在 `api/core/exporters/` 创建新模板类
2. 继承 `ExportTemplate` 基类
3. 实现 `transform()` 方法
4. 在 `registry.py` 注册模板

### Q: 数据库如何迁移？
A: 使用Alembic管理迁移：
```bash
# 创建迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

### Q: 如何调试PDF处理？
A:
1. 启用DEBUG日志
2. 使用 `print()` 输出中间结果
3. 保存清洗前后的文本对比
4. 检查正则表达式匹配

---

## 版本历史

### v3.0.0 (计划中)
- ✅ 重构后端架构
- ✅ 银行处理器抽象化
- ✅ AI提供商可切换
- ✅ 导出模板系统
- ✅ 交易记录持久化

### v2.0.0 (当前)
- ✅ 前后端分离
- ✅ JWT认证
- ✅ 用户系统
- ✅ 基础PDF处理

### v1.0.0
- ✅ Streamlit原型
- ✅ PDF解析
- ✅ AI处理

---

## 贡献指南

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

---

## 许可证

MIT License - 详见 LICENSE 文件
