#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能文档自动排版系统 - 增强版主程序
====================================
基于 PocketFlow 框架的智能文档处理系统

作者: AI Assistant
版本: v2.1.0
日期: 2024-12-28
"""

import os
import sys
import argparse
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# 确保本地模块路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入版本信息
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

# 导入核心模块
try:
    from flow import get_flow_by_type
    from utils.call_llm import test_api_connection
    CORE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  核心模块加载失败: {e}")
    CORE_AVAILABLE = False

# 导入增强功能模块
try:
    from utils.content_analyzer import analyze_document_comprehensive
    from utils.format_converter import FormatConverter, get_supported_formats
    from utils.template_manager import get_template_manager, recommend_templates_for_content
    from interactive_ui import InteractiveUI
    ENHANCED_FEATURES = True
except ImportError as e:
    print(f"ℹ️  增强功能模块加载失败: {e}")
    print("   将使用基础功能模式")
    ENHANCED_FEATURES = False

# 导入Web服务模块
try:
    from web_api import create_app
    import uvicorn
    WEB_AVAILABLE = True
except ImportError as e:
    print(f"ℹ️  Web服务模块加载失败: {e}")
    WEB_AVAILABLE = False

# 配置日志
def setup_logging(level=logging.INFO):
    """设置日志系统"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 创建logs目录
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # 配置日志处理器
    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            logs_dir / f"document_processor_{datetime.now().strftime('%Y%m%d')}.log",
            encoding='utf-8'
        )
    ]
    
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=handlers
    )

logger = logging.getLogger(__name__)

