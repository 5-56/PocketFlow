# 🎨 智能文档自动排版系统

> 基于 PocketFlow 框架构建的智能文档处理系统，一句话完成文档格式化、排版和图片统一！

## ✨ 功能特色

- **🗣️ 自然语言交互**: 用一句话描述需求，AI自动理解并执行
- **🎨 智能排版设计**: 自动分析文档结构，生成专业的排版方案
- **🖼️ 图片统一处理**: 自动调整图片尺寸、添加效果、统一风格
- **📄 多格式支持**: 输出HTML、Markdown等多种格式
- **⚡ 批量处理**: 支持批量处理多个文档
- **🔧 灵活配置**: 支持完整处理、快速格式化、仅图片处理等模式

## 📋 系统要求

- Python 3.8+
- OpenAI API Key（用于LLM功能）
- 网络连接（API调用）

## 🚀 快速开始

### 1. 安装依赖

```bash
# 克隆项目（如果是本地开发）
# git clone <repository-url>
# cd document-processor

# 安装依赖
pip install -r requirements.txt
```

### 2. 设置API密钥

```bash
# 设置OpenAI API密钥
export OPENAI_API_KEY="your-api-key-here"

# Windows用户可以使用
# set OPENAI_API_KEY=your-api-key-here
```

### 3. 运行系统

```bash
# 交互式模式（推荐新手）
python main.py

# 快速处理单个文件
python main.py -f document.md -i "转换为现代商务风格的HTML文档"

# 批量处理
python main.py -b input_folder output_folder -i "统一格式为学术论文风格"
```

## 📖 使用示例

### 交互式模式

```bash
$ python main.py

============================================================
🎨 智能文档自动排版系统
============================================================
让AI帮您一句话完成文档的格式化和排版！

📝 请描述您想要的文档格式（例如：
   • '请帮我生成一个现代商务风格的HTML文档，图片统一加圆角边框'
   • '转换成学术论文格式，使用蓝白配色方案'
   • '制作一个创意设计文档，图片添加阴影效果'

💬 您的需求: 请帮我生成一个现代商务风格的HTML文档，图片统一加圆角边框
```

### 命令行模式

```bash
# 处理Markdown文件
python main.py -f report.md -i "转换为学术论文格式，使用蓝白配色"

# 仅图片处理
python main.py -f document.md -i "图片添加阴影效果" -t image

# 快速格式化
python main.py -f text.md -i "现代简约风格" -t simple
```

### 批量处理

```bash
# 批量处理目录中的所有文档
python main.py -b ./documents ./output -i "统一转换为商务报告格式"
```

## 🎯 支持的指令示例

### 风格指令
- "现代商务风格"
- "学术论文格式"
- "创意设计文档"
- "技术报告风格"
- "简约清新风格"

### 配色指令
- "蓝白配色方案"
- "深色主题"
- "暖色调设计"
- "科技感配色"

### 图片处理指令
- "图片统一加圆角边框"
- "添加阴影效果"
- "图片居中对齐"
- "统一图片尺寸"

### 复合指令
- "生成现代商务风格的HTML文档，图片加圆角边框，使用蓝白配色"
- "转换为学术论文格式，图片添加阴影，段落间距加大"

## 🏗️ 系统架构

系统采用 **工作流（Workflow）** 设计模式，包含以下核心节点：

```mermaid
flowchart LR
    A[解析用户需求] --> B[分析文档结构]
    B --> C[设计排版方案]
    C --> D[处理文本格式]
    D --> E[统一图片样式]
    E --> F[生成最终文档]
```

### 核心组件

1. **ParseRequirementNode**: 解析用户的自然语言需求
2. **AnalyzeDocumentNode**: 分析文档结构和内容
3. **DesignLayoutNode**: 设计排版方案和样式
4. **ProcessTextNode**: 处理文本格式和结构
5. **UnifyImagesNode**: 统一图片样式和效果
6. **GenerateDocumentNode**: 生成最终格式化文档

## 📁 项目结构

```
.
├── docs/
│   └── design.md          # 系统设计文档
├── utils/
│   ├── __init__.py
│   ├── call_llm.py       # LLM调用工具
│   ├── document_processor.py  # 文档处理工具
│   └── image_processor.py     # 图片处理工具
├── nodes.py              # 工作流节点定义
├── flow.py               # 工作流构建
├── main.py               # 主应用程序
├── requirements.txt      # 依赖列表
└── README.md            # 说明文档
```

## ⚙️ 配置选项

### 处理类型

- **complete**: 完整处理（包含图片优化）
- **simple**: 快速格式化（仅文本）
- **image**: 仅图片处理

### 支持的输入格式

- Markdown (`.md`, `.markdown`)
- 纯文本 (`.txt`)

### 支持的输出格式

- HTML（带CSS样式）
- Markdown（优化后）
- 其他格式（基础支持）

## 🔧 自定义扩展

### 添加新的文档格式支持

在 `utils/document_processor.py` 中添加新的解析函数：

```python
def parse_your_format(content: str) -> Dict[str, Any]:
    # 实现您的格式解析逻辑
    return document_structure
```

### 添加新的图片效果

在 `utils/image_processor.py` 中添加新的处理函数：

```python
def add_your_effect(image: Image.Image, **kwargs) -> Image.Image:
    # 实现您的图片效果
    return processed_image
```

### 自定义工作流

在 `flow.py` 中创建新的工作流：

```python
def create_custom_flow():
    # 创建自定义节点组合
    node1 = CustomNode()
    node2 = AnotherNode()
    
    node1 >> node2
    return Flow(start=node1)
```

## 📊 性能优化

- **重试机制**: 内置LLM调用重试，提高稳定性
- **错误处理**: 完善的错误处理和回退机制
- **日志记录**: 详细的处理日志，便于调试
- **批量处理**: 支持大规模文档批量处理

## 🐛 故障排除

### 常见问题

1. **API密钥错误**
   ```
   ⚠️ 警告: 未设置 OPENAI_API_KEY 环境变量
   ```
   解决方案: 正确设置OpenAI API密钥

2. **依赖包缺失**
   ```
   ModuleNotFoundError: No module named 'xxx'
   ```
   解决方案: 运行 `pip install -r requirements.txt`

3. **文件路径错误**
   ```
   ❌ 文件不存在: document.md
   ```
   解决方案: 检查文件路径是否正确

### 调试模式

查看详细日志：

```bash
# 日志会自动保存到 document_processor.log
tail -f document_processor.log
```

## 🤝 贡献指南

欢迎贡献代码和建议！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🔗 相关链接

- [PocketFlow 框架](https://github.com/The-Pocket/PocketFlow)
- [OpenAI API 文档](https://platform.openai.com/docs)
- [项目设计文档](docs/design.md)

## 💡 使用技巧

1. **明确描述需求**: 越具体的描述，AI理解得越准确
2. **分步处理**: 复杂文档可以先用简化模式快速查看效果
3. **批量优化**: 处理多个相似文档时使用批量模式
4. **样式复用**: 记录满意的指令模板，便于重复使用

---

**让AI帮您轻松完成文档排版，专注于内容创作！** 🚀


