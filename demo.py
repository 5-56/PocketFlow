#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能文档自动排版系统 - 功能演示
演示系统的各种功能和使用方法
"""

import os
import sys
from pathlib import Path

# 确保可以导入项目模块
sys.path.insert(0, str(Path(__file__).parent))

def demo_basic_processing():
    """演示基础文档处理功能"""
    print("🎯 演示1: 基础文档处理")
    print("-" * 50)
    
    # 示例文档内容
    sample_content = """
# 人工智能技术报告

## 概述

人工智能（AI）正在快速发展，为各行各业带来革命性变化。

![AI图片](ai-demo.jpg)

## 核心技术

### 机器学习
机器学习是AI的基础技术，包括：
- 监督学习
- 无监督学习
- 强化学习

### 深度学习
深度学习在以下领域表现突出：
1. 计算机视觉
2. 自然语言处理
3. 语音识别

## 应用前景

AI技术将在医疗、教育、交通等领域发挥重要作用。
"""
    
    print("📄 示例文档内容已准备")
    print("📝 处理指令: '转换为现代商务风格的HTML文档，图片加圆角边框'")
    
    try:
        from main import DocumentProcessorApp
        
        app = DocumentProcessorApp()
        
        # 创建临时文件
        temp_file = "temp_demo.md"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(sample_content)
        
        # 处理文档
        success = app.process_single_document(
            temp_file,
            "转换为现代商务风格的HTML文档，图片加圆角边框",
            "HTML",
            enable_analysis=True,
            enable_template_recommendation=True
        )
        
        if success:
            print("✅ 演示1完成：基础处理成功")
        else:
            print("❌ 演示1失败")
        
        # 清理临时文件
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
    except Exception as e:
        print(f"❌ 演示1错误: {e}")
    
    print()

def demo_content_analysis():
    """演示内容分析功能"""
    print("🎯 演示2: 智能内容分析")
    print("-" * 50)
    
    try:
        from utils.content_analyzer import analyze_document_comprehensive
        
        sample_content = """
# 测试文档

## 第一章

这是一个测试文档。这是一个测试文档。这是一个测试文档。

## 第二章

这一章的内容很长，包含很多信息，需要仔细阅读才能理解，而且句子结构比较复杂，可能会影响阅读体验，但是内容确实很重要。

### 子章节

简短内容。

![测试图片](test.jpg)

## 总结

总结内容。
"""
        
        print("📊 开始分析文档...")
        result = analyze_document_comprehensive(sample_content)
        
        if result:
            overall_score = result.get("overall_score", {})
            print(f"📈 整体评分: {overall_score.get('overall_score', 0)}/100")
            
            suggestions = result.get("suggestions", [])
            if suggestions:
                print(f"💡 优化建议数量: {len(suggestions)}")
                for i, suggestion in enumerate(suggestions[:2], 1):
                    print(f"   {i}. {suggestion.get('title', '')}")
            
            print("✅ 演示2完成：内容分析成功")
        else:
            print("❌ 演示2失败：分析结果为空")
            
    except ImportError:
        print("⚠️  内容分析模块未安装，跳过演示")
    except Exception as e:
        print(f"❌ 演示2错误: {e}")
    
    print()

def demo_template_recommendation():
    """演示模板推荐功能"""
    print("🎯 演示3: 模板推荐系统")
    print("-" * 50)
    
    try:
        from utils.template_manager import get_template_manager, recommend_templates_for_content
        
        manager = get_template_manager()
        templates = manager.list_templates()
        
        print(f"📚 可用模板数量: {len(templates)}")
        for template in templates[:3]:
            print(f"   • {template.name}: {template.description}")
        
        # 测试推荐
        technical_content = """
# API文档

## 概述

这是一个RESTful API的技术文档。

```python
def get_user(user_id):
    return user_service.get(user_id)
```

## 接口说明

### 获取用户信息
- URL: /api/users/{id}
- 方法: GET
- 参数: user_id
"""
        
        print("\n🎯 为技术文档推荐模板...")
        recommendations = recommend_templates_for_content(technical_content, "技术文档格式")
        
        if recommendations:
            print(f"📋 推荐结果数量: {len(recommendations)}")
            for i, rec in enumerate(recommendations[:2], 1):
                template = rec["template"]
                score = rec["score"]
                print(f"   {i}. {template.name} (匹配度: {score:.1%})")
        
        print("✅ 演示3完成：模板推荐成功")
        
    except ImportError:
        print("⚠️  模板管理模块未安装，跳过演示")
    except Exception as e:
        print(f"❌ 演示3错误: {e}")
    
    print()

def demo_format_conversion():
    """演示格式转换功能"""
    print("🎯 演示4: 多格式转换")
    print("-" * 50)
    
    try:
        from utils.format_converter import FormatConverter
        
        converter = FormatConverter()
        formats_info = converter.get_available_formats()
        
        print("📋 支持的输出格式:")
        for fmt, info in formats_info.items():
            status = "✅" if info["available"] else "❌"
            print(f"   {status} {fmt}: {info['description']}")
            if info.get("requirements"):
                print(f"      💡 需要: {info['requirements']}")
        
        # 测试HTML转换
        sample_content = """
# 测试文档

这是一个测试文档，用于验证格式转换功能。

## 特性

- 支持多种格式
- 自动样式应用
- 高质量输出
"""
        
        print(f"\n🔄 测试HTML转换...")
        result = converter.convert_to_format(sample_content, "HTML")
        
        if result.get("success"):
            print(f"✅ HTML转换成功，文件大小: {result.get('size', 0)} 字节")
        else:
            print(f"❌ HTML转换失败: {result.get('error', '未知错误')}")
        
        print("✅ 演示4完成：格式转换测试成功")
        
    except ImportError:
        print("⚠️  格式转换模块未安装，跳过演示")
    except Exception as e:
        print(f"❌ 演示4错误: {e}")
    
    print()

def main():
    """运行所有演示"""
    print("🎨" + "=" * 60)
    print("        智能文档自动排版系统 - 功能演示")
    print("🎨" + "=" * 60)
    print()
    
    # 检查环境
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  警告: 未设置 OPENAI_API_KEY 环境变量")
        print("   某些功能可能无法完全演示")
        print()
    
    # 运行各个演示
    demo_basic_processing()
    demo_content_analysis()
    demo_template_recommendation()
    demo_format_conversion()
    
    print("🎉 所有演示完成！")
    print()
    print("💡 提示:")
    print("   • 使用 'python main.py --enhanced' 体验完整功能")
    print("   • 使用 'python main.py --help' 查看所有选项")
    print("   • 查看 README.md 了解详细使用说明")

if __name__ == "__main__":
    main()