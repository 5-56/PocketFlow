"""
Smart Document Processor - PocketFlow Workflows
"""
from pocketflow import Flow, AsyncFlow
from nodes import (
    DocumentParseNode, ContentAnalysisNode, AIProcessingNode,
    ImageProcessingNode, TextEditingNode, DocumentGenerationNode,
    BatchTextProcessingNode, AIChatNode, AIQuickActionNode
)

def create_document_processing_flow():
    """创建主要文档处理工作流"""
    
    # 创建节点实例
    parse_node = DocumentParseNode(max_retries=3)
    analyze_node = ContentAnalysisNode()
    ai_process_node = AIProcessingNode(max_retries=2)
    
    # 连接主要处理流程
    parse_node - "analyze" >> analyze_node
    analyze_node - "ai_process" >> ai_process_node
    
    # 创建异步流程
    return AsyncFlow(start=parse_node)

def create_content_editing_flow():
    """创建内容编辑工作流"""
    
    # 创建编辑节点
    text_edit_node = TextEditingNode()
    image_process_node = ImageProcessingNode()
    doc_generation_node = DocumentGenerationNode()
    
    # 连接编辑流程
    text_edit_node - "generate_document" >> image_process_node
    image_process_node - "generate_document" >> doc_generation_node
    
    return Flow(start=text_edit_node)

def create_batch_processing_flow():
    """创建批量处理工作流"""
    
    # 创建批量处理节点
    batch_text_node = BatchTextProcessingNode()
    doc_generation_node = DocumentGenerationNode()
    
    # 连接批量处程
    batch_text_node - "merge_results" >> doc_generation_node
    
    return Flow(start=batch_text_node)

def create_ai_enhancement_flow():
    """创建AI增强工作流"""
    
    # 创建AI增强节点
    ai_process_node = AIProcessingNode(max_retries=3)
    doc_generation_node = DocumentGenerationNode()
    
    # 连接AI增强流程
    ai_process_node - "user_review" >> doc_generation_node
    
    return AsyncFlow(start=ai_process_node)

def create_image_processing_flow():
    """创建图像处理工作流"""
    
    # 创建图像处理节点
    image_process_node = ImageProcessingNode()
    doc_generation_node = DocumentGenerationNode()
    
    # 连接图像处理流程
    image_process_node - "generate_document" >> doc_generation_node
    
    return Flow(start=image_process_node)

def create_ai_chat_flow():
    """创建AI聊天工作流"""
    chat_node = AIChatNode()
    return AsyncFlow(start=chat_node)

def create_ai_quick_action_flow():
    """创建AI快速操作工作流"""
    quick_action_node = AIQuickActionNode()
    return AsyncFlow(start=quick_action_node)

class DocumentProcessingOrchestrator:
    """文档处理编排器 - 管理多个工作流"""
    
    def __init__(self):
        self.main_flow = create_document_processing_flow()
        self.editing_flow = create_content_editing_flow()
        self.batch_flow = create_batch_processing_flow()
        self.ai_flow = create_ai_enhancement_flow()
        self.image_flow = create_image_processing_flow()
        self.chat_flow = create_ai_chat_flow()
        self.quick_action_flow = create_ai_quick_action_flow()
    
    async def process_document(self, shared_data):
        """处理文档 - 主要流程"""
        try:
            await self.main_flow.run_async(shared_data)
            return shared_data
        except Exception as e:
            shared_data["error"] = f"文档处理失败: {str(e)}"
            return shared_data
    
    def edit_content(self, shared_data):
        """编辑内容"""
        try:
            self.editing_flow.run(shared_data)
            return shared_data
        except Exception as e:
            shared_data["error"] = f"内容编辑失败: {str(e)}"
            return shared_data
    
    def batch_process(self, shared_data):
        """批量处理"""
        try:
            self.batch_flow.run(shared_data)
            return shared_data
        except Exception as e:
            shared_data["error"] = f"批量处理失败: {str(e)}"
            return shared_data
    
    async def ai_enhance(self, shared_data):
        """AI增强"""
        try:
            await self.ai_flow.run_async(shared_data)
            return shared_data
        except Exception as e:
            shared_data["error"] = f"AI增强失败: {str(e)}"
            return shared_data
    
    def process_images(self, shared_data):
        """处理图像"""
        try:
            self.image_flow.run(shared_data)
            return shared_data
        except Exception as e:
            shared_data["error"] = f"图像处理失败: {str(e)}"
            return shared_data
    
    async def ai_chat(self, shared_data):
        """AI聊天"""
        try:
            await self.chat_flow.run_async(shared_data)
            return shared_data
        except Exception as e:
            shared_data["error"] = f"AI聊天失败: {str(e)}"
            return shared_data
    
    async def ai_quick_action(self, shared_data):
        """AI快速操作"""
        try:
            await self.quick_action_flow.run_async(shared_data)
            return shared_data
        except Exception as e:
            shared_data["error"] = f"AI快速操作失败: {str(e)}"
            return shared_data

# 全局编排器实例
orchestrator = DocumentProcessingOrchestrator()