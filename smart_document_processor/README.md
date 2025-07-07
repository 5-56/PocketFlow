# 智能文档处理系统

基于PocketFlow框架的AI增强文档处理系统，具有类似WPS Office的现代化界面。

## 功能特性

### 🚀 核心功能
- **多格式文档解析** - 支持Word、PDF、TXT、HTML等格式
- **AI智能处理** - 使用大语言模型优化文档内容
- **图像智能编辑** - 自动分析和处理文档中的图片
- **多格式导出** - 支持导出为Word、PDF、HTML格式
- **实时协作** - WebSocket实时状态更新

### 🎨 界面特性
- **WPS Office风格界面** - 熟悉的操作体验
- **响应式设计** - 支持桌面和移动设备
- **拖拽上传** - 便捷的文件上传方式
- **实时进度显示** - 处理进度实时更新
- **智能通知系统** - 优雅的消息提示

### 🤖 AI功能
- **多种文本风格** - 专业、学术、商务、创意风格
- **图像分析** - 自动生成图片描述和优化建议
- **内容优化** - 改善文档结构和可读性
- **智能建议** - 基于内容提供改进建议

### 🔧 技术特性
- **基于PocketFlow** - 轻量级工作流框架
- **异步处理** - 高性能文档处理
- **模块化设计** - 易于扩展和维护
- **容错机制** - 自动重试和降级处理

## 系统架构

```
智能文档处理系统
├── 前端界面 (HTML + CSS + JavaScript)
│   ├── WPS Office风格UI
│   ├── 实时状态更新
│   └── 响应式设计
├── 后端API (FastAPI)
│   ├── 文档上传和管理
│   ├── WebSocket通信
│   └── 多格式导出
├── PocketFlow工作流
│   ├── 文档解析节点
│   ├── AI处理节点
│   ├── 图像处理节点
│   └── 文档生成节点
└── 工具模块
    ├── 文档解析器
    ├── AI处理器
    ├── 图像处理器
    └── 文档生成器
```

## 快速开始

### 环境要求
- Python 3.8+
- Node.js (可选，用于前端开发)

### 安装依赖
```bash
cd smart_document_processor
pip install -r requirements.txt
```

### 配置环境变量
```bash
# 设置OpenAI API密钥
export OPENAI_API_KEY="your-openai-api-key"

# 或者创建 .env 文件
echo "OPENAI_API_KEY=your-openai-api-key" > .env
```

### 启动系统
```bash
# 开发模式
python main.py

# 或使用uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 访问系统
打开浏览器访问: http://localhost:8000

## 使用指南

### 1. 上传文档
- 点击"上传文档"按钮选择文件
- 或直接拖拽文件到上传区域
- 支持的格式：.docx, .pdf, .txt, .html

### 2. AI处理
- 选择已上传的文档
- 点击"AI处理"按钮
- 输入处理指令（可选）
- 选择处理选项和文本风格
- 点击"开始处理"

### 3. 内容编辑
- 使用AI增强功能优化文档
- 手动编辑文本内容
- 调整图片大小和效果
- 实时预览修改结果

### 4. 导出文档
- 点击"导出"按钮
- 选择导出格式（Word/PDF/HTML）
- 选择模板类型和导出选项
- 点击"导出"下载文件

## 配置说明

### AI模型配置
在 `utils/ai_processor.py` 中配置AI模型：
```python
# 支持的模型
self.text_model = "gpt-4"
self.vision_model = "gpt-4-vision-preview"

# 参数调整
self.max_tokens = 4000
self.temperature = 0.7
```

### 文档处理配置
在 `utils/document_parser.py` 中配置支持的格式：
```python
self.supported_formats = {
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'application/pdf': 'pdf',
    'text/plain': 'txt',
    'text/html': 'html'
}
```

### 图像处理配置
在 `utils/image_processor.py` 中配置图像参数：
```python
self.supported_formats = ['JPEG', 'PNG', 'BMP', 'TIFF', 'WEBP']
self.max_size = (4096, 4096)  # 最大尺寸限制
```

## 开发指南

### 添加新的处理节点
1. 在 `nodes.py` 中创建新的节点类
2. 继承适当的基类（Node, AsyncNode, BatchNode等）
3. 实现 `prep()`, `exec()`, `post()` 方法
4. 在 `flows.py` 中连接到工作流

### 添加新的文档格式
1. 在 `utils/document_parser.py` 中添加解析方法
2. 在 `utils/document_generator.py` 中添加生成方法
3. 更新支持的格式列表
4. 测试新格式的完整流程

### 自定义AI处理
1. 在 `utils/ai_processor.py` 中添加新的处理方法
2. 创建新的提示模板
3. 在前端添加对应的选项
4. 更新API接口

## 部署指南

### Docker部署
```bash
# 构建镜像
docker build -t smart-document-processor .

# 运行容器
docker run -d -p 8000:8000 \
  -e OPENAI_API_KEY="your-key" \
  smart-document-processor
```

### 生产环境
```bash
# 使用Gunicorn部署
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 使用Nginx反向代理
# 配置SSL证书
# 设置负载均衡
```

## 故障排除

### 常见问题

1. **上传失败**
   - 检查文件大小是否超过50MB限制
   - 确认文件格式是否受支持
   - 检查网络连接

2. **AI处理失败**
   - 验证OpenAI API密钥是否正确
   - 检查API使用额度
   - 查看服务器日志获取详细错误信息

3. **图像处理问题**
   - 确认图像格式是否受支持
   - 检查图像文件是否损坏
   - 验证图像尺寸是否过大

4. **导出失败**
   - 确认文档已经过AI处理
   - 检查导出格式是否正确
   - 查看系统日志获取错误详情

### 日志查看
```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- 项目主页：[GitHub Repository]
- 问题反馈：[GitHub Issues]
- 邮箱：your-email@example.com

## 致谢

- [PocketFlow](https://github.com/the-pocket/PocketFlow) - 核心工作流框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化Web框架
- [OpenAI](https://openai.com/) - AI模型支持
- 所有贡献者和测试用户

---

**智能文档处理系统** - 让文档处理更智能、更高效