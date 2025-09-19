# BankEaseAI - Streamlit Web App

BankEaseAI是一个基于Streamlit的银行对账单AI处理应用，可以将银行对账单转换为iCost格式。

## 功能特性

- 📄 PDF银行对账单解析
- 🤖 AI智能文本处理
- 📊 数据格式转换
- 🌐 Web界面操作
- 📱 响应式设计

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
