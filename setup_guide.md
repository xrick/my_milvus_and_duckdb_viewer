# 資料庫集合檢視器 - 安裝和使用指南

這是一個基於 FastAPI 和現代 Web 技術的資料庫檢視器，支持 Milvus 向量數據庫和 DuckDB 分析型數據庫。

## 📋 功能特點

### Milvus 功能
- 🔗 連接到 Milvus 服務器
- 📊 查看集合列表和詳細信息
- 🔍 瀏覽集合數據
- 🎯 執行向量相似性搜索

### DuckDB 功能
- 📤 上傳 DuckDB 文件
- 📋 查看數據表列表
- 📊 瀏覽表格數據
- 💾 執行自定義 SQL 查詢

## 🚀 安裝步驟

### 1. 環境準備

確保您的系統已安裝：
- Python 3.8 或更高版本
- pip (Python 套件管理器)

### 2. 創建項目目錄

```bash
mkdir database-viewer
cd database-viewer
```

### 3. 創建虛擬環境（推薦）

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. 安裝依賴項

將 `requirements.txt` 的內容保存到文件中，然後執行：

```bash
pip install -r requirements.txt
```

### 5. 保存代碼文件

- 將 FastAPI 後端代碼保存為 `main.py`
- 將前端 HTML 代碼保存為獨立的 HTML 文件（可選）

## 🏃‍♂️ 啟動應用程序

### 方法 1：直接運行 Python 文件

```bash
python main.py
```

### 方法 2：使用 uvicorn 命令

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

啟動成功後，您將看到類似以下的輸出：

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 🌐 訪問應用程序

### 主要界面
- **Web 界面**: http://localhost:8000
- **API 文檔**: http://localhost:8000/docs
- **健康檢查**: http://localhost:8000/health

## 📖 使用指南

### Milvus 使用步驟

1. **連接 Milvus 服務器**
   - 在左側面板選擇 "Milvus 集合檢視器"
   - 輸入 Milvus 服務器地址和端口（默認：localhost:19530）
   - 點擊 "連接 Milvus" 按鈕

2. **查看集合**
   - 連接成功後，點擊 "載入集合列表"
   - 從下拉選單中選擇要查看的集合
   - 點擊 "查看集合信息" 或 "查看集合數據"

3. **執行向量搜索**（需要通過 API 端點）
   - 使用 POST 請求到 `/milvus/collection/{collection_name}/search`

### DuckDB 使用步驟

1. **上傳數據庫文件**
   - 在左側面板選擇 "DuckDB 數據檢視器"
   - 點擊上傳區域或拖放 .db/.duckdb 文件
   - 等待上傳完成

2. **查看表格數據**
   - 上傳成功後，從下拉選單中選擇表格
   - 點擊 "查看表格數據" 瀏覽數據

3. **執行 SQL 查詢**
   - 在 SQL 查詢文本區域輸入您的 SQL 語句
   - 點擊 "執行 SQL 查詢" 查看結果

## 🔧 配置選項

### 環境變量（可選）

您可以創建 `.env` 文件來設置環境變量：

```env
# Milvus 默認連接設置
MILVUS_HOST=localhost
MILVUS_PORT=19530

# 服務器設置
HOST=0.0.0.0
PORT=8000
DEBUG=True

# 上傳文件大小限制（字節）
MAX_FILE_SIZE=104857600  # 100MB
```

## 🛠 API 端點

### Milvus API

- `POST /milvus/connect` - 連接到 Milvus 服務器
- `GET /milvus/collections` - 獲取集合列表
- `GET /milvus/collection/{name}/info` - 獲取集合信息
- `GET /milvus/collection/{name}/data` - 獲取集合數據
- `POST /milvus/collection/{name}/search` - 執行向量搜索

### DuckDB API

- `POST /duckdb/upload` - 上傳 DuckDB 文件
- `GET /duckdb/tables` - 獲取表格列表
- `GET /duckdb/table/{name}/info` - 獲取表格信息
- `GET /duckdb/table/{name}/data` - 獲取表格數據
- `POST /duckdb/query` - 執行 SQL 查詢

## 🔍 故障排除

### 常見問題

1. **Milvus 連接失敗**
   - 確保 Milvus 服務器正在運行
   - 檢查防火牆設置
   - 驗證主機地址和端口

2. **DuckDB 文件上傳失敗**
   - 確保文件格式正確（.db 或 .duckdb）
   - 檢查文件大小是否過大
   - 驗證文件權限

3. **SQL 查詢錯誤**
   - 檢查 SQL 語法
   - 確保表名和列名正確
   - 注意 DuckDB 的特定語法

### 日誌查看

應用程序會在控制台輸出詳細的日誌信息，包括：
- 連接狀態
- 錯誤消息
- 操作記錄

## 🔒 安全注意事項

1. **生產環境部署**
   - 修改 CORS 設置，限制允許的來源域名
   - 使用 HTTPS
   - 設置適當的認證機制

2. **文件上傳安全**
   - 限制上傳文件大小
   - 驗證文件類型
   - 定期清理臨時文件

## 📞 技術支持

如果您遇到問題或需要幫助：

1. 檢查 API 文檔：http://localhost:8000/docs
2. 查看應用程序日誌
3. 確保所有依賴項正確安裝

## 🔄 更新和維護

定期更新依賴項以獲得安全修復和新功能：

```bash
pip install --upgrade -r requirements.txt
```

## 📄 許可證

本項目僅供學習和開發使用。在生產環境中使用前請確保遵循相關的許可證要求。