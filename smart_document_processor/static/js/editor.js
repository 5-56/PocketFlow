/**
 * Rich Text Editor - 富文本编辑器核心功能
 */

class RichTextEditor {
    constructor(containerSelector) {
        this.container = document.querySelector(containerSelector);
        this.editor = null;
        this.toolbar = null;
        this.outline = null;
        this.contextMenu = null;
        
        // 编辑器状态
        this.currentDocument = null;
        this.isEditing = false;
        this.selectedText = '';
        this.selectedElement = null;
        this.versions = [];
        this.currentVersion = 0;
        
        // 初始化编辑器
        this.init();
    }
    
    init() {
        this.createEditor();
        this.createToolbar();
        this.createOutline();
        this.createContextMenu();
        this.bindEvents();
        
        console.log('📝 富文本编辑器已初始化');
    }
    
    createEditor() {
        const editorHTML = `
            <div class="editor-container">
                <div class="editor-toolbar" id="editorToolbar">
                    <!-- 工具栏将动态创建 -->
                </div>
                <div class="editor-content">
                    <div class="outline-sidebar" id="outlineSidebar">
                        <div class="outline-header">
                            <span>文档大纲</span>
                            <button class="icon-btn small" onclick="toggleOutline()">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                        <div class="outline-content" id="outlineContent">
                            <!-- 大纲内容 -->
                        </div>
                    </div>
                    <div class="editor-main">
                        <div class="editor-area">
                            <div class="editor-document" 
                                 id="editorDocument" 
                                 contenteditable="true"
                                 data-placeholder="开始输入您的文档内容...">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 右键菜单 -->
            <div class="context-menu" id="contextMenu">
                <!-- 右键菜单项将动态创建 -->
            </div>
            
            <!-- LLM操作面板 -->
            <div class="llm-panel" id="llmPanel">
                <div class="llm-panel-header">
                    <span class="llm-panel-title">AI文本处理</span>
                    <button class="llm-panel-close" onclick="closeLLMPanel()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="llm-panel-content">
                    <div class="llm-action-grid">
                        <button class="llm-action-btn" onclick="llmAction('polish')">
                            <i class="fas fa-magic"></i>
                            <span>润色</span>
                        </button>
                        <button class="llm-action-btn" onclick="llmAction('expand')">
                            <i class="fas fa-expand-arrows-alt"></i>
                            <span>扩写</span>
                        </button>
                        <button class="llm-action-btn" onclick="llmAction('summarize')">
                            <i class="fas fa-compress-alt"></i>
                            <span>缩写</span>
                        </button>
                        <button class="llm-action-btn" onclick="llmAction('translate')">
                            <i class="fas fa-language"></i>
                            <span>翻译</span>
                        </button>
                        <button class="llm-action-btn" onclick="llmAction('formal')">
                            <i class="fas fa-user-tie"></i>
                            <span>正式化</span>
                        </button>
                        <button class="llm-action-btn" onclick="llmAction('casual')">
                            <i class="fas fa-smile"></i>
                            <span>口语化</span>
                        </button>
                    </div>
                    <textarea class="llm-custom-input" id="llmCustomInput" 
                              placeholder="输入自定义指令..."></textarea>
                </div>
                <div class="llm-panel-footer">
                    <button class="btn secondary" onclick="closeLLMPanel()">取消</button>
                    <button class="btn primary" onclick="executeLLMAction()">执行</button>
                </div>
            </div>
            
            <!-- 版本历史 -->
            <div class="version-history" id="versionHistory">
                <div class="version-history-header">
                    <span class="version-history-title">版本历史</span>
                    <button class="icon-btn small" onclick="toggleVersionHistory()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="version-history-content" id="versionHistoryContent">
                    <!-- 版本历史内容 -->
                </div>
            </div>
        `;
        
        this.container.innerHTML = editorHTML;
        this.editor = document.getElementById('editorDocument');
        this.toolbar = document.getElementById('editorToolbar');
        this.outline = document.getElementById('outlineContent');
        this.contextMenu = document.getElementById('contextMenu');
    }
    
