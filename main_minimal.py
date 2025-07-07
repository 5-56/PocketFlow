#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能文档自动排版与设计系统 - 主程序（最小化版本）
用于演示和构建的简化版本
"""

import os
import sys
import argparse
import json
from pathlib import Path

def show_banner():
    """显示程序横幅"""
    print("=" * 60)
    print("🎨 智能文档自动排版系统 v1.0.0")
    print("=" * 60)
    print("基于 PocketFlow 框架的智能文档处理系统")
    print("支持一句话完成文档格式化、排版和图片统一")
    print()

def check_environment():
    """检查运行环境"""
    print("🔍 检查运行环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"❌ Python版本过低: {python_version.major}.{python_version.minor}")
        print("需要Python 3.8或更高版本")
        return False
    
    # 检查API密钥
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"✅ OpenAI API密钥: 已设置 ({api_key[:8]}...)")
    else:
        print("⚠️  OpenAI API密钥未设置")
        print("请设置OPENAI_API_KEY环境变量")
    
    # 检查PocketFlow
    try:
        import pocketflow
        print(f"✅ PocketFlow框架: 已安装")
    except ImportError:
        print("❌ PocketFlow框架未安装")
        print("请运行: pip install pocketflow")
        return False
    
    return True

def get_version_info():
    """获取版本信息"""
    try:
        with open('version.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "version": "1.0.0",
            "description": "智能文档自动排版系统",
            "release_date": "2024-12-28"
        }

def show_features():
    """显示功能特色"""
    print("✨ 功能特色:")
    print("-" * 50)
    print("🗣️  自然语言交互: 用一句话描述需求，AI自动理解并执行")
    print("🎨 智能排版设计: 自动分析文档结构，生成专业的排版方案")
    print("🖼️  图片统一处理: 自动调整图片尺寸、添加效果、统一风格")
    print("📄 多格式输出: 支持HTML、PDF、Word、PowerPoint、Markdown")
    print("📊 智能内容分析: 自动分析文档质量，提供优化建议")
    print("🎯 模板智能推荐: 基于内容特征推荐最适合的排版模板")
    print("⚡ 批量处理: 支持批量处理多个文档")
    print("🔄 实时预览调整: 交互式调整和预览功能")
    print()

def show_examples():
    """显示使用示例"""
    print("📖 使用示例:")
    print("-" * 50)
    print("• '转换为现代商务风格的HTML文档，图片加圆角边框'")
    print("• '生成学术论文格式的PDF，使用蓝白配色'")
    print("• '制作创意设计文档，图片添加阴影效果'")
    print("• '将报告转换为PowerPoint演示文稿'")
    print("• '优化文档结构，提升可读性'")
    print()

def show_supported_formats():
    """显示支持的格式"""
    print("📋 支持的格式:")
    print("-" * 50)
    print("📥 输入格式:")
    print("   • Markdown (.md, .markdown)")
    print("   • 纯文本 (.txt)")
    print()
    print("📤 输出格式:")
    print("   • HTML: 响应式网页格式")
    print("   • PDF: 高质量文档格式")
    print("   • DOCX: Microsoft Word格式")
    print("   • PPTX: PowerPoint演示文稿")
    print("   • Markdown: 优化后的Markdown")
    print()

def get_user_input():
    """获取用户输入"""
    print("请选择操作:")
    print("1. 🚀 开始使用（需要完整版）")
    print("2. 📋 查看支持格式")
    print("3. 📖 查看使用示例")
    print("4. ℹ️  查看版本信息")
    print("5. 🔧 检查环境")
    print("0. 退出")
    
    choice = input("\n请输入选择 (0-5): ").strip()
    return choice

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='智能文档自动排版系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s                          # 启动交互模式
  %(prog)s --version               # 显示版本信息
  %(prog)s --check                 # 检查环境
  %(prog)s --formats               # 显示支持格式
  %(prog)s --examples              # 显示使用示例

完整功能需要安装所有依赖，请参考README.md
        """
    )
    
    parser.add_argument('--version', action='store_true', help='显示版本信息')
    parser.add_argument('--check', action='store_true', help='检查运行环境')
    parser.add_argument('--formats', action='store_true', help='显示支持的格式')
    parser.add_argument('--examples', action='store_true', help='显示使用示例')
    parser.add_argument('--features', action='store_true', help='显示功能特色')
    
    args = parser.parse_args()
    
    # 处理命令行参数
    if args.version:
        version_info = get_version_info()
        print(f"智能文档自动排版系统 v{version_info['version']}")
        print(f"发布日期: {version_info.get('release_date', 'Unknown')}")
        print(f"描述: {version_info.get('description', '')}")
        return
    
    if args.check:
        check_environment()
        return
    
    if args.formats:
        show_supported_formats()
        return
    
    if args.examples:
        show_examples()
        return
    
    if args.features:
        show_features()
        return
    
    # 交互模式
    show_banner()
    show_features()
    
    # 检查环境
    if not check_environment():
        print("\n❌ 环境检查未通过，请按照提示解决问题后重试")
        print("💡 可以使用 --check 参数单独检查环境")
        return
    
    print("\n🎉 环境检查通过！")
    
    # 主交互循环
    while True:
        print("\n" + "=" * 60)
        choice = get_user_input()
        
        if choice == '0':
            print("👋 感谢使用智能文档自动排版系统！")
            break
        elif choice == '1':
            print("\n🚀 启动完整功能需要安装额外依赖:")
            print("pip install -r requirements.txt")
            print("\n💡 然后运行:")
            print("python main.py")
            print("\n📖 详细说明请查看 README.md")
        elif choice == '2':
            print()
            show_supported_formats()
        elif choice == '3':
            print()
            show_examples()
        elif choice == '4':
            version_info = get_version_info()
            print(f"\n📦 版本: {version_info['version']}")
            print(f"📅 发布日期: {version_info.get('release_date', 'Unknown')}")
            print(f"📝 描述: {version_info.get('description', '')}")
        elif choice == '5':
            print()
            check_environment()
        else:
            print("❌ 无效选择，请重新输入")

if __name__ == "__main__":
    main()