#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能文档处理系统 - 增强交互界面
支持实时预览、多轮对话和智能建议
"""

import os
import sys
import json
from typing import Dict, List, Any
from flow import get_flow_by_type
from utils.call_llm import call_llm
import time
from pathlib import Path

class DocumentProcessor:
    """增强的文档处理器"""
    
    def __init__(self):
        self.conversation_history = []
        self.current_document = None
        self.processing_history = []
        self.user_preferences = self.load_user_preferences()
        
    def load_user_preferences(self):
        """加载用户偏好设置"""
        prefs_file = "user_preferences.json"
        if os.path.exists(prefs_file):
            try:
                with open(prefs_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "favorite_styles": [],
            "default_output_format": "HTML",
            "preferred_colors": ["#2196F3", "#4CAF50", "#FF9800"],
            "image_preferences": {
                "default_effects": ["rounded_corners", "shadow"],
                "default_size": [800, 600]
            }
        }
    
    def save_user_preferences(self):
        """保存用户偏好设置"""
        try:
            with open("user_preferences.json", 'w', encoding='utf-8') as f:
                json.dump(self.user_preferences, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存偏好设置失败: {e}")

class InteractiveUI:
    """增强的交互式用户界面"""
    
    def __init__(self):
        self.processor = DocumentProcessor()
        self.templates = self.load_templates()
        self.session_id = str(int(time.time()))
        
    def load_templates(self):
        """加载文档模板"""
        return {
            "商务报告": {
                "description": "专业的商务报告格式，适合企业使用",
                "style": "现代商务风格",
                "colors": {"primary": "#1e3a8a", "secondary": "#3b82f6"},
                "fonts": {"title": "Arial Black", "body": "Arial"},
                "layout": {"spacing": "宽松", "alignment": "左对齐"}
            },
            "学术论文": {
                "description": "标准的学术论文格式，符合期刊要求",
                "style": "学术严谨风格",
                "colors": {"primary": "#374151", "secondary": "#6b7280"},
                "fonts": {"title": "Times New Roman", "body": "Times New Roman"},
                "layout": {"spacing": "标准", "alignment": "两端对齐"}
            },
            "创意设计": {
                "description": "充满创意的设计风格，适合展示创意作品",
                "style": "创意艺术风格",
                "colors": {"primary": "#7c3aed", "secondary": "#a855f7"},
                "fonts": {"title": "Helvetica", "body": "Open Sans"},
                "layout": {"spacing": "动态", "alignment": "居中"}
            },
            "技术文档": {
                "description": "清晰的技术文档格式，便于阅读和理解",
                "style": "技术专业风格",
                "colors": {"primary": "#059669", "secondary": "#10b981"},
                "fonts": {"title": "Roboto", "body": "Source Code Pro"},
                "layout": {"spacing": "紧凑", "alignment": "左对齐"}
            },
            "产品说明": {
                "description": "友好的产品说明格式，突出产品特色",
                "style": "友好亲和风格",
                "colors": {"primary": "#ea580c", "secondary": "#fb923c"},
                "fonts": {"title": "Sans-serif", "body": "Sans-serif"},
                "layout": {"spacing": "舒适", "alignment": "居中"}
            }
        }
    
    def show_welcome(self):
        """显示欢迎界面"""
        print("🎨" + "=" * 80)
        print("     智能文档自动排版与设计系统 - 增强交互版")
        print("🤖" + "=" * 80)
        print("✨ 新功能亮点:")
        print("   🔄 实时预览和迭代调整")
        print("   💬 智能对话式交互")
        print("   🎯 个性化模板和建议")
        print("   📚 丰富的预设模板库")
        print("   🎨 高级排版和设计功能")
        print("   📱 多种输出格式支持")
        print("\n💡 提示：您可以随时说 'help' 获取帮助，'quit' 退出系统")
        print("-" * 80)
    
    def show_templates(self):
        """显示可用模板"""
        print("\n📚 可用文档模板:")
        print("-" * 50)
        for i, (name, template) in enumerate(self.templates.items(), 1):
            print(f"{i}. 【{name}】")
            print(f"   📝 {template['description']}")
            print(f"   🎨 风格: {template['style']}")
            print(f"   🌈 主色调: {template['colors']['primary']}")
            print()
    
    def get_smart_suggestions(self, user_input: str, document_content: str = "") -> List[str]:
        """获取智能建议"""
        prompt = f"""
