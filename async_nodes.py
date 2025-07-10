#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
异步文档处理节点 - 高性能版本
基于PocketFlow AsyncNode实现的新一代文档处理工作流
"""

import asyncio
import json
import yaml
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pocketflow import AsyncNode, AsyncParallelBatchNode

# 导入工具函数
from utils.async_llm_pool import call_llm_async, batch_call_llm_async
from utils.document_processor import parse_document, apply_styles, generate_html_from_markdown
from utils.image_processor import process_image_with_effects, batch_process_images

logger = logging.getLogger(__name__)

@dataclass
class ProcessingContext:
    """处理上下文数据结构"""
    user_instruction: str
    document_content: str
    file_type: str = "markdown"
    processing_strategy: str = "complete"
    quality_level: str = "high"
    
class AsyncParseRequirementNode(AsyncNode):
    """异步解析用户需求节点"""
    
    async def prep_async(self, shared):
        """异步准备用户指令数据"""
        instruction = shared.get("user_instruction", "")
        context = shared.get("context", {})
        
        return {
            "instruction": instruction,
            "context": context,
            "timestamp": asyncio.get_event_loop().time()
        }
    
    async def exec_async(self, prep_res):
        """异步解析用户需求"""
        instruction = prep_res["instruction"]
        
        if not instruction:
            return {"error": "没有提供用户指令"}
        
        # 构建智能提示词
        prompt = f"""
作为专业的文档设计专家，请分析用户的需求并提取具体的格式要求。

用户指令："{instruction}"

请分析并返回以下JSON格式的结果：
{{
    "style": "整体设计风格（如现代商务、学术严谨、创意艺术等）",
    "format": "输出格式（HTML、PDF、Word、PowerPoint等）",
    "layout": {{
        "font_family": "字体系列偏好",
        "font_size": "字体大小级别（small/medium/large）",
        "color_scheme": "配色方案描述",
        "spacing": "间距要求（compact/standard/loose）",
        "alignment": "对齐方式（left/center/justify）"
    }},
    "image_style": {{
        "unified_size": "是否统一图片尺寸（true/false）",
        "effects": ["图片效果列表（如rounded_corners、shadow、border等）"],
        "alignment": "图片对齐方式（left/center/right）",
        "max_width": "最大宽度设置"
    }},
    "content_enhancement": {{
        "auto_formatting": "是否自动格式化（true/false）",
        "structure_optimization": "是否优化结构（true/false）",
        "language_polishing": "是否进行语言润色（true/false）"
    }},
    "priority": "处理优先级（low/medium/high/urgent）",
    "complexity_level": "复杂度级别（simple/moderate/complex）",
    "special_requirements": "其他特殊要求列表"
}}

