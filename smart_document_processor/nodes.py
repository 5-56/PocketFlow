"""
Smart Document Processor - PocketFlow Nodes
"""
import asyncio
import json
import uuid
from typing import Dict, Any, List
from pocketflow import Node, BatchNode, AsyncNode
from utils.document_parser import DocumentParser
from utils.ai_processor import AIProcessor
from utils.image_processor import ImageProcessor
from utils.document_generator import DocumentGenerator

class DocumentParseNode(Node):
    """文档解析节点 - 解析上传的文档并提取结构化内容"""
    
    def __init__(self, max_retries=3):
        super().__init__(max_retries=max_retries)
        self.parser = DocumentParser()
    
    def prep(self, shared):
        """准备文档数据"""
        return {
            "file_data": shared["uploaded_file"]["content"],
            "file_name": shared["uploaded_file"]["name"],
            "content_type": shared["uploaded_file"]["content_type"]
        }
    
    def exec(self, prep_data):
        """执行文档解析"""
        try:
            document_structure = self.parser.parse(
                prep_data["file_data"],
                prep_data["file_name"],
                prep_data["content_type"]
            )
            return document_structure
        except Exception as e:
            raise Exception(f"文档解析失败: {str(e)}")
    
    def post(self, shared, prep_res, exec_res):
        """保存解析结果"""
        shared["document_structure"] = exec_res
        shared["processing_stage"] = "parsed"
        shared["original_content"] = exec_res.copy()
        return "analyze"

class ContentAnalysisNode(Node):
    """内容分析节点 - 分析文档内容类型和结构"""
    
    def prep(self, shared):
        return shared["document_structure"]
    
    def exec(self, doc_structure):
        """分析文档内容"""
        analyzed_content = {
            "text_elements": [],
            "image_elements": [],
            "chart_elements": [],
            "table_elements": [],
            "metadata": doc_structure.get("metadata", {})
        }
        
        # 分析每个元素
        for element in doc_structure.get("elements", []):
            element["id"] = str(uuid.uuid4())  # 添加唯一ID
            
            if element["type"] == "text":
                analyzed_content["text_elements"].append(element)
            elif element["type"] == "image":
                analyzed_content["image_elements"].append(element)
            elif element["type"] == "chart":
                analyzed_content["chart_elements"].append(element)
            elif element["type"] == "table":
                analyzed_content["table_elements"].append(element)
        
        # 添加统计信息
        analyzed_content["statistics"] = {
            "total_elements": len(doc_structure.get("elements", [])),
            "text_count": len(analyzed_content["text_elements"]),
            "image_count": len(analyzed_content["image_elements"]),
            "chart_count": len(analyzed_content["chart_elements"]),
            "table_count": len(analyzed_content["table_elements"])
        }
        
        return analyzed_content
    
    def post(self, shared, prep_res, exec_res):
        shared["analyzed_content"] = exec_res
        shared["processing_stage"] = "analyzed"
        return "ai_process"

