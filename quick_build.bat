@echo off
chcp 65001 >nul
echo 🚀 智能文档处理系统 - 快速构建
echo ================================

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到pip，请检查Python安装
    pause
    exit /b 1
)

echo ✅ Python环境检查通过

REM 安装构建依赖
echo 📦 安装构建依赖...
pip install -r requirements-build.txt
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo ✅ 依赖安装完成

REM 运行构建脚本
echo 🔨 开始构建...
python build.py
if errorlevel 1 (
    echo ❌ 构建失败
    pause
    exit /b 1
)

echo ✅ 构建完成！
echo 📦 可执行文件位置: dist\DocumentProcessor.exe
echo 📁 发布包位置: release\
echo.
echo 💡 测试可执行文件:
echo    cd dist
echo    DocumentProcessor.exe --help
echo.

pause