    createToolbar() {
        const toolbarHTML = `
            <!-- 文件操作 -->
            <div class="toolbar-group">
                <button class="toolbar-btn" onclick="newDocument()" title="新建">
                    <i class="fas fa-file-plus"></i>
                </button>
                <button class="toolbar-btn" onclick="openDocument()" title="打开">
                    <i class="fas fa-folder-open"></i>
                </button>
                <button class="toolbar-btn" onclick="saveDocument()" title="保存">
                    <i class="fas fa-save"></i>
                </button>
            </div>
            
            <!-- 撤销重做 -->
            <div class="toolbar-group">
                <button class="toolbar-btn" onclick="undo()" title="撤销">
                    <i class="fas fa-undo"></i>
                </button>
                <button class="toolbar-btn" onclick="redo()" title="重做">
                    <i class="fas fa-redo"></i>
                </button>
            </div>
            
            <!-- 字体设置 -->
            <div class="toolbar-group">
                <select class="toolbar-select" id="fontFamily" onchange="changeFontFamily(this.value)">
                    <option value="Inter">Inter</option>
                    <option value="Arial">Arial</option>
                    <option value="Georgia">Georgia</option>
                    <option value="Times New Roman">Times New Roman</option>
                    <option value="Courier New">Courier New</option>
                </select>
                <select class="toolbar-select" id="fontSize" onchange="changeFontSize(this.value)">
                    <option value="12">12px</option>
                    <option value="14" selected>14px</option>
                    <option value="16">16px</option>
                    <option value="18">18px</option>
                    <option value="20">20px</option>
                    <option value="24">24px</option>
                    <option value="28">28px</option>
                    <option value="32">32px</option>
                </select>
            </div>
            
            <!-- 文本格式 -->
            <div class="toolbar-group">
                <button class="toolbar-btn" onclick="toggleBold()" title="加粗">
                    <i class="fas fa-bold"></i>
                </button>
                <button class="toolbar-btn" onclick="toggleItalic()" title="斜体">
                    <i class="fas fa-italic"></i>
                </button>
                <button class="toolbar-btn" onclick="toggleUnderline()" title="下划线">
                    <i class="fas fa-underline"></i>
                </button>
                <button class="toolbar-btn" onclick="toggleStrikethrough()" title="删除线">
                    <i class="fas fa-strikethrough"></i>
                </button>
            </div>
            
            <!-- 颜色 -->
            <div class="toolbar-group">
                <div class="color-picker">
                    <div class="color-preview" id="textColorPreview" 
                         style="background: #000000" onclick="toggleColorPicker('text')"></div>
                    <div class="color-dropdown" id="textColorDropdown">
                        <div class="color-grid" id="textColorGrid"></div>
                        <input type="color" id="textColorCustom" onchange="setTextColor(this.value)">
                    </div>
                </div>
                <div class="color-picker">
                    <div class="color-preview" id="bgColorPreview" 
                         style="background: #ffffff" onclick="toggleColorPicker('bg')"></div>
                    <div class="color-dropdown" id="bgColorDropdown">
                        <div class="color-grid" id="bgColorGrid"></div>
                        <input type="color" id="bgColorCustom" onchange="setBackgroundColor(this.value)">
                    </div>
                </div>
            </div>
            
            <!-- 对齐 -->
            <div class="toolbar-group">
                <button class="toolbar-btn" onclick="setAlignment('left')" title="左对齐">
                    <i class="fas fa-align-left"></i>
                </button>
                <button class="toolbar-btn" onclick="setAlignment('center')" title="居中">
                    <i class="fas fa-align-center"></i>
                </button>
                <button class="toolbar-btn" onclick="setAlignment('right')" title="右对齐">
                    <i class="fas fa-align-right"></i>
                </button>
                <button class="toolbar-btn" onclick="setAlignment('justify')" title="两端对齐">
                    <i class="fas fa-align-justify"></i>
                </button>
            </div>
            
            <!-- 列表 -->
            <div class="toolbar-group">
                <button class="toolbar-btn" onclick="toggleList('ul')" title="无序列表">
                    <i class="fas fa-list-ul"></i>
                </button>
                <button class="toolbar-btn" onclick="toggleList('ol')" title="有序列表">
                    <i class="fas fa-list-ol"></i>
                </button>
                <button class="toolbar-btn" onclick="decreaseIndent()" title="减少缩进">
                    <i class="fas fa-outdent"></i>
                </button>
                <button class="toolbar-btn" onclick="increaseIndent()" title="增加缩进">
                    <i class="fas fa-indent"></i>
                </button>
            </div>
            
            <!-- 插入元素 -->
            <div class="toolbar-group">
                <button class="toolbar-btn" onclick="insertTable()" title="插入表格">
                    <i class="fas fa-table"></i>
                </button>
                <button class="toolbar-btn" onclick="insertImage()" title="插入图片">
                    <i class="fas fa-image"></i>
                </button>
                <button class="toolbar-btn" onclick="insertLink()" title="插入链接">
                    <i class="fas fa-link"></i>
                </button>
            </div>
            
            <!-- 标题 -->
            <div class="toolbar-group">
                <select class="toolbar-select" id="headingLevel" onchange="setHeading(this.value)">
                    <option value="">正文</option>
                    <option value="h1">标题 1</option>
                    <option value="h2">标题 2</option>
                    <option value="h3">标题 3</option>
                    <option value="h4">标题 4</option>
                    <option value="h5">标题 5</option>
                    <option value="h6">标题 6</option>
                </select>
            </div>
            
            <!-- AI功能 -->
            <div class="toolbar-group">
                <button class="toolbar-btn" onclick="openLLMPanel()" title="AI处理">
                    <i class="fas fa-robot"></i>
                </button>
                <button class="toolbar-btn" onclick="toggleVersionHistory()" title="版本历史">
                    <i class="fas fa-history"></i>
                </button>
            </div>
        `;
        
        this.toolbar.innerHTML = toolbarHTML;
        this.initColorPickers();
    }
    