class AIProcessingNode(AsyncNode):
    """AI处理节点 - 使用大模型处理文档内容"""
    
    def __init__(self, max_retries=3):
        super().__init__(max_retries=max_retries)
        self.ai_processor = AIProcessor()
    
    async def prep_async(self, shared):
        return {
            "analyzed_content": shared["analyzed_content"],
            "user_instruction": shared.get("user_instruction", ""),
            "processing_options": shared.get("processing_options", {})
        }
    
    async def exec_async(self, prep_data):
        """异步执行AI处理"""
        content = prep_data["analyzed_content"]
        instruction = prep_data["user_instruction"]
        options = prep_data["processing_options"]
        
        processed_content = {
            "text_elements": [],
            "image_elements": [],
            "chart_elements": content["chart_elements"],
            "table_elements": content["table_elements"],
            "metadata": content["metadata"],
            "statistics": content["statistics"]
        }
        
        # 处理文本元素
        for text_elem in content["text_elements"]:
            try:
                if instruction and options.get("process_text", True):
                    enhanced_text = await self.ai_processor.process_text_async(
                        text_elem["content"], 
                        instruction,
                        options.get("text_style", "professional")
                    )
                else:
                    enhanced_text = text_elem["content"]
                
                processed_content["text_elements"].append({
                    "id": text_elem["id"],
                    "content": enhanced_text,
                    "original": text_elem["content"],
                    "position": text_elem.get("position", {}),
                    "style": text_elem.get("style", {}),
                    "modified": enhanced_text != text_elem["content"]
                })
            except Exception as e:
                # 如果AI处理失败，保留原内容
                processed_content["text_elements"].append({
                    "id": text_elem["id"],
                    "content": text_elem["content"],
                    "original": text_elem["content"],
                    "position": text_elem.get("position", {}),
                    "style": text_elem.get("style", {}),
                    "modified": False,
                    "error": str(e)
                })
        
        # 处理图像元素
        for img_elem in content["image_elements"]:
            try:
                if options.get("analyze_images", True):
                    img_analysis = await self.ai_processor.analyze_image_async(
                        img_elem["data"]
                    )
                else:
                    img_analysis = {"description": "未分析", "suggestions": []}
                
                processed_content["image_elements"].append({
                    "id": img_elem["id"],
                    "data": img_elem["data"],
                    "original_data": img_elem["data"],
                    "analysis": img_analysis,
                    "suggested_modifications": img_analysis.get("suggestions", []),
                    "position": img_elem.get("position", {}),
                    "size": img_elem.get("size", {}),
                    "modified": False
                })
            except Exception as e:
                processed_content["image_elements"].append({
                    "id": img_elem["id"],
                    "data": img_elem["data"],
                    "original_data": img_elem["data"],
                    "analysis": {"description": "分析失败", "suggestions": []},
                    "suggested_modifications": [],
                    "position": img_elem.get("position", {}),
                    "size": img_elem.get("size", {}),
                    "modified": False,
                    "error": str(e)
                })
        
        return processed_content
    
    async def post_async(self, shared, prep_res, exec_res):
        shared["processed_content"] = exec_res
        shared["processing_stage"] = "ai_processed"
        return "user_review"

class ImageProcessingNode(Node):
    """图像处理节点 - 处理图像修改请求"""
    
    def __init__(self):
        super().__init__()
        self.image_processor = ImageProcessor()
    
    def prep(self, shared):
        return {
            "processed_content": shared.get("processed_content", {}),
            "image_modifications": shared.get("image_modifications", {})
        }
    
    def exec(self, prep_data):
        """执行图像处理"""
        processed_content = prep_data["processed_content"]
        modifications = prep_data["image_modifications"]
        
        if not modifications:
            return processed_content
        
        # 处理图像修改
        for img_id, mod_params in modifications.items():
            # 在processed_content中找到对应的图像
            for img_elem in processed_content.get("image_elements", []):
                if img_elem["id"] == img_id:
                    try:
                        modified_data = self.image_processor.modify_image(
                            img_elem["original_data"],
                            mod_params.get("operations", {})
                        )
                        img_elem["data"] = modified_data
                        img_elem["modified"] = True
                        img_elem["modification_history"] = mod_params
                    except Exception as e:
                        img_elem["error"] = f"图像处理失败: {str(e)}"
                    break
        
        return processed_content
    
    def post(self, shared, prep_res, exec_res):
        shared["processed_content"] = exec_res
        shared["processing_stage"] = "images_processed"
        return "generate_document"

class TextEditingNode(Node):
    """文本编辑节点 - 处理用户的文本修改"""
    
    def prep(self, shared):
        return {
            "processed_content": shared.get("processed_content", {}),
            "text_modifications": shared.get("text_modifications", {})
        }
    
    def exec(self, prep_data):
        """执行文本修改"""
        processed_content = prep_data["processed_content"]
        modifications = prep_data["text_modifications"]
        
        if not modifications:
            return processed_content
        
        # 处理文本修改
        for text_id, new_content in modifications.items():
            for text_elem in processed_content.get("text_elements", []):
                if text_elem["id"] == text_id:
                    text_elem["content"] = new_content
                    text_elem["modified"] = True
                    break
        
        return processed_content
    
    def post(self, shared, prep_res, exec_res):
        shared["processed_content"] = exec_res
        return "generate_document"

