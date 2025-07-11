# 🚀 智能文档处理系统 v2.0.0 - 快速开始

## 📥 下载与安装

### 1. 下载可执行文件
访问 [GitHub Releases](https://github.com/5-56/PocketFlow/releases/latest) 下载适合您平台的版本：

- **Windows**: `DocumentProcessor-Optimized-2.0.0-win64.zip`
- **Linux**: `DocumentProcessor-Optimized-2.0.0-linux-x64.tar.gz`

### 2. 设置API密钥
```bash
# Windows
set OPENAI_API_KEY=your_api_key_here

# Linux/Mac
export OPENAI_API_KEY=your_api_key_here
```

## 🌐 Web服务模式 (推荐)

### 启动Web服务
```bash
# Windows
DocumentProcessor-Optimized.exe --web

# Linux
./DocumentProcessor-Optimized-linux --web
```

### 访问Web界面
打开浏览器访问：http://localhost:8000

### 功能特色
- 📱 现代化响应式界面
- 🔗 实时进度更新
- 📊 系统状态监控
- 🔄 批量处理支持
- 👥 多用户协作

## 💻 命令行模式

### 单文档处理
```bash
# 基本用法
./DocumentProcessor-Optimized --cli \
  -f document.md \
  -i "转换为现代商务风格的HTML文档"

# 指定输出格式
./DocumentProcessor-Optimized --cli \
  -f document.md \
  -i "生成学术论文格式" \
  --format PDF \
  --strategy complete
```

### 批量处理
```bash
# 批量处理多个文档
./DocumentProcessor-Optimized --batch \
  --pattern "docs/*.md" \
  -i "统一转换为企业标准格式" \
  --max-concurrent 5
```

## 📋 使用示例

### 常用指令示例
```bash
# 商务文档
"转换为现代商务风格的HTML文档，图片加圆角边框"

# 学术论文
"生成学术论文格式，使用蓝白配色方案，严格的段落结构"

# 技术文档
"制作技术文档格式，代码块高亮，添加目录导航"

# 创意设计
"创建创意设计文档，图片添加阴影效果，使用暖色调"

# 产品介绍
"生成产品展示文档，突出特性，添加视觉效果"
```

### 处理策略选择
- **auto**: 智能自动选择 (推荐)
- **complete**: 完整处理，包含所有优化
- **quick**: 快速处理，适合简单任务
- **text_only**: 仅处理文本，跳过图片
- **analysis_focus**: 重点分析和优化

### 输出格式支持
- **HTML**: 响应式网页文档
- **PDF**: 高质量PDF文档
- **DOCX**: Microsoft Word格式
- **PPTX**: PowerPoint演示文稿
- **MARKDOWN**: 优化的Markdown

## 🔧 高级用法

### API调用
系统提供完整的RESTful API：

```python
import requests

# 单文档处理
response = requests.post('http://localhost:8000/api/process', json={
    'content': '# 我的文档\n\n这是文档内容...',
    'instruction': '转换为现代商务格式',
    'processing_strategy': 'auto',
    'output_format': 'HTML'
})

# 检查处理状态
session_id = response.json()['session_id']
status = requests.get(f'http://localhost:8000/api/session/{session_id}')
```

### WebSocket实时通信
```javascript
// 连接WebSocket获取实时进度
const ws = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);

ws.onmessage = function(event) {
    const message = JSON.parse(event.data);
    if (message.type === 'progress_update') {
        console.log(`进度: ${message.progress}%`);
    }
};
```

## 📊 性能监控

### 系统状态查询
```bash
# 查看系统状态
curl http://localhost:8000/api/status

# 清空缓存
curl -X POST http://localhost:8000/api/clear-cache
```

### 性能指标
- **处理速度**: < 10秒 (1000字符文档)
- **Web响应**: < 500ms (实时预览)
- **并发能力**: 100+ 同时会话
- **缓存命中率**: 80%+ 目标

## 🐛 故障排除

### 常见问题

1. **API密钥错误**
   ```
   错误: API key not found
   解决: 正确设置 OPENAI_API_KEY 环境变量
   ```

2. **端口被占用**
   ```
   错误: Port 8000 already in use
   解决: 使用 --port 参数指定其他端口
   ./DocumentProcessor-Optimized --web --port 8080
   ```

3. **内存不足**
   ```
   错误: Out of memory
   解决: 减少并发数或使用 text_only 策略
   ```

### 调试模式
```bash
# 启用详细日志
./DocumentProcessor-Optimized --web --log-level DEBUG

# 查看日志文件
tail -f document_processor.log
```

## 🔗 更多资源

- **完整文档**: [README.md](README.md)
- **发布说明**: [RELEASE.md](RELEASE.md)
- **API文档**: http://localhost:8000/api/docs
- **GitHub仓库**: https://github.com/5-56/PocketFlow
- **问题反馈**: https://github.com/5-56/PocketFlow/issues

## 💡 使用技巧

1. **明确指令**: 越具体的描述，AI理解得越准确
2. **选择合适策略**: 根据文档复杂度选择处理策略
3. **利用缓存**: 相似文档会自动使用缓存提升速度
4. **批量优化**: 处理多个文档时使用批量模式
5. **监控性能**: 通过Web界面查看实时性能指标

---

**🎯 开始您的智能文档处理之旅吧！** 🚀