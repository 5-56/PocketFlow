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