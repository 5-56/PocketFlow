#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能代理系统 - 动态决策与自适应处理
基于PocketFlow Agent模式实现的智能文档处理代理
"""

import asyncio
import json
import yaml
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from pocketflow import AsyncNode

from utils.async_llm_pool import call_llm_async, batch_call_llm_async

logger = logging.getLogger(__name__)

class ProcessingAction(Enum):
    """处理行动枚举"""
    ANALYZE_DEEPER = "analyze_deeper"
    OPTIMIZE_CONTENT = "optimize_content"
    ENHANCE_DESIGN = "enhance_design"
    PROCESS_IMAGES = "process_images"
    GENERATE_OUTPUT = "generate_output"
    REFINE_QUALITY = "refine_quality"
    SWITCH_STRATEGY = "switch_strategy"
    REQUEST_FEEDBACK = "request_feedback"
    COMPLETE_TASK = "complete_task"

@dataclass
class AgentContext:
    """代理上下文数据"""
    current_stage: str
    user_instruction: str
    document_content: str
    processing_history: List[Dict[str, Any]]
    quality_metrics: Dict[str, float]
    time_constraints: Optional[float]
    user_feedback: Optional[str]
    error_count: int = 0
    iteration_count: int = 0

@dataclass
class AgentDecision:
    """代理决策结果"""
    action: ProcessingAction
    reasoning: str
    parameters: Dict[str, Any]
    confidence: float
    expected_improvement: float
    estimated_time: float

class IntelligentDocumentAgent(AsyncNode):
    """智能文档处理代理"""
    
    def __init__(self, max_iterations: int = 5, quality_threshold: float = 0.8):
        super().__init__()
        self.max_iterations = max_iterations
        self.quality_threshold = quality_threshold
        self.decision_history = []
        
    async def prep_async(self, shared):
        """准备代理上下文"""
        # 收集当前处理状态
        context = AgentContext(
            current_stage=self._determine_current_stage(shared),
            user_instruction=shared.get("user_instruction", ""),
            document_content=shared.get("original_document", ""),
            processing_history=shared.get("processing_history", []),
            quality_metrics=self._calculate_quality_metrics(shared),
            time_constraints=shared.get("time_constraints"),
            user_feedback=shared.get("user_feedback"),
            iteration_count=shared.get("agent_iteration_count", 0)
        )
        
        return context
    
    async def exec_async(self, context: AgentContext) -> AgentDecision:
        """执行智能决策"""
        logger.info(f"代理决策 - 阶段: {context.current_stage}, 迭代: {context.iteration_count}")
        
        # 构建决策提示词
        decision_prompt = self._build_decision_prompt(context)
        
        try:
            # 调用LLM进行决策
            decision_result = await call_llm_async(
                decision_prompt,
                model="gpt-4o",  # 使用更强大的模型进行决策
                temperature=0.3,
                max_tokens=2000
            )
            
            # 解析决策结果
            decision = self._parse_decision(decision_result, context)
            
            # 记录决策历史
            self.decision_history.append({
                "iteration": context.iteration_count,
                "stage": context.current_stage,
                "decision": decision,
                "timestamp": asyncio.get_event_loop().time()
            })
            
            logger.info(f"代理决策: {decision.action.value} (置信度: {decision.confidence:.2f})")
            
            return decision
            
        except Exception as e:
            logger.error(f"代理决策失败: {e}")
            # 返回安全的默认决策
            return self._get_fallback_decision(context)
    
    async def post_async(self, shared, prep_res: AgentContext, exec_res: AgentDecision):
        """执行决策并更新状态"""
        decision = exec_res
        context = prep_res
        
        # 更新迭代计数
        shared["agent_iteration_count"] = context.iteration_count + 1
        
        # 记录决策到处理历史
        if "processing_history" not in shared:
            shared["processing_history"] = []
        
        shared["processing_history"].append({
            "stage": context.current_stage,
            "action": decision.action.value,
            "reasoning": decision.reasoning,
            "confidence": decision.confidence,
            "parameters": decision.parameters,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # 更新代理状态
        shared["agent_state"] = {
            "current_action": decision.action.value,
            "confidence": decision.confidence,
            "expected_improvement": decision.expected_improvement,
            "total_iterations": context.iteration_count + 1
        }
        
        # 根据决策返回对应的动作
        return decision.action.value
    
    def _determine_current_stage(self, shared: Dict[str, Any]) -> str:
        """确定当前处理阶段"""
        if "final_document" in shared:
            return "completion"
        elif "processed_text" in shared:
            return "post_processing"
        elif "layout_design" in shared:
            return "content_processing"
        elif "document_structure" in shared:
            return "design_phase"
        elif "requirements" in shared:
            return "analysis_phase"
        else:
            return "initialization"
    
    def _calculate_quality_metrics(self, shared: Dict[str, Any]) -> Dict[str, float]:
        """计算当前质量指标"""
        metrics = {
            "completeness": 0.0,
            "quality": 0.0,
            "user_satisfaction": 0.0,
            "efficiency": 0.0
        }
        
        # 计算完整性
        stages = ["requirements", "document_structure", "layout_design", "processed_text", "final_document"]
        completed_stages = sum(1 for stage in stages if stage in shared)
        metrics["completeness"] = completed_stages / len(stages)
        
        # 从AI分析中获取质量指标
        if "document_structure" in shared:
            ai_insights = shared["document_structure"].get("ai_insights", {})
            if "readability_score" in ai_insights:
                metrics["quality"] = float(ai_insights["readability_score"]) / 100
        
        # 计算效率（基于处理时间）
        workflow_metadata = shared.get("workflow_metadata", {})
        if "total_time" in workflow_metadata:
            # 假设30秒是理想处理时间
            ideal_time = 30.0
            actual_time = workflow_metadata["total_time"]
            metrics["efficiency"] = min(1.0, ideal_time / max(actual_time, 1.0))
        
        return metrics
    
    def _build_decision_prompt(self, context: AgentContext) -> str:
        """构建决策提示词"""
        return f"""
