from pocketflow import Flow
from nodes import (
    ParseRequirementNode, 
    AnalyzeDocumentNode, 
    DesignLayoutNode,
    ProcessTextNode,
    UnifyImagesNode,
    GenerateDocumentNode,
    ErrorHandlingNode
)

def create_document_processing_flow():
    """
    创建智能文档处理工作流
    
    工作流程：
    1. 解析用户需求 -> 分析文档结构
    2. 分析文档结构 -> 设计排版方案
    3. 设计排版方案 -> 处理文本格式
    4. 处理文本格式 -> 统一图片样式
    5. 统一图片样式 -> 生成最终文档
    """
    
    # 创建节点实例
    parse_requirement = ParseRequirementNode(max_retries=2, wait=1)
    analyze_document = AnalyzeDocumentNode(max_retries=2, wait=1)
    design_layout = DesignLayoutNode(max_retries=3, wait=2)
    process_text = ProcessTextNode(max_retries=2, wait=1)
    unify_images = UnifyImagesNode(max_retries=2, wait=1)
    generate_document = GenerateDocumentNode(max_retries=2, wait=1)
    error_handler = ErrorHandlingNode()
    
    # 构建工作流链
    parse_requirement >> analyze_document >> design_layout >> process_text >> unify_images >> generate_document
    
    # 创建并返回流程
    document_flow = Flow(start=parse_requirement)
    return document_flow

def create_simple_formatting_flow():
    """
    创建简化的格式化工作流（用于快速处理）
    """
    
    # 创建必要的节点
    parse_requirement = ParseRequirementNode()
    design_layout = DesignLayoutNode()
    process_text = ProcessTextNode()
    generate_document = GenerateDocumentNode()
    
    # 简化的工作流
    parse_requirement >> design_layout >> process_text >> generate_document
    
    simple_flow = Flow(start=parse_requirement)
    return simple_flow

def create_image_only_flow():
    """
    创建仅处理图片的工作流
    """
    
    analyze_document = AnalyzeDocumentNode()
    design_layout = DesignLayoutNode()
    unify_images = UnifyImagesNode()
    
    analyze_document >> design_layout >> unify_images
    
    image_flow = Flow(start=analyze_document)
    return image_flow

# 主要的文档处理流程
document_processing_flow = create_document_processing_flow()

# 备用流程
simple_flow = create_simple_formatting_flow()
image_flow = create_image_only_flow()

def get_flow_by_type(flow_type="complete"):
    """
    根据类型获取不同的工作流
    
    Args:
        flow_type (str): 流程类型
            - "complete": 完整的文档处理流程
            - "simple": 简化的格式化流程
            - "image": 仅图片处理流程
    
    Returns:
        Flow: 对应的工作流对象
    """
    flows = {
        "complete": document_processing_flow,
        "simple": simple_flow,
        "image": image_flow
    }
    
    return flows.get(flow_type, document_processing_flow)

if __name__ == "__main__":
    # 测试工作流创建
    print("正在创建文档处理工作流...")
    flow = create_document_processing_flow()
    print("✓ 完整工作流创建成功")
    
    simple = create_simple_formatting_flow()
    print("✓ 简化工作流创建成功")
    
    images = create_image_only_flow()
    print("✓ 图片处理工作流创建成功")
    
    print("\n可用的工作流类型:")
    print("- complete: 完整的文档处理流程")
    print("- simple: 简化的格式化流程")  
    print("- image: 仅图片处理流程")