注意：请根据用户指令的具体内容进行智能推断，补充合理的默认设置。
"""
        
        try:
            result = await call_llm_async(
                prompt, 
                model="gpt-4o-mini",
                temperature=0.3  # 降低温度以获得更一致的结果
            )
            
            # 解析JSON响应
            if "```json" in result:
                json_str = result.split("```json")[1].split("```")[0].strip()
            else:
                json_str = result
            
            parsed_requirements = json.loads(json_str)
            
            # 验证必要字段
            required_fields = ["style", "format", "layout", "image_style"]
            for field in required_fields:
                if field not in parsed_requirements:
                    parsed_requirements[field] = {}
            
            # 添加处理元数据
            parsed_requirements["processing_metadata"] = {
                "parsed_at": asyncio.get_event_loop().time(),
                "model_used": "gpt-4o-mini",
                "instruction_length": len(instruction),
                "complexity_score": len(instruction.split()) / 10  # 简单复杂度评分
            }
            
            return parsed_requirements
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON解析失败: {e}, 使用默认设置")
            return self._get_default_requirements(instruction)
        except Exception as e:
            logger.error(f"需求解析失败: {e}")
            return self._get_default_requirements(instruction)
    
    def _get_default_requirements(self, instruction: str) -> Dict[str, Any]:
        """获取默认需求设置"""
        return {
            "style": "现代简约",
            "format": "HTML",
            "layout": {
                "font_family": "系统默认",
                "font_size": "medium",
                "color_scheme": "蓝白配色",
                "spacing": "standard",
                "alignment": "left"
            },
            "image_style": {
                "unified_size": True,
                "effects": ["rounded_corners"],
                "alignment": "center",
                "max_width": "100%"
            },
            "content_enhancement": {
                "auto_formatting": True,
                "structure_optimization": True,
                "language_polishing": False
            },
            "priority": "medium",
            "complexity_level": "moderate",
            "special_requirements": [instruction],
            "processing_metadata": {
                "fallback_used": True,
                "instruction_length": len(instruction)
            }
        }
    
    async def post_async(self, shared, prep_res, exec_res):
        """异步保存解析结果"""
        shared["requirements"] = exec_res
        shared["processing_start_time"] = asyncio.get_event_loop().time()
        
        style = exec_res.get("style", "Unknown")
        complexity = exec_res.get("complexity_level", "moderate")
        
        logger.info(f"需求解析完成: {style}风格, 复杂度: {complexity}")
        
        return "default"

class AsyncAnalyzeDocumentNode(AsyncNode):
    """异步文档分析节点"""
    
    async def prep_async(self, shared):
        """异步准备文档内容"""
        return {
            "content": shared.get("original_document", ""),
            "file_type": shared.get("file_type", "markdown"),
            "requirements": shared.get("requirements", {})
        }
    
    async def exec_async(self, prep_res):
        """异步分析文档结构"""
        content = prep_res["content"]
        file_type = prep_res["file_type"]
        requirements = prep_res["requirements"]
        
        if not content:
            return {"error": "没有提供文档内容"}
        
        # 并行执行基础解析和AI分析
        basic_analysis_task = asyncio.create_task(
            self._basic_document_analysis(content, file_type)
        )
        
        ai_analysis_task = asyncio.create_task(
            self._ai_enhanced_analysis(content, requirements)
        )
        
        # 等待两个分析任务完成
        basic_analysis, ai_analysis = await asyncio.gather(
            basic_analysis_task, ai_analysis_task
        )
        
        # 合并分析结果
        combined_analysis = {
            **basic_analysis,
            "ai_insights": ai_analysis,
            "analysis_timestamp": asyncio.get_event_loop().time(),
            "processing_time": 0  # 将在post中计算
        }
        
        return combined_analysis
    
    async def _basic_document_analysis(self, content: str, file_type: str) -> Dict[str, Any]:
        """基础文档结构分析"""
        # 运行在线程池中以避免阻塞
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, parse_document, content, file_type)
    
    async def _ai_enhanced_analysis(self, content: str, requirements: Dict) -> Dict[str, Any]:
        """AI增强分析"""
        analysis_prompt = f"""
请对以下文档进行深度分析，重点关注用户需求的契合度：

用户需求风格: {requirements.get('style', '未指定')}
输出格式: {requirements.get('format', 'HTML')}
复杂度级别: {requirements.get('complexity_level', 'moderate')}

文档内容（前1000字符）:
{content[:1000]}...