class DocumentGenerationNode(Node):
    """文档生成节点 - 生成最终文档"""
    
    def __init__(self):
        super().__init__()
        self.generator = DocumentGenerator()
    
    def prep(self, shared):
        return {
            "processed_content": shared["processed_content"],
            "output_format": shared.get("output_format", "docx"),
            "template_settings": shared.get("template_settings", {}),
            "export_options": shared.get("export_options", {})
        }
    
    def exec(self, prep_data):
        """生成文档"""
        content = prep_data["processed_content"]
        output_format = prep_data["output_format"]
        template_settings = prep_data["template_settings"]
        export_options = prep_data["export_options"]
        
        try:
            if output_format.lower() == "docx":
                document_data = self.generator.generate_docx(
                    content, template_settings, export_options
                )
            elif output_format.lower() == "pdf":
                document_data = self.generator.generate_pdf(
                    content, template_settings, export_options
                )
            elif output_format.lower() == "html":
                document_data = self.generator.generate_html(
                    content, template_settings, export_options
                )
            else:
                raise ValueError(f"不支持的输出格式: {output_format}")
            
            return {
                "data": document_data,
                "format": output_format,
                "size": len(document_data),
                "generated_at": str(asyncio.get_event_loop().time())
            }
        except Exception as e:
            raise Exception(f"文档生成失败: {str(e)}")
    
    def post(self, shared, prep_res, exec_res):
        shared["generated_document"] = exec_res
        shared["processing_stage"] = "completed"
        return "download_ready"

class BatchTextProcessingNode(BatchNode):
    """批量文本处理节点"""
    
    def __init__(self):
        super().__init__()
        self.ai_processor = AIProcessor()
    
    def prep(self, shared):
        """准备批量处理的文本"""
        content = shared.get("analyzed_content", {})
        return content.get("text_elements", [])
    
    def exec(self, text_element):
        """处理单个文本元素"""
        instruction = "优化文本内容，保持原意的同时提高可读性"
        try:
            enhanced_text = self.ai_processor.process_text(
                text_element["content"], 
                instruction
            )
            return {
                "id": text_element["id"],
                "content": enhanced_text,
                "original": text_element["content"],
                "modified": enhanced_text != text_element["content"]
            }
        except Exception as e:
            return {
                "id": text_element["id"],
                "content": text_element["content"],
                "original": text_element["content"],
                "modified": False,
                "error": str(e)
            }
    
    def post(self, shared, prep_res, exec_res_list):
        """保存批量处理结果"""
        shared["batch_processed_texts"] = exec_res_list
        return "merge_results"

