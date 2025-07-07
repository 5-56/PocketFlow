#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能文档自动排版系统 - 使用示例

这个示例展示了如何使用系统快速处理文档
"""

from flow import get_flow_by_type

def example_document_processing():
    """示例：自动处理文档"""
    
    # 示例文档内容
    document_content = """
# 产品介绍

## 概述

这是一个创新的人工智能产品，致力于提高工作效率。

![产品图片](product.jpg)

## 核心功能

### 智能分析
- 自动数据处理
- 智能报告生成
- 实时性能监控

### 用户体验
- 直观的界面设计
- 快速响应时间
- 个性化定制

![界面截图](ui-screenshot.png)

## 技术优势

我们的产品采用了最新的AI技术，具有以下优势：

1. **高效性**: 处理速度提升300%
2. **准确性**: 错误率降低至0.1%
3. **易用性**: 5分钟即可上手

## 应用场景

适用于多种行业和场景，包括但不限于：
- 金融分析
- 医疗诊断
- 教育培训
- 企业管理

## 联系我们

如需了解更多信息，请访问我们的官网或联系客服。
"""

    # 用户指令示例
    instructions = [
        "转换为现代商务风格的HTML文档，图片统一加圆角边框",
        "制作学术报告格式，使用蓝白配色方案",
        "生成创意设计文档，图片添加阴影效果"
    ]
    
    print("🎨 智能文档自动排版系统 - 使用示例")
    print("=" * 50)
    
    for i, instruction in enumerate(instructions, 1):
        print(f"\n📝 示例 {i}: {instruction}")
        print("-" * 40)
        
        # 创建共享数据
        shared = {
            "user_instruction": instruction,
            "original_document": document_content,
            "file_type": "markdown"
        }
        
        try:
            # 获取工作流
            flow = get_flow_by_type("complete")
            
            # 运行处理
            print("🚀 开始处理...")
            flow.run(shared)
            
            # 检查结果
            if "final_document" in shared:
                final_doc = shared["final_document"]
                print(f"✅ 处理完成!")
                print(f"📄 格式: {final_doc.get('format', 'Unknown')}")
                print(f"📏 内容长度: {len(final_doc.get('content', ''))}字符")
                
                if "requirements" in shared:
                    req = shared["requirements"]
                    print(f"🎨 应用风格: {req.get('style', 'Unknown')}")
                
            else:
                print("❌ 处理失败")
                
        except Exception as e:
            print(f"❌ 错误: {e}")
        
        print()

def quick_test():
    """快速测试"""
    print("🧪 快速功能测试")
    print("=" * 30)
    
    # 简单的测试文档
    test_content = """
# 测试文档

这是一个简单的测试。

## 子标题

包含一些文本内容。

![测试图片](test.jpg)

- 列表项1
- 列表项2
"""
    
    shared = {
        "user_instruction": "现代简约风格",
        "original_document": test_content,
        "file_type": "markdown"
    }
    
    try:
        # 使用简化工作流
        flow = get_flow_by_type("simple")
        flow.run(shared)
        
        if "final_document" in shared:
            print("✅ 快速测试通过!")
        else:
            print("❌ 快速测试失败")
            
    except Exception as e:
        print(f"❌ 测试错误: {e}")

if __name__ == "__main__":
    import os
    
    # 检查API密钥
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  注意: 需要设置 OPENAI_API_KEY 环境变量来运行完整示例")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        print("\n🧪 运行基础测试...")
        quick_test()
    else:
        print("🚀 运行完整示例...")
        example_document_processing()