请分析并返回JSON格式结果：
{{
    "readability_score": "可读性评分 0-100",
    "structure_quality": "结构质量评分 0-100", 
    "content_coherence": "内容连贯性评分 0-100",
    "style_matching": "与用户需求的匹配度 0-100",
    "optimization_suggestions": [
        "具体的优化建议1",
        "具体的优化建议2",
        "具体的优化建议3"
    ],
    "estimated_processing_time": "预估处理时间（秒）",
    "recommended_strategy": "推荐的处理策略（quick/standard/comprehensive）",
    "content_type": "内容类型（technical/business/academic/creative等）",
    "language_quality": "语言质量评估",
    "visual_elements_count": "视觉元素数量统计"
}}
"""
        
        try:
            result = await call_llm_async(
                analysis_prompt,
                model="gpt-4o-mini",
                temperature=0.2
            )
            
            if "```json" in result:
                json_str = result.split("```json")[1].split("```")[0].strip()
            else:
                json_str = result
            
            return json.loads(json_str)
            
        except Exception as e:
            logger.warning(f"AI分析失败: {e}, 返回基础分析")
            return {
                "readability_score": 75,
                "structure_quality": 70,
                "content_coherence": 75,
                "style_matching": 60,
                "optimization_suggestions": ["建议优化文档结构", "改进段落布局"],
                "estimated_processing_time": 30,
                "recommended_strategy": "standard",
                "content_type": "general",
                "language_quality": "良好",
                "analysis_error": str(e)
            }
    
    async def post_async(self, shared, prep_res, exec_res):
        """异步保存分析结果"""
        # 计算处理时间
        start_time = shared.get("processing_start_time", 0)
        exec_res["processing_time"] = asyncio.get_event_loop().time() - start_time
        
        shared["document_structure"] = exec_res
        
        # 更新处理策略（如果AI建议不同）
        recommended_strategy = exec_res.get("ai_insights", {}).get("recommended_strategy")
        if recommended_strategy and recommended_strategy != shared.get("requirements", {}).get("complexity_level"):
            shared["requirements"]["recommended_strategy"] = recommended_strategy
            logger.info(f"AI建议使用 {recommended_strategy} 策略")
        
        titles_count = len(exec_res.get("titles", []))
        images_count = len(exec_res.get("images", []))
        ai_score = exec_res.get("ai_insights", {}).get("readability_score", "N/A")
        
        logger.info(f"文档分析完成: {titles_count}个标题, {images_count}张图片, AI评分: {ai_score}")
        
        return "default"

class AsyncDesignLayoutNode(AsyncNode):
    """异步排版设计节点"""
    
    async def prep_async(self, shared):
        """准备设计数据"""
        return {
            "requirements": shared.get("requirements", {}),
            "document_structure": shared.get("document_structure", {}),
            "ai_insights": shared.get("document_structure", {}).get("ai_insights", {})
        }
    
    async def exec_async(self, prep_res):
        """异步设计排版方案"""
        requirements = prep_res["requirements"]
        doc_structure = prep_res["document_structure"]
        ai_insights = prep_res["ai_insights"]
        
        # 构建智能设计提示词
        design_prompt = f"""
作为顶级UI/UX设计师，请为文档设计专业的排版方案。

用户需求分析:
- 风格: {requirements.get('style', '现代简约')}
- 格式: {requirements.get('format', 'HTML')}
- 复杂度: {requirements.get('complexity_level', 'moderate')}
- 优先级: {requirements.get('priority', 'medium')}

文档结构分析:
- 标题层级数: {len(doc_structure.get('titles', []))}
- 图片数量: {len(doc_structure.get('images', []))}
- 段落数量: {len(doc_structure.get('paragraphs', []))}
- 内容类型: {ai_insights.get('content_type', 'general')}

AI分析评分:
- 可读性: {ai_insights.get('readability_score', 'N/A')}
- 结构质量: {ai_insights.get('structure_quality', 'N/A')}
- 风格匹配度: {ai_insights.get('style_matching', 'N/A')}

请设计并返回JSON格式的完整排版方案：
{{
    "typography": {{
        "primary_font": "主字体（具体字体名称）",
        "secondary_font": "辅助字体",
        "heading_scale": {{
            "h1": "h1字体大小（如2.5rem）",
            "h2": "h2字体大小（如2rem）",
            "h3": "h3字体大小（如1.5rem）",
            "h4": "h4字体大小（如1.25rem）"
        }},
        "body_text": "正文字体大小（如1rem）",
        "line_height": "行高（如1.6）",
        "letter_spacing": "字间距（如normal）"
    }},
    "colors": {{
        "primary": "主色调（hex值）",
        "secondary": "辅助色（hex值）",
        "accent": "强调色（hex值）",
        "text_primary": "主要文字颜色",
        "text_secondary": "次要文字颜色",
        "background": "背景色",
        "border": "边框色",
        "gradient": "渐变色方案（可选）"
    }},
    "spacing": {{
        "section_margin": "章节间距（如3rem）",
        "paragraph_margin": "段落间距（如1.5rem）",
        "title_margin_top": "标题上间距（如2rem）",
        "title_margin_bottom": "标题下间距（如1rem）",
        "list_margin": "列表间距",
        "container_padding": "容器内边距"
    }},
    "layout": {{
        "max_width": "最大宽度（如1200px）",
        "container_alignment": "容器对齐（center/left/right）",
        "grid_system": "网格系统（如12列）",
        "responsive_breakpoints": "响应式断点"
    }},
    "image_design": {{
        "max_width": "图片最大宽度",
        "aspect_ratio": "推荐宽高比",
        "border_radius": "圆角大小（如8px）",
        "shadow": "阴影效果",
        "border": "边框样式",
        "hover_effects": "悬停效果",
        "caption_style": "图片说明样式"
    }},
    "interactive_elements": {{
        "button_style": "按钮样式",
        "link_style": "链接样式", 
        "hover_transitions": "悬停过渡效果",
        "focus_indicators": "焦点指示器"
    }},
    "accessibility": {{
        "contrast_ratio": "对比度比例",
        "font_size_scalability": "字体缩放性",
        "color_blind_friendly": "色盲友好性"
    }},
    "design_principles": "设计原理说明",
    "implementation_notes": "实现注意事项"
}}

