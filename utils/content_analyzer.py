#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能内容分析和建议系统
提供文档内容的深度分析和优化建议
"""

import re
import json
from typing import Dict, List, Any, Tuple
from utils.call_llm import call_llm, analyze_with_llm
from collections import Counter
import math

class ContentAnalyzer:
    """智能内容分析器"""
    
    def __init__(self):
        self.analysis_cache = {}
        
    def analyze_readability(self, content: str) -> Dict[str, Any]:
        """分析文档可读性"""
        sentences = re.split(r'[.!?。！？]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = re.findall(r'\b\w+\b', content.lower())
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # 基本统计
        word_count = len(words)
        sentence_count = len(sentences)
        paragraph_count = len(paragraphs)
        
        # 平均值计算
        avg_words_per_sentence = word_count / sentence_count if sentence_count > 0 else 0
        avg_sentences_per_paragraph = sentence_count / paragraph_count if paragraph_count > 0 else 0
        
        # 简单的可读性评分（基于句子长度）
        readability_score = self._calculate_readability_score(avg_words_per_sentence)
        
        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "paragraph_count": paragraph_count,
            "avg_words_per_sentence": round(avg_words_per_sentence, 2),
            "avg_sentences_per_paragraph": round(avg_sentences_per_paragraph, 2),
            "readability_score": readability_score,
            "readability_level": self._get_readability_level(readability_score)
        }
    
    def _calculate_readability_score(self, avg_words_per_sentence: float) -> float:
        """计算可读性评分（简化版）"""
        # 基于平均每句话的词数来评估
        if avg_words_per_sentence <= 10:
            return 90  # 很容易阅读
        elif avg_words_per_sentence <= 15:
            return 80  # 容易阅读
        elif avg_words_per_sentence <= 20:
            return 70  # 中等难度
        elif avg_words_per_sentence <= 25:
            return 60  # 稍难阅读
        else:
            return 50  # 难以阅读
    
    def _get_readability_level(self, score: float) -> str:
        """获取可读性等级"""
        if score >= 90:
            return "非常易读"
        elif score >= 80:
            return "易读"
        elif score >= 70:
            return "中等"
        elif score >= 60:
            return "稍难"
        else:
            return "困难"
    
    def analyze_structure(self, content: str) -> Dict[str, Any]:
        """分析文档结构"""
        lines = content.split('\n')
        
        structure = {
            "title_hierarchy": [],
            "content_distribution": {},
            "missing_elements": [],
            "structure_score": 0
        }
        
        # 分析标题层级
        title_pattern = re.compile(r'^(#{1,6})\s+(.+)$')
        current_section_lengths = {}
        current_level = 0
        
        for line in lines:
            line = line.strip()
            title_match = title_pattern.match(line)
            
            if title_match:
                level = len(title_match.group(1))
                title_text = title_match.group(2)
                
                structure["title_hierarchy"].append({
                    "level": level,
                    "title": title_text,
                    "length": len(title_text)
                })
                
                # 检查层级跳跃
                if current_level > 0 and level > current_level + 1:
                    structure["missing_elements"].append(f"标题层级跳跃：从H{current_level}直接到H{level}")
                
                current_level = level
        
        # 计算结构评分
        structure["structure_score"] = self._calculate_structure_score(structure)
        
        return structure
    
    def _calculate_structure_score(self, structure: Dict[str, Any]) -> int:
        """计算结构评分"""
        score = 100
        
        # 检查是否有标题
        if not structure["title_hierarchy"]:
            score -= 30
        
        # 检查标题层级是否合理
        if len(structure["missing_elements"]) > 0:
            score -= len(structure["missing_elements"]) * 10
        
        # 检查标题数量是否适中
        title_count = len(structure["title_hierarchy"])
        if title_count == 0:
            score -= 20
        elif title_count > 10:
            score -= 10  # 过多标题
        
        return max(0, score)
    
    def analyze_content_quality(self, content: str) -> Dict[str, Any]:
        """分析内容质量"""
        # 检查重复内容
        sentences = re.split(r'[.!?。！？]+', content)
        sentence_counts = Counter(sentences)
        duplicate_sentences = [s for s, count in sentence_counts.items() if count > 1 and s.strip()]
        
        # 检查段落长度分布
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        paragraph_lengths = [len(p.split()) for p in paragraphs]
        
        avg_paragraph_length = sum(paragraph_lengths) / len(paragraph_lengths) if paragraph_lengths else 0
        
        # 检查图片文本比例
        image_pattern = re.compile(r'!\[.*?\]\(.*?\)')
        image_count = len(image_pattern.findall(content))
        text_length = len(content.replace('\n', ' ').split())
        
        return {
            "duplicate_sentences": len(duplicate_sentences),
            "avg_paragraph_length": round(avg_paragraph_length, 2),
            "paragraph_length_distribution": {
                "short": len([l for l in paragraph_lengths if l < 50]),
                "medium": len([l for l in paragraph_lengths if 50 <= l <= 150]),
                "long": len([l for l in paragraph_lengths if l > 150])
            },
            "image_to_text_ratio": round(image_count / text_length * 100, 2) if text_length > 0 else 0,
            "image_count": image_count,
            "quality_issues": self._identify_quality_issues(duplicate_sentences, avg_paragraph_length, image_count)
        }
    
    def _identify_quality_issues(self, duplicate_count: int, avg_para_length: float, image_count: int) -> List[str]:
        """识别内容质量问题"""
        issues = []
        
        if duplicate_count > 0:
            issues.append(f"发现{duplicate_count}个重复句子")
        
        if avg_para_length < 20:
            issues.append("段落过短，建议增加内容深度")
        elif avg_para_length > 200:
            issues.append("段落过长，建议分段处理")
        
        if image_count == 0:
            issues.append("缺少图片，建议添加视觉元素")
        elif image_count > 10:
            issues.append("图片过多，可能影响阅读体验")
        
        return issues
    
    def get_optimization_suggestions(self, content: str) -> List[Dict[str, Any]]:
        """获取AI优化建议"""
        # 获取基础分析结果
        readability = self.analyze_readability(content)
        structure = self.analyze_structure(content)
        quality = self.analyze_content_quality(content)
        
        prompt = f"""
