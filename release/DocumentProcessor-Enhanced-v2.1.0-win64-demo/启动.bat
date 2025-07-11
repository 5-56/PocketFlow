@echo off
chcp 65001 >nul
echo 🎨 智能文档自动排版系统 v2.1.0 - 增强版 (演示版)
echo ================================================
echo.
echo ⚠️  这是演示版本，实际exe文件将通过GitHub Actions构建
echo 📦 请等待GitHub Actions完成构建，然后从Release页面下载
echo 🔗 GitHub Release: https://github.com/5-56/PocketFlow/releases
echo.
echo 当前包含:
echo - Python源码版本 (需要Python环境)
echo - 完整文档和说明
echo - 构建配置文件
echo.
echo 环境检查...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Python环境
    echo 💡 请安装Python 3.8+或等待真正的exe文件构建完成
    echo.
) else (
    echo ✅ 检测到Python环境
    echo 💡 您可以直接运行: python main_enhanced.py --web
    echo.
)

echo 选择操作:
echo [1] 🌐 使用Python运行Web服务 (如果已安装Python)
echo [2] 📱 打开GitHub Release页面下载真正的exe
echo [3] 📖 查看使用说明
echo [4] 🚪 退出
echo.
set /p choice="请选择 (1-4): "

if "%choice%"=="1" (
    echo 启动Python版本...
    python main_enhanced.py --web
) else if "%choice%"=="2" (
    echo 打开GitHub Release页面...
    start https://github.com/5-56/PocketFlow/releases
) else if "%choice%"=="3" (
    echo 查看使用说明...
    type "使用说明.txt"
    pause
) else (
    echo 感谢使用！
)
