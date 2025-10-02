#!/bin/bash

# BankEaseAI HTTPS 证书生成脚本

set -e

echo "🔒 BankEaseAI HTTPS 证书生成工具"
echo "================================"
echo ""

# 检查 mkcert 是否安装
if ! command -v mkcert &> /dev/null; then
    echo "❌ mkcert 未安装"
    echo ""
    echo "请先安装 mkcert:"
    echo ""
    echo "macOS:"
    echo "  brew install mkcert"
    echo "  brew install nss  # 用于Firefox"
    echo ""
    echo "Ubuntu/Debian:"
    echo "  sudo apt install libnss3-tools"
    echo "  wget -O mkcert https://github.com/FiloSottile/mkcert/releases/download/v1.4.4/mkcert-v1.4.4-linux-amd64"
    echo "  chmod +x mkcert"
    echo "  sudo mv mkcert /usr/local/bin/"
    echo ""
    echo "Windows:"
    echo "  choco install mkcert"
    echo ""
    exit 1
fi

echo "✅ mkcert 已安装"
echo ""

# 创建证书目录
CERT_DIR="./frontend/.cert"
mkdir -p "$CERT_DIR"

echo "📂 证书目录: $CERT_DIR"
echo ""

# 安装本地 CA
echo "🔐 安装本地证书颁发机构 (CA)..."
mkcert -install
echo ""

# 生成证书
echo "🔑 生成本地 HTTPS 证书..."
mkcert -key-file "$CERT_DIR/localhost-key.pem" \
       -cert-file "$CERT_DIR/localhost-cert.pem" \
       localhost 127.0.0.1 ::1

echo ""
echo "✅ HTTPS 证书生成成功！"
echo ""
echo "证书文件:"
echo "  - 私钥: $CERT_DIR/localhost-key.pem"
echo "  - 证书: $CERT_DIR/localhost-cert.pem"
echo ""
echo "📝 下一步:"
echo "  1. cd frontend"
echo "  2. npm run dev"
echo "  3. 访问 https://localhost:3000"
echo ""
echo "⚠️  注意: .cert/ 目录已添加到 .gitignore，不会被提交到 Git"
echo ""