作为专业的文档编辑顾问，基于以下分析结果，为文档提供具体的优化建议：

可读性分析：
- 词数: {readability['word_count']}
- 句子数: {readability['sentence_count']}
- 每句平均词数: {readability['avg_words_per_sentence']}
- 可读性等级: {readability['readability_level']}

结构分析：
- 标题数量: {len(structure['title_hierarchy'])}
- 结构评分: {structure['structure_score']}/100
- 结构问题: {structure['missing_elements']}

内容质量：
- 重复句子: {quality['duplicate_sentences']}个
- 平均段落长度: {quality['avg_paragraph_length']}词
- 质量问题: {quality['quality_issues']}

请提供5个具体的优化建议，格式如下：
```json
[
  {{
    "type": "结构优化/内容优化/格式优化",
    "priority": "高/中/低",
    "title": "建议标题",
    "description": "具体描述",
    "action": "具体行动指导"
  }}
]
```
"""
        
        try:
            response = call_llm(prompt)
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
                suggestions = json.loads(json_str)
                return suggestions
        except Exception as e:
            print(f"获取AI建议失败: {e}")
        
        # 返回基础建议
        return self._get_basic_suggestions(readability, structure, quality)
    
    def _get_basic_suggestions(self, readability: Dict, structure: Dict, quality: Dict) -> List[Dict[str, Any]]:
        """生成基础优化建议"""
        suggestions = []
        
        # 可读性建议
        if readability['readability_score'] < 70:
            suggestions.append({
                "type": "内容优化",
                "priority": "高",
                "title": "提高可读性",
                "description": "文档当前可读性较低，建议简化句子结构",
                "action": "将长句拆分为较短的句子，每句控制在15-20个词以内"
            })
        
        # 结构建议
        if structure['structure_score'] < 80:
            suggestions.append({
                "type": "结构优化",
                "priority": "高",
                "title": "改善文档结构",
                "description": "文档结构需要优化以提高逻辑性",
                "action": "检查标题层级，确保逻辑清晰，避免层级跳跃"
            })
        
        # 内容质量建议
        if quality['duplicate_sentences'] > 0:
            suggestions.append({
                "type": "内容优化",
                "priority": "中",
                "title": "消除重复内容",
                "description": f"发现{quality['duplicate_sentences']}个重复句子",
                "action": "检查并删除或改写重复的句子"
            })
        
        # 图片建议
        if quality['image_count'] == 0:
            suggestions.append({
                "type": "格式优化",
                "priority": "中",
                "title": "添加视觉元素",
                "description": "文档缺少图片或图表",
                "action": "在关键章节添加相关图片、图表或示意图"
            })
        
        return suggestions

class SmartContentEnhancer:
    """智能内容增强器"""
    
    def __init__(self):
        self.analyzer = ContentAnalyzer()
    
    def enhance_titles(self, content: str) -> str:
        """智能优化标题"""
        prompt = f"""
请优化以下文档的标题，使其更具吸引力和描述性：

原文档：
{content}

要求：
1. 保持原有的标题层级结构
2. 使标题更简洁、有力
3. 确保标题能准确反映内容
4. 使用吸引人的表达方式

