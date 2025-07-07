"""
AI Processor - AI处理工具
支持多种AI模型的文本和图像处理
"""
import asyncio
import base64
import json
import os
from typing import Dict, Any, List, Optional
import openai
from openai import AsyncOpenAI
import httpx

class AIProcessor:
    """AI处理器"""
    
    def __init__(self):
        # 配置OpenAI客户端
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
        self.client = openai.OpenAI(api_key=self.openai_api_key)
        self.async_client = AsyncOpenAI(api_key=self.openai_api_key)
    
    async def test_connection(self, api_key: str, model: str = "gpt-4") -> dict:
        """测试API连接"""
        try:
            import time
            
            # 创建临时客户端
            test_client = AsyncOpenAI(api_key=api_key)
            
            start_time = time.time()
            
            # 发送测试请求
            response = await test_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": "Hello, this is a test message."}
                ],
                max_tokens=10,
                temperature=0
            )
            
            end_time = time.time()
            latency = round((end_time - start_time) * 1000, 2)  # 毫秒
            
            if response and response.choices:
                return {
                    "success": True,
                    "latency": latency,
                    "model": model,
                    "usage": response.usage.dict() if hasattr(response, 'usage') else {}
                }
            else:
                return {"success": False, "error": "No response received"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
        
        # 配置模型参数
        self.text_model = "gpt-4"
        self.vision_model = "gpt-4-vision-preview"
        self.max_tokens = 4000
        self.temperature = 0.7
        
        # 预定义提示模板
        self.prompt_templates = {
            "professional": """
请将以下文本改写为更专业、正式的表达方式，保持原意不变：

原文：{text}

请返回改写后的文本：
""",
            "casual": """
请将以下文本改写为更轻松、通俗易懂的表达方式，保持原意不变：

原文：{text}

请返回改写后的文本：
""",
            "academic": """
请将以下文本改写为学术风格的表达方式，使用更精确的用词和表达：

原文：{text}

请返回改写后的文本：
""",
            "summary": """
请对以下文本进行总结，保留核心信息：

原文：{text}

请返回总结：
""",
            "expand": """
请扩展以下文本，添加更多细节和解释：

原文：{text}

请返回扩展后的文本：
""",
            "translate": """
请将以下文本翻译为{target_language}：

原文：{text}

请返回翻译结果：
""",
            "polish": """
请润色以下文本，改善表达方式、语法和流畅度，保持原意：

原文：{text}

请返回润色后的文本：
""",
            "formal": """
请将以下文本改写为正式、严谨的表达方式：

原文：{text}

请返回正式化的文本：
""",
            "explain": """
请解释以下文本的含义、背景或重要性：

文本：{text}

请提供简洁的解释：
""",
            "rewrite": """
请用不同的表达方式重写以下文本，保持相同的意思：

原文：{text}

请返回重写的文本：
""",
            "check_grammar": """
请检查以下文本的语法错误并修正：

原文：{text}

请返回修正后的文本：
""",
            "style_convert": """
请将以下文本转换为{style}风格：

原文：{text}

请返回转换后的文本：
""",
            "generate_outline": """
请为以下文档内容生成结构化的大纲：

文档内容：{text}

请返回HTML格式的大纲：
""",
            "content_audit": """
请审核以下内容，检查是否存在敏感词、不当内容或逻辑漏洞：

内容：{text}

请返回审核结果和建议：
""",
            "generate_section": """
请根据以下大纲或主题生成详细的章节内容：

主题/大纲：{text}

请返回章节内容：
""",
            "extract_keywords": """
请从以下文本中提取关键词和主题：

文本：{text}

请返回关键词列表：
"""
        }
    
    def process_text(self, text: str, instruction: str, style: str = "professional") -> str:
        """同步处理文本"""
        try:
            # 根据指令类型选择提示模板
            if instruction.lower() in self.prompt_templates:
                prompt = self.prompt_templates[instruction.lower()].format(text=text)
            elif style in self.prompt_templates:
                prompt = self.prompt_templates[style].format(text=text)
            else:
                # 自定义指令
                prompt = f"""
请根据以下指令修改文本内容：
指令：{instruction}

原文：{text}

请返回修改后的文本：
"""
            
            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {"role": "system", "content": "你是一个专业的文档编辑助手，能够根据用户指令优化文本内容。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"文本处理失败: {str(e)}")
    
    async def process_text_async(self, text: str, instruction: str, style: str = "professional") -> str:
        """异步处理文本"""
        try:
            # 根据指令类型选择提示模板
            if instruction.lower() in self.prompt_templates:
                prompt = self.prompt_templates[instruction.lower()].format(text=text)
            elif style in self.prompt_templates:
                prompt = self.prompt_templates[style].format(text=text)
            else:
                # 自定义指令
                prompt = f"""
请根据以下指令修改文本内容：
指令：{instruction}

原文：{text}

请返回修改后的文本：
"""
            
            response = await self.async_client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {"role": "system", "content": "你是一个专业的文档编辑助手，能够根据用户指令优化文本内容。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"文本处理失败: {str(e)}")
    
    def analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """同步分析图像"""
        try:
            # 将图像转换为base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """
请分析这张图片的内容，并提供以下信息：
1. 图片的主要内容和主题
2. 图片的构图和视觉效果
3. 可能的改进建议（如调整尺寸、优化色彩、改善清晰度等）
4. 图片在文档中的潜在作用和意义

请以JSON格式返回分析结果，包含description、composition、suggestions、purpose等字段。
"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # 尝试解析JSON，如果失败则返回文本分析
            try:
                analysis_json = json.loads(analysis_text)
                return analysis_json
            except json.JSONDecodeError:
                return {
                    "description": analysis_text,
                    "suggestions": self._extract_suggestions_from_text(analysis_text),
                    "composition": "未能解析构图信息",
                    "purpose": "未能解析用途信息"
                }
            
        except Exception as e:
            return {
                "description": f"图像分析失败: {str(e)}",
                "suggestions": [],
                "composition": "分析失败",
                "purpose": "分析失败"
            }
    
    async def analyze_image_async(self, image_data: bytes) -> Dict[str, Any]:
        """异步分析图像"""
        try:
            # 将图像转换为base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            response = await self.async_client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """
请分析这张图片的内容，并提供以下信息：
1. 图片的主要内容和主题
2. 图片的构图和视觉效果
3. 可能的改进建议（如调整尺寸、优化色彩、改善清晰度等）
4. 图片在文档中的潜在作用和意义

请以JSON格式返回分析结果，包含description、composition、suggestions、purpose等字段。
"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # 尝试解析JSON，如果失败则返回文本分析
            try:
                analysis_json = json.loads(analysis_text)
                return analysis_json
            except json.JSONDecodeError:
                return {
                    "description": analysis_text,
                    "suggestions": self._extract_suggestions_from_text(analysis_text),
                    "composition": "未能解析构图信息",
                    "purpose": "未能解析用途信息"
                }
            
        except Exception as e:
            return {
                "description": f"图像分析失败: {str(e)}",
                "suggestions": [],
                "composition": "分析失败",
                "purpose": "分析失败"
            }
    
    def generate_content(self, prompt: str, content_type: str = "text") -> str:
        """生成新内容"""
        try:
            system_prompts = {
                "text": "你是一个专业的内容创作助手，能够生成高质量的文本内容。",
                "title": "你是一个专业的标题创作助手，能够生成吸引人且准确的标题。",
                "summary": "你是一个专业的摘要生成助手，能够提取关键信息并生成准确的摘要。",
                "outline": "你是一个专业的大纲制作助手，能够生成结构清晰的文档大纲。"
            }
            
            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {"role": "system", "content": system_prompts.get(content_type, system_prompts["text"])},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"内容生成失败: {str(e)}")
    
    def translate_text(self, text: str, target_language: str = "英文") -> str:
        """翻译文本"""
        try:
            prompt = self.prompt_templates["translate"].format(
                text=text, 
                target_language=target_language
            )
            
            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {"role": "system", "content": "你是一个专业的翻译助手，能够准确翻译各种语言。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.3  # 翻译使用较低的温度
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"翻译失败: {str(e)}")
    
    def batch_process_texts(self, texts: List[str], instruction: str, style: str = "professional") -> List[str]:
        """批量处理文本"""
        results = []
        
        for text in texts:
            try:
                result = self.process_text(text, instruction, style)
                results.append(result)
            except Exception as e:
                results.append(f"处理失败: {str(e)}")
        
        return results
    
    async def batch_process_texts_async(self, texts: List[str], instruction: str, style: str = "professional") -> List[str]:
        """异步批量处理文本"""
        tasks = []
        
        for text in texts:
            task = self.process_text_async(text, instruction, style)
            tasks.append(task)
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理异常结果
            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    processed_results.append(f"处理失败: {str(result)}")
                else:
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            return [f"批量处理失败: {str(e)}"] * len(texts)
    
    def optimize_for_readability(self, text: str) -> str:
        """优化文本可读性"""
        prompt = f"""
请优化以下文本的可读性，使其更容易理解和阅读：
1. 调整句子长度，避免过长的句子
2. 使用更清晰的表达
3. 改善段落结构
4. 保持原意不变

原文：{text}

请返回优化后的文本：
"""
        
        return self.process_text(text, prompt)
    
    def _extract_suggestions_from_text(self, analysis_text: str) -> List[str]:
        """从分析文本中提取建议"""
        suggestions = []
        
        # 简单的关键词匹配
        keywords = {
            "尺寸": "调整图片尺寸",
            "大小": "调整图片尺寸", 
            "色彩": "优化色彩平衡",
            "颜色": "优化色彩平衡",
            "清晰度": "提高图片清晰度",
            "对比度": "调整对比度",
            "亮度": "调整亮度",
            "构图": "优化构图",
            "裁剪": "重新裁剪图片"
        }
        
        for keyword, suggestion in keywords.items():
            if keyword in analysis_text:
                suggestions.append(suggestion)
        
        # 如果没有找到建议，提供通用建议
        if not suggestions:
            suggestions = ["检查图片质量", "考虑调整尺寸", "优化色彩效果"]
        
        return list(set(suggestions))  # 去重
    
    def create_document_summary(self, elements: List[Dict[str, Any]]) -> str:
        """创建文档摘要"""
        text_content = []
        
        # 提取所有文本内容
        for element in elements:
            if element.get("type") == "text":
                text_content.append(element.get("content", ""))
        
        if not text_content:
            return "文档中没有文本内容可供总结。"
        
        combined_text = "\n".join(text_content)
        
        # 如果文本太长，先进行分段总结
        if len(combined_text) > 8000:
            return self._create_long_document_summary(text_content)
        else:
            return self.process_text(combined_text, "summary")
    
    def _create_long_document_summary(self, text_segments: List[str]) -> str:
        """为长文档创建摘要"""
        try:
            # 分段总结
            segment_summaries = []
            
            for segment in text_segments:
                if len(segment) > 100:  # 只总结较长的段落
                    summary = self.process_text(segment, "summary")
                    segment_summaries.append(summary)
            
            # 合并分段摘要
            if segment_summaries:
                combined_summary = "\n".join(segment_summaries)
                final_summary = self.process_text(combined_summary, "summary")
                return final_summary
            else:
                return "文档内容过短，无法生成有效摘要。"
                
        except Exception as e:
            return f"摘要生成失败: {str(e)}"
    
    def quick_action(self, action: str, text: str, **kwargs) -> Dict[str, Any]:
        """
        执行快速AI操作
        
        Args:
            action: 操作类型
            text: 输入文本
            **kwargs: 其他参数
            
        Returns:
            处理结果
        """
        try:
            # 映射操作到模板
            action_mapping = {
                'polish': 'polish',
                'expand': 'expand', 
                'summarize': 'summary',
                'translate': 'translate',
                'formal': 'formal',
                'casual': 'casual',
                'explain': 'explain',
                'rewrite': 'rewrite',
                'grammar': 'check_grammar',
                'outline': 'generate_outline',
                'audit': 'content_audit',
                'keywords': 'extract_keywords'
            }
            
            template_key = action_mapping.get(action, action)
            
            if template_key not in self.prompt_templates:
                return {
                    'success': False,
                    'message': f'不支持的操作: {action}'
                }
            
            # 处理特殊参数
            prompt_kwargs = {'text': text}
            if action == 'translate':
                prompt_kwargs['target_language'] = kwargs.get('target_language', '英文')
            elif action in ['style_convert']:
                prompt_kwargs['style'] = kwargs.get('style', '专业')
            
            # 生成提示词
            prompt = self.prompt_templates[template_key].format(**prompt_kwargs)
            
            # 调用AI
            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {"role": "system", "content": "你是一个专业的文本处理助手，请按照用户要求处理文本。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            result = response.choices[0].message.content.strip()
            
            return {
                'success': True,
                'result': result,
                'action': action,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"Quick action failed: {str(e)}")
            return {
                'success': False,
                'message': f'操作失败: {str(e)}'
            }
    
    def custom_action(self, instruction: str, text: str) -> Dict[str, Any]:
        """
        执行自定义AI操作
        
        Args:
            instruction: 自定义指令
            text: 输入文本
            
        Returns:
            处理结果
        """
        try:
            prompt = f"""
请按照以下指令处理文本：

指令：{instruction}

文本：{text}

请返回处理结果：
"""
            
            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {"role": "system", "content": "你是一个专业的文本处理助手，请严格按照用户的指令处理文本。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            result = response.choices[0].message.content.strip()
            
            return {
                'success': True,
                'result': result,
                'instruction': instruction,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"Custom action failed: {str(e)}")
            return {
                'success': False,
                'message': f'自定义操作失败: {str(e)}'
            }