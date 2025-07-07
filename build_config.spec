# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from pathlib import Path

# 获取项目根目录
project_root = Path(__file__).parent

# 分析main.py的依赖
a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # 包含utils目录
        ('utils', 'utils'),
        # 包含模板文件（如果存在）
        ('templates', 'templates'),
        # 包含必要的数据文件
        ('README.md', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'pocketflow',
        'openai', 
        'markdown',
        'PIL',
        'yaml',
        'weasyprint',
        'docx',
        'pptx',
        'beautifulsoup4',
        'lxml',
        # 确保所有可选依赖都被包含
        'utils.content_analyzer',
        'utils.format_converter', 
        'utils.template_manager',
        'interactive_ui',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不必要的模块以减小文件大小
        'tkinter',
        'matplotlib',
        'scipy',
        'numpy.distutils',
        'setuptools',
        'pip',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# 移除重复的二进制文件
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 创建可执行文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DocumentProcessor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 保持控制台窗口，便于用户交互
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
)

# 如果需要创建目录结构（用于--onedir模式）
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='DocumentProcessor'
# )