#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能文档自动排版与设计系统 - 主程序
整合了内容分析、模板管理、多格式输出等功能
"""

import os
import sys
import argparse
import json
from pathlib import Path
from flow import get_flow_by_type
import logging
from typing import Dict, Any, Optional

# 导入新功能模块
try:
    from utils.content_analyzer import analyze_document_comprehensive
    from utils.format_converter import FormatConverter, get_supported_formats
    from utils.template_manager import get_template_manager, recommend_templates_for_content
    from interactive_ui import InteractiveUI
    NEW_FEATURES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  新功能模块加载失败: {e}")
    print("   将使用基础功能模式")
    NEW_FEATURES_AVAILABLE = False

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

class DocumentProcessorApp:
    """文档处理应用主类"""
    
    def __init__(self):
        if NEW_FEATURES_AVAILABLE:
            self.format_converter = FormatConverter()
            self.template_manager = get_template_manager()
            self.supported_formats = get_supported_formats()
        else:
            self.format_converter = None
            self.template_manager = None
            self.supported_formats = ['HTML']
        
    def load_document_from_file(self, file_path: str) -> tuple[Optional[str], Optional[str]]:
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
                file_type = 'text'  # 默认作为文本处理
            
            return content, file_type
        except Exception as e:
            logger.error(f"加载文档失败: {e}")
            return None, None

    def analyze_document(self, content: str) -> Dict[str, Any]:
        """分析文档内容"""
        if not NEW_FEATURES_AVAILABLE:
            return {}
            
        try:
            logger.info("开始分析文档内容...")
            analysis_result = analyze_document_comprehensive(content)
            
            print("\n📊 文档分析结果:")
            print("-" * 50)
            
            # 显示整体评分
            overall_score = analysis_result.get("overall_score", {})
            print(f"📈 整体评分: {overall_score.get('overall_score', 0)}/100 ({overall_score.get('grade', 'N/A')})")
            
            # 显示各项得分
            component_scores = overall_score.get("component_scores", {})
            print(f"   可读性: {component_scores.get('readability', 0)}/100")
            print(f"   结构性: {component_scores.get('structure', 0)}/100") 
            print(f"   内容质量: {component_scores.get('quality', 0)}/100")
            
            # 显示主要问题
            suggestions = analysis_result.get("suggestions", [])
            if suggestions:
                print(f"\n💡 优化建议 ({len(suggestions)}条):")
                for i, suggestion in enumerate(suggestions[:3], 1):
                    print(f"   {i}. {suggestion.get('title', '')}")
                    print(f"      {suggestion.get('description', '')}")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"文档分析失败: {e}")
            return {}

    def recommend_templates(self, content: str, instruction: str = "") -> list:
        """推荐适合的模板"""
        if not NEW_FEATURES_AVAILABLE:
            return []
            
        try:
            logger.info("正在推荐适合的模板...")
            recommendations = recommend_templates_for_content(content, instruction)
            
            if recommendations:
                print("\n🎯 模板推荐:")
                print("-" * 50)
                for i, rec in enumerate(recommendations[:3], 1):
                    template = rec["template"]
                    score = rec["score"]
                    reasons = rec["reasons"]
                    
                    print(f"{i}. 【{template.name}】(匹配度: {score:.1%})")
                    print(f"   📝 {template.description}")
                    print(f"   💡 推荐理由: {', '.join(reasons)}")
                    print()
                    
                return recommendations
            else:
                print("未找到合适的模板推荐")
                return []
                
        except Exception as e:
            logger.error(f"模板推荐失败: {e}")
            return []

    def process_single_document(self, input_file: str, instruction: str, 
                              output_format: str = 'HTML', 
                              enable_analysis: bool = True,
                              enable_template_recommendation: bool = True) -> bool:
        """处理单个文档"""
        logger.info(f"开始处理文档: {input_file}")
        
        # 加载文档
        content, file_type = self.load_document_from_file(input_file)
        if content is None:
            return False
        
        print(f"📄 加载文档: {Path(input_file).name}")
        print(f"📏 文档长度: {len(content)}字符")
        
        # 文档分析
        analysis_result = {}
        if enable_analysis and NEW_FEATURES_AVAILABLE:
            analysis_result = self.analyze_document(content)
        
        # 模板推荐
        template_recommendations = []
        if enable_template_recommendation and NEW_FEATURES_AVAILABLE:
            template_recommendations = self.recommend_templates(content, instruction)
            
            # 询问是否使用推荐模板
            if template_recommendations:
                use_template = input("\n是否使用推荐的模板？(输入编号 1-3，或回车跳过): ").strip()
                if use_template.isdigit():
                    idx = int(use_template) - 1
                    if 0 <= idx < len(template_recommendations):
                        template = template_recommendations[idx]["template"]
                        template_instruction = template.generate_instruction()
                        instruction = f"{instruction}，{template_instruction}"
                        print(f"✅ 已应用模板: {template.name}")
                        
                        # 增加模板使用计数
                        self.template_manager.use_template(template.name)
        
        # 创建共享数据
        shared_data = {
            "user_instruction": instruction,
            "original_document": content,
            "file_type": file_type,
            "output_format": output_format,
            "analysis_result": analysis_result,
            "template_recommendations": template_recommendations
        }
        
        try:
            # 选择处理流程
            if len(instruction.split()) > 50:  # 复杂指令使用完整流程
                flow = get_flow_by_type("complete")
            else:  # 简单指令使用快速流程
                flow = get_flow_by_type("quick")
            
            print(f"\n🚀 开始处理文档...")
            print(f"📝 指令: {instruction}")
            print(f"📄 输出格式: {output_format}")
            
            # 运行流程
            flow.run(shared_data)
            
            if "final_document" in shared_data:
                print("✅ 文档处理完成!")
                
                # 使用格式转换器保存文档
                final_doc = shared_data["final_document"]
                if "content" in final_doc and NEW_FEATURES_AVAILABLE and self.format_converter:
                    result = self.format_converter.convert_to_format(
                        final_doc["content"], 
                        output_format,
                        final_doc.get("styles", {}),
                        final_doc.get("metadata", {})
                    )
                    
                    if result.get("success"):
                        print(f"💾 文件已保存: {result['file_path']}")
                        print(f"📊 文件大小: {result.get('size', 0)} 字节")
                    else:
                        print(f"❌ 保存失败: {result.get('error', '未知错误')}")
                else:
                    print(f"💾 文档已保存到 output/ 目录")
                
                return True
            else:
                print("❌ 文档处理失败")
                return False
                
        except Exception as e:
            logger.error(f"处理过程中发生错误: {e}")
            print(f"❌ 处理错误: {e}")
            return False

    def process_batch_documents(self, input_dir: str, output_dir: str, instruction: str) -> bool:
        """批量处理文档"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        if not input_path.exists():
            logger.error(f"输入目录不存在: {input_dir}")
            return False
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 查找所有支持的文档文件
        supported_extensions = ['.md', '.txt', '.markdown']
        files = []
        for ext in supported_extensions:
            files.extend(input_path.glob(f"*{ext}"))
        
        if not files:
            logger.warning("未找到支持的文档文件")
            return False
        
        print(f"📁 找到 {len(files)} 个文档文件")
        
        success_count = 0
        for i, file_path in enumerate(files, 1):
            try:
                print(f"\n📄 处理文件 {i}/{len(files)}: {file_path.name}")
                if self.process_single_document(
                    str(file_path), 
                    instruction, 
                    enable_analysis=False,  # 批量处理时关闭分析以提高速度
                    enable_template_recommendation=False
                ):
                    success_count += 1
                    print(f"✅ 成功")
                else:
                    print(f"❌ 失败")
            except Exception as e:
                logger.error(f"处理文件 {file_path} 时发生错误: {e}")
                print(f"❌ 错误: {e}")
        
        print(f"\n📊 批量处理完成: {success_count}/{len(files)} 个文件成功")
        return success_count > 0

    def show_format_info(self):
        """显示支持的格式信息"""
        if not NEW_FEATURES_AVAILABLE or not self.format_converter:
            print("\n📋 支持的输出格式:")
            print("-" * 50)
            print("✅ HTML: 基础HTML输出")
            print("❌ 其他格式需要安装额外依赖")
            return
            
        formats_info = self.format_converter.get_available_formats()
        
        print("\n📋 支持的输出格式:")
        print("-" * 50)
        for fmt, info in formats_info.items():
            status = "✅" if info["available"] else "❌"
            print(f"{status} {fmt}: {info['description']}")
            if info.get("requirements"):
                print(f"   💡 需要安装: {info['requirements']}")
        print()

    def show_template_info(self):
        """显示模板信息"""
        if not NEW_FEATURES_AVAILABLE or not self.template_manager:
            print("\n📚 模板功能需要安装额外依赖")
            return
            
        templates = self.template_manager.list_templates()
        categories = self.template_manager.get_categories()
        
        print(f"\n📚 可用模板 ({len(templates)}个):")
        print("-" * 50)
        
        for category in categories:
            category_templates = [t for t in templates if t.category == category]
            if category_templates:
                print(f"\n🏷️  {category} ({len(category_templates)}个):")
                for template in category_templates:
                    usage_indicator = "🔥" if template.usage_count > 10 else "📝"
                    rating_indicator = "⭐" if template.rating > 4.0 else ""
                    print(f"   {usage_indicator} {template.name} {rating_indicator}")
                    print(f"      {template.description}")
        print()

    def interactive_mode(self):
        """简化的交互模式"""
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
                document_content, file_type = self.load_document_from_file(file_path)
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
            document_content = get_example_document()
            print("✓ 使用示例文档")
        
        else:
            print("❌ 无效选择")
            return
        
        if not document_content:
            print("❌ 没有获取到有效的文档内容")
            return
        
        # 运行处理流程
        print("\n🚀 开始处理文档...")
        self.run_document_processing(user_instruction, document_content, file_type)

    def run_document_processing(self, user_instruction, document_content, file_type, flow_type="complete"):
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

    def show_help(self):
        """显示帮助信息"""
        print("\n📖 智能文档自动排版系统 - 帮助")
        print("=" * 60)
        print("🎯 指令示例:")
        print("  • '现代商务风格的HTML文档，图片加圆角边框'")
        print("  • '学术论文格式，使用蓝白配色方案'")
        print("  • '创意设计风格，图片添加阴影效果'")
        print("  • '技术文档格式，代码块高亮显示'")
        print()
        print("📁 支持的文件格式:")
        print("  • 输入: .md, .txt, .markdown")
        print("  • 输出: HTML, PDF, Word, PowerPoint, Markdown")
        print()
        print("🔧 命令行选项:")
        print("  • -f, --file        输入文件路径")
        print("  • -i, --instruction 格式化指令")
        print("  • -o, --output      输出格式 (HTML/PDF/DOCX/PPTX/MARKDOWN)")
        print("  • -b, --batch       批量处理 (输入目录 输出目录)")
        print("  • --analysis        启用文档分析")
        print("  • --templates       启用模板推荐")
        print("  • --formats         显示支持的格式")
        print("  • --template-info   显示模板信息")
        print()
        print("💡 使用技巧:")
        print("  • 交互模式提供最佳体验")
        print("  • 使用文档分析功能获取优化建议")
        print("  • 模板推荐可大幅提升效果")
        print("  • 支持多种专业格式输出")

