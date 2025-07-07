# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from pathlib import Path

# 获取项目根目录
project_root = Path('.')

# 分析main.py的依赖
a = Analysis(
    ['main_minimal.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # 包含必要的文件
        ('README.md', '.'),
        ('requirements.txt', '.'),
        ('version.json', '.'),
    ],
    hiddenimports=[
        'pocketflow',
        # 基础Python模块
        'json',
        'os',
        'sys',
        'argparse',
        'pathlib',
        'logging',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除大型依赖以减小文件大小
        'tkinter',
        'matplotlib',
        'scipy',
        'numpy',
        'pandas',
        'PIL',
        'weasyprint',
        'docx',
        'pptx',
        'beautifulsoup4',
        'lxml',
        'openai',
        'markdown',
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
    console=True,  # 保持控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)