/**
 * 資料庫檢視器 - 主應用程序 JavaScript
 */

// 全局配置
const CONFIG = {
    API_BASE: window.location.origin,
    ENDPOINTS: {
        MILVUS: {
            CONNECT: '/milvus/connect',
            COLLECTIONS: '/milvus/collections',
            COLLECTION_INFO: '/milvus/collection',
            COLLECTION_DATA: '/milvus/collection'
        },
        DUCKDB: {
            UPLOAD: '/duckdb/upload',
            TABLES: '/duckdb/tables',
            TABLE_INFO: '/duckdb/table',
            TABLE_DATA: '/duckdb/table',
            QUERY: '/duckdb/query'
        },
        HEALTH: '/health'
    }
};

// 應用程序狀態
const AppState = {
    currentView: 'milvus',
    milvusConnected: false,
    duckdbLoaded: false,
    loading: false
};

// DOM 元素緩存
const Elements = {
    // 通用元素
    loading: null,
    errorMessage: null,
    successMessage: null,
    
    // Milvus 相關元素
    milvusViewer: null,
    milvusStatus: null,
    milvusHost: null,
    milvusPort: null,
    collectionSelect: null,
    milvusData: null,
    
    // DuckDB 相關元素
    duckdbViewer: null,
    duckdbFile: null,
    tableSelect: null,
    sqlQuery: null,
    duckdbData: null,
    uploadArea: null
};

// 初始化應用程序
document.addEventListener('DOMContentLoaded', function() {
    initializeElements();
    setupEventListeners();
    checkApplicationHealth();
    console.log('🚀 資料庫檢視器已初始化');
});

// 初始化 DOM 元素引用
function initializeElements() {
    // 通用元素
    Elements.loading = document.getElementById('loading');
    Elements.errorMessage = document.getElementById('error-message');
    Elements.successMessage = document.getElementById('success-message');
    
    // Milvus 元素
    Elements.milvusViewer = document.getElementById('milvus-viewer');
    Elements.milvusStatus = document.getElementById('milvus-status');
    Elements.milvusHost = document.getElementById('milvus-host');
    Elements.milvusPort = document.getElementById('milvus-port');
    Elements.collectionSelect = document.getElementById('collection-select');
    Elements.milvusData = document.getElementById('milvus-data');
    
    // DuckDB 元素
    Elements.duckdbViewer = document.getElementById('duckdb-viewer');
    Elements.duckdbFile = document.getElementById('duckdb-file');
    Elements.tableSelect = document.getElementById('table-select');
    Elements.sqlQuery = document.getElementById('sql-query');
    Elements.duckdbData = document.getElementById('duckdb-data');
    Elements.uploadArea = document.querySelector('.upload-area');
}