你是一个专业的文档处理智能代理，需要根据当前状态做出最优决策。

### 当前状态
处理阶段: {context.current_stage}
迭代次数: {context.iteration_count}/{self.max_iterations}
用户指令: {context.user_instruction}

### 质量指标
完整性: {context.quality_metrics.get('completeness', 0):.2f}
质量得分: {context.quality_metrics.get('quality', 0):.2f}
效率得分: {context.quality_metrics.get('efficiency', 0):.2f}

### 处理历史
{self._format_processing_history(context.processing_history)}

### 用户反馈
{context.user_feedback or "暂无用户反馈"}

### 可选行动
1. analyze_deeper - 进行更深入的文档分析
2. optimize_content - 优化文档内容和结构  
3. enhance_design - 改进排版设计方案
4. process_images - 处理和优化图片
5. generate_output - 生成最终文档输出
6. refine_quality - 质量优化和润色
7. switch_strategy - 切换处理策略
8. request_feedback - 请求用户反馈
9. complete_task - 完成任务

### 决策要求
请分析当前状态，选择最优的下一步行动。考虑以下因素：
- 当前质量指标是否达到要求（阈值: {self.quality_threshold}）
- 是否还有改进空间
- 时间成本与收益平衡
- 用户需求的满足程度

返回JSON格式的决策：
{{
    "action": "选择的行动",
    "reasoning": "详细的决策理由",
    "parameters": {{
        "focus_areas": ["需要关注的具体方面"],
        "priority_level": "high/medium/low",
        "expected_duration": "预估时间（秒）"
    }},
    "confidence": "决策置信度 0-1",
    "expected_improvement": "预期改进幅度 0-1",
    "estimated_time": "预估执行时间（秒）"
}}
"""
    
    def _format_processing_history(self, history: List[Dict[str, Any]]) -> str:
        """格式化处理历史"""
        if not history:
            return "无处理历史"
        
        formatted = []
        for i, record in enumerate(history[-3:], 1):  # 只显示最近3条
            formatted.append(f"{i}. {record.get('stage', 'Unknown')} -> {record.get('action', 'Unknown')}")
        
        return "\n".join(formatted)
    
    def _parse_decision(self, decision_result: str, context: AgentContext) -> AgentDecision:
        """解析LLM决策结果"""
        try:
            if "```json" in decision_result:
                json_str = decision_result.split("```json")[1].split("```")[0].strip()
            else:
                json_str = decision_result
            
            decision_data = json.loads(json_str)
            
            # 验证行动类型
            action_str = decision_data.get("action", "complete_task")
            try:
                action = ProcessingAction(action_str)
            except ValueError:
                logger.warning(f"无效的行动类型: {action_str}, 使用默认行动")
                action = ProcessingAction.COMPLETE_TASK
            
            return AgentDecision(
                action=action,
                reasoning=decision_data.get("reasoning", "默认决策"),
                parameters=decision_data.get("parameters", {}),
                confidence=float(decision_data.get("confidence", 0.5)),
                expected_improvement=float(decision_data.get("expected_improvement", 0.1)),
                estimated_time=float(decision_data.get("estimated_time", 10.0))
            )
            
        except Exception as e:
            logger.error(f"决策解析失败: {e}")
            return self._get_fallback_decision(context)
    
    def _get_fallback_decision(self, context: AgentContext) -> AgentDecision:
        """获取fallback决策"""
        # 根据当前阶段和质量指标决定fallback行动
        if context.iteration_count >= self.max_iterations:
            action = ProcessingAction.COMPLETE_TASK
        elif context.quality_metrics.get("completeness", 0) < 0.5:
            action = ProcessingAction.ANALYZE_DEEPER
        elif context.quality_metrics.get("quality", 0) < self.quality_threshold:
            action = ProcessingAction.OPTIMIZE_CONTENT
        else:
            action = ProcessingAction.GENERATE_OUTPUT
        
        return AgentDecision(
            action=action,
            reasoning="使用fallback决策逻辑",
            parameters={"priority_level": "medium"},
            confidence=0.6,
            expected_improvement=0.2,
            estimated_time=15.0
        )

class AdaptiveProcessingAgent(AsyncNode):
    """自适应处理代理 - 根据实时反馈调整策略"""
    
    def __init__(self):
        super().__init__()
        self.adaptation_history = []
        
    async def prep_async(self, shared):
        """准备自适应分析数据"""
        return {
            "current_results": self._extract_current_results(shared),
            "user_expectations": self._analyze_user_expectations(shared),
            "performance_metrics": self._gather_performance_metrics(shared),
            "error_patterns": self._identify_error_patterns(shared)
        }
    
    async def exec_async(self, prep_res):
        """执行自适应分析"""
        adaptation_prompt = f"""