class EnhancedDocumentProcessor:
    """增强版文档处理器"""
    
    def __init__(self):
        self.version = VERSION_INFO["version"]
        self.format_converter = None
        self.template_manager = None
        self.supported_formats = ['HTML']  # 基础支持
        
        # 初始化增强功能
        if ENHANCED_FEATURES:
            try:
                self.format_converter = FormatConverter()
                self.template_manager = get_template_manager()
                self.supported_formats = get_supported_formats()
                logger.info("✅ 增强功能初始化成功")
            except Exception as e:
                logger.warning(f"增强功能初始化失败: {e}")
                ENHANCED_FEATURES = False
    
    def check_environment(self) -> Dict[str, Any]:
        """检查运行环境"""
        env_status = {
            "python_version": sys.version,
            "platform": sys.platform,
            "core_available": CORE_AVAILABLE,
            "enhanced_features": ENHANCED_FEATURES,
            "web_available": WEB_AVAILABLE,
            "api_key_set": bool(os.getenv('OPENAI_API_KEY')),
            "dependencies": {}
        }
        
        # 检查关键依赖
        key_deps = ['openai', 'fastapi', 'uvicorn', 'pydantic']
        for dep in key_deps:
            try:
                __import__(dep)
                env_status["dependencies"][dep] = "✅ 已安装"
            except ImportError:
                env_status["dependencies"][dep] = "❌ 未安装"
        
        return env_status
    
    def show_system_info(self):
        """显示系统信息"""
        print(f"\n🎨 智能文档自动排版系统 v{self.version}")
        print("=" * 60)
        print(f"📅 版本: {VERSION_INFO.get('version', 'Unknown')}")
        print(f"📅 发布日期: {VERSION_INFO.get('release_date', 'Unknown')}")
        print(f"🔢 构建号: {VERSION_INFO.get('build_number', 'Unknown')}")
        print(f"📝 描述: {VERSION_INFO.get('description', '')}")
        
        # 显示功能特性
        features = VERSION_INFO.get('features', [])
        if features:
            print(f"\n✨ 功能特性:")
            for feature in features:
                print(f"  • {feature}")
        
        # 显示环境状态
        env_status = self.check_environment()
        print(f"\n🔧 环境状态:")
        print(f"  Python: {sys.version.split()[0]}")
        print(f"  平台: {sys.platform}")
        print(f"  核心功能: {'✅' if env_status['core_available'] else '❌'}")
        print(f"  增强功能: {'✅' if env_status['enhanced_features'] else '❌'}")
        print(f"  Web服务: {'✅' if env_status['web_available'] else '❌'}")
        print(f"  API密钥: {'✅' if env_status['api_key_set'] else '❌'}")
        
        # 显示依赖状态
        print(f"\n📦 关键依赖:")
        for dep, status in env_status["dependencies"].items():
            print(f"  {dep}: {status}")
    
    async def test_api_connection(self) -> bool:
        """测试API连接"""
        if not os.getenv('OPENAI_API_KEY'):
            print("❌ 未设置 OPENAI_API_KEY 环境变量")
            return False
        
        try:
            if CORE_AVAILABLE:
                result = await test_api_connection()
                if result:
                    print("✅ API连接测试成功")
                    return True
                else:
                    print("❌ API连接测试失败")
                    return False
            else:
                print("⚠️  无法测试API连接（核心模块未加载）")
                return False
        except Exception as e:
            print(f"❌ API连接测试出错: {e}")
            return False
    
    def start_web_service(self, host: str = "0.0.0.0", port: int = 8000, dev_mode: bool = False):
        """启动Web服务"""
        if not WEB_AVAILABLE:
            print("❌ Web服务功能不可用，请安装相关依赖")
            return
        
        try:
            print(f"\n🌐 启动Web服务...")
            print(f"📡 地址: http://{host}:{port}")
            print(f"🔧 开发模式: {'启用' if dev_mode else '禁用'}")
            print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("\n💡 使用说明:")
            print("  • 在浏览器中访问上述地址")
            print("  • 使用现代化的Web界面处理文档")
            print("  • 支持实时进度更新和批量处理")
            print("  • 按 Ctrl+C 停止服务")
            print("\n" + "=" * 60)
            
            # 创建FastAPI应用
            app = create_app()
            
            # 启动服务
            uvicorn.run(
                app,
                host=host,
                port=port,
                reload=dev_mode,
                log_level="info" if dev_mode else "warning"
            )
            
        except Exception as e:
            logger.error(f"Web服务启动失败: {e}")
            print(f"❌ Web服务启动失败: {e}")
    
    def start_cli_mode(self):
        """启动命令行交互模式"""
        if not CORE_AVAILABLE:
            print("❌ 核心功能不可用，无法启动CLI模式")
            return
        
        print(f"\n💻 命令行交互模式")
        print("=" * 60)
        print("📝 请描述您想要的文档格式（例如：")
        print("   • '转换为现代商务风格的HTML文档，图片加圆角边框'")
        print("   • '生成学术论文格式，使用蓝白配色方案'")
        print("   • '制作创意设计文档，图片添加阴影效果'")
        print()
        
        try:
            # 获取用户指令
            user_instruction = input("💬 您的需求: ").strip()
            
            if not user_instruction:
                print("❌ 请提供具体的格式需求")
                return
            
            # 获取文档内容
            self._get_document_content_and_process(user_instruction)
            
        except KeyboardInterrupt:
            print("\n\n👋 感谢使用！")
        except Exception as e:
            logger.error(f"CLI模式出错: {e}")
            print(f"❌ 处理出错: {e}")
    
    def _get_document_content_and_process(self, user_instruction: str):
        """获取文档内容并处理"""
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
                document_content, file_type = self._load_document_from_file(file_path)
            else:
                print("❌ 文件不存在")
                return
        
        elif choice == "2":
            # 直接输入内容
            print("📝 请粘贴您的文档内容（输入'END'结束）:")
            lines = []
            while True:
                try:
                    line = input()
                    if line.strip().upper() == 'END':
                        break
                    lines.append(line)
                except EOFError:
                    break
            document_content = '\n'.join(lines)
        
        elif choice == "3":
            # 使用示例文档
            document_content = self._get_example_document()
            print("✓ 使用示例文档")
        
        else:
            print("❌ 无效选择")
            return
        
        if not document_content:
            print("❌ 没有获取到有效的文档内容")
            return
        
        # 运行处理流程
        print("\n🚀 开始处理文档...")
        self._run_document_processing(user_instruction, document_content, file_type)
    
    def _load_document_from_file(self, file_path: str) -> tuple[Optional[str], Optional[str]]:
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
    
    def _run_document_processing(self, user_instruction: str, document_content: str, file_type: str):
        """运行文档处理流程"""
        try:
            # 创建共享数据
            shared = {
                "user_instruction": user_instruction,
                "original_document": document_content,
                "file_type": file_type
            }
            
            # 选择流程类型
            if len(user_instruction.split()) > 50:
                flow_type = "complete"
            else:
                flow_type = "quick"
            
            # 获取并运行工作流
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
    
    def _get_example_document(self) -> str:
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

