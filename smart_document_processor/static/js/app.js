/**
 * Smart Document Processor - Main Application JS
 * WPS Office Style Document Processing System
 */

// 全局应用状态
const App = {
    state: {
        currentDocument: null,
        documentList: [],
        isProcessing: false,
        zoomLevel: 100,
        activeTab: 'files',
        connectionStatus: 'disconnected'
    },
    
    elements: {},
    
    init() {
        this.initElements();
        this.bindEvents();
        this.initWebSocket();
        this.loadDocumentList();
        this.updateClock();
        this.setupDragAndDrop();
        
        console.log('📱 智能文档处理系统已启动');
    },
    
    initElements() {
        // 缓存常用元素
        this.elements = {
            documentTitle: document.getElementById('documentTitle'),
            currentDocumentTitle: document.getElementById('currentDocumentTitle'),
            welcomeScreen: document.getElementById('welcomeScreen'),
            documentContent: document.getElementById('documentContent'),
            documentViewer: document.getElementById('documentViewer'),
            fileList: document.getElementById('fileList'),
            connectionStatus: document.getElementById('connectionStatus'),
            documentCount: document.getElementById('documentCount'),
            wordCount: document.getElementById('wordCount'),
            currentTime: document.getElementById('currentTime'),
            progressContainer: document.getElementById('progressContainer'),
            progressFill: document.getElementById('progressFill'),
            progressText: document.getElementById('progressText'),
            zoomLevel: document.getElementById('zoomLevel'),
            notificationContainer: document.getElementById('notificationContainer'),
            
            // 工具栏按钮
            processBtn: document.getElementById('processBtn'),
            enhanceBtn: document.getElementById('enhanceBtn'),
            enhanceMenuBtn: document.getElementById('enhanceMenuBtn'),
            exportBtn: document.getElementById('exportBtn'),
            shareBtn: document.getElementById('shareBtn'),
            
            // 文件输入
            fileInput: document.getElementById('fileInput'),
            hiddenFileInput: document.getElementById('hiddenFileInput'),
            
            // 上传区域
            uploadArea: document.getElementById('uploadArea')
        };
    },
    
    bindEvents() {
        // 文件上传事件
        if (this.elements.fileInput) {
            this.elements.fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        }
        
        if (this.elements.hiddenFileInput) {
            this.elements.hiddenFileInput.addEventListener('change', this.handleFileSelect.bind(this));
        }
        
        // 点击事件委托
        document.addEventListener('click', this.handleDocumentClick.bind(this));
        
        // 键盘快捷键
        document.addEventListener('keydown', this.handleKeyboardShortcuts.bind(this));
        
        // 窗口大小变化
        window.addEventListener('resize', this.handleWindowResize.bind(this));
        
        // 页面离开前确认
        window.addEventListener('beforeunload', this.handleBeforeUnload.bind(this));
    },
    
    handleDocumentClick(event) {
        const target = event.target;
        
        // 关闭下拉菜单
        if (!target.closest('.dropdown') && !target.closest('.file-menu')) {
            this.closeAllDropdowns();
        }
        
        // 文件项点击
        if (target.closest('.file-item')) {
            const fileItem = target.closest('.file-item');
            const docId = fileItem.dataset.documentId;
            if (docId) {
                this.selectDocument(docId);
            }
        }
    },
    
    handleKeyboardShortcuts(event) {
        if (event.ctrlKey || event.metaKey) {
            switch (event.key) {
                case 'o':
                    event.preventDefault();
                    this.openFileDialog();
                    break;
                case 's':
                    event.preventDefault();
                    if (this.state.currentDocument) {
                        this.showExportOptions();
                    }
                    break;
                case 'n':
                    event.preventDefault();
                    this.newDocument();
                    break;
                case '=':
                case '+':
                    event.preventDefault();
                    this.zoomIn();
                    break;
                case '-':
                    event.preventDefault();
                    this.zoomOut();
                    break;
            }
        }
        
        // ESC 键关闭模态框
        if (event.key === 'Escape') {
            this.closeAllModals();
        }
    },
    
    handleWindowResize() {
        // 响应式布局调整
        this.adjustLayout();
    },
    
    handleBeforeUnload(event) {
        if (this.state.isProcessing) {
            const message = '文档正在处理中，确定要离开吗？';
            event.returnValue = message;
            return message;
        }
    },
    
    setupDragAndDrop() {
        const uploadArea = this.elements.uploadArea;
        if (!uploadArea) return;
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, this.preventDefaults.bind(this), false);
            document.body.addEventListener(eventName, this.preventDefaults.bind(this), false);
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.add('dragover');
            }, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.remove('dragover');
            }, false);
        });
        
        uploadArea.addEventListener('drop', this.handleDrop.bind(this), false);
    },
    
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    },
    
    handleDrop(e) {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.handleFiles(files);
            this.closeModal('uploadModal');
        }
    },
    
    async handleFileSelect(event) {
        const files = event.target.files;
        if (files.length > 0) {
            await this.handleFiles(files);
        }
    },
    
    async handleFiles(files) {
        for (let file of files) {
            if (this.validateFile(file)) {
                await this.uploadFile(file);
            }
        }
    },
    
    validateFile(file) {
        const maxSize = 50 * 1024 * 1024; // 50MB
        const allowedTypes = [
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/pdf',
            'text/plain',
            'text/html',
            'application/msword'
        ];
        
        if (file.size > maxSize) {
            this.showNotification('error', '文件太大', `文件 "${file.name}" 超过 50MB 限制`);
            return false;
        }
        
        if (!allowedTypes.includes(file.type) && !file.name.match(/\.(docx|pdf|txt|html|doc)$/i)) {
            this.showNotification('error', '不支持的文件格式', `文件 "${file.name}" 格式不受支持`);
            return false;
        }
        
        return true;
    },
    
    async uploadFile(file) {
        try {
            this.showProgress(0, '正在上传文件...');
            
            const formData = new FormData();
            formData.append('file', file);
            
            const xhr = new XMLHttpRequest();
            
            // 上传进度
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    this.updateProgress(percentComplete, '正在上传文件...');
                }
            });
            
            const response = await new Promise((resolve, reject) => {
                xhr.onload = () => {
                    if (xhr.status === 200) {
                        resolve(JSON.parse(xhr.responseText));
                    } else {
                        reject(new Error(xhr.responseText));
                    }
                };
                xhr.onerror = () => reject(new Error('上传失败'));
                xhr.open('POST', '/api/upload');
                xhr.send(formData);
            });
            
            this.hideProgress();
            
            if (response.success) {
                this.showNotification('success', '上传成功', `文件 "${response.filename}" 上传完成`);
                await this.loadDocumentList();
                this.selectDocument(response.document_id);
            } else {
                throw new Error(response.message || '上传失败');
            }
            
        } catch (error) {
            this.hideProgress();
            this.showNotification('error', '上传失败', error.message);
            console.error('File upload error:', error);
        }
    },
    
    async loadDocumentList() {
        try {
            const response = await fetch('/api/documents');
            const data = await response.json();
            
            if (data.success) {
                this.state.documentList = data.documents;
                this.renderDocumentList();
                this.updateDocumentCount();
            }
        } catch (error) {
            console.error('Failed to load document list:', error);
            this.showNotification('error', '加载失败', '无法获取文档列表');
        }
    },
    
    renderDocumentList() {
        const fileList = this.elements.fileList;
        if (!fileList) return;
        
        if (this.state.documentList.length === 0) {
            fileList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-file-upload"></i>
                    <p>还没有文档</p>
                    <button class="upload-btn" onclick="openFileDialog()">上传文档</button>
                </div>
            `;
            return;
        }
        
        const fileItemsHTML = this.state.documentList.map(doc => {
            const isActive = this.state.currentDocument && this.state.currentDocument.document_id === doc.document_id;
            const statusClass = this.getStatusClass(doc.processing_stage);
            const statusText = this.getStatusText(doc.processing_stage);
            const fileIcon = this.getFileIcon(doc.filename);
            const fileSize = this.formatFileSize(doc.size);
            const uploadTime = this.formatTime(doc.upload_time);
            
            return `
                <div class="file-item ${isActive ? 'active' : ''}" data-document-id="${doc.document_id}">
                    <div class="file-info">
                        <i class="file-icon ${fileIcon}"></i>
                        <span class="file-name" title="${doc.filename}">${doc.filename}</span>
                    </div>
                    <div class="file-meta">
                        <span class="file-status ${statusClass}">${statusText}</span>
                        <span>${fileSize}</span>
                    </div>
                    <div class="file-meta">
                        <span>${uploadTime}</span>
                        <button class="icon-btn small" onclick="deleteDocument('${doc.document_id}')" title="删除">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
        }).join('');
        
        fileList.innerHTML = fileItemsHTML;
    },
    
    getStatusClass(stage) {
        const statusMap = {
            'uploaded': 'uploaded',
            'parsed': 'processing',
            'analyzed': 'processing',
            'ai_processed': 'processing',
            'processed': 'processed',
            'completed': 'processed'
        };
        return statusMap[stage] || 'uploaded';
    },
    
    getStatusText(stage) {
        const statusMap = {
            'uploaded': '已上传',
            'parsed': '解析中',
            'analyzed': '分析中',
            'ai_processed': '处理中',
            'processed': '已处理',
            'completed': '已完成'
        };
        return statusMap[stage] || '未知';
    },
    
    getFileIcon(filename) {
        const extension = filename.split('.').pop().toLowerCase();
        const iconMap = {
            'docx': 'fas fa-file-word',
            'doc': 'fas fa-file-word',
            'pdf': 'fas fa-file-pdf',
            'txt': 'fas fa-file-alt',
            'html': 'fas fa-file-code'
        };
        return iconMap[extension] || 'fas fa-file';
    },
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    formatTime(timeString) {
        const date = new Date(timeString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 1) return '刚刚';
        if (diffMins < 60) return `${diffMins}分钟前`;
        if (diffHours < 24) return `${diffHours}小时前`;
        if (diffDays < 7) return `${diffDays}天前`;
        
        return date.toLocaleDateString('zh-CN');
    },
    
    async selectDocument(documentId) {
        try {
            const response = await fetch(`/api/document/${documentId}`);
            const data = await response.json();
            
            if (data.success) {
                this.state.currentDocument = data;
                this.renderDocument();
                this.updateToolbarState();
                this.updateDocumentTitle(data.filename);
                
                // 更新文件列表选中状态
                this.renderDocumentList();
            } else {
                throw new Error(data.message || '获取文档失败');
            }
        } catch (error) {
            console.error('Failed to select document:', error);
            this.showNotification('error', '加载失败', error.message);
        }
    },
    
    renderDocument() {
        if (!this.state.currentDocument) return;
        
        const doc = this.state.currentDocument;
        
        // 隐藏欢迎页面，显示文档内容
        this.elements.welcomeScreen.style.display = 'none';
        this.elements.documentContent.style.display = 'block';
        
        // 更新文档信息
        this.elements.currentDocumentTitle.textContent = doc.filename;
        document.getElementById('documentStatus').textContent = this.getStatusText(doc.processing_stage);
        document.getElementById('lastModified').textContent = '刚刚';
        document.getElementById('documentSize').textContent = this.formatFileSize(doc.metadata?.file_size || 0);
        
        // 渲染文档内容
        this.renderDocumentContent();
        
        // 更新字数统计
        this.updateWordCount();
    },
    
    renderDocumentContent() {
        const doc = this.state.currentDocument;
        const viewer = this.elements.documentViewer;
        
        if (!doc.processed_content && !doc.analyzed_content) {
            viewer.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-file-alt"></i>
                    <p>文档尚未处理</p>
                    <p class="small">点击 "AI处理" 按钮开始处理文档</p>
                </div>
            `;
            return;
        }
        
        const content = doc.processed_content || doc.analyzed_content;
        let html = '';
        
        // 渲染文本元素
        if (content.text_elements) {
            content.text_elements.forEach(elem => {
                const isModified = elem.modified ? 'modified' : '';
                html += `
                    <div class="document-element text-element ${isModified}" data-element-id="${elem.id}">
                        ${this.escapeHtml(elem.content)}
                    </div>
                `;
            });
        }
        
        // 渲染图像元素
        if (content.image_elements) {
            content.image_elements.forEach(elem => {
                const imageDataUrl = `data:image/jpeg;base64,${this.arrayBufferToBase64(elem.data)}`;
                const caption = elem.analysis?.description || '';
                
                html += `
                    <div class="document-element image-element" data-element-id="${elem.id}">
                        <img src="${imageDataUrl}" alt="文档图片" />
                        ${caption ? `<div class="image-caption">${this.escapeHtml(caption)}</div>` : ''}
                    </div>
                `;
            });
        }
        
        // 渲染表格元素
        if (content.table_elements) {
            content.table_elements.forEach(elem => {
                if (elem.content && elem.content.length > 0) {
                    html += `
                        <div class="document-element table-element" data-element-id="${elem.id}">
                            <table class="document-table">
                    `;
                    
                    elem.content.forEach((row, rowIndex) => {
                        const isHeader = rowIndex === 0;
                        html += '<tr>';
                        row.forEach(cell => {
                            const tag = isHeader ? 'th' : 'td';
                            html += `<${tag}>${this.escapeHtml(cell)}</${tag}>`;
                        });
                        html += '</tr>';
                    });
                    
                    html += '</table></div>';
                }
            });
        }
        
        if (!html) {
            html = `
                <div class="empty-state">
                    <i class="fas fa-file-alt"></i>
                    <p>文档内容为空</p>
                </div>
            `;
        }
        
        viewer.innerHTML = html;
    },
    
    updateToolbarState() {
        const hasDocument = !!this.state.currentDocument;
        const isProcessed = hasDocument && (this.state.currentDocument.processed_content || this.state.currentDocument.analyzed_content);
        
        // 启用/禁用按钮
        this.elements.processBtn.disabled = !hasDocument;
        this.elements.enhanceBtn.disabled = !hasDocument;
        this.elements.enhanceMenuBtn.disabled = !hasDocument;
        this.elements.exportBtn.disabled = !isProcessed;
        this.elements.shareBtn.disabled = !isProcessed;
    },
    
    updateDocumentTitle(filename) {
        if (filename) {
            this.elements.documentTitle.value = filename;
            document.title = `${filename} - 智能文档处理系统`;
        } else {
            this.elements.documentTitle.value = '未命名文档';
            document.title = '智能文档处理系统';
        }
    },
    
    updateDocumentCount() {
        this.elements.documentCount.textContent = `${this.state.documentList.length} 个文档`;
    },
    
    updateWordCount() {
        let wordCount = 0;
        
        if (this.state.currentDocument?.processed_content?.text_elements) {
            this.state.currentDocument.processed_content.text_elements.forEach(elem => {
                wordCount += elem.content.length;
            });
        }
        
        this.elements.wordCount.textContent = `${wordCount} 字`;
    },
    
    updateClock() {
        const updateTime = () => {
            const now = new Date();
            this.elements.currentTime.textContent = now.toLocaleTimeString('zh-CN', {
                hour: '2-digit',
                minute: '2-digit'
            });
        };
        
        updateTime();
        setInterval(updateTime, 60000); // 每分钟更新
    },
    
    adjustLayout() {
        // 响应式布局调整逻辑
        const width = window.innerWidth;
        
        if (width < 768) {
            // 移动端布局调整
            document.body.classList.add('mobile-layout');
        } else {
            document.body.classList.remove('mobile-layout');
        }
    },
    
    showProgress(percent, text) {
        this.elements.progressContainer.style.display = 'flex';
        this.updateProgress(percent, text);
    },
    
    updateProgress(percent, text) {
        this.elements.progressFill.style.width = `${percent}%`;
        this.elements.progressText.textContent = text;
    },
    
    hideProgress() {
        this.elements.progressContainer.style.display = 'none';
    },
    
    showNotification(type, title, message, duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const iconMap = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        notification.innerHTML = `
            <div class="notification-icon">
                <i class="${iconMap[type]}"></i>
            </div>
            <div class="notification-content">
                <div class="notification-title">${title}</div>
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // 添加关闭事件
        notification.querySelector('.notification-close').addEventListener('click', () => {
            this.removeNotification(notification);
        });
        
        // 添加到容器
        this.elements.notificationContainer.appendChild(notification);
        
        // 显示动画
        setTimeout(() => notification.classList.add('show'), 100);
        
        // 自动移除
        if (duration > 0) {
            setTimeout(() => this.removeNotification(notification), duration);
        }
    },
    
    removeNotification(notification) {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    },
    
    closeAllDropdowns() {
        document.querySelectorAll('.dropdown-menu, .dropdown-content').forEach(menu => {
            menu.classList.remove('show');
        });
    },
    
    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('show');
        });
    },
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },
    
    arrayBufferToBase64(buffer) {
        if (typeof buffer === 'string') return buffer;
        let binary = '';
        const bytes = new Uint8Array(buffer);
        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return btoa(binary);
    }
};

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});