def get_example_document():
    """获取示例文档"""
    return """
# 智能科技产品介绍

## 产品概述

我们的智能产品采用了最新的人工智能技术，为用户提供前所未有的智能体验。

![产品主图](product-main.jpg)

## 核心特性

### 🤖 智能交互
- 自然语言理解和处理
- 多轮对话支持
- 个性化学习能力

### ⚡ 高效处理
- 实时响应，毫秒级延迟
- 支持大规模批量处理
- 云端同步，随时随地访问

![功能展示](features.png)

## 技术优势

1. **先进算法**: 基于最新深度学习技术的核心算法
2. **高度集成**: 可无缝集成到现有系统中
3. **安全可靠**: 提供企业级安全保障

## 应用场景

适用于多个行业和领域：
- 🏥 医疗健康：智能诊断辅助
- 🏭 制造业：生产流程优化
- 📚 教育培训：个性化学习推荐
- 💼 企业管理：自动化办公

## 联系我们

了解更多详情，请访问我们的官网或联系销售团队。

📧 Email: contact@example.com  
📞 电话: 400-888-8888  
🌐 官网: www.example.com
"""

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='智能文档自动排版与设计系统',
        epilog='使用交互模式获得最佳体验: python main.py'
    )
    parser.add_argument('-f', '--file', help='输入文件路径')
    parser.add_argument('-i', '--instruction', help='格式化指令')
    parser.add_argument('-o', '--output', default='HTML', 
                       choices=['HTML', 'PDF', 'DOCX', 'PPTX', 'MARKDOWN'],
                       help='输出格式')
    parser.add_argument('-b', '--batch', nargs=2, metavar=('INPUT_DIR', 'OUTPUT_DIR'),
                       help='批量处理模式')
    parser.add_argument('--analysis', action='store_true', help='启用文档分析')
    parser.add_argument('--templates', action='store_true', help='启用模板推荐')
    parser.add_argument('--formats', action='store_true', help='显示支持的格式')
    parser.add_argument('--template-info', action='store_true', help='显示模板信息')
    parser.add_argument('--enhanced', action='store_true', help='使用增强交互模式')
    
    args = parser.parse_args()
    
    # 检查环境
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  警告: 未设置 OPENAI_API_KEY 环境变量")
        print("   某些AI功能可能无法正常工作")
        print("   设置方法: export OPENAI_API_KEY='your-api-key-here'")
        print()
    
    # 创建应用实例
    app = DocumentProcessorApp()
    
    try:
        # 显示格式信息
        if args.formats:
            app.show_format_info()
            return
        
        # 显示模板信息
        if args.template_info:
            app.show_template_info()
            return
        
        # 使用增强交互模式
        if args.enhanced and NEW_FEATURES_AVAILABLE:
            ui = InteractiveUI()
            ui.run()
            return
        
        # 批量处理模式
        if args.batch:
            input_dir, output_dir = args.batch
            if not args.instruction:
                print("❌ 批量处理模式需要提供格式化指令 (-i)")
                print("   示例: python main.py -b input/ output/ -i '现代商务风格'")
                return
            
            success = app.process_batch_documents(input_dir, output_dir, args.instruction)
            if success:
                print("✅ 批量处理完成")
            else:
                print("❌ 批量处理失败")
                
        # 单文件处理模式
        elif args.file and args.instruction:
            success = app.process_single_document(
                args.file, 
                args.instruction, 
                args.output,
                enable_analysis=args.analysis,
                enable_template_recommendation=args.templates
            )
            if success:
                print("✅ 文档处理完成")
            else:
                print("❌ 文档处理失败")
                
        # 默认交互模式
        else:
            if NEW_FEATURES_AVAILABLE:
                print("🎨 启动增强交互模式...")
                ui = InteractiveUI()
                ui.run()
            else:
                print("🎨 启动基础交互模式...")
                app.interactive_mode()
            
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，退出系统")
    except Exception as e:
        logger.error(f"程序执行过程中发生错误: {e}")
        print(f"❌ 系统错误: {e}")
        print("💡 尝试使用 --help 参数查看使用说明")

if __name__ == "__main__":
    main()