    initColorPickers() {
        const colors = [
            '#000000', '#434343', '#666666', '#999999', '#B7B7B7', '#CCCCCC', '#D9D9D9', '#EFEFEF',
            '#F3F3F3', '#FFFFFF', '#980000', '#FF0000', '#FF9900', '#FFFF00', '#00FF00', '#00FFFF',
            '#4A86E8', '#0000FF', '#9900FF', '#FF00FF', '#E6B8AF', '#F4CCCC', '#FCE5CD', '#FFF2CC',
            '#D9EAD3', '#D0E0E3', '#C9DAF8', '#CFE2F3', '#D9D2E9', '#EAD1DC'
        ];
        
        ['textColorGrid', 'bgColorGrid'].forEach(gridId => {
            const grid = document.getElementById(gridId);
            if (grid) {
                grid.innerHTML = colors.map(color => 
                    `<div class="color-option" style="background: ${color}" 
                          onclick="setColor('${gridId.includes('text') ? 'text' : 'bg'}', '${color}')"></div>`
                ).join('');
            }
        });
    }
    
    createOutline() {
        // 大纲将在文档内容变化时动态更新
        this.updateOutline();
    }
    
    createContextMenu() {
        const menuHTML = `
            <button class="context-menu-item" onclick="cutText()">
                <i class="fas fa-cut"></i>
                剪切
            </button>
            <button class="context-menu-item" onclick="copyText()">
                <i class="fas fa-copy"></i>
                复制
            </button>
            <button class="context-menu-item" onclick="pasteText()">
                <i class="fas fa-paste"></i>
                粘贴
            </button>
            <div class="context-menu-divider"></div>
            <button class="context-menu-item" onclick="openLLMPanel()">
                <i class="fas fa-magic"></i>
                AI润色
            </button>
            <button class="context-menu-item" onclick="llmAction('translate')">
                <i class="fas fa-language"></i>
                翻译
            </button>
            <button class="context-menu-item" onclick="llmAction('explain')">
                <i class="fas fa-question-circle"></i>
                解释
            </button>
            <div class="context-menu-divider"></div>
            <button class="context-menu-item" onclick="selectAll()">
                <i class="fas fa-check-square"></i>
                全选
            </button>
        `;
        
        this.contextMenu.innerHTML = menuHTML;
    }
    
    bindEvents() {
        // 编辑器事件
        this.editor.addEventListener('input', this.handleInput.bind(this));
        this.editor.addEventListener('keydown', this.handleKeydown.bind(this));
        this.editor.addEventListener('mouseup', this.handleSelection.bind(this));
        this.editor.addEventListener('keyup', this.handleSelection.bind(this));
        this.editor.addEventListener('contextmenu', this.handleContextMenu.bind(this));
        this.editor.addEventListener('paste', this.handlePaste.bind(this));
        
        // 全局事件
        document.addEventListener('click', this.handleDocumentClick.bind(this));
        document.addEventListener('keydown', this.handleGlobalKeydown.bind(this));
        
        // 图片和表格事件委托
        this.editor.addEventListener('click', this.handleElementClick.bind(this));
        
        // 自动保存
        setInterval(() => {
            this.autoSave();
        }, 30000); // 30秒自动保存
    }
    
