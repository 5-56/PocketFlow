"""
Smart Document Processor - FastAPI主应用程序
类似WPS Office的智能文档处理系统
"""
import asyncio
import io
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 导入我们的工作流组件
from flows import orchestrator
from utils.document_generator import DocumentGenerator

# 创建FastAPI应用
app = FastAPI(
    title="智能文档处理系统",
    description="基于PocketFlow的智能文档处理系统，支持AI增强、图像处理和多格式导出",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 模板设置
templates = Jinja2Templates(directory="templates")

# 全局存储，实际应用中应使用数据库
documents_storage: Dict[str, Dict[str, Any]] = {}
websocket_connections: List[WebSocket] = []

# Pydantic模型
class ProcessingRequest(BaseModel):
    document_id: str
    instruction: str
    processing_options: Dict[str, Any]

class TextEditRequest(BaseModel):
    document_id: str
    text_modifications: Dict[str, str]

class ImageEditRequest(BaseModel):
    document_id: str
    image_modifications: Dict[str, Dict[str, Any]]

class ExportRequest(BaseModel):
    document_id: str
    output_format: str
    template_type: str = "default"
    export_options: str = "standard"

# 工具函数
def generate_document_id() -> str:
    """生成文档ID"""
    return str(uuid.uuid4())

async def broadcast_to_websockets(message: Dict[str, Any]):
    """广播消息到所有WebSocket连接"""
    if websocket_connections:
        for websocket in websocket_connections[:]:  # 创建副本避免修改时迭代
            try:
                await websocket.send_json(message)
            except:
                # 移除断开的连接
                if websocket in websocket_connections:
                    websocket_connections.remove(websocket)

# 路由定义

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """首页 - WPS Office风格的主界面"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """上传文档"""
    try:
        # 检查文件大小（限制为50MB）
        MAX_SIZE = 50 * 1024 * 1024
        content = await file.read()
        
        if len(content) > MAX_SIZE:
            raise HTTPException(status_code=413, detail="文件太大，请上传小于50MB的文件")
        
        # 生成文档ID
        doc_id = generate_document_id()
        
        # 准备共享数据
        shared_data = {
            "uploaded_file": {
                "name": file.filename,
                "content": content,
                "content_type": file.content_type,
                "size": len(content)
            },
            "document_id": doc_id,
            "upload_time": datetime.now().isoformat(),
            "processing_stage": "uploaded"
        }
        
        # 存储文档
        documents_storage[doc_id] = shared_data
        
        # 广播上传成功消息
        await broadcast_to_websockets({
            "type": "upload_success",
            "document_id": doc_id,
            "filename": file.filename,
            "size": len(content)
        })
        
        return {
            "success": True,
            "document_id": doc_id,
            "filename": file.filename,
            "size": len(content),
            "message": "文档上传成功"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文档上传失败: {str(e)}")

@app.post("/api/process")
async def process_document(request: ProcessingRequest):
    """处理文档"""
    try:
        doc_id = request.document_id
        
        if doc_id not in documents_storage:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # 获取共享数据
        shared_data = documents_storage[doc_id]
        
        # 添加处理指令和选项
        shared_data["user_instruction"] = request.instruction
        shared_data["processing_options"] = request.processing_options
        
        # 广播处理开始消息
        await broadcast_to_websockets({
            "type": "processing_started",
            "document_id": doc_id,
            "instruction": request.instruction
        })
        
        # 异步处理文档
        try:
            processed_data = await orchestrator.process_document(shared_data)
            documents_storage[doc_id] = processed_data
            
            # 广播处理完成消息
            await broadcast_to_websockets({
                "type": "processing_completed",
                "document_id": doc_id,
                "stage": processed_data.get("processing_stage", "completed")
            })
            
            return {
                "success": True,
                "document_id": doc_id,
                "processing_stage": processed_data.get("processing_stage"),
                "message": "文档处理完成"
            }
            
        except Exception as e:
            # 广播处理失败消息
            await broadcast_to_websockets({
                "type": "processing_failed",
                "document_id": doc_id,
                "error": str(e)
            })
            raise HTTPException(status_code=500, detail=f"文档处理失败: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理请求失败: {str(e)}")

@app.get("/api/document/{doc_id}")
async def get_document(doc_id: str):
    """获取文档内容"""
    try:
        if doc_id not in documents_storage:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        shared_data = documents_storage[doc_id]
        
        # 返回处理后的内容
        return {
            "success": True,
            "document_id": doc_id,
            "filename": shared_data["uploaded_file"]["name"],
            "processing_stage": shared_data.get("processing_stage", "uploaded"),
            "analyzed_content": shared_data.get("analyzed_content"),
            "processed_content": shared_data.get("processed_content"),
            "metadata": shared_data.get("metadata", {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文档失败: {str(e)}")

@app.post("/api/edit/text")
async def edit_text(request: TextEditRequest):
    """编辑文本内容"""
    try:
        doc_id = request.document_id
        
        if doc_id not in documents_storage:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        shared_data = documents_storage[doc_id]
        shared_data["text_modifications"] = request.text_modifications
        
        # 处理文本编辑
        edited_data = orchestrator.edit_content(shared_data)
        documents_storage[doc_id] = edited_data
        
        # 广播编辑完成消息
        await broadcast_to_websockets({
            "type": "text_edited",
            "document_id": doc_id,
            "modifications_count": len(request.text_modifications)
        })
        
        return {
            "success": True,
            "document_id": doc_id,
            "message": "文本编辑完成"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文本编辑失败: {str(e)}")

@app.post("/api/edit/image")
async def edit_image(request: ImageEditRequest):
    """编辑图像"""
    try:
        doc_id = request.document_id
        
        if doc_id not in documents_storage:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        shared_data = documents_storage[doc_id]
        shared_data["image_modifications"] = request.image_modifications
        
        # 处理图像编辑
        edited_data = orchestrator.process_images(shared_data)
        documents_storage[doc_id] = edited_data
        
        # 广播编辑完成消息
        await broadcast_to_websockets({
            "type": "image_edited",
            "document_id": doc_id,
            "modifications_count": len(request.image_modifications)
        })
        
        return {
            "success": True,
            "document_id": doc_id,
            "message": "图像编辑完成"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图像编辑失败: {str(e)}")

@app.post("/api/ai/enhance")
async def ai_enhance(doc_id: str = Form(...), enhancement_type: str = Form("general")):
    """AI增强处理"""
    try:
        if doc_id not in documents_storage:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        shared_data = documents_storage[doc_id]
        
        # 设置增强选项
        enhancement_options = {
            "general": {"process_text": True, "analyze_images": True, "text_style": "professional"},
            "academic": {"process_text": True, "analyze_images": True, "text_style": "academic"},
            "business": {"process_text": True, "analyze_images": True, "text_style": "professional"},
            "creative": {"process_text": True, "analyze_images": True, "text_style": "casual"}
        }
        
        shared_data["processing_options"] = enhancement_options.get(enhancement_type, enhancement_options["general"])
        shared_data["user_instruction"] = f"以{enhancement_type}风格优化文档内容"
        
        # 广播AI增强开始消息
        await broadcast_to_websockets({
            "type": "ai_enhancement_started",
            "document_id": doc_id,
            "enhancement_type": enhancement_type
        })
        
        # 执行AI增强
        enhanced_data = await orchestrator.ai_enhance(shared_data)
        documents_storage[doc_id] = enhanced_data
        
        # 广播AI增强完成消息
        await broadcast_to_websockets({
            "type": "ai_enhancement_completed",
            "document_id": doc_id,
            "enhancement_type": enhancement_type
        })
        
        return {
            "success": True,
            "document_id": doc_id,
            "enhancement_type": enhancement_type,
            "message": "AI增强完成"
        }
        
    except Exception as e:
        await broadcast_to_websockets({
            "type": "ai_enhancement_failed",
            "document_id": doc_id,
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail=f"AI增强失败: {str(e)}")

@app.post("/api/export")
async def export_document(request: ExportRequest):
    """导出文档"""
    try:
        doc_id = request.document_id
        
        if doc_id not in documents_storage:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        shared_data = documents_storage[doc_id]
        
        # 检查是否有处理后的内容
        if "processed_content" not in shared_data:
            raise HTTPException(status_code=400, detail="文档尚未处理，无法导出")
        
        # 创建文档生成器
        generator = DocumentGenerator()
        
        # 设置模板和导出选项
        template_settings = generator.create_template_settings(request.template_type)
        export_options = generator.create_export_options(request.export_options)
        
        # 准备导出参数
        shared_data["output_format"] = request.output_format
        shared_data["template_settings"] = template_settings
        shared_data["export_options"] = export_options
        
        # 生成文档
        generated_data = orchestrator.editing_flow.start.run(shared_data)
        
        if "generated_document" not in shared_data:
            raise HTTPException(status_code=500, detail="文档生成失败")
        
        document_data = shared_data["generated_document"]
        
        # 准备响应
        filename = f"{shared_data['uploaded_file']['name'].split('.')[0]}_processed.{request.output_format.lower()}"
        
        # 设置内容类型
        content_types = {
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "pdf": "application/pdf",
            "html": "text/html"
        }
        
        content_type = content_types.get(request.output_format.lower(), "application/octet-stream")
        
        # 广播导出完成消息
        await broadcast_to_websockets({
            "type": "export_completed",
            "document_id": doc_id,
            "format": request.output_format,
            "filename": filename
        })
        
        return StreamingResponse(
            io.BytesIO(document_data["data"]),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        await broadcast_to_websockets({
            "type": "export_failed",
            "document_id": doc_id,
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail=f"文档导出失败: {str(e)}")

@app.get("/api/documents")
async def list_documents():
    """获取文档列表"""
    try:
        document_list = []
        
        for doc_id, data in documents_storage.items():
            document_list.append({
                "document_id": doc_id,
                "filename": data["uploaded_file"]["name"],
                "size": data["uploaded_file"]["size"],
                "upload_time": data["upload_time"],
                "processing_stage": data.get("processing_stage", "uploaded")
            })
        
        return {
            "success": True,
            "documents": document_list,
            "total": len(document_list)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文档列表失败: {str(e)}")

@app.delete("/api/document/{doc_id}")
async def delete_document(doc_id: str):
    """删除文档"""
    try:
        if doc_id not in documents_storage:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        filename = documents_storage[doc_id]["uploaded_file"]["name"]
        del documents_storage[doc_id]
        
        # 广播删除消息
        await broadcast_to_websockets({
            "type": "document_deleted",
            "document_id": doc_id,
            "filename": filename
        })
        
        return {
            "success": True,
            "document_id": doc_id,
            "message": "文档删除成功"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除文档失败: {str(e)}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket连接端点"""
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        # 发送欢迎消息
        await websocket.send_json({
            "type": "connection_established",
            "message": "WebSocket连接已建立"
        })
        
        while True:
            # 保持连接活跃
            data = await websocket.receive_text()
            
            # 处理客户端消息（如果需要）
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)
    except Exception as e:
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_documents": len(documents_storage),
        "websocket_connections": len(websocket_connections)
    }

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    print("🚀 智能文档处理系统启动成功!")
    print("📚 支持的功能:")
    print("   - 多格式文档解析 (Word, PDF, TXT, HTML)")
    print("   - AI智能内容处理")
    print("   - 图像编辑和优化")
    print("   - 多格式导出 (Word, PDF, HTML)")
    print("   - 实时协作和状态更新")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    print("📝 智能文档处理系统正在关闭...")
    
    # 关闭所有WebSocket连接
    for websocket in websocket_connections:
        try:
            await websocket.close()
        except:
            pass
    
    print("✅ 系统已安全关闭")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )