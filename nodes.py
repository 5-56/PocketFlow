from pocketflow import Node
from utils.call_llm import call_llm, analyze_with_llm, generate_with_llm
from utils.document_processor import parse_document, apply_styles, generate_html_from_markdown
from utils.image_processor import process_image_with_effects, batch_process_images
import json
import yaml
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ParseRequirementNode(Node):
    """解析用户需求节点"""
    
    def prep(self, shared):
        """准备用户指令数据"""
        return shared.get("user_instruction", "")
    
    def exec(self, prep_res):
        """使用LLM解析用户需求"""
        if not prep_res:
            return {"error": "没有提供用户指令"}
        
        prompt = f"""
作为专业的文档设计师，请分析用户的以下指令，并提取出具体的格式要求：

用户指令："{prep_res}"

请分析并返回以下信息（JSON格式）：
{{
    "style": "用户希望的整体风格（如商务、学术、创意等）",
    "format": "输出格式（如PDF、HTML、Word等）",
    "layout": {{
        "font_size": "字体大小偏好",
        "color_scheme": "配色方案",
        "spacing": "间距要求"
    }},
    "image_style": {{
        "unified_size": "是否统一图片尺寸",
        "effects": "图片效果要求（如边框、阴影、圆角等）",
        "alignment": "图片对齐方式"
    }},
    "special_requirements": "其他特殊要求"
}}

如果用户指令比较简单，请根据常见的设计原则补充合理的默认设置。
"""
        
        result = call_llm(prompt)
        
        try:
            # 尝试解析JSON
            if "```json" in result:
                json_str = result.split("```json")[1].split("```")[0].strip()
            else:
                json_str = result
            
            parsed_requirements = json.loads(json_str)
            return parsed_requirements
        except json.JSONDecodeError:
            # 如果JSON解析失败，返回基本的默认设置
            logger.warning("无法解析LLM返回的JSON，使用默认设置")
            return {
                "style": "现代简约",
                "format": "HTML",
                "layout": {
                    "font_size": "适中",
                    "color_scheme": "蓝白配色",
                    "spacing": "标准"
                },
                "image_style": {
                    "unified_size": True,
                    "effects": "圆角边框",
                    "alignment": "居中"
                },
                "special_requirements": prep_res
            }
    
    def post(self, shared, prep_res, exec_res):
        """保存解析结果"""
        shared["requirements"] = exec_res
        logger.info(f"需求解析完成: {exec_res.get('style', 'Unknown')}风格")
        return "default"

class AnalyzeDocumentNode(Node):
    """文档分析节点"""
    
    def prep(self, shared):
        """准备文档内容"""
        return {
            "content": shared.get("original_document", ""),
            "file_type": shared.get("file_type", "markdown")
        }
    
    def exec(self, prep_res):
        """分析文档结构"""
        content = prep_res["content"]
        file_type = prep_res["file_type"]
        
        if not content:
            return {"error": "没有提供文档内容"}
        
        # 使用文档处理器解析结构
        document_structure = parse_document(content, file_type)
        
        # 使用LLM进行更深入的分析
        analysis_prompt = f"""
请分析以下文档结构，并提供优化建议：

文档类型：{file_type}
标题数量：{len(document_structure.get('titles', []))}
段落数量：{len(document_structure.get('paragraphs', []))}
图片数量：{len(document_structure.get('images', []))}

文档内容摘要：
{content[:500]}...

请分析文档的：
1. 结构层次是否清晰
2. 内容组织是否合理
3. 建议的排版改进点

返回JSON格式的分析结果。
"""
        
        llm_analysis = analyze_with_llm(content[:1000], "分析文档结构和排版建议")
        
        # 合并结构信息和LLM分析
        document_structure["llm_analysis"] = llm_analysis
        
        return document_structure
    
    def post(self, shared, prep_res, exec_res):
        """保存文档分析结果"""
        shared["document_structure"] = exec_res
        
        titles_count = len(exec_res.get("titles", []))
        images_count = len(exec_res.get("images", []))
        logger.info(f"文档分析完成: {titles_count}个标题, {images_count}张图片")
        
        return "default"