    handleInput(event) {
        this.updateOutline();
        this.markUnsaved();
        
        // 延迟创建版本快照
        clearTimeout(this.saveTimeout);
        this.saveTimeout = setTimeout(() => {
            this.createVersionSnapshot('文档编辑');
        }, 2000);
    }
    
    handleKeydown(event) {
        // 快捷键处理
        if (event.ctrlKey || event.metaKey) {
            switch (event.key) {
                case 'b':
                    event.preventDefault();
                    this.toggleBold();
                    break;
                case 'i':
                    event.preventDefault();
                    this.toggleItalic();
                    break;
                case 'u':
                    event.preventDefault();
                    this.toggleUnderline();
                    break;
                case 's':
                    event.preventDefault();
                    this.saveDocument();
                    break;
                case 'z':
                    event.preventDefault();
                    if (event.shiftKey) {
                        this.redo();
                    } else {
                        this.undo();
                    }
                    break;
                case 'y':
                    event.preventDefault();
                    this.redo();
                    break;
            }
        }
        
        // Tab键缩进
        if (event.key === 'Tab') {
            event.preventDefault();
            if (event.shiftKey) {
                this.decreaseIndent();
            } else {
                this.increaseIndent();
            }
        }
    }
    
    handleSelection(event) {
        const selection = window.getSelection();
        this.selectedText = selection.toString();
        
        // 更新工具栏状态
        this.updateToolbarState();
        
        // 更新AI面板中的选中文本
        if (this.selectedText && AIAssistant) {
            AIAssistant.showSelectedContent(this.selectedText);
        }
    }
    
    handleContextMenu(event) {
        event.preventDefault();
        
        const selection = window.getSelection();
        if (selection.toString().trim()) {
            this.selectedText = selection.toString();
            this.showContextMenu(event.clientX, event.clientY);
        }
    }
    
    handlePaste(event) {
        event.preventDefault();
        
        const clipboardData = event.clipboardData || window.clipboardData;
        const htmlData = clipboardData.getData('text/html');
        const textData = clipboardData.getData('text/plain');
        
        if (htmlData) {
            // 清理HTML内容
            const cleanHTML = this.cleanPastedHTML(htmlData);
            document.execCommand('insertHTML', false, cleanHTML);
        } else if (textData) {
            document.execCommand('insertText', false, textData);
        }
        
        this.updateOutline();
    }
    
    handleDocumentClick(event) {
        // 关闭颜色选择器
        if (!event.target.closest('.color-picker')) {
            document.querySelectorAll('.color-dropdown').forEach(dropdown => {
                dropdown.classList.remove('show');
            });
        }
        
        // 关闭右键菜单
        if (!event.target.closest('.context-menu')) {
            this.hideContextMenu();
        }
    }
    
    handleGlobalKeydown(event) {
        // ESC键关闭面板
        if (event.key === 'Escape') {
            this.hideContextMenu();
            this.closeLLMPanel();
        }
    }
    
    handleElementClick(event) {
        const target = event.target;
        
        // 图片点击处理
        if (target.tagName === 'IMG') {
            this.selectImage(target);
        }
        
        // 表格点击处理
        if (target.closest('.table-editor')) {
            this.selectTable(target.closest('.table-editor'));
        }
    }
    
    // 基础编辑功能
    toggleBold() {
        document.execCommand('bold');
        this.updateToolbarState();
    }
    
    toggleItalic() {
        document.execCommand('italic');
        this.updateToolbarState();
    }
    
    toggleUnderline() {
        document.execCommand('underline');
        this.updateToolbarState();
    }
    
    toggleStrikethrough() {
        document.execCommand('strikeThrough');
        this.updateToolbarState();
    }
    
    changeFontFamily(font) {
        document.execCommand('fontName', false, font);
    }
    
    changeFontSize(size) {
        document.execCommand('fontSize', false, '7');
        const fontElements = document.querySelectorAll('font[size="7"]');
        fontElements.forEach(el => {
            el.removeAttribute('size');
            el.style.fontSize = size + 'px';
        });
    }
    
    setAlignment(align) {
        const commands = {
            'left': 'justifyLeft',
            'center': 'justifyCenter',
            'right': 'justifyRight',
            'justify': 'justifyFull'
        };
        
        document.execCommand(commands[align]);
        this.updateToolbarState();
    }
    
