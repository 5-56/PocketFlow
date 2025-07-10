#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Web API服务 - FastAPI后端
提供RESTful API和WebSocket实时通信支持
"""

import asyncio
import json
import time
import logging
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field

# 导入处理模块
from async_flow import (
    create_async_document_flow,
    create_batch_async_flow,
    auto_create_optimal_flow,
    workflow_monitor,
    adaptive_workflow
)
from utils.async_llm_pool import get_llm_stats, clear_llm_cache
from intelligent_agent import IntelligentDocumentAgent

logger = logging.getLogger(__name__)

# 配置日志
logging.basicConfig(level=logging.INFO)

# 创建FastAPI应用
app = FastAPI(
    title="智能文档自动排版系统",
    description="基于AI的高性能文档处理平台",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该配置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局状态管理
class AppState:
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}
        self.processing_tasks: Dict[str, asyncio.Task] = {}
        self.websocket_connections: Dict[str, WebSocket] = {}

app_state = AppState()

# 数据模型
class DocumentRequest(BaseModel):
    content: str = Field(..., description="文档内容")
    instruction: str = Field(..., description="处理指令")
    file_type: str = Field(default="markdown", description="文件类型")
    output_format: str = Field(default="HTML", description="输出格式")
    processing_strategy: str = Field(default="auto", description="处理策略")
    quality_level: str = Field(default="high", description="质量级别")

class BatchDocumentRequest(BaseModel):
    documents: List[Dict[str, str]] = Field(..., description="文档列表")
    instruction: str = Field(..., description="批处理指令")
    processing_strategy: str = Field(default="quick", description="批处理策略")
    max_concurrent: int = Field(default=3, description="最大并发数")

class ProcessingResponse(BaseModel):
    session_id: str
    status: str
    message: str
    progress: float = 0.0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class SystemStatus(BaseModel):
    status: str
    active_sessions: int
    total_processed: int
    cache_stats: Dict[str, Any]
    performance_metrics: Dict[str, Any]

# WebSocket连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket连接建立: {session_id}")

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        logger.info(f"WebSocket连接断开: {session_id}")

    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"发送WebSocket消息失败: {e}")
                self.disconnect(session_id)

    async def broadcast(self, message: dict):
        """广播消息给所有连接"""
        for session_id in list(self.active_connections.keys()):
            await self.send_message(session_id, message)

manager = ConnectionManager()

# API路由
@app.get("/", response_class=HTMLResponse)
async def root():
    """返回主页面"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>智能文档自动排版系统</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: 'Segoe UI', sans-serif; margin: 0; padding: 2rem; background: #f5f7fa; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 3rem; }
            .card { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 2rem; }
            .btn { background: #2196F3; color: white; padding: 1rem 2rem; border: none; border-radius: 8px; cursor: pointer; text-decoration: none; display: inline-block; }
            .btn:hover { background: #1976D2; }
            .feature { display: inline-block; margin: 1rem; padding: 1rem; background: #e3f2fd; border-radius: 8px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎨 智能文档自动排版系统</h1>
                <p>基于AI的高性能文档处理平台</p>
            </div>
            
            <div class="card">
                <h2>核心功能</h2>
                <div class="feature">🚀 异步高性能处理</div>
                <div class="feature">🤖 智能AI决策</div>
                <div class="feature">📱 实时Web界面</div>
                <div class="feature">🔄 多格式输出</div>
                <div class="feature">📊 质量分析</div>
                <div class="feature">🎯 模板推荐</div>
            </div>
            
            <div class="card">
                <h2>快速开始</h2>
                <p>访问以下链接开始使用：</p>
                <a href="/api/docs" class="btn">📚 API文档</a>
                <a href="/web" class="btn">🌐 Web界面</a>
                <a href="/status" class="btn">📊 系统状态</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/api/status", response_model=SystemStatus)
async def get_system_status():
    """获取系统状态"""
    try:
        cache_stats = await get_llm_stats()
        performance_metrics = workflow_monitor.get_performance_report()
        
        return SystemStatus(
            status="healthy",
            active_sessions=len(app_state.active_sessions),
            total_processed=performance_metrics["overall_metrics"]["total_runs"],
            cache_stats=cache_stats,
            performance_metrics=performance_metrics
        )
    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        raise HTTPException(status_code=500, detail="无法获取系统状态")

@app.post("/api/process", response_model=ProcessingResponse)
async def process_document(request: DocumentRequest):
    """异步处理单个文档"""
    session_id = str(uuid.uuid4())
    
    try:
        # 创建处理会话
        app_state.active_sessions[session_id] = {
            "request": request.dict(),
            "status": "processing",
            "start_time": time.time(),
            "progress": 0.0
        }
        
        # 异步处理文档
        task = asyncio.create_task(
            _process_document_async(session_id, request)
        )
        app_state.processing_tasks[session_id] = task
        
        return ProcessingResponse(
            session_id=session_id,
            status="started",
            message="文档处理已开始",
            progress=0.0
        )
        
    except Exception as e:
        logger.error(f"启动文档处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"处理启动失败: {str(e)}")

@app.post("/api/batch-process", response_model=ProcessingResponse)
async def batch_process_documents(request: BatchDocumentRequest):
    """批量处理文档"""
    session_id = str(uuid.uuid4())
    
    try:
        # 创建批处理会话
        app_state.active_sessions[session_id] = {
            "request": request.dict(),
            "status": "processing",
            "start_time": time.time(),
            "progress": 0.0,
            "batch_mode": True
        }
        
        # 异步批量处理
        task = asyncio.create_task(
            _batch_process_documents_async(session_id, request)
        )
        app_state.processing_tasks[session_id] = task
        
        return ProcessingResponse(
            session_id=session_id,
            status="started",
            message=f"批量处理已开始，共{len(request.documents)}个文档",
            progress=0.0
        )
        
    except Exception as e:
        logger.error(f"启动批量处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量处理启动失败: {str(e)}")

@app.get("/api/session/{session_id}", response_model=ProcessingResponse)
async def get_session_status(session_id: str):
    """获取处理会话状态"""
    if session_id not in app_state.active_sessions:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    session = app_state.active_sessions[session_id]
    
    return ProcessingResponse(
        session_id=session_id,
        status=session["status"],
        message=session.get("message", ""),
        progress=session.get("progress", 0.0),
        result=session.get("result"),
        error=session.get("error")
    )

@app.delete("/api/session/{session_id}")
async def cancel_session(session_id: str):
    """取消处理会话"""
    if session_id in app_state.processing_tasks:
        task = app_state.processing_tasks[session_id]
        task.cancel()
        del app_state.processing_tasks[session_id]
    
    if session_id in app_state.active_sessions:
        app_state.active_sessions[session_id]["status"] = "cancelled"
    
    return {"message": "会话已取消"}

@app.post("/api/clear-cache")
async def clear_system_cache():
    """清空系统缓存"""
    try:
        await clear_llm_cache()
        return {"message": "缓存已清空"}
    except Exception as e:
        logger.error(f"清空缓存失败: {e}")
        raise HTTPException(status_code=500, detail="清空缓存失败")

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传文件"""
    if not file.filename.endswith(('.md', '.txt', '.markdown')):
        raise HTTPException(status_code=400, detail="只支持Markdown和文本文件")
    
    try:
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # 确定文件类型
        file_type = "markdown" if file.filename.endswith(('.md', '.markdown')) else "text"
        
        return {
            "filename": file.filename,
            "content": content_str,
            "file_type": file_type,
            "size": len(content)
        }
        
    except Exception as e:
        logger.error(f"文件上传失败: {e}")
        raise HTTPException(status_code=500, detail="文件上传失败")

@app.get("/api/templates")
async def get_templates():
    """获取可用模板"""
    templates = [
        {
            "id": "business",
            "name": "商务报告",
            "description": "专业的商务报告格式，适合企业使用",
            "preview": "modern_business_style.jpg",
            "category": "business"
        },
        {
            "id": "academic",
            "name": "学术论文",
            "description": "标准的学术论文格式，符合期刊要求",
            "preview": "academic_paper_style.jpg",
            "category": "academic"
        },
        {
            "id": "creative",
            "name": "创意设计",
            "description": "充满创意的设计风格，适合展示创意作品",
            "preview": "creative_design_style.jpg",
            "category": "creative"
        },
        {
            "id": "technical",
            "name": "技术文档",
            "description": "清晰的技术文档格式，便于阅读和理解",
            "preview": "technical_doc_style.jpg",
            "category": "technical"
        },
        {
            "id": "presentation",
            "name": "产品展示",
            "description": "友好的产品说明格式，突出产品特色",
            "preview": "product_presentation_style.jpg",
            "category": "marketing"
        }
    ]
    
    return {"templates": templates}

# WebSocket路由
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket实时通信端点"""
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理不同类型的消息
            if message["type"] == "ping":
                await manager.send_message(session_id, {"type": "pong"})
            
            elif message["type"] == "get_progress":
                # 发送当前进度
                if session_id in app_state.active_sessions:
                    session = app_state.active_sessions[session_id]
                    await manager.send_message(session_id, {
                        "type": "progress_update",
                        "progress": session.get("progress", 0.0),
                        "status": session.get("status", "unknown"),
                        "message": session.get("message", "")
                    })
            
            elif message["type"] == "cancel_processing":
                # 取消处理
                await cancel_session(session_id)
                await manager.send_message(session_id, {
                    "type": "processing_cancelled",
                    "message": "处理已取消"
                })
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        manager.disconnect(session_id)

# 内部处理函数
async def _process_document_async(session_id: str, request: DocumentRequest):
    """异步处理文档"""
    try:
        session = app_state.active_sessions[session_id]
        
        # 更新进度
        await _update_session_progress(session_id, 10, "准备处理工作流...")
        
        # 创建最优工作流
        if request.processing_strategy == "auto":
            flow = await auto_create_optimal_flow(request.instruction, request.content)
        else:
            flow = create_async_document_flow(request.processing_strategy)
        
        # 准备共享数据
        shared_data = {
            "user_instruction": request.instruction,
            "original_document": request.content,
            "file_type": request.file_type,
            "output_format": request.output_format,
            "session_id": session_id
        }
        
        # 更新进度
        await _update_session_progress(session_id, 20, "开始文档处理...")
        
        # 监控并运行工作流
        await workflow_monitor.monitor_flow_execution(flow, shared_data)
        
        # 更新进度
        await _update_session_progress(session_id, 90, "生成最终结果...")
        
        # 处理完成
        result = {
            "final_document": shared_data.get("final_document", {}),
            "processing_metadata": shared_data.get("workflow_metadata", {}),
            "quality_report": shared_data.get("quality_assurance_report", {}),
            "session_id": session_id
        }
        
        session["result"] = result
        session["status"] = "completed"
        session["progress"] = 100.0
        session["message"] = "文档处理完成"
        
        # 通过WebSocket发送完成通知
        await manager.send_message(session_id, {
            "type": "processing_completed",
            "result": result,
            "message": "文档处理完成"
        })
        
    except Exception as e:
        logger.error(f"文档处理失败 {session_id}: {e}")
        session = app_state.active_sessions.get(session_id, {})
        session["status"] = "failed"
        session["error"] = str(e)
        session["message"] = f"处理失败: {str(e)}"
        
        # 通过WebSocket发送错误通知
        await manager.send_message(session_id, {
            "type": "processing_failed",
            "error": str(e),
            "message": f"处理失败: {str(e)}"
        })

async def _batch_process_documents_async(session_id: str, request: BatchDocumentRequest):
    """异步批量处理文档"""
    try:
        session = app_state.active_sessions[session_id]
        
        # 更新进度
        await _update_session_progress(session_id, 10, "准备批量处理...")
        
        # 创建批量工作流
        batch_flow = create_batch_async_flow(
            request.processing_strategy,
            request.max_concurrent
        )
        
        # 准备批量数据
        shared_data = {
            "user_instruction": request.instruction,
            "documents": request.documents,
            "session_id": session_id
        }
        
        # 更新进度
        await _update_session_progress(session_id, 20, "开始批量处理...")
        
        # 运行批量工作流
        await batch_flow.run_async(shared_data)
        
        # 处理完成
        result = {
            "batch_results": shared_data.get("batch_results", {}),
            "processing_metadata": shared_data.get("workflow_metadata", {}),
            "session_id": session_id
        }
        
        session["result"] = result
        session["status"] = "completed"
        session["progress"] = 100.0
        session["message"] = "批量处理完成"
        
        # 通过WebSocket发送完成通知
        await manager.send_message(session_id, {
            "type": "batch_processing_completed",
            "result": result,
            "message": "批量处理完成"
        })
        
    except Exception as e:
        logger.error(f"批量处理失败 {session_id}: {e}")
        session = app_state.active_sessions.get(session_id, {})
        session["status"] = "failed"
        session["error"] = str(e)
        session["message"] = f"批量处理失败: {str(e)}"
        
        # 通过WebSocket发送错误通知
        await manager.send_message(session_id, {
            "type": "batch_processing_failed",
            "error": str(e),
            "message": f"批量处理失败: {str(e)}"
        })

async def _update_session_progress(session_id: str, progress: float, message: str):
    """更新会话进度"""
    if session_id in app_state.active_sessions:
        session = app_state.active_sessions[session_id]
        session["progress"] = progress
        session["message"] = message
        
        # 通过WebSocket发送进度更新
        await manager.send_message(session_id, {
            "type": "progress_update",
            "progress": progress,
            "message": message
        })

# 定期清理任务
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("智能文档处理Web API启动")
    
    # 启动定期清理任务
    asyncio.create_task(cleanup_expired_sessions())

async def cleanup_expired_sessions():
    """定期清理过期会话"""
    while True:
        try:
            current_time = time.time()
            expired_sessions = []
            
            for session_id, session in app_state.active_sessions.items():
                # 清理超过1小时的会话
                if current_time - session.get("start_time", current_time) > 3600:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                if session_id in app_state.processing_tasks:
                    app_state.processing_tasks[session_id].cancel()
                    del app_state.processing_tasks[session_id]
                
                del app_state.active_sessions[session_id]
                logger.info(f"清理过期会话: {session_id}")
            
            # 每5分钟清理一次
            await asyncio.sleep(300)
            
        except Exception as e:
            logger.error(f"清理会话失败: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "web_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )