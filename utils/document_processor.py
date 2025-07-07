import re
import json
import base64
from pathlib import Path
from typing import Dict, List, Any
import markdown
from PIL import Image
import io

def parse_document(content: str, file_type: str = "markdown") -> Dict[str, Any]:
    """
    解析各种格式的文档内容
    """
    if file_type.lower() == "markdown":
        return parse_markdown(content)
    elif file_type.lower() in ["txt", "text"]:
        return parse_text(content)
    else:
        return {"error": f"不支持的文件类型: {file_type}"}

def parse_markdown(content: str) -> Dict[str, Any]:
    """
    解析Markdown文档
    """
    document_structure = {
        "type": "markdown",
        "titles": [],
        "paragraphs": [],
        "images": [],
        "code_blocks": [],
        "lists": [],
        "links": []
    }
    
    lines = content.split('\n')
    current_section = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # 提取标题
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            title_text = line.lstrip('#').strip()
            document_structure["titles"].append({
                "level": level,
                "text": title_text,
                "line_number": i + 1
            })
            current_section = title_text
        
        # 提取图片
        elif '![' in line:
            img_matches = re.findall(r'!\[(.*?)\]\((.*?)\)', line)
            for alt_text, img_url in img_matches:
                document_structure["images"].append({
                    "alt_text": alt_text,
                    "url": img_url,
                    "line_number": i + 1,
                    "section": current_section
                })
        
        # 提取代码块
        elif line.startswith('```'):
            # 简单的代码块检测
            document_structure["code_blocks"].append({
                "line_number": i + 1,
                "section": current_section
            })
        
        # 提取链接
        elif '[' in line and '](' in line:
            link_matches = re.findall(r'\[(.*?)\]\((.*?)\)', line)
            for link_text, url in link_matches:
                if not url.startswith('http') and '![' not in f'[{link_text}]({url})':
                    document_structure["links"].append({
                        "text": link_text,
                        "url": url,
                        "line_number": i + 1,
                        "section": current_section
                    })
        
        # 提取列表
        elif line.startswith(('-', '*', '+')):
            document_structure["lists"].append({
                "text": line[1:].strip(),
                "line_number": i + 1,
                "section": current_section,
                "type": "unordered"
            })
        elif re.match(r'^\d+\.', line):
            document_structure["lists"].append({
                "text": re.sub(r'^\d+\.\s*', '', line),
                "line_number": i + 1,
                "section": current_section,
                "type": "ordered"
            })
        
        # 提取段落
        elif line and not line.startswith('#') and not line.startswith('```'):
            document_structure["paragraphs"].append({
                "text": line,
                "line_number": i + 1,
                "section": current_section
            })
    
    return document_structure

def parse_text(content: str) -> Dict[str, Any]:
    """
    解析纯文本文档
    """
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    
    return {
        "type": "text",
        "paragraphs": [{"text": p, "line_number": i+1} for i, p in enumerate(paragraphs)],
        "word_count": len(content.split()),
        "char_count": len(content)
    }

def extract_images(document_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    从文档结构中提取图片信息
    """
    return document_structure.get("images", [])

def apply_styles(content: str, styles: Dict[str, Any]) -> str:
    """
    应用样式到内容
    """
    styled_content = content
    
    # 应用标题样式
    if "title_style" in styles:
        title_style = styles["title_style"]
        # 这里可以添加更复杂的样式应用逻辑
        for level in range(1, 7):
            pattern = f"^{'#' * level}\\s+(.+)$"
            replacement = f"{'#' * level} {title_style.get('prefix', '')}\g<1>{title_style.get('suffix', '')}"
            styled_content = re.sub(pattern, replacement, styled_content, flags=re.MULTILINE)
    
    # 应用段落样式
    if "paragraph_style" in styles:
        # 可以添加段落格式化逻辑
        pass
    
    return styled_content

def generate_html_from_markdown(content: str, styles: Dict[str, Any] = None) -> str:
    """
    将Markdown转换为HTML，并应用样式
    """
    # 转换为HTML
    html = markdown.markdown(content, extensions=['extra', 'codehilite'])
    
    # 添加CSS样式
    if styles:
        css = generate_css_from_styles(styles)
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
    {css}
    </style>
</head>
<body>
    {html}
</body>
</html>
"""
    
    return html

def generate_css_from_styles(styles: Dict[str, Any]) -> str:
    """
    从样式字典生成CSS
    """
    css_rules = []
    
    # 基础样式
    css_rules.append("""
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
    """)
    
    # 标题样式
    if "title_style" in styles:
        title_style = styles["title_style"]
        color = title_style.get("color", "#2c3e50")
        css_rules.append(f"""
        h1, h2, h3, h4, h5, h6 {{
            color: {color};
            margin-top: 2em;
            margin-bottom: 1em;
        }}
        h1 {{ font-size: 2.5em; }}
        h2 {{ font-size: 2em; }}
        h3 {{ font-size: 1.5em; }}
        """)
    
    # 图片样式
    if "image_style" in styles:
        image_style = styles["image_style"]
        css_rules.append(f"""
        img {{
            max-width: 100%;
            height: auto;
            border-radius: {image_style.get('border_radius', '8px')};
            box-shadow: {image_style.get('shadow', '0 4px 8px rgba(0,0,0,0.1)')};
            margin: 1em 0;
        }}
        """)
    
    return '\n'.join(css_rules)

if __name__ == "__main__":
    # 测试文档解析
    test_content = """
# 测试文档

这是一个测试段落。

## 二级标题

![测试图片](test.jpg)

- 列表项1
- 列表项2

[链接](https://example.com)
"""
    
    result = parse_document(test_content, "markdown")
    print(json.dumps(result, ensure_ascii=False, indent=2))