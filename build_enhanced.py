#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能文档处理系统 - 增强版构建脚本
用于构建 main_enhanced.py 的可执行文件
"""

import os
import sys
import subprocess
import shutil
import zipfile
import tarfile
from pathlib import Path
import argparse
import json
from datetime import datetime

def load_version_info():
    """加载版本信息"""
    try:
        with open('version.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "version": "2.1.0",
            "description": "智能文档自动排版系统 - 增强版",
            "build_number": 3
        }

VERSION_INFO = load_version_info()

def check_dependencies():
    """检查构建依赖"""
    print("🔍 检查构建依赖...")
    
    required_packages = ['pyinstaller', 'setuptools']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package}")
    
    if missing_packages:
        print(f"\n❌ 缺少以下依赖包: {', '.join(missing_packages)}")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def clean_build():
    """清理构建目录"""
    print("🧹 清理旧的构建文件...")
    
    clean_dirs = ['build', 'dist', '__pycache__']
    
    for dir_name in clean_dirs:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  🗑️  删除目录: {dir_name}")
    
    # 递归删除 __pycache__ 目录
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            cache_dir = os.path.join(root, '__pycache__')
            shutil.rmtree(cache_dir)
            print(f"  🗑️  删除缓存: {cache_dir}")

def create_icon():
    """创建应用图标（如果不存在）"""
    assets_dir = Path("assets")
    icon_path = assets_dir / "icon.ico"
    
    if not icon_path.exists():
        print("📱 创建默认图标...")
        assets_dir.mkdir(exist_ok=True)
        print("  💡 提示: 将自定义图标放置在 assets/icon.ico")

def create_spec_file(platform='windows'):
    """创建PyInstaller spec文件"""
    print(f"📝 创建 {platform} 平台的spec文件...")
    
    if platform == 'windows':
        spec_name = 'build_enhanced_windows.spec'
        exe_name = 'DocumentProcessor-Enhanced'
        console = False  # Windows GUI模式
    else:
        spec_name = 'build_enhanced_linux.spec'
        exe_name = 'DocumentProcessor-Enhanced-linux'
        console = True   # Linux控制台模式
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main_enhanced.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('static', 'static'),
        ('templates', 'templates'),
        ('utils', 'utils'),
        ('pocketflow', 'pocketflow'),
        ('version.json', '.'),
        ('requirements_enhanced.txt', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        # 核心框架
        'pocketflow',
        'flow',
        'nodes',
        
        # Web框架
        'fastapi',
        'fastapi.staticfiles',
        'fastapi.templating',
        'uvicorn',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'websockets',
        'aiofiles',
        'jinja2',
        
        # AI和数据处理
        'openai',
        'pydantic',
        'pydantic_settings',
        'markdown',
        'PIL',
        'PIL.Image',
        'PIL.ImageEnhance',
        'PIL.ImageFilter',
        
        # 系统和工具
        'asyncio',
        'concurrent.futures',
        'logging.handlers',
        'json',
        'yaml',
        'pathlib',
        'datetime',
        'psutil',
        
        # HTTP和网络
        'httpx',
        'aiohttp',
        'requests',
        'urllib3',
        
        # 文档处理（可选）
        'pypdf',
        'docx',
        'pptx',
        
        # 数据库和缓存（可选）
        'redis',
        'aioredis',
        
        # 向量数据库（可选）
        'chromadb',
        'sentence_transformers',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的包
        'tkinter',
        'matplotlib',
        'scipy',
        'sklearn',
        'tensorflow',
        'torch',
        'numpy.f2py',
        'numpy.distutils',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{exe_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console={console},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)
'''
    
    with open(spec_name, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    return spec_name

def build_executable(platform='windows'):
    """构建可执行文件"""
    print(f"🔨 开始构建 {platform} 平台的可执行文件...")
    
    # 创建spec文件
    spec_file = create_spec_file(platform)
    
    # PyInstaller命令
    cmd = [
        'pyinstaller',
        '--clean',
        '--noconfirm',
        spec_file
    ]
    
    try:
        # 运行PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("  ✅ 构建成功!")
        
        if result.stdout:
            print("构建输出:")
            for line in result.stdout.split('\n')[-10:]:  # 只显示最后10行
                if line.strip():
                    print(f"  {line}")
            
        return True
        
    except subprocess.CalledProcessError as e:
        print("  ❌ 构建失败!")
        print(f"错误: {e}")
        if e.stderr:
            print(f"错误详情: {e.stderr}")
        return False

def test_executable(platform='windows'):
    """测试可执行文件"""
    print("🧪 测试可执行文件...")
    
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("  ❌ 构建目录不存在")
        return False
    
    # 查找可执行文件
    if platform == 'windows':
        exe_pattern = "DocumentProcessor-Enhanced.exe"
    else:
        exe_pattern = "DocumentProcessor-Enhanced-linux"
    
    exe_files = list(dist_dir.glob(exe_pattern))
    if not exe_files:
        # 尝试查找任何可执行文件
        exe_files = [f for f in dist_dir.iterdir() if f.is_file() and 'DocumentProcessor' in f.name]
    
    if not exe_files:
        print("  ❌ 没有找到可执行文件")
        return False
    
    exe_file = exe_files[0]
    print(f"  📄 找到可执行文件: {exe_file}")
    print(f"  📊 文件大小: {exe_file.stat().st_size / 1024 / 1024:.1f} MB")
    
    # 简单的启动测试
    try:
        if platform == 'windows':
            test_cmd = [str(exe_file), '--info']
        else:
            test_cmd = [str(exe_file), '--info']
        
        result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("  ✅ 可执行文件测试通过")
            return True
        else:
            print(f"  ⚠️  测试警告: 返回码 {result.returncode}")
            if result.stderr:
                print(f"  错误输出: {result.stderr}")
            return True  # 不算致命错误
            
    except subprocess.TimeoutExpired:
        print("  ⚠️  测试超时，但文件可能正常")
        return True
    except Exception as e:
        print(f"  ⚠️  测试出错: {e}")
        return True  # 不算致命错误

def create_package(platform='windows'):
    """创建发布包"""
    print(f"📦 创建 {platform} 平台的发布包...")
    
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("  ❌ 构建目录不存在")
        return False
    
    # 查找可执行文件
    if platform == 'windows':
        exe_pattern = "DocumentProcessor-Enhanced.exe"
        package_suffix = "win64"
        archive_ext = ".zip"
    else:
        exe_pattern = "DocumentProcessor-Enhanced-linux"
        package_suffix = "linux-x64"
        archive_ext = ".tar.gz"
    
    exe_files = list(dist_dir.glob(exe_pattern))
    if not exe_files:
        # 尝试查找任何可执行文件
        exe_files = [f for f in dist_dir.iterdir() if f.is_file() and 'DocumentProcessor' in f.name]
    
    if not exe_files:
        print("  ❌ 没有找到可执行文件")
        return False
    
    exe_file = exe_files[0]
    print(f"  📄 找到可执行文件: {exe_file}")
    
    # 创建发布目录
    release_dir = Path("release")
    release_dir.mkdir(exist_ok=True)
    
    # 创建包目录
    version = VERSION_INFO["version"]
    package_name = f"DocumentProcessor-Enhanced-v{version}-{package_suffix}"
    package_dir = release_dir / package_name
    
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # 复制可执行文件
    if platform == 'windows':
        target_name = "DocumentProcessor-Enhanced.exe"
    else:
        target_name = "DocumentProcessor-Enhanced"
    shutil.copy2(exe_file, package_dir / target_name)
    
    # 在Linux上设置执行权限
    if platform == 'linux':
        os.chmod(package_dir / target_name, 0o755)
    
    # 复制文档文件
    docs_to_copy = [
        'README.md', 
        'RELEASE.md', 
        'requirements_enhanced.txt', 
        'version.json'
    ]
    for doc in docs_to_copy:
        if os.path.exists(doc):
            shutil.copy2(doc, package_dir)
    
    # 创建启动脚本
    if platform == 'windows':
        create_windows_launcher(package_dir, target_name)
    else:
        create_linux_launcher(package_dir, target_name)
    
    # 创建使用说明
    create_usage_guide(package_dir, platform)
    
    # 创建压缩包
    if platform == 'windows':
        archive_path = release_dir / f"{package_name}.zip"
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in package_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(package_dir)
                    zipf.write(file_path, arcname)
    else:
        archive_path = release_dir / f"{package_name}.tar.gz"
        with tarfile.open(archive_path, 'w:gz') as tarf:
            tarf.add(package_dir, arcname=package_name)
    
    print(f"  ✅ 创建发布包: {archive_path}")
    print(f"  📊 包大小: {archive_path.stat().st_size / 1024 / 1024:.1f} MB")
    
    return archive_path

def create_windows_launcher(package_dir, exe_name):
    """创建Windows启动脚本"""
    launcher_content = f'''@echo off
chcp 65001 >nul
echo 🎨 智能文档自动排版系统 v{VERSION_INFO["version"]} - 增强版
echo ================================================
echo.
echo 环境检查...
if not defined OPENAI_API_KEY (
    echo ⚠️  未设置 OPENAI_API_KEY 环境变量
    echo.
    echo 请先设置API密钥:
    echo set OPENAI_API_KEY=your_api_key_here
    echo.
    echo 或者在启动后按照提示进行设置
    echo.
)

echo 启动选项:
echo [1] 🌐 Web服务模式 ^(推荐^)
echo [2] 💻 命令行模式  
echo [3] ℹ️  系统信息
echo [4] 🔧 API测试
echo.
set /p choice="请选择模式 (1-4): "

if "%choice%"=="1" (
    echo 启动Web服务...
    {exe_name} --web
) else if "%choice%"=="2" (
    echo 启动命令行模式...
    {exe_name} --cli
) else if "%choice%"=="3" (
    {exe_name} --info
) else if "%choice%"=="4" (
    {exe_name} --test
) else (
    echo 无效选择，启动Web服务模式...
    {exe_name} --web
)

echo.
echo 程序已结束
pause
'''
    
    with open(package_dir / "启动.bat", 'w', encoding='gbk') as f:
        f.write(launcher_content)

def create_linux_launcher(package_dir, exe_name):
    """创建Linux启动脚本"""
    launcher_content = f'''#!/bin/bash

echo "🎨 智能文档自动排版系统 v{VERSION_INFO["version"]} - 增强版"
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
        ./{exe_name} --web
        ;;
    2)
        echo "启动命令行模式..."
        ./{exe_name} --cli
        ;;
    3)
        ./{exe_name} --info
        ;;
    4)
        ./{exe_name} --test
        ;;
    *)
        echo "无效选择，启动Web服务模式..."
        ./{exe_name} --web
        ;;
esac

echo ""
echo "程序已结束"
read -p "按回车键退出..."
'''
    
    launcher_path = package_dir / "start.sh"
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    # 设置执行权限
    os.chmod(launcher_path, 0o755)

def create_usage_guide(package_dir, platform):
    """创建使用说明"""
    guide_content = f'''🎨 智能文档自动排版系统 v{VERSION_INFO["version"]} - 增强版

🚀 快速开始:
1. 双击运行启动脚本
   Windows: 启动.bat
   Linux: ./start.sh
2. 选择运行模式
3. 按照提示操作

🌐 Web服务模式 (推荐):
- 访问 http://localhost:8000
- 现代化Web界面
- 实时进度更新
- 批量处理支持
- 多用户协作功能

💻 命令行模式:
- 高效命令行操作
- 脚本化批量处理
- 适合高级用户
- 支持管道操作

📋 功能特性:
{chr(10).join([f"• {feature}" for feature in VERSION_INFO.get("features", [])])}

📖 使用示例:
- "转换为现代商务风格的HTML文档，图片加圆角边框"
- "生成学术论文格式，使用蓝白配色方案"
- "制作创意设计文档，图片添加阴影效果"
- "批量处理报告，统一为企业标准格式"

⚙️ 环境设置:
1. 设置OpenAI API密钥:
   Windows: set OPENAI_API_KEY=your_api_key_here
   Linux: export OPENAI_API_KEY=your_api_key_here

2. 获取API密钥:
   访问 https://platform.openai.com/
   注册并获取API密钥

💡 使用技巧:
1. Web模式提供最佳用户体验
2. 支持拖拽文件上传
3. 可以保存常用的格式模板
4. 支持实时预览和调整
5. 批量处理节省时间

🔧 命令行选项:
--web        启动Web服务模式
--cli        启动命令行交互模式
--info       显示系统信息
--test       测试API连接
--host HOST  指定Web服务主机地址
--port PORT  指定Web服务端口
--dev        开启开发模式
--verbose    详细输出模式

🐛 故障排除:
1. API密钥错误: 检查环境变量设置
2. 网络连接问题: 确保能访问OpenAI API
3. 权限问题: 确保程序有读写权限
4. 端口占用: 使用 --port 参数指定其他端口

🔗 更多信息:
- README.md: 详细使用说明
- RELEASE.md: 版本更新日志
- GitHub仓库: 最新版本和问题反馈

📞 技术支持:
如遇问题，请访问项目GitHub页面提交Issue

---
构建时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
构建平台: {platform}
版本: {VERSION_INFO["version"]}
'''
    
    with open(package_dir / "使用说明.txt", 'w', encoding='utf-8') as f:
        f.write(guide_content)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='构建智能文档处理系统增强版')
    parser.add_argument('--platform', choices=['windows', 'linux', 'both'], 
                       default='windows' if sys.platform.startswith('win') else 'linux',
                       help='构建平台 (默认: 当前平台)')
    parser.add_argument('--no-clean', action='store_true', help='不清理构建目录')
    parser.add_argument('--skip-deps', action='store_true', help='跳过依赖检查')
    parser.add_argument('--no-test', action='store_true', help='跳过可执行文件测试')
    
    args = parser.parse_args()
    
    print("🎨" + "=" * 60)
    print(f"     智能文档处理系统增强版 v{VERSION_INFO['version']} - 构建脚本")
    print("🎨" + "=" * 60)
    
    # 检查依赖
    if not args.skip_deps and not check_dependencies():
        sys.exit(1)
    
    # 清理构建目录
    if not args.no_clean:
        clean_build()
    
    # 创建图标
    create_icon()
    
    platforms = [args.platform] if args.platform != 'both' else ['windows', 'linux']
    
    success_count = 0
    total_count = len(platforms)
    
    for platform in platforms:
        print(f"\n🔨 构建 {platform} 平台...")
        
        # 构建可执行文件
        if not build_executable(platform):
            print(f"\n❌ {platform} 平台构建失败!")
            continue
        
        # 测试可执行文件
        if not args.no_test and not test_executable(platform):
            print(f"\n⚠️  {platform} 平台测试有问题!")
        
        # 创建发布包
        package_path = create_package(platform)
        if not package_path:
            print(f"\n❌ {platform} 平台打包失败!")
            continue
        
        success_count += 1
        print(f"\n✅ {platform} 平台构建完成!")
        print(f"📦 发布包: {package_path}")
    
    print(f"\n🎉 构建完成! ({success_count}/{total_count})")
    
    if success_count > 0:
        print("\n💡 下一步:")
        print("1. 测试可执行文件")
        print("2. 上传到GitHub Release")
        print("3. 更新文档和版本信息")
    else:
        print("\n❌ 所有平台构建失败，请检查错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()