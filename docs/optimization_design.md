import asyncio
import aiohttp
import hashlib
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

@dataclass
class LLMResponse:
    content: str
    model: str
    tokens_used: int
    response_time: float
    from_cache: bool = False

class AsyncLLMPool:
    """异步LLM调用池，支持连接池、缓存、重试等功能"""
    
    def __init__(self, 
                 max_connections: int = 10,
                 cache_size: int = 1000,
                 cache_ttl: int = 3600,
                 rate_limit: int = 60):
        self.max_connections = max_connections
        self.cache_size = cache_size
        self.cache_ttl = cache_ttl
        self.rate_limit = rate_limit
        
        # 缓存系统
        self.cache: Dict[str, tuple] = {}  # key: (response, timestamp)
        
        # 速率限制
        self.rate_limiter = asyncio.Semaphore(rate_limit)
        self.request_times: List[float] = []
        
        # 连接池
        self.connector = None
        self.session = None
        
        # 统计信息
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "failures": 0,
            "avg_response_time": 0.0
        }
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.connector = aiohttp.TCPConnector(
            limit=self.max_connections,
            limit_per_host=self.max_connections
        )
        self.session = aiohttp.ClientSession(connector=self.connector)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
        if self.connector:
            await self.connector.close()
    
    def _get_cache_key(self, prompt: str, model: str, **kwargs) -> str:
        """生成缓存键"""
        cache_data = {
            "prompt": prompt,
            "model": model,
            **kwargs
        }
        return hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[LLMResponse]:
        """获取缓存的响应"""
        if cache_key in self.cache:
            response, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                response.from_cache = True
                self.stats["cache_hits"] += 1
                return response
            else:
                del self.cache[cache_key]
        return None
    
    def _cache_response(self, cache_key: str, response: LLMResponse):
        """缓存响应"""
        # 简单的LRU实现
        if len(self.cache) >= self.cache_size:
            # 删除最旧的条目
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        self.cache[cache_key] = (response, time.time())
    
    async def _wait_for_rate_limit(self):
        """等待速率限制"""
        now = time.time()
        # 清理超过1分钟的请求记录
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        if len(self.request_times) >= self.rate_limit:
            sleep_time = 60 - (now - self.request_times[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        self.request_times.append(now)
    
    async def call_llm_async(self, 
                           prompt: str, 
                           model: str = "gpt-4o",
                           max_tokens: int = 3000,
                           temperature: float = 0.7,
                           max_retries: int = 3,
                           **kwargs) -> LLMResponse:
        """异步调用LLM"""
        start_time = time.time()
        
        # 检查缓存
        cache_key = self._get_cache_key(prompt, model, max_tokens=max_tokens, 
                                      temperature=temperature, **kwargs)
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            return cached_response
        
        # 速率限制
        await self._wait_for_rate_limit()
        
        # 使用信号量限制并发
        async with self.rate_limiter:
            for attempt in range(max_retries):
                try:
                    response = await self._make_llm_request(
                        prompt, model, max_tokens, temperature, **kwargs
                    )
                    
                    # 统计
                    response_time = time.time() - start_time
                    llm_response = LLMResponse(
                        content=response["content"],
                        model=model,
                        tokens_used=response.get("tokens_used", 0),
                        response_time=response_time
                    )
                    
                    # 缓存结果
                    self._cache_response(cache_key, llm_response)
                    
                    # 更新统计
                    self.stats["total_requests"] += 1
                    self.stats["avg_response_time"] = (
                        (self.stats["avg_response_time"] * (self.stats["total_requests"] - 1) + response_time) /
                        self.stats["total_requests"]
                    )
                    
                    return llm_response
                    
                except Exception as e:
                    logger.warning(f"LLM调用失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                    if attempt == max_retries - 1:
                        self.stats["failures"] += 1
                        raise
                    
                    # 指数退避
                    await asyncio.sleep(2 ** attempt)
    
    async def _make_llm_request(self, prompt: str, model: str, max_tokens: int, 
                              temperature: float, **kwargs) -> Dict[str, Any]:
        """实际的LLM API调用"""
        import os
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
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
                                 model: str = "gpt-4o",
                                 max_tokens: int = 3000,
                                 temperature: float = 0.7,
                                 max_concurrent: int = 5) -> List[LLMResponse]:
        """批量异步调用LLM"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def limited_call(prompt):
            async with semaphore:
                return await self.call_llm_async(prompt, model, max_tokens, temperature)
        
        tasks = [limited_call(prompt) for prompt in prompts]
        return await asyncio.gather(*tasks)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        cache_hit_rate = (self.stats["cache_hits"] / max(1, self.stats["total_requests"])) * 100
        failure_rate = (self.stats["failures"] / max(1, self.stats["total_requests"])) * 100
        
        return {
            **self.stats,
            "cache_hit_rate": f"{cache_hit_rate:.2f}%",
            "failure_rate": f"{failure_rate:.2f}%",
            "cached_items": len(self.cache)
        }

# 全局实例
llm_pool = None

async def get_llm_pool() -> AsyncLLMPool:
    """获取全局LLM池实例"""
    global llm_pool
    if llm_pool is None:
        llm_pool = AsyncLLMPool()
        await llm_pool.__aenter__()
    return llm_pool

async def call_llm_async(prompt: str, **kwargs) -> str:
    """便捷的异步LLM调用函数"""
    pool = await get_llm_pool()
    response = await pool.call_llm_async(prompt, **kwargs)
    return response.content

async def batch_call_llm_async(prompts: List[str], **kwargs) -> List[str]:
    """便捷的批量异步LLM调用函数"""
    pool = await get_llm_pool()
    responses = await pool.batch_call_llm_async(prompts, **kwargs)
    return [response.content for response in responses]

if __name__ == "__main__":
    async def test_async_llm():
        async with AsyncLLMPool() as pool:
            # 单个调用测试
            response = await pool.call_llm_async("你好，请简单介绍一下自己")
            print(f"响应: {response.content}")
            print(f"耗时: {response.response_time:.2f}秒")
            
            # 批量调用测试
            prompts = [
                "介绍Python编程语言",
                "解释机器学习概念",
                "描述人工智能的应用"
            ]
            responses = await pool.batch_call_llm_async(prompts, max_concurrent=3)
            for i, response in enumerate(responses):
                print(f"批量响应 {i+1}: {response.content[:50]}...")
            
            # 统计信息
            stats = pool.get_stats()
            print(f"统计信息: {stats}")
    
    asyncio.run(test_async_llm())