    toggleList(type) {
        const command = type === 'ul' ? 'insertUnorderedList' : 'insertOrderedList';
        document.execCommand(command);
        this.updateToolbarState();
    }
    
    increaseIndent() {
        document.execCommand('indent');
    }
    
    decreaseIndent() {
        document.execCommand('outdent');
    }
    
    setHeading(level) {
        if (level) {
            document.execCommand('formatBlock', false, level);
        } else {
            document.execCommand('formatBlock', false, 'p');
        }
        this.updateOutline();
        this.updateToolbarState();
    }
    
    // 颜色设置
    setColor(type, color) {
        if (type === 'text') {
            document.execCommand('foreColor', false, color);
            document.getElementById('textColorPreview').style.background = color;
        } else {
            document.execCommand('backColor', false, color);
            document.getElementById('bgColorPreview').style.background = color;
        }
        
        this.toggleColorPicker(type);
    }
    
    toggleColorPicker(type) {
        const dropdown = document.getElementById(type + 'ColorDropdown');
        dropdown.classList.toggle('show');
    }
    
    // 插入元素
    insertTable() {
        const rows = prompt('请输入行数:', '3');
        const cols = prompt('请输入列数:', '3');
        
        if (rows && cols) {
            const table = this.createTable(parseInt(rows), parseInt(cols));
            this.insertHTML(table);
        }
    }
    
    createTable(rows, cols) {
        let tableHTML = '<table class="table-editor"><tbody>';
        
        for (let i = 0; i < rows; i++) {
            tableHTML += '<tr>';
            for (let j = 0; j < cols; j++) {
                const tag = i === 0 ? 'th' : 'td';
                tableHTML += `<${tag} contenteditable="true">${i === 0 ? `列 ${j + 1}` : ''}</${tag}>`;
            }
            tableHTML += '</tr>';
        }
        
        tableHTML += '</tbody></table>';
        return tableHTML;
    }
    
