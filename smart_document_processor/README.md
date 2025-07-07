# 智能文档处理系统 - AI增强版WPS

一个基于PocketFlow框架的智能文档处理系统，集成了现代富文本编辑器和AI增强功能，提供类似WPS Office的用户体验。

## 🌟 主要特性

### � 富文本编辑器
- **完整的编辑功能**：字体、字号、颜色、加粗、斜体、下划线、删除线
- **段落格式**：对齐方式、缩进、行间距、标题层级
- **列表支持**：有序列表、无序列表
- **多媒体元素**：图片插入、表格创建、链接添加
- **文档结构**：实时大纲生成、标题导航
- **版本管理**：自动版本快照、版本历史浏览、版本恢复
- **快捷键支持**：Ctrl+B/I/U、Ctrl+S、Ctrl+Z/Y等

### 🤖 AI智能助手
- **快速操作**：润色、扩写、缩写、翻译、正式化、口语化
- **右键菜单**：选中文本即可快速AI处理
- **自定义指令**：支持用户自定义处理指令
- **实时聊天**：与AI助手实时对话交流
- **智能建议**：基于上下文的智能建议

### 🎛️ AI设置管理
- **模型配置**：支持GPT-4、Claude等多种AI模型
- **参数调节**：Token数量、创造性水平、响应风格
- **语言设置**：多语言支持
- **提示词管理**：自定义系统提示词
- **连接测试**：API连接状态检测

### � 文档处理能力
- **多格式支持**：Word (.docx)、PDF、TXT、HTML
- **批量处理**：支持批量文档处理
- **AI增强**：智能内容优化和格式调整
- **图像处理**：图片编辑、AI图像分析
- **导出功能**：多格式导出（Word、PDF、HTML、Markdown、TXT）

### 🎨 现代化界面
- **WPS Office风格**：熟悉的三栏布局设计
- **响应式设计**：适配不同屏幕尺寸
- **主题支持**：专业的视觉设计
- **实时预览**：所见即所得编辑体验

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 14+ (可选，用于前端开发)

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置环境变量
```bash
# 创建 .env 文件
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

### 启动服务
```bash
python main.py
```

访问 http://localhost:8000 开始使用

## 📁 项目结构

```
smart_document_processor/
├── main.py                 # FastAPI主应用
├── requirements.txt        # Python依赖
├── pocketflow.py          # PocketFlow核心框架
├── nodes.py               # 工作流节点定义
├── flows.py               # 工作流编排
├── utils/                 # 工具模块
│   ├── ai_processor.py    # AI处理器
│   ├── document_parser.py # 文档解析器
│   ├── image_processor.py # 图像处理器
│   └── document_generator.py # 文档生成器
├── templates/             # 页面模板
│   └── index.html        # 主页面
└── static/               # 静态资源
    ├── css/
    │   ├── style.css     # 主样式
    │   └── editor.css    # 编辑器样式
    └── js/
        ├── app.js        # 主应用逻辑
        ├── editor.js     # 富文本编辑器
        ├── websocket.js  # WebSocket通信
        └── document-handler.js # 文档处理
```

## 💡 技术架构

### 后端架构
- **框架**：FastAPI + Uvicorn
- **工作流引擎**：PocketFlow (100行极简LLM框架)
- **AI集成**：OpenAI GPT-4 / Claude
- **异步处理**：支持异步和批处理
- **实时通信**：WebSocket

### 前端技术
- **核心**：原生JavaScript (ES6+)
- **UI框架**：自定义组件系统
- **样式**：CSS3 + Flexbox/Grid
- **图标**：Font Awesome 6
- **字体**：Inter / Google Fonts

### 核心设计模式
- **工作流编排**：基于PocketFlow的节点和流
- **事件驱动**：WebSocket实时状态同步
- **模块化设计**：各功能模块独立可扩展
- **插件架构**：支持功能插件扩展

## 🔧 API接口

### 文档操作
- `POST /api/upload` - 上传文档
- `GET /api/document/{doc_id}` - 获取文档
- `POST /api/process` - 处理文档
- `POST /api/export` - 导出文档

### AI功能
- `POST /api/ai/chat` - AI聊天
- `POST /api/ai/quick-action` - 快速AI操作
- `GET /api/ai/settings` - 获取AI设置
- `POST /api/ai/settings` - 保存AI设置
- `POST /api/ai/test-connection` - 测试AI连接

### 编辑功能
- `POST /api/edit/text` - 文本编辑
- `POST /api/edit/image` - 图像编辑
- `POST /api/ai/enhance` - AI增强

## 🎯 使用场景

### 个人用户
- **文档写作**：博客文章、学术论文、工作报告
- **内容优化**：AI润色、语法检查、风格调整
- **多语言处理**：翻译、本地化、跨语言编辑

### 企业用户
- **团队协作**：实时文档编辑、版本管理
- **内容标准化**：统一文档风格和格式
- **批量处理**：大量文档的自动化处理

### 教育场景
- **论文写作**：学术写作辅助、引用管理
- **教学资料**：课件制作、教案编写
- **作业批改**：AI辅助评价和建议

## 🔮 未来规划

### 近期功能
- [ ] 协作编辑：多用户实时协作
- [ ] 模板系统：丰富的文档模板
- [ ] 插件市场：第三方功能插件
- [ ] 移动端适配：响应式移动体验

### 中期目标
- [ ] 云存储集成：OneDrive、Google Drive
- [ ] 高级AI功能：图表生成、数据分析
- [ ] 工作流自动化：自定义处理流程
- [ ] API开放平台：第三方集成

### 长期愿景
- [ ] 企业级部署：私有化部署方案
- [ ] 多语言支持：界面多语言化
- [ ] AI训练：领域特定模型训练
- [ ] 生态建设：开发者社区建设

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发流程
1. Fork项目到个人仓库
2. 创建功能分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -am 'Add new feature'`
4. 推送分支：`git push origin feature/new-feature`
5. 创建Pull Request

### 代码规范
- Python代码遵循PEP 8标准
- JavaScript使用ES6+语法
- CSS使用BEM命名规范
- 提交信息使用约定式提交格式

## 📄 许可证

本项目采用MIT许可证 - 详见[LICENSE](LICENSE)文件

## 🙏 致谢

- [PocketFlow](https://github.com/the-pocket/PocketFlow) - 极简LLM工作流框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Web框架
- [OpenAI](https://openai.com/) - AI能力支持
- [Font Awesome](https://fontawesome.com/) - 图标支持

---

**智能文档处理系统** - 让文档编辑更智能，让工作更高效！ 🚀