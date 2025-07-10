#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能文档自动排版系统 - 优化版启动脚本
支持Web服务模式和命令行模式
"""

import asyncio
import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ.setdefault("PYTHONPATH", str(project_root))

def setup_logging(level: str = "INFO"):
    """设置日志配置"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('document_processor.log')
        ]
    )

def start_web_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """启动Web服务器"""
    import uvicorn
    from web_api import app
    
    print(f"""
🚀 智能文档自动排版系统 - Web服务启动
    
📍 访问地址:
   - 主页: http://{host}:{port}/
   - API文档: http://{host}:{port}/api/docs
   - 系统状态: http://{host}:{port}/api/status
   
🎨 核心功能:
   - 🔄 异步高性能处理
   - 🤖 智能AI决策
   - 📱 现代Web界面
   - 🔗 实时WebSocket通信
   - 📊 系统监控和分析
    """)
    
    # 配置静态文件服务
    from fastapi.staticfiles import StaticFiles
    if Path("static").exists():
        app.mount("/static", StaticFiles(directory="static"), name="static")
        app.mount("/web", StaticFiles(directory="static", html=True), name="web")
    
    uvicorn.run(
        "web_api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
        access_log=True
    )

async def process_cli_document(
    content: str,
    instruction: str,
    output_format: str = "HTML",
    strategy: str = "auto",
    output_file: Optional[str] = None
):
    """命令行模式处理文档"""
    from async_flow import auto_create_optimal_flow, create_async_document_flow
    
    print(f"🎯 开始处理文档...")
    print(f"   指令: {instruction}")
    print(f"   格式: {output_format}")
    print(f"   策略: {strategy}")
    
    # 创建工作流
    if strategy == "auto":
        flow = await auto_create_optimal_flow(instruction, content)
        print(f"   智能选择策略: {flow.processing_strategy}")
    else:
        flow = create_async_document_flow(strategy)
    
    # 准备数据
    shared_data = {
        "user_instruction": instruction,
        "original_document": content,
        "file_type": "markdown",
        "output_format": output_format
    }
    
    # 执行处理
    try:
        await flow.run_async(shared_data)
        
        # 获取结果
        result = shared_data.get("final_document", {})
        content_result = result.get("content", "")
        
        if not content_result:
            print("❌ 处理失败：没有生成内容")
            return False
        
        # 保存结果
        if output_file:
            output_path = Path(output_file)
        else:
            # 自动生成文件名
            ext = "html" if output_format.upper() == "HTML" else "md"
            output_path = Path(f"output/processed_document.{ext}")
        
        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        output_path.write_text(content_result, encoding="utf-8")
        
        # 显示结果信息
        processing_time = shared_data.get("workflow_metadata", {}).get("total_time", 0)
        file_size = len(content_result)
        
        print(f"✅ 处理完成!")
        print(f"   输出文件: {output_path}")
        print(f"   文件大小: {file_size} 字符")
        print(f"   处理时间: {processing_time:.2f} 秒")
        
        # 显示质量报告
        quality_report = shared_data.get("quality_assurance_report", {})
        if quality_report:
            score = quality_report.get("overall_score", 0)
            grade = quality_report.get("quality_grade", "N/A")
            print(f"   质量评分: {score}/100 (等级: {grade})")
        
        return True
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        return False

async def process_cli_batch(
    file_pattern: str,
    instruction: str,
    output_dir: str = "output/batch",
    strategy: str = "quick",
    max_concurrent: int = 3
):
    """命令行批量处理"""
    import glob
    from async_flow import create_batch_async_flow
    
    # 查找匹配的文件
    files = glob.glob(file_pattern)
    if not files:
        print(f"❌ 没有找到匹配的文件: {file_pattern}")
        return False
    
    print(f"🔄 开始批量处理 {len(files)} 个文件...")
    print(f"   策略: {strategy}")
    print(f"   并发数: {max_concurrent}")
    
    # 准备文档数据
    documents = []
    for file_path in files:
        try:
            content = Path(file_path).read_text(encoding="utf-8")
            documents.append({
                "content": content,
                "file_type": "markdown" if file_path.endswith(('.md', '.markdown')) else "text",
                "source_file": file_path
            })
        except Exception as e:
            print(f"⚠️  读取文件失败 {file_path}: {e}")
    
    if not documents:
        print("❌ 没有成功读取任何文件")
        return False
    
    # 创建批量工作流
    batch_flow = create_batch_async_flow(strategy, max_concurrent)
    
    # 准备批量数据
    shared_data = {
        "user_instruction": instruction,
        "documents": documents
    }
    
    # 执行批量处理
    try:
        await batch_flow.run_async(shared_data)
        
        # 获取结果
        batch_results = shared_data.get("batch_results", {})
        successful_docs = batch_results.get("successful_documents", [])
        failed_docs = batch_results.get("failed_documents", [])
        
        # 保存成功的结果
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for doc_result in successful_docs:
            index = doc_result["index"]
            source_file = documents[index]["source_file"]
            result_content = doc_result["result"].get("content", "")
            
            if result_content:
                # 生成输出文件名
                source_name = Path(source_file).stem
                output_file = output_path / f"{source_name}_processed.html"
                output_file.write_text(result_content, encoding="utf-8")
        
        # 显示统计信息
        total_time = batch_results.get("total_processing_time", 0)
        avg_time = batch_results.get("average_processing_time", 0)
        
        print(f"✅ 批量处理完成!")
        print(f"   成功: {len(successful_docs)}/{len(documents)}")
        print(f"   失败: {len(failed_docs)}")
        print(f"   总时间: {total_time:.2f} 秒")
        print(f"   平均时间: {avg_time:.2f} 秒/文档")
        print(f"   输出目录: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 批量处理失败: {e}")
        return False