    insertImage() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const img = `<div class="image-wrapper">
                        <img src="${e.target.result}" alt="插入的图片" style="max-width: 100%; height: auto;">
                        <div class="image-controls">
                            <button class="image-control-btn" onclick="resizeImage(this)">调整</button>
                            <button class="image-control-btn" onclick="deleteImage(this)">删除</button>
                        </div>
                        <div class="image-resize-handle nw"></div>
                        <div class="image-resize-handle ne"></div>
                        <div class="image-resize-handle sw"></div>
                        <div class="image-resize-handle se"></div>
                    </div>`;
                    this.insertHTML(img);
                };
                reader.readAsDataURL(file);
            }
        };
        input.click();
    }
    
    insertLink() {
        const url = prompt('请输入链接地址:');
        const text = this.selectedText || prompt('请输入链接文字:');
        
        if (url && text) {
            const link = `<a href="${url}" target="_blank">${text}</a>`;
            this.insertHTML(link);
        }
    }
    
    insertHTML(html) {
        if (document.queryCommandSupported('insertHTML')) {
            document.execCommand('insertHTML', false, html);
        } else {
            // Fallback for browsers that don't support insertHTML
            const selection = window.getSelection();
            if (selection.getRangeAt && selection.rangeCount) {
                const range = selection.getRangeAt(0);
                range.deleteContents();
                
                const el = document.createElement('div');
                el.innerHTML = html;
                const frag = document.createDocumentFragment();
                let node;
                while ((node = el.firstChild)) {
                    frag.appendChild(node);
                }
                range.insertNode(frag);
            }
        }
    }
    
    // 大纲更新
    updateOutline() {
        const headings = this.editor.querySelectorAll('h1, h2, h3, h4, h5, h6');
        const outlineHTML = Array.from(headings).map((heading, index) => {
            const level = heading.tagName.toLowerCase();
            const text = heading.textContent.trim();
            return text ? `
                <div class="outline-item ${level}" onclick="scrollToHeading(${index})">
                    ${text}
                </div>
            ` : '';
        }).join('');
        
        this.outline.innerHTML = outlineHTML || '<div class="empty-state">暂无标题</div>';
    }
    
    // 工具栏状态更新
    updateToolbarState() {
        // 更新按钮激活状态
        const commands = ['bold', 'italic', 'underline', 'strikeThrough'];
        commands.forEach(cmd => {
            const btn = this.toolbar.querySelector(`[onclick*="${cmd}"]`);
            if (btn) {
                btn.classList.toggle('active', document.queryCommandState(cmd));
            }
        });
        
        // 更新字体和字号
        try {
            const fontFamily = document.queryCommandValue('fontName');
            if (fontFamily) {
                const fontSelect = document.getElementById('fontFamily');
                if (fontSelect) fontSelect.value = fontFamily;
            }
        } catch (e) {
            // Ignore errors
        }
    }
    
    // 右键菜单
    showContextMenu(x, y) {
        this.contextMenu.style.left = x + 'px';
        this.contextMenu.style.top = y + 'px';
        this.contextMenu.classList.add('show');
    }
    
    hideContextMenu() {
        this.contextMenu.classList.remove('show');
    }
    
    // 版本管理
    createVersionSnapshot(description) {
        const snapshot = {
            id: Date.now(),
            content: this.editor.innerHTML,
            description: description || '自动保存',
            timestamp: new Date().toISOString(),
            isCurrent: false
        };
        
        // 标记之前的版本为非当前版本
        this.versions.forEach(v => v.isCurrent = false);
        snapshot.isCurrent = true;
        
        this.versions.push(snapshot);
        
        // 限制版本数量
        if (this.versions.length > 50) {
            this.versions = this.versions.slice(-50);
        }
        
        this.updateVersionHistory();
        this.currentVersion = this.versions.length - 1;
    }
    
    updateVersionHistory() {
        const historyContent = document.getElementById('versionHistoryContent');
        if (!historyContent) return;
        
        const historyHTML = this.versions.map((version, index) => `
            <div class="version-item ${version.isCurrent ? 'current' : ''}" 
                 onclick="restoreVersion(${index})">
                <div class="version-time">${new Date(version.timestamp).toLocaleString()}</div>
                <div class="version-description">${version.description}</div>
            </div>
        `).reverse().join('');
        
        historyContent.innerHTML = historyHTML || '<div class="empty-state">暂无版本历史</div>';
    }
    
    restoreVersion(index) {
        if (index >= 0 && index < this.versions.length) {
            const version = this.versions[index];
            this.editor.innerHTML = version.content;
            
            // 标记为当前版本
            this.versions.forEach(v => v.isCurrent = false);
            version.isCurrent = true;
            
            this.currentVersion = index;
            this.updateVersionHistory();
            this.updateOutline();
            
            App.showNotification('success', '版本恢复', '已恢复到选定版本');
        }
    }
    
    // 自动保存
    autoSave() {
        if (this.editor.innerHTML.trim()) {
            this.createVersionSnapshot('自动保存');
            localStorage.setItem('editor_autosave', JSON.stringify({
                content: this.editor.innerHTML,
                timestamp: new Date().toISOString()
            }));
        }
    }
    
    // 文档操作
    newDocument() {
        if (confirm('确定要新建文档吗？未保存的内容将丢失。')) {
            this.editor.innerHTML = '';
            this.versions = [];
            this.currentDocument = null;
            this.updateOutline();
            this.createVersionSnapshot('新建文档');
        }
    }
    
    saveDocument() {
        const content = this.editor.innerHTML;
        const title = this.getDocumentTitle();
        
        // 这里应该调用后端API保存文档
        // 暂时保存到localStorage
        const doc = {
            title: title,
            content: content,
            lastModified: new Date().toISOString()
        };
        
        localStorage.setItem('current_document', JSON.stringify(doc));
        this.createVersionSnapshot('手动保存');
        
        App.showNotification('success', '保存成功', '文档已保存');
    }
    
    getDocumentTitle() {
        const firstHeading = this.editor.querySelector('h1, h2, h3');
        return firstHeading ? firstHeading.textContent.trim() : '未命名文档';
    }
    
    // HTML清理
    cleanPastedHTML(html) {
        // 创建临时元素来清理HTML
        const temp = document.createElement('div');
        temp.innerHTML = html;
        
        // 移除危险的标签和属性
        const dangerousTags = ['script', 'style', 'link', 'meta'];
        dangerousTags.forEach(tag => {
            const elements = temp.querySelectorAll(tag);
            elements.forEach(el => el.remove());
        });
        
        // 清理属性
        const allElements = temp.querySelectorAll('*');
        allElements.forEach(el => {
            // 保留基本样式属性
            const allowedAttrs = ['style', 'href', 'src', 'alt', 'title'];
            const attrs = Array.from(el.attributes);
            attrs.forEach(attr => {
                if (!allowedAttrs.includes(attr.name)) {
                    el.removeAttribute(attr.name);
                }
            });
        });
        
        return temp.innerHTML;
    }
    
    // 撤销重做
    undo() {
        document.execCommand('undo');
    }
    
    redo() {
        document.execCommand('redo');
    }
    
    // 标记文档为未保存状态
    markUnsaved() {
        // 可以在标题栏显示未保存标识
        const title = document.title;
        if (!title.includes('*')) {
            document.title = title + ' *';
        }
    }
    
    // 获取编辑器内容
    getContent() {
        return this.editor.innerHTML;
    }
    
    // 设置编辑器内容
    setContent(html) {
        this.editor.innerHTML = html;
        this.updateOutline();
    }
    
    // 获取纯文本内容
    getTextContent() {
        return this.editor.textContent;
    }
    
    // 插入文本
    insertText(text) {
        document.execCommand('insertText', false, text);
    }
}

