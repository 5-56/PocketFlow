#!/bin/bash

echo "🚀 智能文档处理系统 - 快速构建"
echo "================================"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python 3，请先安装Python 3.8+"
    exit 1
fi

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ 未找到pip3，请检查Python安装"
    exit 1
fi

echo "✅ Python环境检查通过"

# 安装构建依赖
echo "📦 安装构建依赖..."
pip3 install -r requirements-build.txt
if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
fi

echo "✅ 依赖安装完成"

# 运行构建脚本  
echo "🔨 开始构建..."
python3 build.py
if [ $? -ne 0 ]; then
    echo "❌ 构建失败"
    exit 1
fi

echo "✅ 构建完成！"
echo "📦 可执行文件位置: dist/DocumentProcessor"
echo "📁 发布包位置: release/"
echo ""
echo "💡 测试可执行文件:"
echo "   cd dist"
echo "   ./DocumentProcessor --help"
echo ""

# 设置可执行权限
if [ -f "dist/DocumentProcessor" ]; then
    chmod +x dist/DocumentProcessor
    echo "✅ 设置可执行权限完成"
fi