def show_system_info():
    """显示系统信息"""
    print("""
🎨 智能文档自动排版系统 - 优化版

🚀 核心功能:
   - 异步高性能处理 (3-5倍速度提升)
   - 智能AI决策和自适应策略选择
   - 现代Web界面和实时通信
   - 批量处理和并行优化
   - 多格式输出支持
   - 质量分析和监控

🔧 技术栈:
   - PocketFlow异步工作流框架
   - FastAPI + WebSocket实时通信
   - 智能LLM调用池和缓存
   - Alpine.js + Tailwind CSS现代界面

📚 使用方法:
   python start_optimized.py --web              # 启动Web服务
   python start_optimized.py --cli              # 命令行处理
   python start_optimized.py --batch            # 批量处理
   python start_optimized.py --info             # 系统信息

🌟 新增特性:
   - 支持智能策略自动选择
   - 实时处理进度和WebSocket通信
   - 系统性能监控和分析
   - 多种预设模板和快速应用
   - 协作功能和版本管理
    """)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="智能文档自动排版系统 - 优化版",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 主要模式选择
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--web", action="store_true", help="启动Web服务器")
    group.add_argument("--cli", action="store_true", help="命令行处理模式")
    group.add_argument("--batch", action="store_true", help="批量处理模式")
    group.add_argument("--info", action="store_true", help="显示系统信息")
    
    # Web服务器选项
    parser.add_argument("--host", default="0.0.0.0", help="Web服务器主机地址")
    parser.add_argument("--port", type=int, default=8000, help="Web服务器端口")
    parser.add_argument("--reload", action="store_true", help="开发模式自动重载")
    
    # 命令行处理选项
    parser.add_argument("-f", "--file", help="输入文件路径")
    parser.add_argument("-c", "--content", help="直接输入文档内容")
    parser.add_argument("-i", "--instruction", default="转换为现代HTML格式", help="处理指令")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("--format", default="HTML", choices=["HTML", "MARKDOWN", "PDF"], help="输出格式")
    parser.add_argument("--strategy", default="auto", 
                       choices=["auto", "complete", "quick", "text_only", "analysis_focus"], 
                       help="处理策略")
    
    # 批量处理选项
    parser.add_argument("--pattern", help="文件匹配模式 (如: *.md)")
    parser.add_argument("--output-dir", default="output/batch", help="批量输出目录")
    parser.add_argument("--max-concurrent", type=int, default=3, help="最大并发数")
    
    # 通用选项
    parser.add_argument("--log-level", default="INFO", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
                       help="日志级别")
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.log_level)
    
    if args.info:
        show_system_info()
        return
    
    if args.web:
        # 启动Web服务器
        start_web_server(args.host, args.port, args.reload)
        
    elif args.cli:
        # 命令行处理
        if not args.file and not args.content:
            print("❌ 错误: 请提供 --file 或 --content 参数")
            return
        
        # 获取文档内容
        if args.file:
            try:
                content = Path(args.file).read_text(encoding="utf-8")
            except Exception as e:
                print(f"❌ 读取文件失败: {e}")
                return
        else:
            content = args.content
        
        # 异步处理
        success = asyncio.run(process_cli_document(
            content=content,
            instruction=args.instruction,
            output_format=args.format,
            strategy=args.strategy,
            output_file=args.output
        ))
        
        if not success:
            sys.exit(1)
    
    elif args.batch:
        # 批量处理
        if not args.pattern:
            print("❌ 错误: 请提供 --pattern 参数指定文件匹配模式")
            return
        
        # 异步批量处理
        success = asyncio.run(process_cli_batch(
            file_pattern=args.pattern,
            instruction=args.instruction,
            output_dir=args.output_dir,
            strategy=args.strategy,
            max_concurrent=args.max_concurrent
        ))
        
        if not success:
            sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 程序已被用户中断")
    except Exception as e:
        print(f"❌ 程序运行错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)