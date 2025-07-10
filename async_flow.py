#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
异步文档处理工作流 - 高性能版本
基于PocketFlow AsyncFlow实现的新一代文档处理工作流
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from pocketflow import AsyncFlow, AsyncParallelBatchFlow

# 导入异步节点
from async_nodes import (
    AsyncParseRequirementNode,
    AsyncAnalyzeDocumentNode,
    AsyncDesignLayoutNode,
    AsyncProcessTextNode,
    ParallelImageProcessingNode,
    AsyncGenerateDocumentNode
)

logger = logging.getLogger(__name__)

class DocumentProcessingAsyncFlow(AsyncFlow):
    """文档处理异步工作流"""
    
    def __init__(self, processing_strategy: str = "complete"):
        self.processing_strategy = processing_strategy
        
        # 创建异步节点实例
        self.parse_requirement = AsyncParseRequirementNode(
            max_retries=2, wait=1
        )
        self.analyze_document = AsyncAnalyzeDocumentNode(
            max_retries=2, wait=1
        )
        self.design_layout = AsyncDesignLayoutNode(
            max_retries=3, wait=2
        )
        self.process_text = AsyncProcessTextNode(
            max_retries=2, wait=1
        )
        self.unify_images = ParallelImageProcessingNode(
            max_retries=2, wait=1
        )
        self.generate_document = AsyncGenerateDocumentNode(
            max_retries=2, wait=1
        )
        
        # 根据策略构建不同的工作流
        self._build_workflow()
        
        # 初始化父类
        super().__init__(start=self.parse_requirement)
    
    def _build_workflow(self):
        """根据处理策略构建工作流"""
        if self.processing_strategy == "complete":
            # 完整流程：需求解析 -> 文档分析 -> 设计布局 -> 文本处理 -> 图片处理 -> 文档生成
            self.parse_requirement >> self.analyze_document >> self.design_layout >> self.process_text >> self.unify_images >> self.generate_document
            
        elif self.processing_strategy == "quick":
            # 快速流程：需求解析 -> 设计布局 -> 文本处理 -> 文档生成
            self.parse_requirement >> self.design_layout >> self.process_text >> self.generate_document
            
        elif self.processing_strategy == "text_only":
            # 仅文本处理：需求解析 -> 文本处理 -> 文档生成
            self.parse_requirement >> self.process_text >> self.generate_document
            
        elif self.processing_strategy == "analysis_focus":
            # 分析重点：需求解析 -> 文档分析 -> 设计布局 -> 文档生成
            self.parse_requirement >> self.analyze_document >> self.design_layout >> self.generate_document
            
        else:
            # 默认完整流程
            self.parse_requirement >> self.analyze_document >> self.design_layout >> self.process_text >> self.unify_images >> self.generate_document
    
    async def run_async(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """运行异步工作流"""
        logger.info(f"启动异步文档处理流程: {self.processing_strategy}")
        
        # 添加流程元数据
        shared["workflow_metadata"] = {
            "strategy": self.processing_strategy,
            "start_time": asyncio.get_event_loop().time(),
            "async_mode": True
        }
        
        try:
            # 运行异步流程
            await super().run_async(shared)
            
            # 记录完成时间
            end_time = asyncio.get_event_loop().time()
            shared["workflow_metadata"]["end_time"] = end_time
            shared["workflow_metadata"]["total_time"] = end_time - shared["workflow_metadata"]["start_time"]
            
            logger.info(f"异步流程完成，耗时: {shared['workflow_metadata']['total_time']:.2f}秒")
            
            return shared
            
        except Exception as e:
            logger.error(f"异步流程执行失败: {e}")
            shared["workflow_metadata"]["error"] = str(e)
            raise

class BatchDocumentProcessingFlow(AsyncParallelBatchFlow):
    """批量文档处理异步工作流"""
    
    def __init__(self, processing_strategy: str = "complete", max_concurrent: int = 3):
        self.processing_strategy = processing_strategy
        self.max_concurrent = max_concurrent
        
        # 创建单文档处理流程
        self.single_doc_flow = DocumentProcessingAsyncFlow(processing_strategy)
        
        # 初始化父类
        super().__init__(start=self.single_doc_flow)
    
    async def prep_async(self, shared):
        """准备批量处理参数"""
        documents = shared.get("documents", [])
        
        if not documents:
            logger.warning("没有提供文档进行批量处理")
            return []
        
        # 为每个文档创建参数字典
        batch_params = []
        for i, doc in enumerate(documents):
            doc_params = {
                "document_id": f"doc_{i}",
                "original_document": doc.get("content", ""),
                "file_type": doc.get("file_type", "markdown"),
                "user_instruction": shared.get("user_instruction", ""),
                "batch_index": i,
                "total_documents": len(documents)
            }
            batch_params.append(doc_params)
        
        logger.info(f"准备批量处理 {len(batch_params)} 个文档")
        return batch_params
    
    async def post_async(self, shared, prep_res, exec_res_list):
        """处理批量结果"""
        successful_docs = []
        failed_docs = []
        
        for i, result in enumerate(exec_res_list):
            if isinstance(result, Exception):
                failed_docs.append({
                    "index": i,
                    "error": str(result)
                })
            else:
                successful_docs.append({
                    "index": i,
                    "result": result.get("final_document", {}),
                    "metadata": result.get("workflow_metadata", {})
                })
        
        # 保存批量处理结果
        shared["batch_results"] = {
            "successful_count": len(successful_docs),
            "failed_count": len(failed_docs),
            "successful_documents": successful_docs,
            "failed_documents": failed_docs,
            "total_processing_time": sum(
                doc["metadata"].get("total_time", 0) for doc in successful_docs
            ),
            "average_processing_time": sum(
                doc["metadata"].get("total_time", 0) for doc in successful_docs
            ) / max(1, len(successful_docs))
        }
        
        logger.info(f"批量处理完成: {len(successful_docs)}/{len(exec_res_list)} 成功")
        return "default"

class IntelligentWorkflowSelector:
    """智能工作流选择器"""
    
    @staticmethod
    async def analyze_requirements(user_instruction: str, document_content: str) -> str:
        """分析需求并推荐最适合的工作流策略"""
        from utils.async_llm_pool import call_llm_async
        
        analysis_prompt = f"""
分析以下用户需求和文档内容，推荐最适合的处理策略：

用户指令: "{user_instruction}"
文档长度: {len(document_content)}字符
文档预览: {document_content[:200]}...

可选策略:
1. complete - 完整处理（适合复杂文档和高质量要求）
2. quick - 快速处理（适合简单需求和时间敏感）
3. text_only - 仅文本处理（适合纯文本优化）
4. analysis_focus - 分析重点（适合需要深度分析的文档）

请根据以下因素推荐策略：
- 用户指令的复杂度
- 文档的长度和复杂性
- 是否涉及图片处理
- 处理质量要求

返回JSON格式：
{{
    "recommended_strategy": "策略名称",
    "reasoning": "推荐理由",
    "estimated_time": "预估处理时间（秒）",
    "confidence": "置信度 0-100"
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
            
            import json
            analysis = json.loads(json_str)
            
            recommended_strategy = analysis.get("recommended_strategy", "complete")
            logger.info(f"智能推荐策略: {recommended_strategy}, 理由: {analysis.get('reasoning', '')}")
            
            return recommended_strategy
            
        except Exception as e:
            logger.warning(f"策略分析失败: {e}, 使用默认策略")
            return "complete"

def create_async_document_flow(strategy: str = "complete") -> DocumentProcessingAsyncFlow:
    """创建异步文档处理工作流"""
    return DocumentProcessingAsyncFlow(strategy)

def create_batch_async_flow(strategy: str = "complete", max_concurrent: int = 3) -> BatchDocumentProcessingFlow:
    """创建批量异步处理工作流"""
    return BatchDocumentProcessingFlow(strategy, max_concurrent)

async def auto_create_optimal_flow(user_instruction: str, document_content: str) -> DocumentProcessingAsyncFlow:
    """自动创建最优工作流"""
    selector = IntelligentWorkflowSelector()
    optimal_strategy = await selector.analyze_requirements(user_instruction, document_content)
    return create_async_document_flow(optimal_strategy)

def get_async_flow_by_type(flow_type: str = "complete", **kwargs) -> DocumentProcessingAsyncFlow:
    """根据类型获取异步工作流"""
    flows = {
        "complete": lambda: create_async_document_flow("complete"),
        "quick": lambda: create_async_document_flow("quick"),
        "text_only": lambda: create_async_document_flow("text_only"),
        "analysis_focus": lambda: create_async_document_flow("analysis_focus"),
        "batch": lambda: create_batch_async_flow(
            kwargs.get("strategy", "complete"), 
            kwargs.get("max_concurrent", 3)
        )
    }
    
    return flows.get(flow_type, flows["complete"])()

# 高级工作流功能
class AdaptiveWorkflow:
    """自适应工作流"""
    
    def __init__(self):
        self.performance_history = []
        self.current_load = 0
    
    async def create_adaptive_flow(self, shared: Dict[str, Any]) -> DocumentProcessingAsyncFlow:
        """根据系统负载和历史性能创建自适应工作流"""
        # 分析当前系统状态
        system_load = await self._analyze_system_load()
        content_complexity = self._analyze_content_complexity(shared)
        
        # 选择最优策略
        if system_load > 0.8:  # 高负载
            strategy = "quick"
        elif content_complexity > 0.7:  # 高复杂度
            strategy = "complete"
        else:
            strategy = "analysis_focus"
        
        logger.info(f"自适应工作流选择策略: {strategy} (负载: {system_load}, 复杂度: {content_complexity})")
        
        return create_async_document_flow(strategy)
    
    async def _analyze_system_load(self) -> float:
        """分析系统负载"""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            
            # 综合CPU和内存使用率
            system_load = (cpu_percent + memory_percent) / 200.0
            return min(system_load, 1.0)
            
        except ImportError:
            return 0.5  # 默认中等负载
    
    def _analyze_content_complexity(self, shared: Dict[str, Any]) -> float:
        """分析内容复杂度"""
        content = shared.get("original_document", "")
        instruction = shared.get("user_instruction", "")
        
        # 简单复杂度评分
        factors = [
            len(content) / 10000,  # 内容长度
            len(instruction.split()) / 50,  # 指令复杂度
            content.count('\n') / 100,  # 结构复杂度
            content.count('![') / 10,  # 图片数量
        ]
        
        complexity = sum(factors) / len(factors)
        return min(complexity, 1.0)

# 流程监控和优化
class WorkflowMonitor:
    """工作流监控器"""
    
    def __init__(self):
        self.metrics = {
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "average_time": 0.0,
            "strategy_performance": {}
        }
    
    async def monitor_flow_execution(self, flow: DocumentProcessingAsyncFlow, shared: Dict[str, Any]):
        """监控工作流执行"""
        start_time = asyncio.get_event_loop().time()
        strategy = flow.processing_strategy
        
        try:
            await flow.run_async(shared)
            
            # 记录成功指标
            execution_time = asyncio.get_event_loop().time() - start_time
            self._record_success(strategy, execution_time)
            
            logger.info(f"工作流监控: {strategy} 策略执行成功，耗时 {execution_time:.2f}s")
            
        except Exception as e:
            # 记录失败指标
            self._record_failure(strategy)
            logger.error(f"工作流监控: {strategy} 策略执行失败 - {e}")
            raise
    
    def _record_success(self, strategy: str, execution_time: float):
        """记录成功执行"""
        self.metrics["total_runs"] += 1
        self.metrics["successful_runs"] += 1
        
        # 更新平均时间
        current_avg = self.metrics["average_time"]
        total_successful = self.metrics["successful_runs"]
        self.metrics["average_time"] = (
            (current_avg * (total_successful - 1) + execution_time) / total_successful
        )
        
        # 更新策略性能
        if strategy not in self.metrics["strategy_performance"]:
            self.metrics["strategy_performance"][strategy] = {
                "runs": 0, "successes": 0, "avg_time": 0.0
            }
        
        strategy_metrics = self.metrics["strategy_performance"][strategy]
        strategy_metrics["runs"] += 1
        strategy_metrics["successes"] += 1
        
        # 更新策略平均时间
        strategy_avg = strategy_metrics["avg_time"]
        strategy_successes = strategy_metrics["successes"]
        strategy_metrics["avg_time"] = (
            (strategy_avg * (strategy_successes - 1) + execution_time) / strategy_successes
        )
    
    def _record_failure(self, strategy: str):
        """记录执行失败"""
        self.metrics["total_runs"] += 1
        self.metrics["failed_runs"] += 1
        
        if strategy not in self.metrics["strategy_performance"]:
            self.metrics["strategy_performance"][strategy] = {
                "runs": 0, "successes": 0, "avg_time": 0.0
            }
        
        self.metrics["strategy_performance"][strategy]["runs"] += 1
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        success_rate = (self.metrics["successful_runs"] / max(1, self.metrics["total_runs"])) * 100
        
        return {
            "overall_metrics": {
                "total_runs": self.metrics["total_runs"],
                "success_rate": f"{success_rate:.2f}%",
                "average_execution_time": f"{self.metrics['average_time']:.2f}s"
            },
            "strategy_performance": self.metrics["strategy_performance"],
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        if self.metrics["total_runs"] < 10:
            recommendations.append("运行次数较少，建议积累更多数据后进行优化")
        
        success_rate = (self.metrics["successful_runs"] / max(1, self.metrics["total_runs"])) * 100
        if success_rate < 90:
            recommendations.append("成功率偏低，建议检查错误处理和重试机制")
        
        if self.metrics["average_time"] > 60:
            recommendations.append("平均执行时间较长，建议优化或使用更快的策略")
        
        # 分析最佳策略
        best_strategy = None
        best_score = 0
        
        for strategy, metrics in self.metrics["strategy_performance"].items():
            if metrics["runs"] > 0:
                success_rate = metrics["successes"] / metrics["runs"]
                time_score = 1 / max(1, metrics["avg_time"])  # 时间越短分数越高
                overall_score = success_rate * time_score
                
                if overall_score > best_score:
                    best_score = overall_score
                    best_strategy = strategy
        
        if best_strategy:
            recommendations.append(f"推荐使用 {best_strategy} 策略以获得最佳性能")
        
        return recommendations

# 全局实例
workflow_monitor = WorkflowMonitor()
adaptive_workflow = AdaptiveWorkflow()

if __name__ == "__main__":
    async def test_async_flows():
        """测试异步工作流"""
        print("🧪 测试异步文档处理工作流")
        
        # 测试数据
        test_shared = {
            "user_instruction": "转换为现代商务风格的HTML文档，图片加圆角边框",
            "original_document": """
# 测试文档

这是一个测试文档，用于验证异步工作流的性能。

## 核心特性

- 异步处理
- 并行执行
- 智能优化

![测试图片](test.jpg)

## 总结

异步工作流大大提升了处理效率。
""",
            "file_type": "markdown"
        }
        
        print("\n📊 测试完整异步流程...")
        complete_flow = create_async_document_flow("complete")
        
        start_time = asyncio.get_event_loop().time()
        await complete_flow.run_async(test_shared.copy())
        complete_time = asyncio.get_event_loop().time() - start_time
        
        print(f"✅ 完整流程耗时: {complete_time:.2f}秒")
        
        print("\n⚡ 测试快速流程...")
        quick_flow = create_async_document_flow("quick")
        
        start_time = asyncio.get_event_loop().time()
        await quick_flow.run_async(test_shared.copy())
        quick_time = asyncio.get_event_loop().time() - start_time
        
        print(f"✅ 快速流程耗时: {quick_time:.2f}秒")
        
        print(f"\n📈 性能对比: 快速流程比完整流程快 {((complete_time - quick_time) / complete_time * 100):.1f}%")
        
        print("\n🤖 测试智能策略选择...")
        optimal_flow = await auto_create_optimal_flow(
            test_shared["user_instruction"],
            test_shared["original_document"]
        )
        print(f"智能选择策略: {optimal_flow.processing_strategy}")
        
        print("\n📊 性能监控报告:")
        print(workflow_monitor.get_performance_report())
    
    # 运行测试
    asyncio.run(test_async_flows())