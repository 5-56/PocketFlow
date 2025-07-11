# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main_enhanced.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('static', 'static'),
        ('templates', 'templates'),
        ('utils', 'utils'),
        ('pocketflow', 'pocketflow'),
        ('version.json', '.'),
        ('requirements_enhanced.txt', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        # 核心框架
        'pocketflow',
        'flow',
        'nodes',
        
        # Web框架
        'fastapi',
        'fastapi.staticfiles',
        'fastapi.templating',
        'uvicorn',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'websockets',
        'aiofiles',
        'jinja2',
        
        # AI和数据处理
        'openai',
        'pydantic',
        'pydantic_settings',
        'markdown',
        'PIL',
        'PIL.Image',
        'PIL.ImageEnhance',
        'PIL.ImageFilter',
        
        # 系统和工具
        'asyncio',
        'concurrent.futures',
        'logging.handlers',
        'json',
        'yaml',
        'pathlib',
        'datetime',
        'psutil',
        
        # HTTP和网络
        'httpx',
        'aiohttp',
        'requests',
        'urllib3',
        
        # 文档处理（可选）
        'pypdf',
        'docx',
        'pptx',
        
        # 数据库和缓存（可选）
        'redis',
        'aioredis',
        
        # 向量数据库（可选）
        'chromadb',
        'sentence_transformers',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的包
        'tkinter',
        'matplotlib',
        'scipy',
        'sklearn',
        'tensorflow',
        'torch',
        'numpy.f2py',
        'numpy.distutils',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DocumentProcessor-Enhanced-linux',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)
