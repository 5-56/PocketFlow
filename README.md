# 🎨 智能文档自动排版系统

> 基于 PocketFlow 框架构建的智能文档处理系统，一句话完成文档格式化、排版和图片统一！

## ✨ 功能特色

- **🗣️ 自然语言交互**: 用一句话描述需求，AI自动理解并执行
- **🎨 智能排版设计**: 自动分析文档结构，生成专业的排版方案
- **🖼️ 图片统一处理**: 自动调整图片尺寸、添加效果、统一风格
- **📄 多格式输出**: 支持HTML、PDF、Word、PowerPoint、Markdown
- **📊 智能内容分析**: 自动分析文档质量，提供优化建议
- **🎯 模板智能推荐**: 基于内容特征推荐最适合的排版模板
- **⚡ 批量处理**: 支持批量处理多个文档
- **� 实时预览调整**: 交互式调整和预览功能
- **💾 会话记录**: 自动保存处理历史和用户偏好

## 📋 系统要求

- Python 3.8+
- OpenAI API Key（用于LLM功能）
- 网络连接（API调用）

## 🚀 快速开始

### 方式一：下载可执行文件（推荐）

1. **访问发布页面**: [GitHub Releases](../../releases) 下载最新版本
2. **选择对应平台**:
   - Windows: `DocumentProcessor-Enhanced-v*-win64.zip`
   - Linux: `DocumentProcessor-Enhanced-v*-linux-x64.tar.gz`
3. **解压并设置API密钥**:
   ```bash
   # Windows
   set OPENAI_API_KEY=your_api_key_here
   
   # Linux
   export OPENAI_API_KEY=your_api_key_here
   ```
4. **运行程序**:
   ```bash
   # Windows - 双击启动.bat或
   DocumentProcessor-Enhanced.exe --web
   
   # Linux - 运行./start.sh或
   ./DocumentProcessor-Enhanced --web
   ```

### 方式二：从源码安装

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
# 增强版主程序（推荐，统一入口）
python main_enhanced.py --web         # Web服务模式
python main_enhanced.py --cli         # 命令行模式
python main_enhanced.py --info        # 系统信息
python main_enhanced.py --test        # API测试

# 优化版（高性能）
python start_optimized.py --web

# 基础版本
python main.py                        # 交互模式
python main.py -f document.md -i "转换为现代商务风格"

# 多格式输出
python main_enhanced.py --cli         # 然后选择输出格式

# 批量处理
python main.py -b input_folder output_folder -i "统一格式"

# Web服务模式（推荐）
python main_enhanced.py --web --port 8000
# 然后访问 http://localhost:8000
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

## 🆕 新功能亮点

### � 智能内容分析
- **文档质量评估**：自动评分文档的可读性、结构性和内容质量
- **优化建议**：提供具体的改进建议和行动指导
- **统计分析**：词数、句数、段落分布等详细统计

### 🎯 模板智能推荐
- **5种专业模板**：商务报告、学术论文、创意设计、技术文档、产品介绍
- **智能匹配**：基于内容特征和用户指令自动推荐最合适的模板
- **使用统计**：跟踪模板使用情况和用户评价

### 📄 多格式输出支持
- **PDF文档**：高质量PDF生成，适合打印和分发
- **Word文档**：标准DOCX格式，便于进一步编辑
- **PowerPoint**：自动转换为演示文稿格式
- **HTML网页**：响应式设计，适合在线展示

### 🔄 增强交互体验
- **实时预览**：即时查看处理结果
- **迭代调整**：支持多轮对话式优化
- **会话保存**：自动保存处理历史
- **个性化偏好**：记忆用户的样式偏好

## �📁 项目结构

```
.
├── docs/
│   └── design.md          # 系统设计文档
├── utils/
│   ├── __init__.py
│   ├── call_llm.py       # LLM调用工具
│   ├── document_processor.py  # 文档处理工具
│   ├── image_processor.py     # 图片处理工具
│   ├── content_analyzer.py    # 智能内容分析
│   ├── format_converter.py    # 多格式转换器
│   └── template_manager.py    # 模板管理系统
├── templates/             # 文档模板存储
├── sessions/              # 会话记录存储
├── output/               # 输出文件目录
├── nodes.py              # 工作流节点定义
├── flow.py               # 工作流构建
├── main.py               # 主应用程序
├── interactive_ui.py     # 增强交互界面
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

- **HTML**：带完整CSS样式的网页文档
- **PDF**：高质量PDF文档（需要weasyprint）
- **DOCX**：Microsoft Word格式（需要python-docx）
- **PPTX**：PowerPoint演示文稿（需要python-pptx）
- **Markdown**：优化后的Markdown格式

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

## 🔧 构建和发布

### 本地构建

#### Windows
```bash
# 使用快速构建脚本
quick_build.bat

# 或手动构建
pip install -r requirements-build.txt
python build.py
```

#### Linux
```bash
# 使用快速构建脚本
chmod +x quick_build.sh
./quick_build.sh

# 或手动构建
pip3 install -r requirements-build.txt
python3 build.py
```

### 自动发布

#### 创建Release
```bash
# 使用发布脚本（patch版本升级）
python release.py

# 手动指定版本
python release.py --version 1.2.0

# 仅构建不发布
python release.py --build-only
```

#### GitHub Actions
推送版本标签会自动触发构建和发布：
```bash
git tag v1.0.0
git push origin v1.0.0
```

### 构建配置

- **build_config.spec**: PyInstaller配置文件
- **version_info.txt**: Windows可执行文件版本信息
- **requirements-build.txt**: 构建专用依赖列表
- **.github/workflows/build-release.yml**: CI/CD工作流

## 🤝 贡献指南

欢迎贡献代码和建议！

### 开发环境设置

1. **Fork并克隆项目**
   ```bash
   git clone https://github.com/your-username/document-processor.git
   cd document-processor
   ```

2. **安装开发依赖**
   ```bash
   pip install -r requirements-build.txt
   ```

3. **运行测试**
   ```bash
   python demo.py  # 运行功能演示
   python main.py --help  # 测试基本功能
   ```

### 贡献流程

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 代码规范

- 遵循PEP 8编码规范
- 添加必要的文档字符串
- 确保新功能有相应的测试
- 更新README文档（如果需要）

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🔗 相关链接

- [PocketFlow 框架](https://github.com/The-Pocket/PocketFlow)
- [OpenAI API 文档](https://platform.openai.com/docs)
- [项目设计文档](docs/design.md)

## 💡 使用技巧

1. **明确描述需求**: 越具体的描述，AI理解得越准确
2. **利用文档分析**: 使用 `--analysis` 参数获取优化建议
3. **善用模板推荐**: 使用 `--templates` 参数获取专业模板建议
4. **选择合适格式**: 根据用途选择最适合的输出格式
5. **增强交互模式**: 使用 `--enhanced` 体验完整功能
6. **批量优化**: 处理多个相似文档时使用批量模式
7. **样式复用**: 记录满意的指令模板，便于重复使用
8. **会话管理**: 查看 `sessions/` 目录了解历史处理记录

---

**让AI帮您轻松完成文档排版，专注于内容创作！** 🚀