1. **先进算法**: 基于最新深度学习技术
2. **高度集成**: 可无缝集成到现有系统
3. **安全可靠**: 提供企业级安全保障

## 应用场景

### 商务办公
- 智能文档处理
- 自动报告生成
- 数据分析可视化

### 教育培训
- 个性化学习路径
- 智能习题推荐
- 学习进度跟踪

## 联系我们

如需了解更多信息，请联系我们的技术团队。
"""

def main():
    """主函数"""
    # 设置日志
    setup_logging()
    
    # 创建参数解析器
    parser = argparse.ArgumentParser(
        description=f'智能文档自动排版系统 v{VERSION_INFO["version"]}',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s --web                    # 启动Web服务（推荐）
  %(prog)s --cli                    # 启动命令行模式
  %(prog)s --info                   # 显示系统信息
  %(prog)s --test                   # 测试API连接
  %(prog)s --web --port 9000        # 在指定端口启动Web服务
  %(prog)s --web --dev              # 开发模式启动Web服务
        """
    )
    
    # 运行模式选项
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--web', action='store_true', 
                           help='启动Web服务模式（推荐）')
    mode_group.add_argument('--cli', action='store_true', 
                           help='启动命令行交互模式')
    mode_group.add_argument('--info', action='store_true', 
                           help='显示系统信息')
    mode_group.add_argument('--test', action='store_true', 
                           help='测试API连接')
    
    # Web服务选项
    parser.add_argument('--host', default='0.0.0.0', 
                       help='Web服务绑定的主机地址 (默认: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8000, 
                       help='Web服务端口 (默认: 8000)')
    parser.add_argument('--dev', action='store_true', 
                       help='开启开发模式（热重载等）')
    
    # 其他选项
    parser.add_argument('--version', action='version', 
                       version=f'%(prog)s {VERSION_INFO["version"]}')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='详细输出模式')
    
    args = parser.parse_args()
    
    # 设置详细模式
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 创建处理器实例
    processor = EnhancedDocumentProcessor()
    
    # 根据参数执行相应操作
    if args.info:
        processor.show_system_info()
    elif args.test:
        asyncio.run(processor.test_api_connection())
    elif args.web:
        processor.start_web_service(args.host, args.port, args.dev)
    elif args.cli:
        processor.start_cli_mode()
    else:
        # 默认显示帮助信息并提供选择
        print(f"🎨 智能文档自动排版系统 v{VERSION_INFO['version']}")
        print("=" * 60)
        print("请选择运行模式:")
        print("1. 🌐 Web服务模式（推荐）- 现代化界面，功能完整")
        print("2. 💻 命令行模式 - 快速处理，适合脚本化")
        print("3. ℹ️  系统信息 - 查看版本和环境状态")
        print("4. 🔧 API测试 - 测试OpenAI API连接")
        print()
        
        try:
            choice = input("请输入选择 (1-4): ").strip()
            
            if choice == "1":
                processor.start_web_service()
            elif choice == "2":
                processor.start_cli_mode()
            elif choice == "3":
                processor.show_system_info()
            elif choice == "4":
                asyncio.run(processor.test_api_connection())
            else:
                print("❌ 无效选择，请重新运行程序")
                
        except KeyboardInterrupt:
            print("\n\n👋 感谢使用！")

if __name__ == "__main__":
    main()