class DesignLayoutNode(Node):
    """排版设计节点"""
    
    def prep(self, shared):
        """准备需求和文档结构数据"""
        return {
            "requirements": shared.get("requirements", {}),
            "document_structure": shared.get("document_structure", {})
        }
    
    def exec(self, prep_res):
        """设计具体的排版方案"""
        requirements = prep_res["requirements"]
        doc_structure = prep_res["document_structure"]
        
        design_prompt = f"""
作为专业的UI/UX设计师，根据以下信息设计文档排版方案：

用户需求：
- 风格：{requirements.get('style', '现代简约')}
- 格式：{requirements.get('format', 'HTML')}
- 特殊要求：{requirements.get('special_requirements', '无')}

文档结构：
- 标题层级：{len(doc_structure.get('titles', []))}个标题
- 图片数量：{len(doc_structure.get('images', []))}张图片
- 段落数量：{len(doc_structure.get('paragraphs', []))}个段落

请设计详细的排版方案，包括：
{{
    "typography": {{
        "primary_font": "主要字体",
        "heading_sizes": {{"h1": "2.5em", "h2": "2em", "h3": "1.5em"}},
        "line_height": "行高",
        "letter_spacing": "字间距"
    }},
    "colors": {{
        "primary": "主色调",
        "secondary": "辅助色",
        "text": "文字颜色",
        "background": "背景色"
    }},
    "spacing": {{
        "section_margin": "段落间距",
        "paragraph_margin": "段落内间距",
        "title_margin": "标题间距"
    }},
    "image_design": {{
        "max_width": "图片最大宽度",
        "border_radius": "圆角大小",
        "shadow": "阴影效果",
        "border": "边框样式"
    }}
}}

请返回JSON格式的完整设计方案。
"""
        
        result = call_llm(design_prompt)
        
        try:
            if "```json" in result:
                json_str = result.split("```json")[1].split("```")[0].strip()
            else:
                json_str = result
            
            layout_design = json.loads(json_str)
            return layout_design
        except json.JSONDecodeError:
            # 返回默认设计方案
            logger.warning("无法解析设计方案，使用默认设计")
            return {
                "typography": {
                    "primary_font": "'Segoe UI', sans-serif",
                    "heading_sizes": {"h1": "2.5em", "h2": "2em", "h3": "1.5em"},
                    "line_height": "1.6",
                    "letter_spacing": "normal"
                },
                "colors": {
                    "primary": "#2196F3",
                    "secondary": "#FFC107",
                    "text": "#333333",
                    "background": "#FFFFFF"
                },
                "spacing": {
                    "section_margin": "2em",
                    "paragraph_margin": "1em",
                    "title_margin": "1.5em"
                },
                "image_design": {
                    "max_width": "100%",
                    "border_radius": "8px",
                    "shadow": "0 4px 8px rgba(0,0,0,0.1)",
                    "border": "none"
                }
            }
    
    def post(self, shared, prep_res, exec_res):
        """保存设计方案"""
        shared["layout_design"] = exec_res
        
        primary_color = exec_res.get("colors", {}).get("primary", "Unknown")
        logger.info(f"排版设计完成: 主色调 {primary_color}")
        
        return "default"

class ProcessTextNode(Node):
    """文本处理节点"""
    
    def prep(self, shared):
        """准备文档内容和设计方案"""
        return {
            "original_content": shared.get("original_document", ""),
            "layout_design": shared.get("layout_design", {}),
            "requirements": shared.get("requirements", {})
        }
    
    def exec(self, prep_res):
        """处理文本格式"""
        content = prep_res["original_content"]
        layout_design = prep_res["layout_design"]
        
        if not content:
            return {"error": "没有文档内容可处理"}
        
        # 应用基本样式
        styles = {
            "title_style": {
                "color": layout_design.get("colors", {}).get("primary", "#2196F3"),
                "prefix": "",
                "suffix": ""
            },
            "paragraph_style": layout_design.get("spacing", {})
        }
        
        processed_content = apply_styles(content, styles)
        
        # 使用LLM优化文本结构
        optimization_prompt = f"""
请优化以下文档的文本结构和格式：

原始内容：
{content}

优化要求：
1. 确保标题层次清晰
2. 段落结构合理
3. 添加必要的分隔和强调
4. 保持原始内容的完整性

请返回优化后的Markdown格式文档。
"""
        
        optimized_content = call_llm(optimization_prompt)
        
        return {
            "processed_content": processed_content,
            "optimized_content": optimized_content,
            "applied_styles": styles
        }
    
    def post(self, shared, prep_res, exec_res):
        """保存处理后的文本"""
        shared["processed_text"] = exec_res
        logger.info("文本处理完成")
        return "default"