作为专业的文档设计顾问，根据用户的输入和文档内容，提供3个具体的优化建议。

用户输入: "{user_input}"
文档内容摘要: "{document_content[:200]}..."

请提供以下格式的建议：
1. [具体建议1]
2. [具体建议2] 
3. [具体建议3]

建议应该具体、可执行，并能明显改善文档效果。
"""
        
        try:
            response = call_llm(prompt)
            suggestions = []
            for line in response.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    suggestion = line.split('.', 1)[-1].strip() if '.' in line else line[1:].strip()
                    if suggestion:
                        suggestions.append(suggestion)
            return suggestions[:3]
        except:
            return [
                "尝试使用更现代的配色方案",
                "增加图片的视觉效果",
                "优化标题层级结构"
            ]
    
    def process_template_choice(self, choice: str, document_content: str):
        """处理模板选择"""
        try:
            template_names = list(self.templates.keys())
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(template_names):
                    template_name = template_names[idx]
                    template = self.templates[template_name]
                    
                    # 基于模板生成指令
                    instruction = f"请使用{template['style']}格式化文档，主色调使用{template['colors']['primary']}，字体使用{template['fonts']['title']}标题和{template['fonts']['body']}正文，布局采用{template['layout']['spacing']}间距"
                    
                    print(f"✅ 已选择模板：【{template_name}】")
                    print(f"📝 自动生成指令：{instruction}")
                    
                    return instruction
            else:
                # 直接作为自定义指令处理
                return choice
        except:
            return choice
    
    def interactive_refinement(self, shared_data: Dict[str, Any]):
        """交互式细化调整"""
        print("\n🔧 进入交互式调整模式")
        print("您可以要求进一步调整文档格式，例如：")
        print("• '调整字体大小'")
        print("• '更换配色方案为暖色调'") 
        print("• '增加图片边框效果'")
        print("• '调整段落间距'")
        print("• 'preview' - 查看当前效果")
        print("• 'done' - 完成调整")
        
        while True:
            adjustment = input("\n🎯 请描述您想要的调整: ").strip()
            
            if adjustment.lower() in ['done', '完成', 'finish']:
                break
            elif adjustment.lower() in ['preview', '预览']:
                self.show_preview(shared_data)
                continue
            elif adjustment.lower() in ['help', '帮助']:
                print("💡 调整建议：")
                if "original_document" in shared_data:
                    suggestions = self.get_smart_suggestions(adjustment, shared_data["original_document"])
                    for i, suggestion in enumerate(suggestions, 1):
                        print(f"   {i}. {suggestion}")
                continue
            elif not adjustment:
                continue
            
            # 处理调整请求
            print(f"🔄 正在处理调整: {adjustment}")
            
            # 更新用户指令
            original_instruction = shared_data.get("user_instruction", "")
            new_instruction = f"{original_instruction}，并且{adjustment}"
            shared_data["user_instruction"] = new_instruction
            
            try:
                # 重新运行处理流程
                flow = get_flow_by_type("complete")
                flow.run(shared_data)
                
                if "final_document" in shared_data:
                    print("✅ 调整完成！")
                    self.show_preview(shared_data)
                else:
                    print("❌ 调整失败，请尝试其他描述")
                    
            except Exception as e:
                print(f"❌ 调整过程中出现错误: {e}")
                
    def show_preview(self, shared_data: Dict[str, Any]):
        """显示文档预览"""
        if "final_document" not in shared_data:
            print("❌ 没有可预览的文档")
            return
        
        final_doc = shared_data["final_document"]
        content = final_doc.get("content", "")
        
        print("\n📖 文档预览:")
        print("=" * 60)
        
        # 显示基本信息
        print(f"📄 格式: {final_doc.get('format', 'Unknown')}")
        print(f"📏 长度: {len(content)}字符")
        
        if "requirements" in shared_data:
            req = shared_data["requirements"]
            print(f"🎨 风格: {req.get('style', 'Unknown')}")
            print(f"🌈 配色: {req.get('layout', {}).get('color_scheme', 'Unknown')}")
        
        # 显示内容预览（前500字符）
        if content:
            preview_content = content[:500]
            if len(content) > 500:
                preview_content += "..."
            
            print("\n📝 内容预览:")
            print("-" * 40)
            print(preview_content)
            print("-" * 40)
        
        # 显示处理的图片信息
        if "processed_images" in shared_data:
            images_info = shared_data["processed_images"]
            if images_info.get("processed_images"):
                print(f"\n🖼️  已处理图片: {len(images_info['processed_images'])}张")
                for img in images_info["processed_images"][:3]:  # 显示前3张
                    print(f"   • {img.get('alt_text', '未命名图片')}")
        
        print("=" * 60)
    
    def save_session(self, shared_data: Dict[str, Any]):
        """保存会话记录"""
        session_dir = Path("sessions")
        session_dir.mkdir(exist_ok=True)
        
        session_file = session_dir / f"session_{self.session_id}.json"
        
        session_data = {
            "session_id": self.session_id,
            "timestamp": time.time(),
            "conversation_history": self.processor.conversation_history,
            "final_result": shared_data.get("final_document", {}),
            "user_instruction": shared_data.get("user_instruction", ""),
            "processing_summary": {
                "style": shared_data.get("requirements", {}).get("style", ""),
                "format": shared_data.get("final_document", {}).get("format", ""),
                "images_processed": len(shared_data.get("processed_images", {}).get("processed_images", []))
            }
        }
        
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            print(f"💾 会话已保存: {session_file}")
        except Exception as e:
            print(f"⚠️  保存会话失败: {e}")
    
    def run(self):
        """运行增强交互界面"""
        self.show_welcome()
        
        while True:
            try:
                print("\n" + "🤖 助手就绪，等待您的指令..." + "\n")
                
                # 获取用户输入
                user_input = input("💬 请告诉我您想要什么样的文档格式: ").strip()
                
                if not user_input:
                    continue
                    
                # 处理特殊命令
                if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                    print("👋 谢谢使用！再见！")
                    break
                elif user_input.lower() in ['help', '帮助', 'h']:
                    self.show_help()
                    continue
                elif user_input.lower() in ['templates', '模板', 't']:
                    self.show_templates()
                    continue
                elif user_input.lower() in ['preferences', '偏好', 'prefs']:
                    self.show_preferences()
                    continue
                
                # 获取文档内容
                document_content = self.get_document_content()
                if not document_content:
                    continue
                
                # 处理模板选择或自定义指令
                if user_input.isdigit() and 1 <= int(user_input) <= len(self.templates):
                    instruction = self.process_template_choice(user_input, document_content)
                else:
                    instruction = user_input
                
                # 提供智能建议
                suggestions = self.get_smart_suggestions(instruction, document_content)
                if suggestions:
                    print("\n💡 AI建议:")
                    for i, suggestion in enumerate(suggestions, 1):
                        print(f"   {i}. {suggestion}")
                    
                    use_suggestion = input("\n是否采用某个建议？(输入编号或直接回车继续): ").strip()
                    if use_suggestion.isdigit():
                        idx = int(use_suggestion) - 1
                        if 0 <= idx < len(suggestions):
                            instruction += f"，{suggestions[idx]}"
                            print(f"✅ 已采用建议: {suggestions[idx]}")
                
                # 创建共享数据
                shared_data = {
                    "user_instruction": instruction,
                    "original_document": document_content,
                    "file_type": "markdown"
                }
                
                # 处理文档
                print(f"\n🚀 开始处理您的文档...")
                print(f"📝 指令: {instruction}")
                
                try:
                    flow = get_flow_by_type("complete")
                    flow.run(shared_data)
                    
                    if "final_document" in shared_data:
                        print("\n✅ 初始处理完成！")
                        self.show_preview(shared_data)
                        
                        # 询问是否需要调整
                        refine = input("\n🔧 是否需要进一步调整？(y/n): ").strip().lower()
                        if refine in ['y', 'yes', '是', '需要']:
                            self.interactive_refinement(shared_data)
                        
                        # 保存会话
                        self.save_session(shared_data)
                        
                        # 记录到历史
                        self.processor.conversation_history.append({
                            "timestamp": time.time(),
                            "instruction": instruction,
                            "result": "success"
                        })
                        
                        print(f"\n✨ 文档处理完成！已保存到 output/ 目录")
                        
                    else:
                        print("❌ 文档处理失败")
                        
                except Exception as e:
                    print(f"❌ 处理过程中发生错误: {e}")
                    
            except KeyboardInterrupt:
                print("\n\n👋 用户中断，退出系统")
                break
            except Exception as e:
                print(f"\n❌ 系统错误: {e}")
                
        # 保存用户偏好
        self.processor.save_user_preferences()
    
    def get_document_content(self):
        """获取文档内容"""
        print("\n📄 请提供文档内容：")
        print("1. 输入文件路径")
        print("2. 直接粘贴内容")
        print("3. 使用示例文档")
        
        choice = input("\n选择方式 (1/2/3): ").strip()
        
        if choice == "1":
            file_path = input("📁 文件路径: ").strip()
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return f.read()
                except Exception as e:
                    print(f"❌ 读取文件失败: {e}")
                    return None
            else:
                print("❌ 文件不存在")
                return None
                
        elif choice == "2":
            print("📝 请粘贴内容 (输入'END'结束):")
            lines = []
            while True:
                line = input()
                if line.strip().upper() == 'END':
                    break
                lines.append(line)
            return '\n'.join(lines)
            
        elif choice == "3":
            return """