// 全局函数（供HTML调用）
window.App = App;

// 导出常用函数
window.openFileDialog = () => document.getElementById('hiddenFileInput').click();
window.newDocument = () => App.showNotification('info', '功能开发中', '新建文档功能正在开发中');
window.openRecentFiles = () => App.showNotification('info', '功能开发中', '最近文件功能正在开发中');
window.showSettings = () => App.showNotification('info', '功能开发中', '设置功能正在开发中');
window.showHelp = () => App.showNotification('info', '帮助', '智能文档处理系统 v1.0.0');
window.showUserMenu = () => App.showNotification('info', '功能开发中', '用户菜单功能正在开发中');

window.refreshFileList = () => App.loadDocumentList();
window.deleteDocument = async (docId) => {
    if (confirm('确定要删除这个文档吗？此操作不可撤销。')) {
        try {
            const response = await fetch(`/api/document/${docId}`, { method: 'DELETE' });
            const data = await response.json();
            
            if (data.success) {
                App.showNotification('success', '删除成功', '文档已删除');
                App.loadDocumentList();
                
                // 如果删除的是当前文档，重置界面
                if (App.state.currentDocument?.document_id === docId) {
                    App.state.currentDocument = null;
                    App.elements.welcomeScreen.style.display = 'block';
                    App.elements.documentContent.style.display = 'none';
                    App.updateToolbarState();
                    App.updateDocumentTitle();
                }
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            App.showNotification('error', '删除失败', error.message);
        }
    }
};

// 工具栏功能
window.processDocument = () => {
    if (!App.state.currentDocument) {
        App.showNotification('warning', '请先选择文档', '请选择一个文档后再进行AI处理');
        return;
    }
    showModal('processModal');
};

window.enhanceDocument = async (type) => {
    if (!App.state.currentDocument) {
        App.showNotification('warning', '请先选择文档', '请选择一个文档后再进行AI增强');
        return;
    }
    
    try {
        App.showProgress(0, 'AI增强处理中...');
        
        const formData = new FormData();
        formData.append('doc_id', App.state.currentDocument.document_id);
        formData.append('enhancement_type', type);
        
        const response = await fetch('/api/ai/enhance', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            App.hideProgress();
            App.showNotification('success', 'AI增强完成', `文档已使用${type}风格进行优化`);
            
            // 重新加载文档内容
            App.selectDocument(App.state.currentDocument.document_id);
        } else {
            throw new Error(data.message);
        }
        
    } catch (error) {
        App.hideProgress();
        App.showNotification('error', 'AI增强失败', error.message);
    }
};

window.showExportOptions = () => {
    if (!App.state.currentDocument) {
        App.showNotification('warning', '请先选择文档', '请选择一个已处理的文档后再导出');
        return;
    }
    showModal('exportModal');
};

window.shareDocument = () => App.showNotification('info', '功能开发中', '文档分享功能正在开发中');

// 缩放控制
window.zoomIn = () => {
    App.state.zoomLevel = Math.min(App.state.zoomLevel + 10, 200);
    App.elements.zoomLevel.textContent = `${App.state.zoomLevel}%`;
    App.elements.documentViewer.style.zoom = App.state.zoomLevel / 100;
};

window.zoomOut = () => {
    App.state.zoomLevel = Math.max(App.state.zoomLevel - 10, 50);
    App.elements.zoomLevel.textContent = `${App.state.zoomLevel}%`;
    App.elements.documentViewer.style.zoom = App.state.zoomLevel / 100;
};

// 标签页切换
window.switchTab = (tabName) => {
    // 移除所有活动状态
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // 激活选中的标签页
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    App.state.activeTab = tabName;
};

// 下拉菜单控制
window.toggleFileMenu = () => {
    const menu = document.getElementById('fileMenu');
    menu.classList.toggle('show');
};

window.toggleEnhanceMenu = () => {
    const menu = document.getElementById('enhanceMenu');
    menu.classList.toggle('show');
};

// 模态框控制
window.showModal = (modalId) => {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
};

window.closeModal = (modalId) => {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }
};

// 属性面板控制
window.togglePropertiesPanel = () => {
    const panel = document.getElementById('propertiesPanel');
    panel.classList.toggle('show');
};

// 文档操作
window.editDocument = () => App.showNotification('info', '功能开发中', '文档编辑功能正在开发中');
window.previewDocument = () => App.showNotification('info', '功能开发中', '文档预览功能正在开发中');

console.log('🎯 应用核心模块已加载');