请确保设计方案专业、美观且符合用户需求。
"""
        
        try:
            result = await call_llm_async(
                design_prompt,
                model="gpt-4o",  # 使用更强大的模型进行设计
                temperature=0.4,
                max_tokens=3000
            )
            
            if "```json" in result:
                json_str = result.split("```json")[1].split("```")[0].strip()
            else:
                json_str = result
            
            layout_design = json.loads(json_str)
            
            # 添加设计元数据
            layout_design["design_metadata"] = {
                "created_at": asyncio.get_event_loop().time(),
                "model_used": "gpt-4o",
                "design_complexity": ai_insights.get("recommended_strategy", "standard"),
                "optimization_level": requirements.get("priority", "medium")
            }
            
            return layout_design
            
        except Exception as e:
            logger.warning(f"设计方案生成失败: {e}, 使用默认设计")
            return self._get_default_design(requirements)
    
    def _get_default_design(self, requirements: Dict) -> Dict[str, Any]:
        """获取默认设计方案"""
        return {
            "typography": {
                "primary_font": "'Segoe UI', 'PingFang SC', sans-serif",
                "heading_scale": {
                    "h1": "2.5rem",
                    "h2": "2rem", 
                    "h3": "1.5rem",
                    "h4": "1.25rem"
                },
                "body_text": "1rem",
                "line_height": "1.6",
                "letter_spacing": "normal"
            },
            "colors": {
                "primary": "#2196F3",
                "secondary": "#FFC107",
                "text_primary": "#333333",
                "text_secondary": "#666666",
                "background": "#FFFFFF",
                "border": "#E0E0E0"
            },
            "spacing": {
                "section_margin": "3rem",
                "paragraph_margin": "1.5rem",
                "title_margin_top": "2rem",
                "title_margin_bottom": "1rem"
            },
            "layout": {
                "max_width": "1200px",
                "container_alignment": "center"
            },
            "image_design": {
                "max_width": "100%",
                "border_radius": "8px",
                "shadow": "0 4px 8px rgba(0,0,0,0.1)",
                "border": "none"
            },
            "design_metadata": {
                "fallback_used": True,
                "created_at": asyncio.get_event_loop().time()
            }
        }
    
    async def post_async(self, shared, prep_res, exec_res):
        """保存设计方案"""
        shared["layout_design"] = exec_res
        
        primary_color = exec_res.get("colors", {}).get("primary", "Unknown")
        design_complexity = exec_res.get("design_metadata", {}).get("design_complexity", "standard")
        
        logger.info(f"排版设计完成: 主色调 {primary_color}, 复杂度 {design_complexity}")
        
        return "default"

class AsyncProcessTextNode(AsyncNode):
    """异步文本处理节点"""
    
    async def prep_async(self, shared):
        """准备文本处理数据"""
        return {
            "original_content": shared.get("original_document", ""),
            "layout_design": shared.get("layout_design", {}),
            "requirements": shared.get("requirements", {}),
            "ai_insights": shared.get("document_structure", {}).get("ai_insights", {})
        }
    
    async def exec_async(self, prep_res):
        """异步处理文本格式"""
        content = prep_res["original_content"]
        layout_design = prep_res["layout_design"]
        requirements = prep_res["requirements"]
        ai_insights = prep_res["ai_insights"]
        
        if not content:
            return {"error": "没有文档内容可处理"}
        
        # 并行执行样式应用和内容优化
        style_task = asyncio.create_task(
            self._apply_basic_styles(content, layout_design)
        )
        
        optimization_task = asyncio.create_task(
            self._optimize_content_with_ai(content, requirements, ai_insights)
        )
        
        # 等待两个任务完成
        styled_content, optimized_content = await asyncio.gather(
            style_task, optimization_task
        )
        
        return {
            "processed_content": styled_content,
            "optimized_content": optimized_content,
            "applied_styles": layout_design,
            "processing_metadata": {
                "processed_at": asyncio.get_event_loop().time(),
                "optimization_applied": bool(optimized_content),
                "content_length": len(optimized_content or styled_content)
            }
        }
    
    async def _apply_basic_styles(self, content: str, layout_design: Dict) -> str:
        """应用基础样式"""
        loop = asyncio.get_event_loop()
        
        styles = {
            "title_style": {
                "color": layout_design.get("colors", {}).get("primary", "#2196F3"),
                "prefix": "",
                "suffix": ""
            },
            "paragraph_style": layout_design.get("spacing", {})
        }
        
        return await loop.run_in_executor(None, apply_styles, content, styles)
    
    async def _optimize_content_with_ai(self, content: str, requirements: Dict, ai_insights: Dict) -> str:
        """使用AI优化内容"""
        # 检查是否需要内容优化
        enhancement_settings = requirements.get("content_enhancement", {})
        if not enhancement_settings.get("structure_optimization", False):
            return content
        
        optimization_prompt = f"""
