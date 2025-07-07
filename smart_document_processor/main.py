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

# AI交互API
@app.post("/api/ai/chat")
async def ai_chat(request: Request):
    """AI聊天接口"""
    try:
        data = await request.json()
        message = data.get("message", "")
        context = data.get("context", {})
        selected_text = data.get("selected_text")
        settings = data.get("settings", {})
        
        if not message:
            raise HTTPException(status_code=400, detail="消息内容不能为空")
        
        # 准备AI处理数据
        ai_data = {
            "user_message": message,
            "context": context,
            "selected_text": selected_text,
            "ai_settings": settings,
            "task_type": "chat",
            "timestamp": datetime.now().isoformat()
        }
        
        # 使用AI聊天工作流处理
        ai_result = await orchestrator.ai_chat(ai_data)
        
        # 提取AI响应
        ai_response = ai_result.get("ai_response", "抱歉，我无法处理您的请求。")
        suggestions = ai_result.get("ai_suggestions", [])
        modifications = ai_result.get("ai_modifications", [])
        token_usage = ai_result.get("token_usage", 0)
        
        # 广播AI聊天消息
        await broadcast_to_websockets({
            "type": "ai_chat_response",
            "message": message,
            "response": ai_response,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "response": ai_response,
            "suggestions": suggestions,
            "modifications": modifications,
            "token_usage": token_usage
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI聊天失败: {str(e)}")

@app.post("/api/ai/quick-action")
async def ai_quick_action(request: Request):
    """AI快速操作接口"""
    try:
        data = await request.json()
        action = data.get("action", "")
        text = data.get("text", "")
        document_id = data.get("document_id")
        settings = data.get("settings", {})
        instruction = data.get("instruction", "")
        
        if not action or not text:
            raise HTTPException(status_code=400, detail="操作类型和文本内容不能为空")
        
        # 使用AI处理器进行实际处理
        if action == "custom" and instruction:
            result = ai_processor.custom_action(instruction, text)
        else:
            # 传递设置中的参数
            kwargs = {}
            if action == "translate":
                kwargs['target_language'] = settings.get('target_language', '英文')
            elif action == "style_convert":
                kwargs['style'] = settings.get('style', '专业')
                
            result = ai_processor.quick_action(action, text, **kwargs)
        
        # 如果有文档ID，更新文档数据
        if document_id and document_id in documents_storage and result.get("success"):
            if "ai_processed_texts" not in documents_storage[document_id]:
                documents_storage[document_id]["ai_processed_texts"] = []
            
            documents_storage[document_id]["ai_processed_texts"].append({
                "action": action,
                "original": text,
                "result": result.get("result", text),
                "timestamp": datetime.now().isoformat()
            })
        
        # 广播快速操作完成
        await broadcast_to_websockets({
            "type": "ai_quick_action_completed",
            "action": action,
            "document_id": document_id,
            "success": result.get("success", False),
            "timestamp": datetime.now().isoformat()
        })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"快速操作失败: {str(e)}")

@app.get("/api/ai/settings")
async def get_ai_settings():
    """获取AI设置"""
    try:
        # 默认AI设置
        default_settings = {
            "model": "gpt-4",
            "max_tokens": 4000,
            "temperature": 0.7,
            "response_style": "professional",
            "language": "zh-CN",
            "system_prompt": "你是一个专业的文档编辑助手，专注于帮助用户改进文档内容。请保持专业、准确和有帮助的态度。",
            "auto_suggest": True,
            "context_aware": True,
            "available_models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "claude-3"],
            "supported_languages": ["zh-CN", "en-US", "ja-JP", "ko-KR"],
            "response_styles": ["professional", "friendly", "concise", "detailed"]
        }
        
        return {"success": True, "settings": default_settings}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取设置失败: {str(e)}")

@app.post("/api/ai/settings")
async def save_ai_settings(request: Request):
    """保存AI设置"""
    try:
        settings = await request.json()
        
        # 验证必要的设置字段
        required_fields = ["model", "max_tokens", "temperature"]
        for field in required_fields:
            if field not in settings:
                raise HTTPException(status_code=400, detail=f"缺少必要的设置字段: {field}")
        
        # 验证设置值的有效性
        if settings.get("max_tokens", 0) < 100 or settings.get("max_tokens", 0) > 8000:
            raise HTTPException(status_code=400, detail="max_tokens必须在100-8000之间")
        
        if settings.get("temperature", 0) < 0 or settings.get("temperature", 0) > 2:
            raise HTTPException(status_code=400, detail="temperature必须在0-2之间")
        
        # 在生产环境中，这里应该保存到数据库或配置文件
        # 这里简单存储到全局变量中
        if "ai_settings" not in documents_storage:
            documents_storage["ai_settings"] = {}
        
        documents_storage["ai_settings"] = settings
        
        # 广播设置更新
        await broadcast_to_websockets({
            "type": "ai_settings_updated",
            "timestamp": datetime.now().isoformat()
        })
        
        return {"success": True, "message": "设置已保存"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存设置失败: {str(e)}")

@app.post("/api/ai/test-connection")
async def test_ai_connection(request: Request):
    """测试AI连接"""
    try:
        data = await request.json()
        api_key = data.get("api_key", "")
        model = data.get("model", "gpt-4")
        
        if not api_key:
            raise HTTPException(status_code=400, detail="API密钥不能为空")
        
        # 创建测试用的AI处理器
        from utils.ai_processor import AIProcessor
        ai_processor = AIProcessor()
        
        # 测试连接
        test_result = await ai_processor.test_connection(api_key, model)
        
        if test_result:
            return {
                "success": True,
                "message": "连接成功",
                "model": model,
                "latency": test_result.get("latency", 0)
            }
        else:
            return {
                "success": False,
                "message": "连接失败，请检查API密钥和网络连接"
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"连接测试失败: {str(e)}"
        }

@app.get("/api/ai/usage")
async def get_ai_usage():
    """获取AI使用统计"""
    try:
        # 在实际应用中，这些数据应该从数据库或监控系统获取
        usage_data = {
            "today_tokens": 1250,
            "monthly_tokens": 48750,
            "monthly_limit": 50000,
            "requests_today": 35,
            "average_response_time": 2.3,
            "success_rate": 0.97,
            "last_updated": datetime.now().isoformat()
        }
        
        return {"success": True, "usage": usage_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取使用统计失败: {str(e)}")

@app.post("/api/ai/templates")
async def get_ai_templates():
    """获取AI指令模板"""
    try:
        templates = {
            "text_optimization": [
                {"id": "optimize_clarity", "name": "提升清晰度", "template": "请优化这段文字的清晰度，使表达更准确易懂："},
                {"id": "optimize_tone", "name": "调整语调", "template": "请调整这段文字的语调，使其更适合目标读者："},
                {"id": "fix_grammar", "name": "语法修正", "template": "请检查并修正这段文字的语法和拼写错误："}
            ],
            "content_processing": [
                {"id": "summarize", "name": "生成摘要", "template": "请为这段内容生成一个简洁明了的摘要："},
                {"id": "expand", "name": "扩展内容", "template": "请扩展这段内容，添加更多相关细节和解释："},
                {"id": "restructure", "name": "重构结构", "template": "请重新组织这段内容的结构，使逻辑更清晰："}
            ],
            "translation": [
                {"id": "translate_en", "name": "翻译为英文", "template": "请将这段内容翻译为英文，保持原意不变："},
                {"id": "localize", "name": "本地化", "template": "请将这段内容本地化，使其更适合中文读者的习惯："}
            ]
        }
        
        return {"success": True, "templates": templates}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模板失败: {str(e)}")

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