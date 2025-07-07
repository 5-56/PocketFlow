#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能文档处理系统 - 构建脚本
用于本地构建和打包可执行文件
"""

import os
import sys
import subprocess
import shutil
import zipfile
from pathlib import Path
import argparse

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
    clean_files = ['*.pyc', '*.pyo']
    
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
        
        # 这里可以添加创建默认图标的代码
        # 或者从网络下载一个图标
        print("  💡 提示: 将自定义图标放置在 assets/icon.ico")

def build_executable(mode='onefile'):
    """构建可执行文件"""
    print(f"🔨 开始构建可执行文件 (模式: {mode})...")
    
    # 基本的PyInstaller命令
    cmd = [
        'pyinstaller',
        '--clean',
        '--noconfirm',
        'build_config_minimal.spec'  # 使用spec文件时不需要其他选项
    ]
    
    try:
        # 运行PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("  ✅ 构建成功!")
        
        if result.stdout:
            print("构建输出:")
            print(result.stdout)
            
        return True
        
    except subprocess.CalledProcessError as e:
        print("  ❌ 构建失败!")
        print(f"错误: {e}")
        if e.stderr:
            print(f"错误详情: {e.stderr}")
        return False

def create_package():
    """创建发布包"""
    print("📦 创建发布包...")
    
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("  ❌ 构建目录不存在")
        return False
    
    # 查找可执行文件（Linux和Windows兼容）
    exe_files = list(dist_dir.glob("*.exe"))  # Windows
    if not exe_files:
        # 查找Linux可执行文件
        exe_files = [f for f in dist_dir.iterdir() if f.is_file() and f.name == "DocumentProcessor"]
    
    if not exe_files:
        print("  ❌ 没有找到可执行文件")
        return False
    
    exe_file = exe_files[0]
    print(f"  📄 找到可执行文件: {exe_file}")
    
    # 创建发布目录
    release_dir = Path("release")
    release_dir.mkdir(exist_ok=True)
    
    # 复制文件到发布目录
    package_name = f"DocumentProcessor-v1.0.0-win64"
    package_dir = release_dir / package_name
    
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # 复制可执行文件
    if exe_file.suffix == '.exe':
        target_name = "DocumentProcessor.exe"
    else:
        target_name = "DocumentProcessor"
    shutil.copy2(exe_file, package_dir / target_name)
    
    # 复制说明文件
    docs_to_copy = ['README.md', 'requirements.txt']
    for doc in docs_to_copy:
        if os.path.exists(doc):
            shutil.copy2(doc, package_dir)
    
    # 创建使用说明
    usage_file = package_dir / "使用说明.txt"
    with open(usage_file, 'w', encoding='utf-8') as f:
        f.write("""智能文档自动排版系统 v1.0.0

🚀 快速开始：
1. 双击运行 DocumentProcessor.exe
2. 按照提示输入您的需求
3. 选择文档内容来源
4. 等待处理完成

📖 使用示例：
- "转换为现代商务风格的HTML文档，图片加圆角边框"
- "生成学术论文格式的PDF，使用蓝白配色"
- "制作创意设计文档，图片添加阴影效果"

⚙️ 环境要求：
- 需要设置 OPENAI_API_KEY 环境变量
- 需要网络连接（调用AI服务）

💡 获取API密钥：
1. 访问 https://platform.openai.com/
2. 注册并获取API密钥
3. 在系统环境变量中设置 OPENAI_API_KEY

🔗 更多信息：
请查看 README.md 文件或访问项目主页
""")
    
    # 创建ZIP包
    zip_path = release_dir / f"{package_name}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(package_dir)
                zipf.write(file_path, arcname)
    
    print(f"  ✅ 创建发布包: {zip_path}")
    print(f"  📊 包大小: {zip_path.stat().st_size / 1024 / 1024:.1f} MB")
    
    return zip_path

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='构建智能文档处理系统')
    parser.add_argument('--mode', choices=['onefile', 'onedir'], default='onefile',
                       help='构建模式 (默认: onefile)')
    parser.add_argument('--no-clean', action='store_true', help='不清理构建目录')
    parser.add_argument('--skip-deps', action='store_true', help='跳过依赖检查')
    
    args = parser.parse_args()
    
    print("🎨" + "=" * 60)
    print("     智能文档处理系统 - 构建脚本")
    print("🎨" + "=" * 60)
    
    # 检查依赖
    if not args.skip_deps and not check_dependencies():
        sys.exit(1)
    
    # 清理构建目录
    if not args.no_clean:
        clean_build()
    
    # 创建图标
    create_icon()
    
    # 构建可执行文件
    if not build_executable(args.mode):
        print("\n❌ 构建失败!")
        sys.exit(1)
    
    # 创建发布包
    package_path = create_package()
    if not package_path:
        print("\n❌ 打包失败!")
        sys.exit(1)
    
    print("\n🎉 构建完成!")
    print(f"📦 发布包: {package_path}")
    print("\n💡 下一步:")
    print("1. 测试可执行文件")
    print("2. 上传到GitHub Release")
    print("3. 更新文档和版本信息")

if __name__ == "__main__":
    main()