class AIChatNode(AsyncNode):
    """AI聊天节点"""
    
    def __init__(self):
        super().__init__()
        self.ai_processor = AIProcessor()
    
    async def prep_async(self, shared):
        # 准备聊天数据
        message = shared.get("user_message", "")
        context = shared.get("context", {})
        selected_text = shared.get("selected_text", "")
        ai_settings = shared.get("ai_settings", {})
        
        return {
            "message": message,
            "context": context,
            "selected_text": selected_text,
            "settings": ai_settings
        }
    
    async def exec_async(self, prep_res):
        try:
            message = prep_res["message"]
            selected_text = prep_res["selected_text"]
            settings = prep_res["settings"]
            
            # 构建完整的提示
            if selected_text:
                full_prompt = f"""
用户选中的文本：{selected_text}

用户指令：{message}

请根据用户的指令处理选中的文本，如果没有特定指令，请提供有用的建议。
"""
            else:
                full_prompt = message
            
            # 设置AI处理器参数
            if settings.get("max_tokens"):
                self.ai_processor.max_tokens = settings["max_tokens"]
            if settings.get("temperature"):
                self.ai_processor.temperature = settings["temperature"]
            
            # 调用AI处理
            response = await self.ai_processor.process_text_async(
                full_prompt, 
                "chat", 
                settings.get("response_style", "professional")
            )
            
            # 生成建议
            suggestions = self._generate_suggestions(message, selected_text)
            
            # 生成修改建议
            modifications = []
            if selected_text and any(keyword in message.lower() for keyword in ["优化", "修改", "改进", "重写"]):
                modifications = [{
                    "type": "text_replacement",
                    "original": selected_text,
                    "suggested": response,
                    "reason": "基于AI优化建议"
                }]
            
            return {
                "response": response,
                "suggestions": suggestions,
                "modifications": modifications,
                "token_usage": len(full_prompt) + len(response)  # 简单估算
            }
            
        except Exception as e:
            return {
                "response": f"抱歉，处理您的请求时出现了错误：{str(e)}",
                "suggestions": [],
                "modifications": [],
                "token_usage": 0
            }
    
    async def post_async(self, shared, prep_res, exec_res):
        # 保存AI响应
        shared["ai_response"] = exec_res["response"]
        shared["ai_suggestions"] = exec_res["suggestions"]
        shared["ai_modifications"] = exec_res["modifications"]
        shared["token_usage"] = exec_res["token_usage"]
        
        return "completed"
    
    def _generate_suggestions(self, message: str, selected_text: str) -> list:
        """生成相关建议"""
        suggestions = []
        
        # 基于消息内容生成建议
        if selected_text:
            suggestions.extend([
                {"action": "optimize", "target": "selected_text", "text": "进一步优化选中文本"},
                {"action": "translate", "target": "selected_text", "text": "翻译选中文本"},
                {"action": "expand", "target": "selected_text", "text": "扩展选中文本"}
            ])
        
        # 基于关键词生成建议
        keywords_suggestions = {
            "翻译": {"action": "translate", "text": "尝试翻译为其他语言"},
            "摘要": {"action": "summarize", "text": "生成更详细的摘要"},
            "优化": {"action": "optimize", "text": "应用更多优化选项"},
            "格式": {"action": "format", "text": "调整文档格式"}
        }
        
        for keyword, suggestion in keywords_suggestions.items():
            if keyword in message:
                suggestions.append(suggestion)
        
        return suggestions[:3]  # 限制建议数量

class AIQuickActionNode(AsyncNode):
    """AI快速操作节点"""
    
    def __init__(self):
        super().__init__()
        self.ai_processor = AIProcessor()
    
    async def prep_async(self, shared):
        return {
            "action": shared.get("action_type", ""),
            "text": shared.get("target_text", ""),
            "settings": shared.get("ai_settings", {})
        }
    
    async def exec_async(self, prep_res):
        try:
            action = prep_res["action"]
            text = prep_res["text"]
            settings = prep_res["settings"]
            
            # 设置AI处理器参数
            if settings.get("max_tokens"):
                self.ai_processor.max_tokens = settings["max_tokens"]
            if settings.get("temperature"):
                self.ai_processor.temperature = settings["temperature"]
            
            # 根据操作类型处理文本
            action_map = {
                "optimize": ("优化这段文字的表达，使其更清晰流畅", "professional"),
                "summarize": ("为这段内容生成简洁的摘要", "professional"),
                "translate": ("将这段内容翻译为英文", "professional"),
                "rewrite": ("用不同的方式重写这段内容", "professional"),
                "expand": ("扩展这段内容，添加更多细节", "professional"),
                "format": ("改善这段内容的格式和结构", "professional")
            }
            
            if action in action_map:
                instruction, style = action_map[action]
                result = await self.ai_processor.process_text_async(text, instruction, style)
            else:
                result = await self.ai_processor.process_text_async(text, f"执行操作：{action}", "professional")
            
            return {
                "result": result,
                "action": action,
                "original_text": text
            }
            
        except Exception as e:
            return {
                "result": prep_res["text"],  # 返回原文本
                "action": prep_res["action"],
                "original_text": prep_res["text"],
                "error": str(e)
            }
    
    async def post_async(self, shared, prep_res, exec_res):
        shared["ai_result"] = exec_res["result"]
        shared["action_performed"] = exec_res["action"]
        
        # 生成修改建议
        if "error" not in exec_res:
            shared["ai_modifications"] = [{
                "type": "text_replacement",
                "original": exec_res["original_text"],
                "suggested": exec_res["result"],
                "reason": f"AI {exec_res['action']} 操作结果"
            }]
        
        return "completed"