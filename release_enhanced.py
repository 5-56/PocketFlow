#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能文档处理系统 - 增强版发布脚本
自动化版本管理、构建和GitHub发布流程
"""

import os
import sys
import subprocess
import json
import argparse
from pathlib import Path
from datetime import datetime
import re

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

def save_version_info(version_info):
    """保存版本信息"""
    with open('version.json', 'w', encoding='utf-8') as f:
        json.dump(version_info, f, indent=2, ensure_ascii=False)

def increment_version(current_version, bump_type='patch'):
    """增加版本号"""
    # 解析版本号 (semantic versioning)
    match = re.match(r'(\d+)\.(\d+)\.(\d+)', current_version)
    if not match:
        raise ValueError(f"无效的版本格式: {current_version}")
    
    major, minor, patch = map(int, match.groups())
    
    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'patch':
        patch += 1
    else:
        raise ValueError(f"无效的版本增量类型: {bump_type}")
    
    return f"{major}.{minor}.{patch}"

def check_git_status():
    """检查Git状态"""
    print("🔍 检查Git状态...")
    
    try:
        # 检查是否有未提交的更改
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        if result.stdout.strip():
            print("⚠️  存在未提交的更改:")
            print(result.stdout)
            return False
        
        # 检查是否有远程仓库
        result = subprocess.run(['git', 'remote', '-v'], 
                              capture_output=True, text=True, check=True)
        if not result.stdout.strip():
            print("❌ 没有配置远程仓库")
            return False
        
        print("✅ Git状态检查通过")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git状态检查失败: {e}")
        return False

def update_changelog(version, changes):
    """更新CHANGELOG"""
    print("📝 更新更新日志...")
    
    changelog_path = Path("CHANGELOG.md")
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # 创建新的更新日志条目
    new_entry = f"""
## [{version}] - {current_date}

### 新增功能
{chr(10).join([f"- {change}" for change in changes.get("added", [])])}

### 改进优化
{chr(10).join([f"- {change}" for change in changes.get("improved", [])])}

### 问题修复
{chr(10).join([f"- {change}" for change in changes.get("fixed", [])])}

"""
    
    if changelog_path.exists():
        # 读取现有内容
        with open(changelog_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 在第一个 ## 之前插入新条目
        if "## [" in content:
            insert_pos = content.find("## [")
            new_content = content[:insert_pos] + new_entry + content[insert_pos:]
        else:
            new_content = new_entry + content
    else:
        # 创建新的更新日志文件
        header = """# 更新日志

本项目的所有重要更改都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

"""
        new_content = header + new_entry
    
    with open(changelog_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ 更新日志已更新: {changelog_path}")

def create_release_notes(version, changes):
    """创建发布说明"""
    print("📋 创建发布说明...")
    
    version_info = load_version_info()
    
    notes = f"""# 🎉 智能文档处理系统 v{version} - 增强版

## 🚀 重大更新

### 📈 版本亮点
{chr(10).join([f"- **{feature}**" for feature in version_info.get("features", [])[:5]])}

## 📦 下载说明

### Windows 用户
- **DocumentProcessor-Enhanced-v{version}-win64.zip**: Windows 64位增强版
- 解压后运行 `启动.bat` 选择运行模式
- 或直接运行 `DocumentProcessor-Enhanced.exe --web`

### Linux 用户  
- **DocumentProcessor-Enhanced-v{version}-linux-x64.tar.gz**: Linux 64位增强版
- 解压后运行 `./start.sh` 选择运行模式
- 或直接运行 `./DocumentProcessor-Enhanced --web`

## ⚙️ 使用要求
1. **API密钥**: 需要设置 `OPENAI_API_KEY` 环境变量
2. **网络连接**: 需要连接互联网调用AI服务
3. **操作系统**: Windows 10+ 或 Linux (Ubuntu 18.04+)

## 🚀 快速开始

### Web服务模式 (推荐)
```bash
# 设置API密钥
export OPENAI_API_KEY=your_api_key_here

# 启动Web服务
./DocumentProcessor-Enhanced --web

# 访问 http://localhost:8000
```

### 命令行模式
```bash
# 单文档处理
./DocumentProcessor-Enhanced --cli

# 查看系统信息
./DocumentProcessor-Enhanced --info

# 测试API连接
./DocumentProcessor-Enhanced --test
```