请优化以下文档的结构和内容，提升其质量和可读性：

原始内容:
{content}

优化要求:
- 风格: {requirements.get('style', '现代简约')}
- 格式: {requirements.get('format', 'HTML')}
- 自动格式化: {enhancement_settings.get('auto_formatting', True)}
- 语言润色: {enhancement_settings.get('language_polishing', False)}

AI分析建议:
{', '.join(ai_insights.get('optimization_suggestions', []))}

请进行以下优化:
1. 确保标题层次清晰合理
2. 优化段落结构和逻辑流程
3. 改进列表和重点内容的表达
4. 保持原始内容的完整性和准确性
5. 适应目标风格的表达方式

请返回优化后的Markdown格式文档。
"""
        
        try:
            optimized = await call_llm_async(
                optimization_prompt,
                model="gpt-4o-mini",
                temperature=0.3,
                max_tokens=4000
            )
            
            return optimized
            
        except Exception as e:
            logger.warning(f"内容优化失败: {e}, 返回原始内容")
            return content
    
    async def post_async(self, shared, prep_res, exec_res):
        """保存处理后的文本"""
        shared["processed_text"] = exec_res
        
        content_length = exec_res.get("processing_metadata", {}).get("content_length", 0)
        optimization_applied = exec_res.get("processing_metadata", {}).get("optimization_applied", False)
        
        logger.info(f"文本处理完成: {content_length}字符, 优化应用: {optimization_applied}")
        
        return "default"

class ParallelImageProcessingNode(AsyncParallelBatchNode):
    """并行图片处理节点"""
    
    async def prep_async(self, shared):
        """准备图片处理数据"""
        doc_structure = shared.get("document_structure", {})
        layout_design = shared.get("layout_design", {})
        
        images = doc_structure.get("images", [])
        
        if not images:
            return []
        
        # 为每张图片准备处理参数
        image_tasks = []
        for img in images:
            task_data = {
                "image_info": img,
                "design_config": layout_design.get("image_design", {}),
                "requirements": shared.get("requirements", {}).get("image_style", {})
            }
            image_tasks.append(task_data)
        
        return image_tasks
    
    async def exec_async(self, image_task):
        """异步处理单张图片"""
        img_info = image_task["image_info"]
        design_config = image_task["design_config"]
        requirements = image_task["requirements"]
        
        # 构建图片效果配置
        effects = {}
        
        # 从设计配置中提取效果
        if design_config.get("border_radius"):
            effects["rounded_corners"] = {
                "radius": self._parse_size(design_config["border_radius"])
            }
        
        if design_config.get("shadow"):
            effects["shadow"] = {
                "offset": (5, 5),
                "blur_radius": 8,
                "color": "#00000020"
            }
        
        # 从用户需求中提取效果
        if requirements.get("effects"):
            for effect in requirements["effects"]:
                if effect == "rounded_corners":
                    effects["rounded_corners"] = {"radius": 10}
                elif effect == "shadow":
                    effects["shadow"] = {
                        "offset": (3, 3),
                        "blur_radius": 6,
                        "color": "#00000015"
                    }
        
        # 尺寸设置
        if requirements.get("unified_size", False):
            effects["resize"] = {
                "size": (800, 600),
                "maintain_aspect": True
            }
        
        # 模拟异步图片处理（实际应用中需要真实的图片文件）
        await asyncio.sleep(0.1)  # 模拟处理时间
        
        processed_image = {
            "original_url": img_info["url"],
            "alt_text": img_info["alt_text"],
            "effects_applied": effects,
            "new_url": f"processed_{img_info['url']}",
            "section": img_info.get("section", ""),
            "processing_time": 0.1,
            "file_size_optimized": True
        }
        
        return processed_image
    
    def _parse_size(self, size_str: str) -> int:
        """解析尺寸字符串"""
        try:
            return int(size_str.replace("px", "").replace("rem", ""))
        except:
            return 8
    
    async def post_async(self, shared, prep_res, exec_res_list):
        """保存图片处理结果"""
        result = {
            "processed_images": exec_res_list,
            "total_processed": len(exec_res_list),
            "processing_summary": {
                "effects_applied": len([img for img in exec_res_list if img.get("effects_applied")]),
                "size_optimized": len([img for img in exec_res_list if img.get("file_size_optimized")]),
                "total_processing_time": sum(img.get("processing_time", 0) for img in exec_res_list)
            }
        }
        
        shared["processed_images"] = result
        
        logger.info(f"图片并行处理完成: {result['total_processed']}张图片, "
                   f"耗时: {result['processing_summary']['total_processing_time']:.2f}s")
        
        return "default"

class AsyncGenerateDocumentNode(AsyncNode):
    """异步文档生成节点"""
    
    async def prep_async(self, shared):
        """准备文档生成数据"""
        return {
            "processed_text": shared.get("processed_text", {}),
            "processed_images": shared.get("processed_images", {}),
            "layout_design": shared.get("layout_design", {}),
            "requirements": shared.get("requirements", {}),
            "document_structure": shared.get("document_structure", {})
        }
    
    async def exec_async(self, prep_res):
        """异步生成最终文档"""
        processed_text = prep_res["processed_text"]
        layout_design = prep_res["layout_design"]
        requirements = prep_res["requirements"]
        
        # 获取优化后的内容
        content = (processed_text.get("optimized_content") or 
                  processed_text.get("processed_content", ""))
        
        if not content:
            return {"error": "没有可用的文档内容"}
        
        # 根据要求的格式生成文档
        output_format = requirements.get("format", "HTML").upper()
        
        if output_format == "HTML":
            # 并行生成HTML和样式
            html_task = asyncio.create_task(
                self._generate_html_content(content, layout_design)
            )
            
            css_task = asyncio.create_task(
                self._generate_css_styles(layout_design)
            )
            
            html_content, css_styles = await asyncio.gather(html_task, css_task)
            
            # 组合最终HTML
            final_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>智能排版文档</title>
    <style>
{css_styles}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
            
            return {
                "format": "HTML",
                "content": final_html,
                "styles_applied": layout_design,
                "metadata": {
                    "generated_at": asyncio.get_event_loop().time(),
                    "content_length": len(final_html),
                    "css_rules_count": css_styles.count("{")
                }
            }
        
        elif output_format == "MARKDOWN":
            return {
                "format": "MARKDOWN",
                "content": content,
                "styles_applied": layout_design,
                "metadata": {
                    "generated_at": asyncio.get_event_loop().time(),
                    "content_length": len(content)
                }
            }
        
        else:
            return {
                "format": output_format,
                "content": content,
                "note": f"基础{output_format}格式输出",
                "metadata": {
                    "generated_at": asyncio.get_event_loop().time(),
                    "content_length": len(content)
                }
            }
    
    async def _generate_html_content(self, content: str, layout_design: Dict) -> str:
        """异步生成HTML内容"""
        loop = asyncio.get_event_loop()
        
        styles = {
            "title_style": layout_design.get("colors", {}),
            "image_style": layout_design.get("image_design", {})
        }
        
        return await loop.run_in_executor(
            None, generate_html_from_markdown, content, styles
        )
    
    async def _generate_css_styles(self, layout_design: Dict) -> str:
        """异步生成CSS样式"""
        typography = layout_design.get("typography", {})
        colors = layout_design.get("colors", {})
        spacing = layout_design.get("spacing", {})
        image_design = layout_design.get("image_design", {})
        
        css_rules = []
        
        # 基础样式
        css_rules.append(f"""
        body {{
            font-family: {typography.get('primary_font', "'Segoe UI', sans-serif")};
            font-size: {typography.get('body_text', '1rem')};
            line-height: {typography.get('line_height', '1.6')};
            letter-spacing: {typography.get('letter_spacing', 'normal')};
            color: {colors.get('text_primary', '#333333')};
            background-color: {colors.get('background', '#FFFFFF')};
            max-width: {layout_design.get('layout', {}).get('max_width', '1200px')};
            margin: 0 auto;
            padding: 2rem;
        }}""")
        
        # 标题样式
        heading_scale = typography.get("heading_scale", {})
        for level, size in heading_scale.items():
            css_rules.append(f"""
        {level} {{
            font-size: {size};
            color: {colors.get('primary', '#2196F3')};
            margin-top: {spacing.get('title_margin_top', '2rem')};
            margin-bottom: {spacing.get('title_margin_bottom', '1rem')};
        }}""")
        
        # 段落样式
        css_rules.append(f"""
        p {{
            margin-bottom: {spacing.get('paragraph_margin', '1.5rem')};
            color: {colors.get('text_primary', '#333333')};
        }}""")
        
        # 图片样式
        css_rules.append(f"""
        img {{
            max-width: {image_design.get('max_width', '100%')};
            height: auto;
            border-radius: {image_design.get('border_radius', '8px')};
            box-shadow: {image_design.get('shadow', '0 4px 8px rgba(0,0,0,0.1)')};
            margin: {spacing.get('paragraph_margin', '1.5rem')} 0;
            display: block;
        }}""")
        
        # 列表样式
        css_rules.append(f"""
        ul, ol {{
            margin-bottom: {spacing.get('paragraph_margin', '1.5rem')};
            padding-left: 2rem;
        }}
        
        li {{
            margin-bottom: 0.5rem;
        }}""")
        
        # 响应式设计
        css_rules.append("""
        @media (max-width: 768px) {
            body {
                padding: 1rem;
                font-size: 0.9rem;
            }
            
            h1 { font-size: 2rem; }
            h2 { font-size: 1.75rem; }
            h3 { font-size: 1.5rem; }
        }""")
        
        return "\n".join(css_rules)
    
    async def post_async(self, shared, prep_res, exec_res):
        """保存最终文档"""
        shared["final_document"] = exec_res
        
        doc_format = exec_res.get("format", "Unknown")
        content_length = exec_res.get("metadata", {}).get("content_length", 0)
        
        logger.info(f"文档生成完成: {doc_format}格式, {content_length}字符")
        
        # 异步保存到文件
        asyncio.create_task(self._save_document_async(exec_res))
        
        return "default"
    
    async def _save_document_async(self, document: Dict):
        """异步保存文档到文件"""
        try:
            import os
            import aiofiles
            
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
            
            async with aiofiles.open(filename, "w", encoding="utf-8") as f:
                await f.write(content)
            
            logger.info(f"文档已异步保存到: {filename}")
        
        except Exception as e:
            logger.error(f"异步保存文档失败: {e}")

# 导出异步节点类
__all__ = [
    "AsyncParseRequirementNode",
    "AsyncAnalyzeDocumentNode", 
    "AsyncDesignLayoutNode",
    "AsyncProcessTextNode",
    "ParallelImageProcessingNode",
    "AsyncGenerateDocumentNode"
]