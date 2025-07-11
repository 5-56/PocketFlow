#!/bin/bash

echo "🎨 智能文档自动排版系统 v2.1.0 - 增强版"
echo "================================================"
echo ""

# 检查API密钥
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  未设置 OPENAI_API_KEY 环境变量"
    echo ""
    echo "请先设置API密钥:"
    echo "export OPENAI_API_KEY=your_api_key_here"
    echo ""
    echo "或者在启动后按照提示进行设置"
    echo ""
fi

echo "启动选项:"
echo "[1] 🌐 Web服务模式 (推荐)"
echo "[2] 💻 命令行模式"
echo "[3] ℹ️  系统信息"
echo "[4] 🔧 API测试"
echo ""
read -p "请选择模式 (1-4): " choice

case $choice in
    1)
        echo "启动Web服务..."
        ./DocumentProcessor-Enhanced --web
        ;;
    2)
        echo "启动命令行模式..."
        ./DocumentProcessor-Enhanced --cli
        ;;
    3)
        ./DocumentProcessor-Enhanced --info
        ;;
    4)
        ./DocumentProcessor-Enhanced --test
        ;;
    *)
        echo "无效选择，启动Web服务模式..."
        ./DocumentProcessor-Enhanced --web
        ;;
esac

echo ""
echo "程序已结束"
read -p "按回车键退出..."