## 📋 更新内容

"""
    
    # 添加具体更新内容
    if changes.get("added"):
        notes += "### ✨ 新增功能\n"
        for change in changes["added"]:
            notes += f"- {change}\n"
        notes += "\n"
    
    if changes.get("improved"):
        notes += "### 🔧 改进优化\n"
        for change in changes["improved"]:
            notes += f"- {change}\n"
        notes += "\n"
    
    if changes.get("fixed"):
        notes += "### 🐛 问题修复\n"
        for change in changes["fixed"]:
            notes += f"- {change}\n"
        notes += "\n"
    
    notes += f"""
## 💡 使用技巧
1. **明确描述需求**: 越具体的描述，AI理解得越准确
2. **利用Web界面**: Web模式提供最佳用户体验
3. **批量处理优化**: 处理多个相似文档时使用批量模式
4. **模板功能**: 善用内置模板快速格式化
5. **实时预览**: 在Web界面中实时查看处理效果

## 🔗 相关链接
- [项目主页](https://github.com/5-56/PocketFlow)
- [使用文档](https://github.com/5-56/PocketFlow/blob/main/README.md)
- [问题反馈](https://github.com/5-56/PocketFlow/issues)

---
**构建时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**版本**: {version}  
**构建号**: {version_info.get('build_number', 1)}
"""
    
    return notes

def build_release():
    """构建发布包"""
    print("🔨 开始构建发布包...")
    
    try:
        # 运行增强版构建脚本
        result = subprocess.run([
            sys.executable, 'build_enhanced.py', 
            '--platform', 'both'
        ], check=True, capture_output=True, text=True)
        
        print("✅ 构建完成")
        print("构建输出:")
        for line in result.stdout.split('\n')[-20:]:  # 显示最后20行
            if line.strip():
                print(f"  {line}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        if e.stderr:
            print(f"错误详情: {e.stderr}")
        return False

def commit_and_tag(version, changes):
    """提交更改并创建标签"""
    print("📝 提交更改并创建标签...")
    
    try:
        # 添加所有更改
        subprocess.run(['git', 'add', '.'], check=True)
        
        # 创建提交信息
        commit_msg = f"Release v{version}\n\n"
        
        if changes.get("added"):
            commit_msg += "新增功能:\n"
            for change in changes["added"]:
                commit_msg += f"- {change}\n"
            commit_msg += "\n"
        
        if changes.get("improved"):
            commit_msg += "改进优化:\n"
            for change in changes["improved"]:
                commit_msg += f"- {change}\n"
            commit_msg += "\n"
        
        if changes.get("fixed"):
            commit_msg += "问题修复:\n"
            for change in changes["fixed"]:
                commit_msg += f"- {change}\n"
        
        # 提交更改
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        
        # 创建标签
        tag_msg = f"Release v{version}"
        subprocess.run(['git', 'tag', '-a', f'v{version}', '-m', tag_msg], check=True)
        
        print(f"✅ 创建提交和标签: v{version}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git操作失败: {e}")
        return False

def push_to_github():
    """推送到GitHub"""
    print("🚀 推送到GitHub...")
    
    try:
        # 推送主分支
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        print("✅ 主分支推送成功")
        
        # 推送标签
        subprocess.run(['git', 'push', 'origin', '--tags'], check=True)
        print("✅ 标签推送成功")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 推送失败: {e}")
        return False

def create_github_release(version, release_notes, draft=False):
    """创建GitHub Release"""
    print("📦 创建GitHub Release...")
    
    try:
        # 检查是否安装了GitHub CLI
        result = subprocess.run(['gh', '--version'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("⚠️  未安装GitHub CLI，请手动创建Release")
            print("   或运行: pip install gh-cli")
            return True
    except FileNotFoundError:
        print("⚠️  未找到GitHub CLI，请手动创建Release")
        return True
    
    # 查找发布包
    release_dir = Path("release")
    if not release_dir.exists():
        print("❌ 发布目录不存在")
        return False
    
    # 查找压缩包
    archives = []
    for pattern in [f"*v{version}*.zip", f"*v{version}*.tar.gz"]:
        archives.extend(release_dir.glob(pattern))
    
    if not archives:
        print("❌ 没有找到发布包")
        return False
    
    try:
        # 创建release命令
        cmd = [
            'gh', 'release', 'create', f'v{version}',
            '--title', f'智能文档处理系统 v{version} - 增强版',
            '--notes', release_notes
        ]
        
        if draft:
            cmd.append('--draft')
        
        # 添加文件
        for archive in archives:
            cmd.append(str(archive))
        
        subprocess.run(cmd, check=True)
        print(f"✅ GitHub Release创建成功: v{version}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 创建GitHub Release失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='智能文档处理系统增强版发布脚本')
    parser.add_argument('--version', help='指定发布版本 (例如: 2.1.0)')
    parser.add_argument('--bump', choices=['major', 'minor', 'patch'], 
                       default='patch', help='版本增量类型 (默认: patch)')
    parser.add_argument('--build-only', action='store_true', 
                       help='仅构建，不发布')
    parser.add_argument('--draft', action='store_true', 
                       help='创建草稿Release')
    parser.add_argument('--skip-build', action='store_true', 
                       help='跳过构建步骤')
    parser.add_argument('--skip-git', action='store_true', 
                       help='跳过Git操作')
    
    args = parser.parse_args()
    
    print("🎨" + "=" * 60)
    print("     智能文档处理系统增强版 - 发布脚本")
    print("🎨" + "=" * 60)
    
    # 加载当前版本信息
    version_info = load_version_info()
    current_version = version_info["version"]
    
    # 确定新版本号
    if args.version:
        new_version = args.version
    else:
        new_version = increment_version(current_version, args.bump)
    
    print(f"📅 当前版本: {current_version}")
    print(f"📅 新版本: {new_version}")
    
    # 检查Git状态
    if not args.skip_git and not check_git_status():
        print("❌ Git状态检查失败，请解决后重试")
        sys.exit(1)
    
    # 收集更新内容
    print("\n📝 请输入更新内容 (每行一项，空行结束):")
    
    changes = {"added": [], "improved": [], "fixed": []}
    
    print("\n✨ 新增功能:")
    while True:
        change = input("  - ").strip()
        if not change:
            break
        changes["added"].append(change)
    
    print("\n🔧 改进优化:")
    while True:
        change = input("  - ").strip()
        if not change:
            break
        changes["improved"].append(change)
    
    print("\n🐛 问题修复:")
    while True:
        change = input("  - ").strip()
        if not change:
            break
        changes["fixed"].append(change)
    
    # 更新版本信息
    version_info["version"] = new_version
    version_info["release_date"] = datetime.now().strftime("%Y-%m-%d")
    version_info["build_number"] = version_info.get("build_number", 0) + 1
    
    # 添加更新日志到版本信息
    if "changelog" not in version_info:
        version_info["changelog"] = {}
    
    version_changelog = []
    if changes["added"]:
        version_changelog.extend(changes["added"])
    if changes["improved"]:
        version_changelog.extend([f"优化: {item}" for item in changes["improved"]])
    if changes["fixed"]:
        version_changelog.extend([f"修复: {item}" for item in changes["fixed"]])
    
    version_info["changelog"][new_version] = version_changelog
    
    # 保存版本信息
    save_version_info(version_info)
    print(f"✅ 版本信息已更新: v{new_version}")
    
    # 更新更新日志
    update_changelog(new_version, changes)
    
    # 构建发布包
    if not args.skip_build:
        if not build_release():
            print("❌ 构建失败")
            sys.exit(1)
    
    if args.build_only:
        print("\n🎉 构建完成!")
        print("💡 发布包位于 release/ 目录")
        return
    
    # 创建发布说明
    release_notes = create_release_notes(new_version, changes)
    
    # Git操作
    if not args.skip_git:
        if not commit_and_tag(new_version, changes):
            print("❌ Git操作失败")
            sys.exit(1)
        
        if not push_to_github():
            print("❌ 推送到GitHub失败")
            sys.exit(1)
    
    # 创建GitHub Release
    if not create_github_release(new_version, release_notes, args.draft):
        print("⚠️  GitHub Release创建失败，但其他步骤已完成")
    
    print(f"\n🎉 发布完成!")
    print(f"📦 版本: v{new_version}")
    print(f"🔗 GitHub: https://github.com/5-56/PocketFlow/releases/tag/v{new_version}")

if __name__ == "__main__":
    main()