// 全局编辑器实例
let richTextEditor = null;

// 初始化编辑器
function initRichTextEditor() {
    richTextEditor = new RichTextEditor('.document-area');
    
    // 加载自动保存的内容
    const autosave = localStorage.getItem('editor_autosave');
    if (autosave) {
        try {
            const data = JSON.parse(autosave);
            richTextEditor.setContent(data.content);
            App.showNotification('info', '自动恢复', '已恢复自动保存的内容');
        } catch (e) {
            console.error('Failed to load autosave:', e);
        }
    }
}

// 工具栏功能函数 (全局)
function toggleBold() { richTextEditor?.toggleBold(); }
function toggleItalic() { richTextEditor?.toggleItalic(); }
function toggleUnderline() { richTextEditor?.toggleUnderline(); }
function toggleStrikethrough() { richTextEditor?.toggleStrikethrough(); }
function changeFontFamily(font) { richTextEditor?.changeFontFamily(font); }
function changeFontSize(size) { richTextEditor?.changeFontSize(size); }
function setAlignment(align) { richTextEditor?.setAlignment(align); }
function toggleList(type) { richTextEditor?.toggleList(type); }
function increaseIndent() { richTextEditor?.increaseIndent(); }
function decreaseIndent() { richTextEditor?.decreaseIndent(); }
function setHeading(level) { richTextEditor?.setHeading(level); }
function insertTable() { richTextEditor?.insertTable(); }
function insertImage() { richTextEditor?.insertImage(); }
function insertLink() { richTextEditor?.insertLink(); }
function newDocument() { richTextEditor?.newDocument(); }
function saveDocument() { richTextEditor?.saveDocument(); }
function undo() { richTextEditor?.undo(); }
function redo() { richTextEditor?.redo(); }

// 颜色设置
function setColor(type, color) { richTextEditor?.setColor(type, color); }
function toggleColorPicker(type) { richTextEditor?.toggleColorPicker(type); }
function setTextColor(color) { setColor('text', color); }
function setBackgroundColor(color) { setColor('bg', color); }

// 右键菜单功能
function cutText() { document.execCommand('cut'); }
function copyText() { document.execCommand('copy'); }
function pasteText() { document.execCommand('paste'); }
function selectAll() { document.execCommand('selectAll'); }

// 大纲导航
function scrollToHeading(index) {
    const headings = document.querySelectorAll('#editorDocument h1, #editorDocument h2, #editorDocument h3, #editorDocument h4, #editorDocument h5, #editorDocument h6');
    if (headings[index]) {
        headings[index].scrollIntoView({ behavior: 'smooth' });
    }
}

// 版本历史
function restoreVersion(index) { richTextEditor?.restoreVersion(index); }
function toggleVersionHistory() {
    const versionHistory = document.getElementById('versionHistory');
    versionHistory?.classList.toggle('show');
}

// 大纲切换
function toggleOutline() {
    const outline = document.getElementById('outlineSidebar');
    outline?.classList.toggle('show');
}

// LLM面板控制
function openLLMPanel() {
    const panel = document.getElementById('llmPanel');
    panel?.classList.add('show');
}

function closeLLMPanel() {
    const panel = document.getElementById('llmPanel');
    panel?.classList.remove('show');
}