# 智能科技产品介绍

## 产品概述

我们的智能产品采用了最新的人工智能技术，为用户提供前所未有的智能体验。

![产品主图](product-main.jpg)

## 核心特性

### 🤖 智能交互
- 自然语言理解
- 多轮对话支持
- 个性化学习

### ⚡ 高效处理
- 实时响应
- 批量处理
- 云端同步

![功能展示](features.png)

## 技术优势

1. **先进算法**: 基于深度学习的核心算法
2. **高度集成**: 无缝集成现有系统
3. **安全可靠**: 企业级安全保障

## 应用场景

适用于教育、医疗、金融、制造等多个行业，帮助用户提升工作效率。

## 联系我们

了解更多详情，请访问我们的官网或联系销售团队。
"""
        else:
            print("❌ 无效选择")
            return None
    
    def show_help(self):
        """显示帮助信息"""
        print("\n📖 帮助信息:")
        print("-" * 50)
        print("🎯 指令格式示例:")
        print("   • '现代商务风格的HTML文档，图片加圆角'")
        print("   • '学术论文格式，蓝白配色'")
        print("   • '创意设计风格，图片添加阴影'")
        print()
        print("🔧 特殊命令:")
        print("   • 'templates' 或 't' - 查看模板库")
        print("   • 'help' 或 'h' - 显示帮助")
        print("   • 'preferences' - 设置偏好")
        print("   • 'quit' 或 'q' - 退出系统")
        print()
        print("💡 调整模式命令:")
        print("   • 'preview' - 预览当前文档")
        print("   • 'done' - 完成调整")
        print("   • 任何调整描述 - 继续优化")
    
    def show_preferences(self):
        """显示和设置用户偏好"""
        prefs = self.processor.user_preferences
        print("\n⚙️  当前用户偏好:")
        print("-" * 40)
        print(f"🎨 默认输出格式: {prefs['default_output_format']}")
        print(f"🌈 偏好颜色: {', '.join(prefs['preferred_colors'])}")
        print(f"📸 图片默认效果: {', '.join(prefs['image_preferences']['default_effects'])}")
        print(f"📐 图片默认尺寸: {prefs['image_preferences']['default_size']}")
        print()
        
        modify = input("是否修改偏好设置？(y/n): ").strip().lower()
        if modify in ['y', 'yes', '是']:
            # 这里可以添加偏好设置的修改逻辑
            print("💡 偏好设置功能正在开发中...")

if __name__ == "__main__":
    # 检查API密钥
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  需要设置 OPENAI_API_KEY 环境变量")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    # 运行增强交互界面
    ui = InteractiveUI()
    ui.run()