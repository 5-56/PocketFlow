#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能文档处理系统 - 自动发布脚本
用于自动构建、打包并上传到GitHub Release
"""

import os
import sys
import subprocess
import json
import argparse
from datetime import datetime
from pathlib import Path

def get_current_version():
    """获取当前版本号"""
    version_file = Path("version.json")
    if version_file.exists():
        with open(version_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('version', '1.0.0')
    return '1.0.0'

def bump_version(current_version, bump_type='patch'):
    """版本号升级"""
    parts = current_version.split('.')
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    
    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'patch':
        patch += 1
    
    return f"{major}.{minor}.{patch}"

def update_version_file(version):
    """更新版本文件"""
    version_data = {
        "version": version,
        "release_date": datetime.now().isoformat(),
        "build_number": int(datetime.now().timestamp())
    }
    
    with open("version.json", 'w', encoding='utf-8') as f:
        json.dump(version_data, f, indent=2, ensure_ascii=False)
    
    print(f"📝 更新版本文件: {version}")

def run_command(cmd, capture_output=False):
    """运行命令"""
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, shell=True)
            return result.returncode == 0, "", ""
    except Exception as e:
        print(f"❌ 命令执行失败: {e}")
        return False, "", str(e)

def check_git_status():
    """检查Git状态"""
    success, output, _ = run_command("git status --porcelain", capture_output=True)
    if not success:
        print("❌ 无法检查Git状态")
        return False
    
    if output.strip():
        print("⚠️  工作目录有未提交的更改:")
        print(output)
        response = input("是否继续? (y/N): ")
        return response.lower() == 'y'
    
    return True

def create_git_tag(version):
    """创建Git标签"""
    tag_name = f"v{version}"
    
    # 检查标签是否已存在
    success, _, _ = run_command(f"git tag -l {tag_name}", capture_output=True)
    if success:
        print(f"⚠️  标签 {tag_name} 已存在")
        response = input("是否删除并重新创建? (y/N): ")
        if response.lower() == 'y':
            run_command(f"git tag -d {tag_name}")
            run_command(f"git push origin --delete {tag_name}")
        else:
            return False
    
    # 创建标签
    success, _, _ = run_command(f"git tag -a {tag_name} -m 'Release {tag_name}'")
    if not success:
        print(f"❌ 创建标签失败: {tag_name}")
        return False
    
    print(f"✅ 创建标签: {tag_name}")
    return True

def push_to_github(version):
    """推送到GitHub"""
    tag_name = f"v{version}"
    
    # 推送代码
    print("📤 推送代码到GitHub...")
    success, _, _ = run_command("git push origin main")
    if not success:
        print("❌ 推送代码失败")
        return False
    
    # 推送标签
    print("📤 推送标签到GitHub...")
    success, _, _ = run_command(f"git push origin {tag_name}")
    if not success:
        print("❌ 推送标签失败")
        return False
    
    print("✅ 推送完成")
    return True

def main():
    parser = argparse.ArgumentParser(description='自动发布智能文档处理系统')
    parser.add_argument('--bump', choices=['major', 'minor', 'patch'], 
                       default='patch', help='版本升级类型')
    parser.add_argument('--version', help='手动指定版本号')
    parser.add_argument('--build-only', action='store_true', help='仅构建，不发布')
    parser.add_argument('--skip-git-check', action='store_true', help='跳过Git状态检查')
    
    args = parser.parse_args()
    
    print("🚀" + "=" * 50)
    print("  智能文档处理系统 - 自动发布")
    print("🚀" + "=" * 50)
    
    # 检查Git状态
    if not args.skip_git_check and not check_git_status():
        print("❌ Git状态检查失败")
        sys.exit(1)
    
    # 确定版本号
    if args.version:
        new_version = args.version
    else:
        current_version = get_current_version()
        new_version = bump_version(current_version, args.bump)
    
    print(f"📋 发布版本: {new_version}")
    
    # 更新版本文件
    update_version_file(new_version)
    
    # 本地构建
    print("🔨 开始本地构建...")
    success, _, _ = run_command("python build.py")
    if not success:
        print("❌ 本地构建失败")
        sys.exit(1)
    
    if args.build_only:
        print("✅ 仅构建模式完成")
        return
    
    # 提交版本更新
    print("📝 提交版本更新...")
    run_command("git add version.json")
    run_command(f"git commit -m 'Release v{new_version}'")
    
    # 创建Git标签
    if not create_git_tag(new_version):
        print("❌ 创建Git标签失败")
        sys.exit(1)
    
    # 推送到GitHub
    if not push_to_github(new_version):
        print("❌ 推送到GitHub失败")
        sys.exit(1)
    
    # 提示用户
    print("\n🎉 发布流程启动成功!")
    print(f"📦 版本: v{new_version}")
    print("\n⏳ GitHub Actions正在构建中...")
    print("🔗 查看构建状态:")
    
    # 获取仓库信息
    success, output, _ = run_command("git remote get-url origin", capture_output=True)
    if success:
        repo_url = output.strip()
        if repo_url.endswith('.git'):
            repo_url = repo_url[:-4]
        print(f"   {repo_url}/actions")
        print(f"\n🚀 Release页面:")
        print(f"   {repo_url}/releases")
    
    print("\n💡 下一步:")
    print("1. 等待GitHub Actions构建完成")
    print("2. 检查Release页面中的下载文件")
    print("3. 测试下载的可执行文件")
    print("4. 更新项目文档和使用说明")

if __name__ == "__main__":
    main()