请返回优化后的完整文档。
"""
        
        try:
            return call_llm(prompt)
        except:
            return content
    
    def enhance_readability(self, content: str) -> str:
        """提升可读性"""
        prompt = f"""
请改善以下文档的可读性：

原文档：
{content}

优化要求：
1. 将过长的句子分解为较短的句子
2. 使用更简单易懂的词汇
3. 改善段落结构，确保逻辑清晰
4. 添加过渡句，增强连贯性
5. 保持原有信息的完整性

请返回优化后的文档。
"""
        
        try:
            return call_llm(prompt)
        except:
            return content
    
    def add_visual_elements_suggestions(self, content: str) -> List[Dict[str, str]]:
        """建议添加的视觉元素"""
        prompt = f"""
分析以下文档内容，建议应该添加的图片、图表或其他视觉元素：

文档内容：
{content}

请为每个主要章节建议合适的视觉元素，格式如下：
```json
[
  {{
    "section": "章节名称",
    "type": "图片/图表/流程图/示意图",
    "description": "建议的视觉元素描述",
    "purpose": "添加此视觉元素的目的"
  }}
]
```
"""
        
        try:
            response = call_llm(prompt)
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
        except:
            pass
        
        return []
    
    def generate_summary(self, content: str) -> str:
        """生成文档摘要"""
        prompt = f"""
为以下文档生成一个简洁的摘要（200字以内）：

文档内容：
{content}

摘要要求：
1. 涵盖文档的主要内容
2. 突出关键信息和重点
3. 语言简洁明了
4. 适合作为文档的开头或简介
"""
        
        try:
            return call_llm(prompt)
        except:
            return "无法生成摘要"
    
    def generate_outline(self, content: str) -> str:
        """生成文档大纲"""
        prompt = f"""
为以下文档生成一个详细的大纲：

文档内容：
{content}

大纲要求：
1. 使用Markdown格式
2. 包含主要章节和子章节
3. 体现逻辑层次关系
4. 简洁但完整地覆盖所有要点
"""
        
        try:
            return call_llm(prompt)
        except:
            return "无法生成大纲"

def analyze_document_comprehensive(content: str) -> Dict[str, Any]:
    """综合分析文档"""
    analyzer = ContentAnalyzer()
    enhancer = SmartContentEnhancer()
    
    # 基础分析
    readability = analyzer.analyze_readability(content)
    structure = analyzer.analyze_structure(content)
    quality = analyzer.analyze_content_quality(content)
    
    # 获取优化建议
    suggestions = analyzer.get_optimization_suggestions(content)
    
    # 生成增强内容
    summary = enhancer.generate_summary(content)
    outline = enhancer.generate_outline(content)
    visual_suggestions = enhancer.add_visual_elements_suggestions(content)
    
    return {
        "analysis": {
            "readability": readability,
            "structure": structure,
            "quality": quality
        },
        "suggestions": suggestions,
        "enhancements": {
            "summary": summary,
            "outline": outline,
            "visual_suggestions": visual_suggestions
        },
        "overall_score": calculate_overall_score(readability, structure, quality)
    }

def calculate_overall_score(readability: Dict, structure: Dict, quality: Dict) -> Dict[str, Any]:
    """计算文档整体评分"""
    # 各项权重
    weights = {
        "readability": 0.4,
        "structure": 0.35,
        "quality": 0.25
    }
    
    scores = {
        "readability": readability['readability_score'],
        "structure": structure['structure_score'],
        "quality": max(0, 100 - len(quality['quality_issues']) * 15)
    }
    
    overall = sum(scores[key] * weights[key] for key in scores)
    
    return {
        "overall_score": round(overall, 1),
        "component_scores": scores,
        "grade": get_grade(overall),
        "improvement_areas": [k for k, v in scores.items() if v < 70]
    }

def get_grade(score: float) -> str:
    """根据评分获取等级"""
    if score >= 90:
        return "优秀 (A)"
    elif score >= 80:
        return "良好 (B)"
    elif score >= 70:
        return "中等 (C)"
    elif score >= 60:
        return "及格 (D)"
    else:
        return "需改进 (F)"

if __name__ == "__main__":
    # 测试内容分析功能
    test_content = """
# 测试文档

这是一个测试文档。这是一个测试文档。

## 第一章

这是第一章的内容。内容很长，包含很多信息，需要仔细阅读才能理解，而且句子结构比较复杂，可能会影响阅读体验。

## 第二章

第二章内容。

### 子章节

子章节内容。
"""
    
    result = analyze_document_comprehensive(test_content)
    print(json.dumps(result, ensure_ascii=False, indent=2))