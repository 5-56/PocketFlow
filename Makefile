# 智能文档处理系统 - Makefile
# 简化构建、测试和发布流程

.PHONY: help install build test clean release package deps-build deps-dev

# 默认目标
help:
	@echo "🎨 智能文档处理系统 - 构建工具"
	@echo "=================================="
	@echo ""
	@echo "📋 可用命令:"
	@echo "  install      - 安装运行时依赖"
	@echo "  deps-build   - 安装构建依赖"
	@echo "  deps-dev     - 安装开发依赖"
	@echo "  build        - 构建可执行文件"
	@echo "  test         - 运行测试"
	@echo "  clean        - 清理构建文件"
	@echo "  package      - 创建发布包"
	@echo "  release      - 创建新版本发布"
	@echo "  quick        - 快速构建和打包"
	@echo ""

# 安装运行时依赖
install:
	@echo "📦 安装运行时依赖..."
	pip install -r requirements.txt
	@echo "✅ 依赖安装完成"

# 安装构建依赖
deps-build:
	@echo "🔧 安装构建依赖..."
	pip install -r requirements-build.txt
	@echo "✅ 构建依赖安装完成"

# 安装开发依赖（包含构建工具）
deps-dev: deps-build
	@echo "🛠️  安装开发依赖..."
	pip install black flake8 pytest
	@echo "✅ 开发依赖安装完成"

# 构建可执行文件
build: deps-build
	@echo "🔨 开始构建可执行文件..."
	python build.py
	@echo "✅ 构建完成"

# 运行测试
test:
	@echo "🧪 运行功能测试..."
	python demo.py
	@echo "🧪 运行基本功能测试..."
	python main.py --help
	@echo "✅ 测试完成"

# 清理构建文件
clean:
	@echo "🧹 清理构建文件..."
	rm -rf build/
	rm -rf dist/
	rm -rf release/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ 清理完成"

# 创建发布包
package: build
	@echo "📦 创建发布包..."
	@if [ ! -d "dist" ]; then echo "❌ 构建目录不存在，请先运行 make build"; exit 1; fi
	@echo "✅ 发布包创建完成"

# 快速构建和打包
quick: clean build package
	@echo "⚡ 快速构建完成"
	@ls -la release/ 2>/dev/null || echo "📦 发布包位置: release/"

# 创建新版本发布（patch升级）
release:
	@echo "🚀 创建新版本发布..."
	python release.py
	@echo "✅ 发布流程启动完成"

# 创建主要版本发布
release-minor:
	@echo "🚀 创建次要版本发布..."
	python release.py --bump minor

# 创建重大版本发布
release-major:
	@echo "🚀 创建重大版本发布..."
	python release.py --bump major

# 仅构建不发布
build-only:
	@echo "🔨 仅构建模式..."
	python release.py --build-only

# 检查版本信息
version:
	@echo "📋 当前版本信息:"
	@python -c "import json; print('版本:', json.load(open('version.json'))['version'])" 2>/dev/null || echo "版本文件不存在"

# 显示项目统计
stats:
	@echo "📊 项目统计:"
	@echo "Python文件数: $$(find . -name "*.py" | wc -l)"
	@echo "代码行数: $$(find . -name "*.py" -exec cat {} \; | wc -l)"
	@echo "文档文件数: $$(find . -name "*.md" | wc -l)"

# 格式化代码（如果安装了black）
format:
	@echo "🎨 格式化代码..."
	@black . 2>/dev/null || echo "请安装 black: pip install black"
	@echo "✅ 代码格式化完成"

# 代码检查（如果安装了flake8）
lint:
	@echo "🔍 代码质量检查..."
	@flake8 . --max-line-length=88 2>/dev/null || echo "请安装 flake8: pip install flake8"
	@echo "✅ 代码检查完成"

# 完整的质量检查流程
check: lint test
	@echo "✅ 完整质量检查完成"

# 准备发布前检查
pre-release: clean check build test
	@echo "🎯 发布前检查完成，可以安全发布"