// 图片操作
function selectImage(img) {
    // 移除其他图片的选中状态
    document.querySelectorAll('.image-wrapper.selected').forEach(wrapper => {
        wrapper.classList.remove('selected');
    });
    
    // 选中当前图片
    const wrapper = img.closest('.image-wrapper');
    if (wrapper) {
        wrapper.classList.add('selected');
    }
}

function resizeImage(btn) {
    const wrapper = btn.closest('.image-wrapper');
    const img = wrapper?.querySelector('img');
    if (img) {
        const newWidth = prompt('请输入新的宽度(px):', img.style.width || img.offsetWidth);
        if (newWidth) {
            img.style.width = newWidth + 'px';
            img.style.height = 'auto';
        }
    }
}

function deleteImage(btn) {
    if (confirm('确定要删除这张图片吗？')) {
        const wrapper = btn.closest('.image-wrapper');
        wrapper?.remove();
    }
}

// 表格操作
function selectTable(table) {
    // 移除其他表格的选中状态
    document.querySelectorAll('.table-editor.selected').forEach(t => {
        t.classList.remove('selected');
    });
    
    // 选中当前表格
    table.classList.add('selected');
}

// LLM操作
async function llmAction(action) {
    const selectedText = richTextEditor?.selectedText;
    if (!selectedText && !['summarize_all', 'generate_outline'].includes(action)) {
        App.showNotification('warning', '请先选择文本', '请选择要处理的文本内容');
        return;
    }
    
    try {
        const response = await fetch('/api/ai/quick-action', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: action,
                text: selectedText || richTextEditor?.getTextContent(),
                settings: AIAssistant?.settings || {}
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 根据操作类型处理结果
            handleLLMResult(action, data.result, selectedText);
            App.showNotification('success', 'AI处理完成', '内容已处理完成');
        } else {
            throw new Error(data.message || 'AI处理失败');
        }
        
    } catch (error) {
        console.error('LLM Action Error:', error);
        App.showNotification('error', 'AI处理失败', error.message);
    }
    
    closeLLMPanel();
}

function handleLLMResult(action, result, originalText) {
    switch (action) {
        case 'polish':
        case 'expand':
        case 'summarize':
        case 'translate':
        case 'formal':
        case 'casual':
            // 替换选中的文本
            if (originalText && result) {
                replaceSelectedText(result);
            }
            break;
        case 'explain':
            // 在选中文本后插入解释
            if (result) {
                insertAfterSelection(` <em>(${result})</em>`);
            }
            break;
        case 'summarize_all':
            // 在文档开头插入摘要
            insertAtBeginning(`<h2>文档摘要</h2><p>${result}</p><hr>`);
            break;
        case 'generate_outline':
            // 生成大纲
            insertAtBeginning(`<h2>文档大纲</h2>${result}<hr>`);
            break;
    }
}

function replaceSelectedText(newText) {
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        range.deleteContents();
        range.insertNode(document.createTextNode(newText));
    }
}

function insertAfterSelection(html) {
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        range.collapse(false); // 移动到选区末尾
        
        const div = document.createElement('div');
        div.innerHTML = html;
        const fragment = document.createDocumentFragment();
        while (div.firstChild) {
            fragment.appendChild(div.firstChild);
        }
        range.insertNode(fragment);
    }
}

function insertAtBeginning(html) {
    const editor = document.getElementById('editorDocument');
    if (editor) {
        editor.insertAdjacentHTML('afterbegin', html);
    }
}

async function executeLLMAction() {
    const customInput = document.getElementById('llmCustomInput');
    const instruction = customInput?.value.trim();
    const selectedText = richTextEditor?.selectedText;
    
    if (!selectedText) {
        App.showNotification('warning', '请先选择文本', '请选择要处理的文本内容');
        return;
    }
    
    if (instruction) {
        try {
            const response = await fetch('/api/ai/quick-action', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    action: 'custom',
                    text: selectedText,
                    instruction: instruction,
                    settings: AIAssistant?.settings || {}
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // 替换选中的文本
                replaceSelectedText(data.result);
                App.showNotification('success', 'AI处理完成', '自定义指令已执行完成');
                
                // 清空输入框
                customInput.value = '';
                closeLLMPanel();
            } else {
                throw new Error(data.message || 'AI处理失败');
            }
            
        } catch (error) {
            console.error('Custom LLM Action Error:', error);
            App.showNotification('error', 'AI处理失败', error.message);
        }
    } else {
        App.showNotification('warning', '请输入指令', '请输入自定义处理指令');
    }
}