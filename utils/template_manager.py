#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能模板管理系统
支持文档模板的创建、管理、应用和自定义
"""

import os
import json
import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from utils.call_llm import call_llm

class DocumentTemplate:
    """文档模板类"""
    
    def __init__(self, template_data: Dict[str, Any]):
        self.name = template_data.get("name", "")
        self.description = template_data.get("description", "")
        self.category = template_data.get("category", "通用")
        self.style = template_data.get("style", {})
        self.layout = template_data.get("layout", {})
        self.colors = template_data.get("colors", {})
        self.typography = template_data.get("typography", {})
        self.image_design = template_data.get("image_design", {})
        self.metadata = template_data.get("metadata", {})
        self.created_at = template_data.get("created_at", datetime.now().isoformat())
        self.updated_at = template_data.get("updated_at", datetime.now().isoformat())
        self.usage_count = template_data.get("usage_count", 0)
        self.rating = template_data.get("rating", 0.0)
        self.tags = template_data.get("tags", [])
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "style": self.style,
            "layout": self.layout,
            "colors": self.colors,
            "typography": self.typography,
            "image_design": self.image_design,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "usage_count": self.usage_count,
            "rating": self.rating,
            "tags": self.tags
        }
    
    def generate_instruction(self) -> str:
        """生成基于模板的指令"""
        instruction_parts = []
        
        # 风格指令
        if self.style:
            style_name = self.style.get("name", "现代风格")
            instruction_parts.append(f"使用{style_name}")
        
        # 颜色指令
        if self.colors:
            primary_color = self.colors.get("primary", "")
            if primary_color:
                instruction_parts.append(f"主色调使用{primary_color}")
        
        # 字体指令
        if self.typography:
            font_family = self.typography.get("primary_font", "")
            if font_family:
                instruction_parts.append(f"字体使用{font_family}")
        
        # 图片指令
        if self.image_design:
            effects = []
            if self.image_design.get("border_radius"):
                effects.append("圆角边框")
            if self.image_design.get("shadow"):
                effects.append("阴影效果")
            if effects:
                instruction_parts.append(f"图片添加{'/'.join(effects)}")
        
        # 布局指令
        if self.layout:
            spacing = self.layout.get("spacing", "")
            if spacing:
                instruction_parts.append(f"采用{spacing}间距")
        
        return "，".join(instruction_parts)

class TemplateManager:
    """模板管理器"""
    
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)
        self.templates_file = self.templates_dir / "templates.json"
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, DocumentTemplate]:
        """加载模板"""
        templates = {}
        
        if self.templates_file.exists():
            try:
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for name, template_data in data.items():
                        templates[name] = DocumentTemplate(template_data)
            except Exception as e:
                print(f"加载模板失败: {e}")
        
        # 如果没有模板，创建默认模板
        if not templates:
            templates = self._create_default_templates()
            self.save_templates()
        
        return templates
    
    def _create_default_templates(self) -> Dict[str, DocumentTemplate]:
        """创建默认模板"""
        default_templates = {
            "商务报告": DocumentTemplate({
                "name": "商务报告",
                "description": "专业的商务报告格式，适合企业使用",
                "category": "商务",
                "style": {"name": "现代商务风格"},
                "colors": {
                    "primary": "#1e3a8a",
                    "secondary": "#3b82f6",
                    "text": "#1f2937",
                    "background": "#ffffff"
                },
                "typography": {
                    "primary_font": "'Arial', 'Microsoft YaHei', sans-serif",
                    "heading_sizes": {"h1": "2.5em", "h2": "2em", "h3": "1.5em"},
                    "line_height": "1.6"
                },
                "layout": {"spacing": "宽松", "alignment": "左对齐"},
                "image_design": {
                    "border_radius": "8px",
                    "shadow": "0 4px 12px rgba(0,0,0,0.15)",
                    "max_width": "100%"
                },
                "tags": ["商务", "报告", "企业", "专业"]
            }),
            
            "学术论文": DocumentTemplate({
                "name": "学术论文",
                "description": "标准的学术论文格式，符合期刊要求",
                "category": "学术",
                "style": {"name": "学术严谨风格"},
                "colors": {
                    "primary": "#374151",
                    "secondary": "#6b7280",
                    "text": "#111827",
                    "background": "#ffffff"
                },
                "typography": {
                    "primary_font": "'Times New Roman', serif",
                    "heading_sizes": {"h1": "2.2em", "h2": "1.8em", "h3": "1.4em"},
                    "line_height": "1.8"
                },
                "layout": {"spacing": "标准", "alignment": "两端对齐"},
                "image_design": {
                    "border_radius": "4px",
                    "shadow": "0 2px 8px rgba(0,0,0,0.1)",
                    "max_width": "90%"
                },
                "tags": ["学术", "论文", "研究", "严谨"]
            }),
            
            "创意设计": DocumentTemplate({
                "name": "创意设计",
                "description": "充满创意的设计风格，适合展示创意作品",
                "category": "设计",
                "style": {"name": "创意艺术风格"},
                "colors": {
                    "primary": "#7c3aed",
                    "secondary": "#a855f7",
                    "text": "#1f2937",
                    "background": "#fafafa"
                },
                "typography": {
                    "primary_font": "'Helvetica Neue', 'Arial', sans-serif",
                    "heading_sizes": {"h1": "3em", "h2": "2.2em", "h3": "1.6em"},
                    "line_height": "1.5"
                },
                "layout": {"spacing": "动态", "alignment": "居中"},
                "image_design": {
                    "border_radius": "12px",
                    "shadow": "0 8px 24px rgba(124,58,237,0.2)",
                    "max_width": "100%"
                },
                "tags": ["创意", "设计", "艺术", "视觉"]
            }),
            
            "技术文档": DocumentTemplate({
                "name": "技术文档",
                "description": "清晰的技术文档格式，便于阅读和理解",
                "category": "技术",
                "style": {"name": "技术专业风格"},
                "colors": {
                    "primary": "#059669",
                    "secondary": "#10b981",
                    "text": "#1f2937",
                    "background": "#ffffff"
                },
                "typography": {
                    "primary_font": "'Source Sans Pro', 'Arial', sans-serif",
                    "heading_sizes": {"h1": "2.4em", "h2": "1.9em", "h3": "1.5em"},
                    "line_height": "1.7"
                },
                "layout": {"spacing": "紧凑", "alignment": "左对齐"},
                "image_design": {
                    "border_radius": "6px",
                    "shadow": "0 4px 16px rgba(5,150,105,0.1)",
                    "max_width": "100%"
                },
                "tags": ["技术", "文档", "开发", "说明"]
            }),
            
            "产品介绍": DocumentTemplate({
                "name": "产品介绍",
                "description": "友好的产品说明格式，突出产品特色",
                "category": "营销",
                "style": {"name": "友好亲和风格"},
                "colors": {
                    "primary": "#ea580c",
                    "secondary": "#fb923c",
                    "text": "#1f2937",
                    "background": "#ffffff"
                },
                "typography": {
                    "primary_font": "'Open Sans', 'Arial', sans-serif",
                    "heading_sizes": {"h1": "2.8em", "h2": "2.1em", "h3": "1.6em"},
                    "line_height": "1.6"
                },
                "layout": {"spacing": "舒适", "alignment": "居中"},
                "image_design": {
                    "border_radius": "10px",
                    "shadow": "0 6px 20px rgba(234,88,12,0.15)",
                    "max_width": "100%"
                },
                "tags": ["产品", "介绍", "营销", "友好"]
            })
        }
        
        self.templates = default_templates
        return default_templates
    
    def save_templates(self):
        """保存模板到文件"""
        try:
            templates_data = {}
            for name, template in self.templates.items():
                templates_data[name] = template.to_dict()
            
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(templates_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存模板失败: {e}")
    
    def get_template(self, name: str) -> Optional[DocumentTemplate]:
        """获取指定模板"""
        return self.templates.get(name)
    
    def list_templates(self, category: str = None) -> List[DocumentTemplate]:
        """列出模板"""
        templates = list(self.templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
        
        return sorted(templates, key=lambda x: x.usage_count, reverse=True)
    
    def search_templates(self, query: str) -> List[DocumentTemplate]:
        """搜索模板"""
        query = query.lower()
        results = []
        
        for template in self.templates.values():
            # 搜索名称、描述、标签
            if (query in template.name.lower() or 
                query in template.description.lower() or 
                any(query in tag.lower() for tag in template.tags)):
                results.append(template)
        
        return results
    
    def create_template(self, template_data: Dict[str, Any]) -> bool:
        """创建新模板"""
        try:
            name = template_data.get("name")
            if not name:
                return False
            
            if name in self.templates:
                print(f"模板 '{name}' 已存在")
                return False
            
            template = DocumentTemplate(template_data)
            self.templates[name] = template
            self.save_templates()
            return True
        except Exception as e:
            print(f"创建模板失败: {e}")
            return False
    
    def update_template(self, name: str, template_data: Dict[str, Any]) -> bool:
        """更新模板"""
        try:
            if name not in self.templates:
                return False
            
            template_data["updated_at"] = datetime.now().isoformat()
            self.templates[name] = DocumentTemplate(template_data)
            self.save_templates()
            return True
        except Exception as e:
            print(f"更新模板失败: {e}")
            return False
    
    def delete_template(self, name: str) -> bool:
        """删除模板"""
        try:
            if name in self.templates:
                del self.templates[name]
                self.save_templates()
                return True
            return False
        except Exception as e:
            print(f"删除模板失败: {e}")
            return False
    
    def use_template(self, name: str) -> bool:
        """使用模板（增加使用计数）"""
        template = self.get_template(name)
        if template:
            template.usage_count += 1
            template.updated_at = datetime.now().isoformat()
            self.save_templates()
            return True
        return False
    
    def rate_template(self, name: str, rating: float) -> bool:
        """评价模板"""
        template = self.get_template(name)
        if template and 0 <= rating <= 5:
            # 简单的评分更新（实际应用中可能需要更复杂的算法）
            template.rating = (template.rating + rating) / 2
            self.save_templates()
            return True
        return False
    
    def get_categories(self) -> List[str]:
        """获取所有模板分类"""
        categories = set()
        for template in self.templates.values():
            categories.add(template.category)
        return sorted(list(categories))
    
    def export_template(self, name: str, format: str = "json") -> Optional[str]:
        """导出模板"""
        template = self.get_template(name)
        if not template:
            return None
        
        try:
            if format.lower() == "json":
                return json.dumps(template.to_dict(), ensure_ascii=False, indent=2)
            elif format.lower() == "yaml":
                return yaml.dump(template.to_dict(), allow_unicode=True, default_flow_style=False)
            else:
                return None
        except Exception as e:
            print(f"导出模板失败: {e}")
            return None
    
    def import_template(self, template_data: str, format: str = "json") -> bool:
        """导入模板"""
        try:
            if format.lower() == "json":
                data = json.loads(template_data)
            elif format.lower() == "yaml":
                data = yaml.safe_load(template_data)
            else:
                return False
            
            return self.create_template(data)
        except Exception as e:
            print(f"导入模板失败: {e}")
            return False

class SmartTemplateRecommender:
    """智能模板推荐器"""
    
    def __init__(self, template_manager: TemplateManager):
        self.template_manager = template_manager
    
    def recommend_templates(self, content: str, user_instruction: str = "") -> List[Dict[str, Any]]:
        """基于内容和用户指令推荐模板"""
        recommendations = []
        
        # 分析内容特征
        content_features = self._analyze_content_features(content)
        
        # 分析用户指令
        instruction_features = self._analyze_instruction_features(user_instruction)
        
        # 为每个模板计算匹配分数
        for template in self.template_manager.list_templates():
            score = self._calculate_match_score(template, content_features, instruction_features)
            
            if score > 0.3:  # 最低匹配阈值
                recommendations.append({
                    "template": template,
                    "score": score,
                    "reasons": self._get_recommendation_reasons(template, content_features, instruction_features)
                })
        
        # 按分数排序
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return recommendations[:5]  # 返回前5个推荐
    
    def _analyze_content_features(self, content: str) -> Dict[str, Any]:
        """分析内容特征"""
        features = {
            "length": len(content),
            "has_code": "```" in content or "`" in content,
            "has_images": "![" in content,
            "has_tables": "|" in content and "---" in content,
            "title_count": len([line for line in content.split('\n') if line.strip().startswith('#')]),
            "list_count": len([line for line in content.split('\n') if line.strip().startswith(('-', '*', '+'))]),
            "formal_tone": self._detect_formal_tone(content),
            "technical_content": self._detect_technical_content(content)
        }
        
        return features
    
    def _analyze_instruction_features(self, instruction: str) -> Dict[str, Any]:
        """分析用户指令特征"""
        instruction_lower = instruction.lower()
        
        features = {
            "business_style": any(word in instruction_lower for word in ["商务", "企业", "专业", "business"]),
            "academic_style": any(word in instruction_lower for word in ["学术", "论文", "研究", "academic"]),
            "creative_style": any(word in instruction_lower for word in ["创意", "设计", "艺术", "creative"]),
            "technical_style": any(word in instruction_lower for word in ["技术", "开发", "代码", "technical"]),
            "product_style": any(word in instruction_lower for word in ["产品", "介绍", "营销", "product"]),
            "color_preference": self._extract_color_preference(instruction),
            "format_preference": self._extract_format_preference(instruction)
        }
        
        return features
    
    def _detect_formal_tone(self, content: str) -> bool:
        """检测正式语调"""
        formal_indicators = ["根据", "因此", "综上所述", "总结", "分析", "研究表明"]
        return any(indicator in content for indicator in formal_indicators)
    
    def _detect_technical_content(self, content: str) -> bool:
        """检测技术内容"""
        technical_indicators = ["代码", "算法", "API", "函数", "class", "def", "import", "技术"]
        return any(indicator in content for indicator in technical_indicators)
    
    def _extract_color_preference(self, instruction: str) -> str:
        """提取颜色偏好"""
        color_keywords = {
            "蓝": "blue",
            "红": "red", 
            "绿": "green",
            "紫": "purple",
            "橙": "orange",
            "黑": "black",
            "灰": "gray"
        }
        
        for color_cn, color_en in color_keywords.items():
            if color_cn in instruction or color_en in instruction.lower():
                return color_en
        
        return ""
    
    def _extract_format_preference(self, instruction: str) -> str:
        """提取格式偏好"""
        format_keywords = ["PDF", "HTML", "Word", "PowerPoint", "Markdown"]
        
        for fmt in format_keywords:
            if fmt.lower() in instruction.lower():
                return fmt
        
        return ""
    
    def _calculate_match_score(self, template: DocumentTemplate, 
                              content_features: Dict[str, Any], 
                              instruction_features: Dict[str, Any]) -> float:
        """计算模板匹配分数"""
        score = 0.0
        
        # 基于模板类别的匹配
        if template.category == "商务" and instruction_features.get("business_style"):
            score += 0.4
        elif template.category == "学术" and instruction_features.get("academic_style"):
            score += 0.4
        elif template.category == "设计" and instruction_features.get("creative_style"):
            score += 0.4
        elif template.category == "技术" and instruction_features.get("technical_style"):
            score += 0.4
        elif template.category == "营销" and instruction_features.get("product_style"):
            score += 0.4
        
        # 基于内容特征的匹配
        if content_features.get("has_code") and template.category == "技术":
            score += 0.2
        
        if content_features.get("formal_tone") and template.category in ["商务", "学术"]:
            score += 0.2
        
        if content_features.get("technical_content") and template.category == "技术":
            score += 0.2
        
        # 基于使用频率的加分
        if template.usage_count > 10:
            score += 0.1
        
        # 基于评分的加分
        if template.rating > 4.0:
            score += 0.1
        
        return min(score, 1.0)  # 最大分数为1.0
    
    def _get_recommendation_reasons(self, template: DocumentTemplate, 
                                   content_features: Dict[str, Any], 
                                   instruction_features: Dict[str, Any]) -> List[str]:
        """获取推荐原因"""
        reasons = []
        
        if template.category == "商务" and instruction_features.get("business_style"):
            reasons.append("适合商务风格需求")
        
        if template.category == "学术" and instruction_features.get("academic_style"):
            reasons.append("符合学术论文格式")
        
        if content_features.get("has_code") and template.category == "技术":
            reasons.append("适合包含代码的技术文档")
        
        if template.usage_count > 10:
            reasons.append("受用户欢迎的模板")
        
        if template.rating > 4.0:
            reasons.append("高评分模板")
        
        if not reasons:
            reasons.append("通用模板，适合多种场景")
        
        return reasons

# 便捷函数
def get_template_manager() -> TemplateManager:
    """获取模板管理器实例"""
    return TemplateManager()

def recommend_templates_for_content(content: str, instruction: str = "") -> List[Dict[str, Any]]:
    """为内容推荐模板的便捷函数"""
    manager = get_template_manager()
    recommender = SmartTemplateRecommender(manager)
    return recommender.recommend_templates(content, instruction)

if __name__ == "__main__":
    # 测试模板管理功能
    manager = TemplateManager()
    
    print("=== 模板管理系统测试 ===")
    print(f"可用模板数量: {len(manager.templates)}")
    
    # 列出所有模板
    templates = manager.list_templates()
    for template in templates:
        print(f"- {template.name}: {template.description}")
    
    # 测试推荐功能
    recommender = SmartTemplateRecommender(manager)
    test_content = """
# 技术文档

## API接口说明

这是一个RESTful API的技术文档。

```python
def get_user(user_id):
    return user
```
"""
    
    recommendations = recommender.recommend_templates(test_content, "技术文档格式")
    print(f"\n推荐模板:")
    for rec in recommendations:
        print(f"- {rec['template'].name} (分数: {rec['score']:.2f})")
        print(f"  原因: {', '.join(rec['reasons'])}")