作为自适应处理专家，请分析当前处理结果并提供优化建议：

### 当前结果分析
{json.dumps(prep_res["current_results"], ensure_ascii=False, indent=2)}

### 用户期望
{prep_res["user_expectations"]}

### 性能指标
{json.dumps(prep_res["performance_metrics"], ensure_ascii=False, indent=2)}

### 发现的问题模式
{prep_res["error_patterns"]}

请提供JSON格式的自适应建议：
{{
    "adaptation_needed": "是否需要调整策略 (true/false)",
    "recommended_adjustments": [
        {{
            "component": "需要调整的组件",
            "adjustment": "具体调整内容",
            "priority": "优先级 (high/medium/low)",
            "expected_impact": "预期影响"
        }}
    ],
    "quality_improvements": [
        "质量改进建议列表"
    ],
    "performance_optimizations": [
        "性能优化建议列表"
    ],
    "user_experience_enhancements": [
        "用户体验改进建议列表"
    ]
}}
"""
        
        try:
            result = await call_llm_async(
                adaptation_prompt,
                model="gpt-4o-mini",
                temperature=0.3
            )
            
            if "```json" in result:
                json_str = result.split("```json")[1].split("```")[0].strip()
            else:
                json_str = result
            
            return json.loads(json_str)
            
        except Exception as e:
            logger.error(f"自适应分析失败: {e}")
            return {
                "adaptation_needed": False,
                "recommended_adjustments": [],
                "quality_improvements": ["建议进行手动质量检查"],
                "performance_optimizations": ["建议监控系统性能"],
                "user_experience_enhancements": ["建议收集用户反馈"]
            }
    
    async def post_async(self, shared, prep_res, exec_res):
        """应用自适应调整"""
        adaptation = exec_res
        
        # 记录自适应历史
        self.adaptation_history.append({
            "timestamp": asyncio.get_event_loop().time(),
            "adaptation": adaptation,
            "context": prep_res
        })
        
        # 保存自适应建议
        shared["adaptive_recommendations"] = adaptation
        
        # 如果需要调整，标记系统进入自适应模式
        if adaptation.get("adaptation_needed", False):
            shared["adaptive_mode"] = True
            shared["adaptive_adjustments"] = adaptation.get("recommended_adjustments", [])
            logger.info("系统进入自适应模式，将应用推荐的调整")
            return "adapt"
        else:
            return "continue"
    
    def _extract_current_results(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """提取当前处理结果"""
        return {
            "final_document_available": "final_document" in shared,
            "processing_stages_completed": [
                key for key in ["requirements", "document_structure", "layout_design", 
                              "processed_text", "processed_images"] 
                if key in shared
            ],
            "quality_scores": shared.get("document_structure", {}).get("ai_insights", {}),
            "processing_time": shared.get("workflow_metadata", {}).get("total_time", 0)
        }
    
    def _analyze_user_expectations(self, shared: Dict[str, Any]) -> str:
        """分析用户期望"""
        instruction = shared.get("user_instruction", "")
        requirements = shared.get("requirements", {})
        
        expectations = []
        
        # 从指令中提取期望
        if "高质量" in instruction or "专业" in instruction:
            expectations.append("用户期望高质量输出")
        
        if "快速" in instruction or "急" in instruction:
            expectations.append("用户有时间要求")
        
        # 从需求分析中提取期望
        priority = requirements.get("priority", "medium")
        if priority == "high" or priority == "urgent":
            expectations.append("用户需求优先级高")
        
        return "; ".join(expectations) if expectations else "标准处理期望"
    
    def _gather_performance_metrics(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """收集性能指标"""
        workflow_metadata = shared.get("workflow_metadata", {})
        
        return {
            "execution_time": workflow_metadata.get("total_time", 0),
            "memory_usage": workflow_metadata.get("memory_usage", "unknown"),
            "cache_hit_rate": shared.get("llm_stats", {}).get("cache_hit_rate", "0%"),
            "error_count": shared.get("error_count", 0),
            "retry_count": shared.get("retry_count", 0)
        }
    
    def _identify_error_patterns(self, shared: Dict[str, Any]) -> str:
        """识别错误模式"""
        processing_history = shared.get("processing_history", [])
        error_patterns = []
        
        # 分析处理历史中的问题
        for record in processing_history:
            if "error" in record:
                error_patterns.append(f"阶段 {record.get('stage', 'unknown')} 出现错误")
        
        # 检查质量指标
        ai_insights = shared.get("document_structure", {}).get("ai_insights", {})
        if ai_insights.get("readability_score", 100) < 60:
            error_patterns.append("文档可读性偏低")
        
        if ai_insights.get("structure_quality", 100) < 70:
            error_patterns.append("文档结构质量不足")
        
        return "; ".join(error_patterns) if error_patterns else "未发现明显问题模式"

class QualityAssuranceAgent(AsyncNode):
    """质量保证代理 - 多维度质量检查"""
    
    async def prep_async(self, shared):
        """准备质量检查数据"""
        return {
            "final_document": shared.get("final_document", {}),
            "original_requirements": shared.get("requirements", {}),
            "user_instruction": shared.get("user_instruction", ""),
            "processing_metadata": shared.get("workflow_metadata", {})
        }
    
    async def exec_async(self, prep_res):
        """执行全面质量检查"""
        document = prep_res["final_document"]
        requirements = prep_res["original_requirements"]
        
        if not document.get("content"):
            return {"overall_score": 0, "issues": ["没有可检查的文档内容"]}
        
        # 构建质量检查提示词
        quality_check_prompt = f"""