class UnifyImagesNode(Node):
    """图片统一处理节点"""
    
    def prep(self, shared):
        """准备图片信息和设计方案"""
        return {
            "document_structure": shared.get("document_structure", {}),
            "layout_design": shared.get("layout_design", {}),
            "requirements": shared.get("requirements", {})
        }
    
    def exec(self, prep_res):
        """统一处理图片"""
        doc_structure = prep_res["document_structure"]
        layout_design = prep_res["layout_design"]
        
        images = doc_structure.get("images", [])
        
        if not images:
            return {"message": "没有发现图片，跳过图片处理"}
        
        # 构建图片处理效果配置
        image_design = layout_design.get("image_design", {})
        
        effects = {
            "resize": {
                "size": (800, 600),
                "maintain_aspect": True
            },
            "enhance": {
                "brightness": 1.0,
                "contrast": 1.1,
                "saturation": 1.0
            }
        }
        
        # 添加边框和圆角
        if image_design.get("border_radius"):
            effects["rounded_corners"] = {
                "radius": int(image_design["border_radius"].replace("px", ""))
            }
        
        if image_design.get("shadow"):
            effects["shadow"] = {
                "offset": (5, 5),
                "blur_radius": 8,
                "color": "#00000020"
            }
        
        # 模拟图片处理（实际应用中需要真实的图片文件）
        processed_images = []
        for img in images:
            processed_img = {
                "original_url": img["url"],
                "alt_text": img["alt_text"],
                "effects_applied": effects,
                "new_url": f"processed_{img['url']}",
                "section": img.get("section", "")
            }
            processed_images.append(processed_img)
        
        return {
            "processed_images": processed_images,
            "effects_config": effects,
            "total_processed": len(processed_images)
        }
    
    def post(self, shared, prep_res, exec_res):
        """保存图片处理结果"""
        shared["processed_images"] = exec_res
        
        count = exec_res.get("total_processed", 0)
        logger.info(f"图片处理完成: {count}张图片已统一")
        
        return "default"

class GenerateDocumentNode(Node):
    """文档生成节点"""
    
    def prep(self, shared):
        """准备所有处理结果"""
        return {
            "processed_text": shared.get("processed_text", {}),
            "processed_images": shared.get("processed_images", {}),
            "layout_design": shared.get("layout_design", {}),
            "requirements": shared.get("requirements", {})
        }
    
    def exec(self, prep_res):
        """生成最终文档"""
        processed_text = prep_res["processed_text"]
        layout_design = prep_res["layout_design"]
        requirements = prep_res["requirements"]
        
        # 获取优化后的内容
        content = processed_text.get("optimized_content", processed_text.get("processed_content", ""))
        
        if not content:
            return {"error": "没有可用的文档内容"}
        
        # 根据要求的格式生成文档
        output_format = requirements.get("format", "HTML").upper()
        
        if output_format == "HTML":
            # 生成HTML文档
            styles = {
                "title_style": layout_design.get("colors", {}),
                "image_style": layout_design.get("image_design", {})
            }
            
            html_content = generate_html_from_markdown(content, styles)
            
            return {
                "format": "HTML",
                "content": html_content,
                "styles_applied": styles
            }
        
        elif output_format == "MARKDOWN":
            # 返回优化的Markdown
            return {
                "format": "MARKDOWN",
                "content": content,
                "styles_applied": layout_design
            }
        
        else:
            # 其他格式的基本支持
            return {
                "format": output_format,
                "content": content,
                "note": f"基础{output_format}格式输出"
            }
    
    def post(self, shared, prep_res, exec_res):
        """保存最终文档"""
        shared["final_document"] = exec_res
        
        doc_format = exec_res.get("format", "Unknown")
        content_length = len(exec_res.get("content", ""))
        
        logger.info(f"文档生成完成: {doc_format}格式, {content_length}字符")
        
        # 保存到文件
        self._save_document(exec_res)
        
        return "default"
    
    def _save_document(self, document):
        """保存文档到文件"""
        try:
            format_type = document.get("format", "HTML").lower()
            content = document.get("content", "")
            
            # 确保输出目录存在
            os.makedirs("output", exist_ok=True)
            
            if format_type == "html":
                filename = "output/formatted_document.html"
            elif format_type == "markdown":
                filename = "output/formatted_document.md"
            else:
                filename = f"output/formatted_document.{format_type.lower()}"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            
            logger.info(f"文档已保存到: {filename}")
        
        except Exception as e:
            logger.error(f"保存文档失败: {e}")

# 错误处理节点
class ErrorHandlingNode(Node):
    """错误处理节点"""
    
    def prep(self, shared):
        """准备错误信息"""
        return shared.get("error", "")
    
    def exec(self, prep_res):
        """处理错误"""
        if prep_res:
            logger.error(f"处理过程中发生错误: {prep_res}")
            return {"handled": True, "error": prep_res}
        return {"handled": False}
    
    def post(self, shared, prep_res, exec_res):
        """记录错误处理结果"""
        shared["error_handled"] = exec_res
        return "default"