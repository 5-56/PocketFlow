#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import json
from pathlib import Path
from flow import get_flow_by_type
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('document_processor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def load_document_from_file(file_path):
    """从文件加载文档内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 根据文件扩展名确定文件类型
        extension = Path(file_path).suffix.lower()
        if extension in ['.md', '.markdown']:
            file_type = 'markdown'
        elif extension in ['.txt']:
            file_type = 'text'
        else:
            file_type = 'text'  # 默认为文本
        
        return content, file_type
    except Exception as e:
        logger.error(f"加载文件失败: {e}")
        return None, None

def interactive_mode():
    """交互式模式"""
    print("=" * 60)
    print("🎨 智能文档自动排版系统")
    print("=" * 60)
    print("让AI帮您一句话完成文档的格式化和排版！")
    print()
    
    # 获取用户指令
    print("📝 请描述您想要的文档格式（例如：")
    print("   • '请帮我生成一个现代商务风格的HTML文档，图片统一加圆角边框'")
    print("   • '转换成学术论文格式，使用蓝白配色方案'")
    print("   • '制作一个创意设计文档，图片添加阴影效果'")
    print()
    
    user_instruction = input("💬 您的需求: ").strip()
    
    if not user_instruction:
        print("❌ 请提供具体的格式需求")
        return
    
    # 获取文档内容
    print("\n📄 请提供文档内容（三种方式）:")
    print("1. 输入文件路径")
    print("2. 直接粘贴文档内容")
    print("3. 使用示例文档")
    
    choice = input("\n选择方式 (1/2/3): ").strip()
    
    document_content = None
    file_type = "markdown"
    
    if choice == "1":
        # 从文件加载
        file_path = input("📁 请输入文件路径: ").strip()
        if os.path.exists(file_path):
            document_content, file_type = load_document_from_file(file_path)
        else:
            print("❌ 文件不存在")
            return
    
    elif choice == "2":
        # 直接输入内容
        print("📝 请粘贴您的文档内容（输入'END'结束）:")
        lines = []
        while True:
            line = input()
            if line.strip().upper() == 'END':
                break
            lines.append(line)
        document_content = '\n'.join(lines)
    
    elif choice == "3":
        # 使用示例文档
        document_content = """
# 人工智能技术报告

## 概述

人工智能（AI）是计算机科学的一个分支，致力于创建能够模拟人类智能的系统。

![AI图片](ai-illustration.jpg)

## 主要技术

### 机器学习
机器学习是AI的核心技术之一，包括：

- 监督学习
- 无监督学习  
- 强化学习

### 深度学习
深度学习基于神经网络，在以下领域表现出色：

1. 图像识别
2. 自然语言处理
3. 语音识别

![神经网络](neural-network.png)

## 应用领域

AI技术已经广泛应用在多个领域，包括医疗诊断、自动驾驶、金融分析等。

## 未来展望

随着技术的不断发展，AI将在更多领域发挥重要作用。
"""
        print("✓ 使用示例文档")
    
    else:
        print("❌ 无效选择")
        return
    
    if not document_content:
        print("❌ 没有获取到有效的文档内容")
        return
    
    # 选择工作流类型
    print("\n🔧 选择处理类型:")
    print("1. 完整处理（包含图片优化）")
    print("2. 快速格式化（仅文本）")
    print("3. 仅图片处理")
    
    flow_choice = input("\n选择类型 (1/2/3, 默认1): ").strip() or "1"
    
    flow_type_map = {
        "1": "complete",
        "2": "simple", 
        "3": "image"
    }
    
    flow_type = flow_type_map.get(flow_choice, "complete")
    
    # 运行处理流程
    print("\n🚀 开始处理文档...")
    run_document_processing(user_instruction, document_content, file_type, flow_type)

def run_document_processing(user_instruction, document_content, file_type, flow_type="complete"):
    """运行文档处理流程"""
    
    # 创建共享数据
    shared = {
        "user_instruction": user_instruction,
        "original_document": document_content,
        "file_type": file_type
    }
    
    try:
        # 获取对应的工作流
        flow = get_flow_by_type(flow_type)
        
        logger.info(f"开始执行{flow_type}工作流")
        logger.info(f"用户需求: {user_instruction}")
        logger.info(f"文档长度: {len(document_content)}字符")
        
        # 运行工作流
        flow.run(shared)
        
        # 检查处理结果
        if "final_document" in shared:
            final_doc = shared["final_document"]
            print(f"\n✅ 文档处理完成！")
            print(f"📄 格式: {final_doc.get('format', 'Unknown')}")
            print(f"📏 长度: {len(final_doc.get('content', ''))}字符")
            
            # 显示处理摘要
            if "requirements" in shared:
                req = shared["requirements"]
                print(f"🎨 应用风格: {req.get('style', 'Unknown')}")
            
            if "document_structure" in shared:
                structure = shared["document_structure"]
                titles_count = len(structure.get("titles", []))
                images_count = len(structure.get("images", []))
                print(f"📊 文档结构: {titles_count}个标题, {images_count}张图片")
            
            print(f"\n💾 文档已保存到 output/ 目录")
            
        else:
            print("❌ 文档处理失败")
            logger.error("工作流执行失败，没有生成最终文档")
    
    except Exception as e:
        print(f"❌ 处理过程中发生错误: {e}")
        logger.error(f"文档处理失败: {e}", exc_info=True)

def batch_mode(input_dir, output_dir, instruction):
    """批处理模式"""
    print(f"🔄 批处理模式: {input_dir} -> {output_dir}")
    
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"❌ 输入目录不存在: {input_dir}")
        return
    
    # 查找支持的文件
    supported_extensions = ['.md', '.markdown', '.txt']
    files = []
    for ext in supported_extensions:
        files.extend(input_path.glob(f"*{ext}"))
    
    if not files:
        print("❌ 在输入目录中没有找到支持的文档文件")
        return
    
    print(f"📁 找到 {len(files)} 个文件待处理")
    
    # 确保输出目录存在
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 批量处理
    for i, file_path in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] 处理文件: {file_path.name}")
        
        content, file_type = load_document_from_file(file_path)
        if content:
            # 为每个文件创建子目录
            file_output_dir = Path(output_dir) / file_path.stem
            file_output_dir.mkdir(exist_ok=True)
            
            # 临时修改输出目录
            original_output = "output"
            os.makedirs(str(file_output_dir), exist_ok=True)
            
            try:
                # 运行处理
                run_document_processing(instruction, content, file_type, "complete")
                print(f"✅ {file_path.name} 处理完成")
            except Exception as e:
                print(f"❌ {file_path.name} 处理失败: {e}")
        else:
            print(f"❌ 无法加载文件: {file_path.name}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="🎨 智能文档自动排版系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 交互式模式
  python main.py
  
  # 快速处理单个文件
  python main.py -f document.md -i "转换为现代商务风格的HTML文档"
  
  # 批处理
  python main.py -b input_folder output_folder -i "统一格式为学术论文风格"
        """
    )
    
    parser.add_argument('-f', '--file', help='要处理的文档文件路径')
    parser.add_argument('-i', '--instruction', help='格式化指令')
    parser.add_argument('-b', '--batch', nargs=2, metavar=('INPUT_DIR', 'OUTPUT_DIR'), 
                       help='批处理模式：输入目录 输出目录')
    parser.add_argument('-t', '--type', choices=['complete', 'simple', 'image'], 
                       default='complete', help='处理类型 (默认: complete)')
    parser.add_argument('--version', action='version', version='智能文档排版系统 v1.0')
    
    args = parser.parse_args()
    
    # 检查API密钥
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  警告: 未设置 OPENAI_API_KEY 环境变量")
        print("   请设置您的OpenAI API密钥以使用LLM功能")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        print()
    
    if args.batch:
        # 批处理模式
        if not args.instruction:
            print("❌ 批处理模式需要提供指令 (-i)")
            return
        batch_mode(args.batch[0], args.batch[1], args.instruction)
    
    elif args.file:
        # 文件处理模式
        if not args.instruction:
            print("❌ 文件处理模式需要提供指令 (-i)")
            return
        
        if not os.path.exists(args.file):
            print(f"❌ 文件不存在: {args.file}")
            return
        
        content, file_type = load_document_from_file(args.file)
        if content:
            print(f"🔄 处理文件: {args.file}")
            run_document_processing(args.instruction, content, file_type, args.type)
        else:
            print(f"❌ 无法加载文件: {args.file}")
    
    else:
        # 交互式模式
        interactive_mode()

if __name__ == "__main__":
    main()