作为文档质量专家，请对以下文档进行全面的质量评估：

### 原始需求
用户指令: {prep_res["user_instruction"]}
期望风格: {requirements.get("style", "未指定")}
输出格式: {requirements.get("format", "未指定")}

### 生成文档
格式: {document.get("format", "unknown")}
内容长度: {len(document.get("content", ""))}字符

文档内容预览:
{document.get("content", "")[:1000]}...

请从以下维度评估文档质量：

1. **需求符合度** - 是否满足用户需求
2. **格式正确性** - 输出格式是否正确
3. **内容质量** - 文字表达和逻辑结构
4. **视觉设计** - 排版和美观程度
5. **技术实现** - 代码质量和标准化
6. **用户体验** - 整体使用体验

返回JSON格式评估结果：
{{
    "overall_score": "总体评分 0-100",
    "dimension_scores": {{
        "requirement_compliance": "需求符合度 0-100",
        "format_correctness": "格式正确性 0-100", 
        "content_quality": "内容质量 0-100",
        "visual_design": "视觉设计 0-100",
        "technical_quality": "技术质量 0-100",
        "user_experience": "用户体验 0-100"
    }},
    "strengths": ["文档优点列表"],
    "issues": ["发现的问题列表"],
    "improvement_suggestions": ["改进建议列表"],
    "quality_grade": "质量等级 (A/B/C/D/F)"
}}
"""
        
        try:
            result = await call_llm_async(
                quality_check_prompt,
                model="gpt-4o",
                temperature=0.2,
                max_tokens=3000
            )
            
            if "```json" in result:
                json_str = result.split("```json")[1].split("```")[0].strip()
            else:
                json_str = result
            
            quality_report = json.loads(json_str)
            
            # 验证和标准化分数
            overall_score = float(quality_report.get("overall_score", 0))
            quality_report["overall_score"] = max(0, min(100, overall_score))
            
            return quality_report
            
        except Exception as e:
            logger.error(f"质量检查失败: {e}")
            return {
                "overall_score": 50,
                "dimension_scores": {},
                "strengths": [],
                "issues": [f"质量检查过程出现错误: {str(e)}"],
                "improvement_suggestions": ["建议手动检查文档质量"],
                "quality_grade": "C"
            }
    
    async def post_async(self, shared, prep_res, exec_res):
        """保存质量检查结果"""
        quality_report = exec_res
        shared["quality_assurance_report"] = quality_report
        
        overall_score = quality_report.get("overall_score", 0)
        quality_grade = quality_report.get("quality_grade", "C")
        
        logger.info(f"质量检查完成: 总分 {overall_score}/100, 等级 {quality_grade}")
        
        # 根据质量分数决定下一步行动
        if overall_score >= 90:
            return "excellent"
        elif overall_score >= 75:
            return "good"
        elif overall_score >= 60:
            return "acceptable"
        else:
            return "needs_improvement"

# 导出代理类
__all__ = [
    "IntelligentDocumentAgent",
    "AdaptiveProcessingAgent", 
    "QualityAssuranceAgent",
    "ProcessingAction",
    "AgentContext",
    "AgentDecision"
]