// 設置事件監聽器
function setupEventListeners() {
    // 拖拽上傳功能
    if (Elements.uploadArea) {
        Elements.uploadArea.addEventListener('dragover', handleDragOver);
        Elements.uploadArea.addEventListener('dragleave', handleDragLeave);
        Elements.uploadArea.addEventListener('drop', handleFileDrop);
    }
    
    // 鍵盤快捷鍵
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

// ==================== 通用功能函數 ====================

// 顯示載入狀態
function showLoading() {
    if (Elements.loading) {
        Elements.loading.style.display = 'block';
        AppState.loading = true;
    }
}

// 隱藏載入狀態
function hideLoading() {
    if (Elements.loading) {
        Elements.loading.style.display = 'none';
        AppState.loading = false;
    }
}

// 顯示錯誤訊息
function showError(message) {
    console.error('Error:', message);
    if (Elements.errorMessage) {
        Elements.errorMessage.textContent = message;
        Elements.errorMessage.style.display = 'block';
        setTimeout(() => {
            Elements.errorMessage.style.display = 'none';
        }, 5000);
    }
}

// 顯示成功訊息
function showSuccess(message) {
    console.log('Success:', message);
    if (Elements.successMessage) {
        Elements.successMessage.textContent = message;
        Elements.successMessage.style.display = 'block';
        setTimeout(() => {
            Elements.successMessage.style.display = 'none';
        }, 3000);
    }
}

// HTTP 請求封裝
async function makeRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(`${CONFIG.API_BASE}${url}`, finalOptions);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || `HTTP error! status: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('Request failed:', error);
        throw error;
    }
}

// 檢查應用程序健康狀態
async function checkApplicationHealth() {
    try {
        const health = await makeRequest(CONFIG.ENDPOINTS.HEALTH);
        console.log('Application health:', health);
        
        AppState.milvusConnected = health.milvus_connected || false;
        AppState.duckdbLoaded = health.duckdb_loaded || false;
        
        updateConnectionStatus();
    } catch (error) {
        console.warn('Health check failed:', error);
    }
}

// 更新連接狀態顯示
function updateConnectionStatus() {
    if (Elements.milvusStatus) {
        if (AppState.milvusConnected) {
            Elements.milvusStatus.className = 'connection-status connected';
            Elements.milvusStatus.textContent = 'Milvus 連接狀態：已連接';
        } else {
            Elements.milvusStatus.className = 'connection-status disconnected';
            Elements.milvusStatus.textContent = 'Milvus 連接狀態：未連接';
        }
    }
}

// ==================== 視圖切換功能 ====================

// 切換到 Milvus 檢視器
function showMilvusViewer() {
    AppState.currentView = 'milvus';
    
    if (Elements.milvusViewer) Elements.milvusViewer.classList.remove('hidden');
    if (Elements.duckdbViewer) Elements.duckdbViewer.classList.add('hidden');
    
    updateActiveButton(0);
    console.log('Switched to Milvus viewer');
}

// 切換到 DuckDB 檢視器
function showDuckDBViewer() {
    AppState.currentView = 'duckdb';
    
    if (Elements.milvusViewer) Elements.milvusViewer.classList.add('hidden');
    if (Elements.duckdbViewer) Elements.duckdbViewer.classList.remove('hidden');
    
    updateActiveButton(1);
    console.log('Switched to DuckDB viewer');
}

// 更新活動按鈕狀態
function updateActiveButton(activeIndex) {
    const buttons = document.querySelectorAll('.function-button');
    buttons.forEach((btn, index) => {
        if (index === activeIndex) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

// ==================== Milvus 相關功能 ====================

// 連接到 Milvus 服務器
async function connectMilvus() {
    const host = Elements.milvusHost?.value || 'localhost';
    const port = parseInt(Elements.milvusPort?.value) || 19530;
    
    showLoading();
    try {
        const result = await makeRequest(CONFIG.ENDPOINTS.MILVUS.CONNECT, {
            method: 'POST',
            body: JSON.stringify({ host, port })
        });
        
        AppState.milvusConnected = true;
        updateConnectionStatus();
        showSuccess('Milvus 連接成功！');
        
        // 自動載入集合列表
        setTimeout(loadCollections, 1000);
        
    } catch (error) {
        AppState.milvusConnected = false;
        updateConnectionStatus();
        showError(`連接失敗：${error.message}`);
    } finally {
        hideLoading();
    }
}

// 載入集合列表
async function loadCollections() {
    if (!AppState.milvusConnected) {
        showError('請先連接 Milvus 服務器');
        return;
    }
    
    showLoading();
    try {
        const result = await makeRequest(CONFIG.ENDPOINTS.MILVUS.COLLECTIONS);
        
        if (Elements.collectionSelect) {
            Elements.collectionSelect.innerHTML = '<option value="">選擇一個集合</option>';
            
            if (result.collections && result.collections.length > 0) {
                result.collections.forEach(collection => {
                    const option = document.createElement('option');
                    option.value = collection;
                    option.textContent = collection;
                    Elements.collectionSelect.appendChild(option);
                });
                showSuccess(`成功載入 ${result.collections.length} 個集合`);
            } else {
                showError('未找到任何集合');
            }
        }
        
    } catch (error) {
        showError(`載入集合失敗：${error.message}`);
    } finally {
        hideLoading();
    }
}

// 查看集合信息
async function viewCollectionInfo() {
    const collectionName = Elements.collectionSelect?.value;
    if (!collectionName) {
        showError('請先選擇一個集合');
        return;
    }

    showLoading();
    try {
        const result = await makeRequest(`${CONFIG.ENDPOINTS.MILVUS.COLLECTION_INFO}/${collectionName}/info`);
        
        if (Elements.milvusData) {
            Elements.milvusData.innerHTML = `
                <h4>集合信息：${collectionName}</h4>
                <div class="info-grid">
                    <div class="info-item">
                        <strong>名稱:</strong> ${result.name}
                    </div>
                    <div class="info-item">
                        <strong>實體數量:</strong> ${result.num_entities}
                    </div>
                    <div class="info-item">
                        <strong>是否為空:</strong> ${result.is_empty ? '是' : '否'}
                    </div>
                </div>
                <h5>字段信息:</h5>
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>字段名</th>
                                <th>類型</th>
                                <th>主鍵</th>
                                <th>自動ID</th>
                                <th>維度</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${result.schema.fields.map(field => `
                                <tr>
                                    <td>${field.name}</td>
                                    <td>${field.type}</td>
                                    <td>${field.is_primary ? '是' : '否'}</td>
                                    <td>${field.auto_id ? '是' : '否'}</td>
                                    <td>${field.dimension || '-'}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }
        
    } catch (error) {
        showError(`獲取集合信息失敗：${error.message}`);
    } finally {
        hideLoading();
    }
}

// 查看集合數據
async function viewCollectionData() {
    const collectionName = Elements.collectionSelect?.value;
    if (!collectionName) {
        showError('請先選擇一個集合');
        return;
    }

    showLoading();
    try {
        const result = await makeRequest(`${CONFIG.ENDPOINTS.MILVUS.COLLECTION_DATA}/${collectionName}/data?limit=100`);
        
        if (Elements.milvusData) {
            if (result.data && result.data.length > 0) {
                const tableHTML = generateDataTable(result.data, `集合數據：${collectionName}`);
                Elements.milvusData.innerHTML = `
                    <div class="data-summary">
                        <h4>集合數據：${collectionName}</h4>
                        <p>總計 ${result.total_count} 條記錄，顯示 ${result.returned_count} 條</p>
                    </div>
                    ${tableHTML}
                `;
            } else {
                Elements.milvusData.innerHTML = `
                    <h4>集合數據：${collectionName}</h4>
                    <p class="no-data">此集合暫無數據</p>
                `;
            }
        }
        
    } catch (error) {
        showError(`獲取集合數據失敗：${error.message}`);
    } finally {
        hideLoading();
    }
}

// ==================== DuckDB 相關功能 ====================

// 上傳 DuckDB 文件
async function uploadDuckDB() {
    const fileInput = Elements.duckdbFile;
    const file = fileInput?.files[0];
    
    if (!file) {
        showError('請選擇一個文件');
        return;
    }

    if (!file.name.match(/\.(db|duckdb)$/i)) {
        showError('請選擇 .db 或 .duckdb 文件');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    showLoading();
    try {
        const response = await fetch(`${CONFIG.API_BASE}${CONFIG.ENDPOINTS.DUCKDB.UPLOAD}`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '上傳失敗');
        }
        
        const result = await response.json();
        AppState.duckdbLoaded = true;
        showSuccess(`文件上傳成功！包含 ${result.tables_count} 個表格`);
        
        // 自動載入表格列表
        setTimeout(loadTables, 1000);
        
    } catch (error) {
        AppState.duckdbLoaded = false;
        showError(`上傳失敗：${error.message}`);
    } finally {
        hideLoading();
    }
}

// 載入表格列表
async function loadTables() {
    if (!AppState.duckdbLoaded) {
        showError('請先上傳 DuckDB 文件');
        return;
    }
    
    try {
        const result = await makeRequest(CONFIG.ENDPOINTS.DUCKDB.TABLES);
        
        if (Elements.tableSelect) {
            Elements.tableSelect.innerHTML = '<option value="">選擇一個表格</option>';
            
            if (result.tables && result.tables.length > 0) {
                result.tables.forEach(table => {
                    const option = document.createElement('option');
                    option.value = table;
                    option.textContent = table;
                    Elements.tableSelect.appendChild(option);
                });
                console.log(`載入了 ${result.tables.length} 個表格`);
            } else {
                showError('數據庫中未找到任何表格');
            }
        }
        
    } catch (error) {
        showError(`載入表格失敗：${error.message}`);
    }
}

// 查看表格數據
async function viewTableData() {
    const tableName = Elements.tableSelect?.value;
    if (!tableName) {
        showError('請先選擇一個表格');
        return;
    }

    showLoading();
    try {
        const result = await makeRequest(`${CONFIG.ENDPOINTS.DUCKDB.TABLE_DATA}/${tableName}/data?limit=100`);
        displayDuckDBResults(result.data, `表格數據：${tableName}`, result.total_count);
        
    } catch (error) {
        showError(`獲取表格數據失敗：${error.message}`);
    } finally {
        hideLoading();
    }
}

// 執行 SQL 查詢
async function executeSQLQuery() {
    const sqlQuery = Elements.sqlQuery?.value?.trim();
    if (!sqlQuery) {
        showError('請輸入 SQL 查詢語句');
        return;
    }

    if (!AppState.duckdbLoaded) {
        showError('請先上傳 DuckDB 文件');
        return;
    }

    showLoading();
    try {
        const result = await makeRequest(CONFIG.ENDPOINTS.DUCKDB.QUERY, {
            method: 'POST',
            body: JSON.stringify({ query: sqlQuery })
        });
        
        if (result.data) {
            displayDuckDBResults(result.data, 'SQL 查詢結果', result.returned_count);
        } else {
            showSuccess(result.message || '查詢執行成功');
            if (Elements.duckdbData) {
                Elements.duckdbData.innerHTML = `
                    <h4>查詢執行結果</h4>
                    <p class="success-message">${result.message}</p>
                    ${result.affected_rows ? `<p>影響行數: ${result.affected_rows}</p>` : ''}
                `;
            }
        }
        
    } catch (error) {
        showError(`執行查詢失敗：${error.message}`);
    } finally {
        hideLoading();
    }
}

// 顯示 DuckDB 結果
function displayDuckDBResults(data, title, totalCount = null) {
    if (!Elements.duckdbData) return;
    
    if (data && data.length > 0) {
        const tableHTML = generateDataTable(data, title);
        const summaryHTML = totalCount ? 
            `<p>總計 ${totalCount} 行數據，顯示 ${data.length} 行</p>` : 
            `<p>共 ${data.length} 行數據</p>`;
            
        Elements.duckdbData.innerHTML = `
            <div class="data-summary">
                <h4>${title}</h4>
                ${summaryHTML}
            </div>
            ${tableHTML}
        `;
    } else {
        Elements.duckdbData.innerHTML = `
            <h4>${title}</h4>
            <p class="no-data">查詢未返回任何數據</p>
        `;
    }
}

// 清除結果
function clearResults() {
    if (Elements.duckdbData) {
        Elements.duckdbData.innerHTML = '';
    }
    console.log('Results cleared');
}

// ==================== 通用數據顯示功能 ====================

// 生成數據表格 HTML
function generateDataTable(data, title) {
    if (!data || data.length === 0) {
        return '<p class="no-data">無數據</p>';
    }
    
    const columns = Object.keys(data[0]);
    
    let tableHTML = `
        <div class="table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        ${columns.map(col => `<th>${escapeHtml(col)}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
    `;
    
    data.forEach(row => {
        tableHTML += '<tr>';
        columns.forEach(col => {
            const value = row[col];
            let displayValue;
            
            if (value === null || value === undefined) {
                displayValue = '<span class="null-value">NULL</span>';
            } else if (typeof value === 'object') {
                displayValue = `<span class="json-value">${escapeHtml(JSON.stringify(value))}</span>`;
            } else if (typeof value === 'string' && value.length > 100) {
                displayValue = `<span class="long-text" title="${escapeHtml(value)}">${escapeHtml(value.substring(0, 100))}...</span>`;
            } else {
                displayValue = escapeHtml(String(value));
            }
            
            tableHTML += `<td>${displayValue}</td>`;
        });
        tableHTML += '</tr>';
    });
    
    tableHTML += `
                </tbody>
            </table>
        </div>
    `;
    
    return tableHTML;
}

// HTML 轉義函數
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ==================== 拖拽上傳功能 ====================

// 處理拖拽懸停
function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.style.background = '#d5dbdb';
    e.currentTarget.style.borderColor = '#2980b9';
}

// 處理拖拽離開
function handleDragLeave(e) {
    e.preventDefault();
    e.currentTarget.style.background = '#ecf0f1';
    e.currentTarget.style.borderColor = '#3498db';
}

// 處理文件拖拽放置
function handleFileDrop(e) {
    e.preventDefault();
    e.currentTarget.style.background = '#ecf0f1';
    e.currentTarget.style.borderColor = '#3498db';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        if (file.name.match(/\.(db|duckdb)$/i)) {
            if (Elements.duckdbFile) {
                Elements.duckdbFile.files = files;
                uploadDuckDB();
            }
        } else {
            showError('請選擇 .db 或 .duckdb 文件');
        }
    }
}

// ==================== 鍵盤快捷鍵 ====================

// 處理鍵盤快捷鍵
function handleKeyboardShortcuts(e) {
    // Ctrl/Cmd + 1: 切換到 Milvus 視圖
    if ((e.ctrlKey || e.metaKey) && e.key === '1') {
        e.preventDefault();
        showMilvusViewer();
    }
    
    // Ctrl/Cmd + 2: 切換到 DuckDB 視圖
    if ((e.ctrlKey || e.metaKey) && e.key === '2') {
        e.preventDefault();
        showDuckDBViewer();
    }
    
    // Escape: 隱藏錯誤和成功訊息
    if (e.key === 'Escape') {
        if (Elements.errorMessage) Elements.errorMessage.style.display = 'none';
        if (Elements.successMessage) Elements.successMessage.style.display = 'none';
    }
    
    // Ctrl/Cmd + Enter: 執行 SQL 查詢（當在 SQL 文本區域時）
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && e.target === Elements.sqlQuery) {
        e.preventDefault();
        executeSQLQuery();
    }
}

// ==================== 工具函數 ====================

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 格式化時間戳
function formatTimestamp(timestamp) {
    return new Date(timestamp).toLocaleString('zh-TW');
}

// 深度複製對象
function deepClone(obj) {
    return JSON.parse(JSON.stringify(obj));
}

// 防抖函數
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func.apply(this, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ==================== 導出全局函數 ====================

// 將需要在 HTML 中調用的函數添加到全局作用域
window.showMilvusViewer = showMilvusViewer;
window.showDuckDBViewer = showDuckDBViewer;
window.connectMilvus = connectMilvus;
window.loadCollections = loadCollections;
window.viewCollectionInfo = viewCollectionInfo;
window.viewCollectionData = viewCollectionData;
window.uploadDuckDB = uploadDuckDB;
window.viewTableData = viewTableData;
window.executeSQLQuery = executeSQLQuery;
window.clearResults = clearResults;

// ==================== 錯誤處理 ====================

// 全局錯誤處理
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    showError(`發生未預期的錯誤: ${e.error.message}`);
});

// 全局 Promise 錯誤處理
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    showError(`Promise 錯誤: ${e.reason}`);
    e.preventDefault();
});

console.log('📱 應用程序 JavaScript 已載入完成');