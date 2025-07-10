#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
异步LLM调用池 - 高性能LLM调用管理
支持连接池、智能缓存、速率限制、故障转移
"""

import asyncio
import aiohttp
import hashlib
import json
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from contextlib import asynccontextmanager
import psutil
import os

logger = logging.getLogger(__name__)

@dataclass
class LLMResponse:
    """LLM响应结果"""
    content: str
    model: str
    tokens_used: int
    response_time: float
    from_cache: bool = False
    cost_estimate: float = 0.0

@dataclass
class LLMStats:
    """LLM调用统计"""
    total_requests: int = 0
    cache_hits: int = 0
    failures: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    avg_response_time: float = 0.0

class AsyncLLMPool:
    """高性能异步LLM调用池"""
    
    def __init__(self, 
                 max_connections: int = 20,
                 cache_size: int = 1000,
                 cache_ttl: int = 3600,
                 rate_limit: int = 60,
                 max_retries: int = 3):
        
        self.max_connections = max_connections
        self.cache_size = cache_size
        self.cache_ttl = cache_ttl
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        
        # 缓存系统
        self.cache: Dict[str, tuple] = {}
        
        # 速率限制
        self.rate_semaphore = asyncio.Semaphore(rate_limit)
        self.request_times: List[float] = []
        
        # 连接池
        self.connector = None
        self.session = None
        
        # 统计信息
        self.stats = LLMStats()
        
        # 支持的模型配置
        self.model_config = {
            "gpt-4o": {"cost_per_1k": 0.005, "max_tokens": 4096},
            "gpt-4o-mini": {"cost_per_1k": 0.0015, "max_tokens": 4096},
            "gpt-3.5-turbo": {"cost_per_1k": 0.001, "max_tokens": 4096}
        }
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.connector = aiohttp.TCPConnector(
            limit=self.max_connections,
            limit_per_host=self.max_connections,
            enable_cleanup_closed=True
        )
        timeout = aiohttp.ClientTimeout(total=60, connect=10)
        self.session = aiohttp.ClientSession(
            connector=self.connector,
            timeout=timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
        if self.connector:
            await self.connector.close()
    
    def _get_cache_key(self, prompt: str, model: str, **kwargs) -> str:
        """生成缓存键"""
        # 排除非确定性参数
        cache_params = {k: v for k, v in kwargs.items() 
                       if k not in ['stream', 'user']}
        
        cache_data = {
            "prompt": prompt,
            "model": model,
            **cache_params
        }
        
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[LLMResponse]:
        """获取缓存的响应"""
        if cache_key in self.cache:
            response, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                # 创建新的响应对象并标记为缓存
                cached_response = LLMResponse(
                    content=response.content,
                    model=response.model,
                    tokens_used=response.tokens_used,
                    response_time=response.response_time,
                    from_cache=True,
                    cost_estimate=response.cost_estimate
                )
                self.stats.cache_hits += 1
                return cached_response
            else:
                # 缓存过期，删除
                del self.cache[cache_key]
        return None
    
    def _cache_response(self, cache_key: str, response: LLMResponse):
        """缓存响应 - LRU策略"""
        if len(self.cache) >= self.cache_size:
            # 删除最旧的条目
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        self.cache[cache_key] = (response, time.time())
    
    async def _wait_for_rate_limit(self):
        """智能速率限制"""
        now = time.time()
        
        # 清理超过1分钟的请求记录
        self.request_times = [t for t in self.request_times 
                            if now - t < 60]
        
        # 检查是否超过速率限制
        if len(self.request_times) >= self.rate_limit:
            sleep_time = 60 - (now - self.request_times[0])
            if sleep_time > 0:
                logger.info(f"Rate limit reached, sleeping for {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
        
        self.request_times.append(now)
    
    def _calculate_cost(self, model: str, tokens: int) -> float:
        """计算API调用成本"""
        if model in self.model_config:
            cost_per_1k = self.model_config[model]["cost_per_1k"]
            return (tokens / 1000) * cost_per_1k
        return 0.0
    
    async def call_llm_async(self, 
                           prompt: str, 
                           model: str = "gpt-4o-mini",
                           max_tokens: int = 3000,
                           temperature: float = 0.7,
                           **kwargs) -> LLMResponse:
        """异步调用LLM"""
        start_time = time.time()
        
        # 生成缓存键
        cache_key = self._get_cache_key(
            prompt, model, max_tokens=max_tokens, 
            temperature=temperature, **kwargs
        )
        
        # 检查缓存
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            logger.debug(f"Cache hit for prompt: {prompt[:50]}...")
            return cached_response
        
        # 速率限制
        await self._wait_for_rate_limit()
        
        # 使用信号量限制并发
        async with self.rate_semaphore:
            # 重试机制
            last_error = None
            for attempt in range(self.max_retries):
                try:
                    response_data = await self._make_llm_request(
                        prompt, model, max_tokens, temperature, **kwargs
                    )
                    
                    # 计算响应时间和成本
                    response_time = time.time() - start_time
                    cost = self._calculate_cost(model, response_data.get("tokens_used", 0))
                    
                    # 创建响应对象
                    llm_response = LLMResponse(
                        content=response_data["content"],
                        model=model,
                        tokens_used=response_data.get("tokens_used", 0),
                        response_time=response_time,
                        cost_estimate=cost
                    )
                    
                    # 缓存结果
                    self._cache_response(cache_key, llm_response)
                    
                    # 更新统计
                    self._update_stats(llm_response, success=True)
                    
                    logger.debug(f"LLM call successful in {response_time:.2f}s, "
                               f"tokens: {llm_response.tokens_used}, "
                               f"cost: ${cost:.4f}")
                    
                    return llm_response
                    
                except Exception as e:
                    last_error = e
                    logger.warning(f"LLM调用失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                    
                    if attempt < self.max_retries - 1:
                        # 指数退避
                        sleep_time = (2 ** attempt) + (time.time() % 1)
                        await asyncio.sleep(sleep_time)
            
            # 所有重试都失败
            self.stats.failures += 1
            logger.error(f"LLM调用最终失败: {last_error}")
            raise last_error
    
    async def _make_llm_request(self, prompt: str, model: str, max_tokens: int, 
                              temperature: float, **kwargs) -> Dict[str, Any]:
        """实际的LLM API调用"""
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError("需要安装 openai 库: pip install openai")
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("未设置 OPENAI_API_KEY 环境变量")
        
        client = AsyncOpenAI(api_key=api_key)
        
        # 构建消息
        messages = [{"role": "user", "content": prompt}]
        if "system" in kwargs:
            messages.insert(0, {"role": "system", "content": kwargs.pop("system")})
        
        # API调用
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        
        return {
            "content": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens if response.usage else 0
        }
    
    async def batch_call_llm_async(self, 
                                 prompts: List[str],
                                 model: str = "gpt-4o-mini",
                                 max_tokens: int = 3000,
                                 temperature: float = 0.7,
                                 max_concurrent: int = 5,
                                 **kwargs) -> List[LLMResponse]:
        """批量异步调用LLM"""
        if not prompts:
            return []
        
        # 创建并发限制信号量
        concurrent_semaphore = asyncio.Semaphore(max_concurrent)
        
        async def limited_call(prompt):
            async with concurrent_semaphore:
                return await self.call_llm_async(
                    prompt, model, max_tokens, temperature, **kwargs
                )
        
        # 并发执行所有任务
        logger.info(f"开始批量处理 {len(prompts)} 个请求，并发数: {max_concurrent}")
        start_time = time.time()
        
        try:
            responses = await asyncio.gather(
                *[limited_call(prompt) for prompt in prompts],
                return_exceptions=True
            )
            
            # 处理异常
            successful_responses = []
            failed_count = 0
            
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    logger.error(f"批量请求 {i} 失败: {response}")
                    failed_count += 1
                    # 可以选择添加默认响应或者跳过
                    successful_responses.append(LLMResponse(
                        content=f"处理失败: {str(response)}",
                        model=model,
                        tokens_used=0,
                        response_time=0,
                        from_cache=False
                    ))
                else:
                    successful_responses.append(response)
            
            total_time = time.time() - start_time
            logger.info(f"批量处理完成: {len(successful_responses) - failed_count}/"
                       f"{len(prompts)} 成功，耗时 {total_time:.2f}s")
            
            return successful_responses
            
        except Exception as e:
            logger.error(f"批量处理发生异常: {e}")
            raise
    
    def _update_stats(self, response: LLMResponse, success: bool = True):
        """更新统计信息"""
        self.stats.total_requests += 1
        
        if success:
            self.stats.total_tokens += response.tokens_used
            self.stats.total_cost += response.cost_estimate
            
            # 更新平均响应时间
            if not response.from_cache:
                current_avg = self.stats.avg_response_time
                total_non_cached = self.stats.total_requests - self.stats.cache_hits
                
                if total_non_cached > 0:
                    self.stats.avg_response_time = (
                        (current_avg * (total_non_cached - 1) + response.response_time) /
                        total_non_cached
                    )
    
    def get_stats(self) -> Dict[str, Any]:
        """获取详细统计信息"""
        cache_hit_rate = (self.stats.cache_hits / max(1, self.stats.total_requests)) * 100
        failure_rate = (self.stats.failures / max(1, self.stats.total_requests)) * 100
        
        return {
            "total_requests": self.stats.total_requests,
            "cache_hits": self.stats.cache_hits,
            "cache_hit_rate": f"{cache_hit_rate:.2f}%",
            "failures": self.stats.failures,
            "failure_rate": f"{failure_rate:.2f}%",
            "total_tokens": self.stats.total_tokens,
            "total_cost": f"${self.stats.total_cost:.4f}",
            "avg_response_time": f"{self.stats.avg_response_time:.2f}s",
            "cached_items": len(self.cache),
            "memory_usage": f"{psutil.Process().memory_info().rss / 1024 / 1024:.2f}MB"
        }
    
    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        logger.info("LLM缓存已清空")
    
    def get_cache_size(self) -> int:
        """获取当前缓存大小"""
        return len(self.cache)

# 全局单例实例
_global_llm_pool = None

async def get_global_llm_pool() -> AsyncLLMPool:
    """获取全局LLM池实例"""
    global _global_llm_pool
    if _global_llm_pool is None:
        _global_llm_pool = AsyncLLMPool()
        await _global_llm_pool.__aenter__()
    return _global_llm_pool

async def call_llm_async(prompt: str, **kwargs) -> str:
    """便捷的异步LLM调用函数"""
    pool = await get_global_llm_pool()
    response = await pool.call_llm_async(prompt, **kwargs)
    return response.content

async def batch_call_llm_async(prompts: List[str], **kwargs) -> List[str]:
    """便捷的批量异步LLM调用函数"""
    pool = await get_global_llm_pool()
    responses = await pool.batch_call_llm_async(prompts, **kwargs)
    return [response.content for response in responses]

async def get_llm_stats() -> Dict[str, Any]:
    """获取LLM调用统计信息"""
    pool = await get_global_llm_pool()
    return pool.get_stats()

async def clear_llm_cache():
    """清空LLM缓存"""
    pool = await get_global_llm_pool()
    pool.clear_cache()

if __name__ == "__main__":
    async def test_async_llm_pool():
        """测试异步LLM池"""
        async with AsyncLLMPool(rate_limit=10) as pool:
            print("🧪 测试异步LLM调用池")
            
            # 单个调用测试
            print("\n📞 测试单个调用...")
            response = await pool.call_llm_async(
                "请用一句话介绍Python编程语言", 
                model="gpt-4o-mini"
            )
            print(f"响应: {response.content}")
            print(f"耗时: {response.response_time:.2f}s")
            print(f"Tokens: {response.tokens_used}")
            print(f"成本: ${response.cost_estimate:.4f}")
            
            # 缓存测试
            print("\n💾 测试缓存功能...")
            cached_response = await pool.call_llm_async(
                "请用一句话介绍Python编程语言", 
                model="gpt-4o-mini"
            )
            print(f"缓存命中: {cached_response.from_cache}")
            print(f"响应时间: {cached_response.response_time:.2f}s")
            
            # 批量调用测试
            print("\n📦 测试批量调用...")
            prompts = [
                "介绍机器学习的基本概念",
                "解释深度学习和传统机器学习的区别", 
                "描述人工智能在医疗领域的应用"
            ]
            
            batch_responses = await pool.batch_call_llm_async(
                prompts, 
                model="gpt-4o-mini",
                max_concurrent=2
            )
            
            for i, response in enumerate(batch_responses):
                print(f"批量响应 {i+1}: {response.content[:50]}...")
                print(f"  耗时: {response.response_time:.2f}s, Tokens: {response.tokens_used}")
            
            # 统计信息
            print("\n📊 统计信息:")
            stats = pool.get_stats()
            for key, value in stats.items():
                print(f"  {key}: {value}")
    
    # 运行测试
    asyncio.run(test_async_llm_pool())