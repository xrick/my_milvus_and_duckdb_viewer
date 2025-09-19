# 資料庫檢視器 (Database Viewer)

一個基於 FastAPI 和現代 Web 技術的資料庫檢視器，支持 Milvus 向量資料庫和 DuckDB 分析型資料庫。

## 🌟 功能特色

### Milvus 功能
- 🔗 連接到 Milvus 服務器
- 📊 查看集合列表和詳細信息  
- 🔍 瀏覽集合數據
- 📈 支援向量相似性搜索

### DuckDB 功能  
- 📤 上傳 DuckDB 文件
- 📋 查看資料表列表
- 📊 瀏覽表格數據
- 💾 執行自定義 SQL 查詢

## 🚀 快速開始

### 系統要求
- Python 3.8 或更高版本
- 2GB+ RAM (建議 4GB+)
- 500MB+ 磁碟空間

### 安裝步驟

1. **克隆項目**
   ```bash
   git clone <repository-url>
   cd database-viewer
   ```

2. **創建虛擬環境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```

3. **安裝依賴項**
   ```bash
   pip install -r requirements.txt
   ```

4. **啟動應用程序**
   ```bash
   # 使用啟動腳本 (推薦)
   python start.py
   
   # 或直接運行
   python main.py
   
   # 或使用 uvicorn
   uvicorn main:app --reload
   ```

5. **訪問應用程序**
   - 主界面: http://localhost:8000
   - API 文檔: http://localhost:8000/docs
   - 健康檢查: http://localhost:8000/health

## 📁 項目結構

```
database-viewer/
├── main.py                 # FastAPI 主程序
├── config.py              # 配置管理
├── start.py               # 啟動腳本
├── requirements.txt       # Python 依賴項
├── .env                   # 環境變量配置
├── static/               # 靜態資源
│   ├── index.html        # 主前端頁面
│   ├── css/style.css     # 樣式文件
│   └── js/app.js         # JavaScript 應用邏輯
├── uploads/              # 上傳文件目錄
├── temp/                # 臨時文件目錄
├── logs/                # 日誌文件目錄
└── README.md            # 項目說明
```

## 🔧 配置選項

### 環境變量 (.env)

```env
# Milvus 配置
MILVUS_HOST=localhost
MILVUS_PORT=19530

# 服務器配置
HOST=0.0.0.0
PORT=8000
DEBUG=True

# 文件上傳配置
MAX_FILE_SIZE=104857600  # 100MB
UPLOAD_DIR=./uploads

# 日誌配置
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

## 📖 使用指南

### Milvus 使用

1. **連接服務器**
   - 輸入 Milvus 服務器地址和端口
   - 點擊 "連接 Milvus" 按鈕

2. **查看數據**
   - 載入集合列表
   - 選擇要檢視的集合
   - 查看集合信息或數據內容

### DuckDB 使用

1. **上傳文件**
   - 點擊上傳區域選擇 .db 或 .duckdb 文件
   - 或直接拖拽文件到上傳區域

2. **查詢數據**
   - 從下拉選單選擇資料表
   - 查看表格數據或執行自定義 SQL 查詢

## 🛠 API 端點

### Milvus API
- `POST /milvus/connect` - 連接到 Milvus 服務器
- `GET /milvus/collections` - 獲取集合列表
- `GET /milvus/collection/{name}/info` - 獲取集合信息
- `GET /milvus/collection/{name}/data` - 獲取集合數據

### DuckDB API  
- `POST /duckdb/upload` - 上傳 DuckDB 文件
- `GET /duckdb/tables` - 獲取表格列表
- `GET /duckdb/table/{name}/data` - 獲取表格數據
- `POST /duckdb/query` - 執行 SQL 查詢

### 通用 API
- `GET /health` - 健康檢查
- `GET /docs` - API 文檔

## 🐛 故障排除

### 常見問題

1. **端口被占用**
   ```bash
   # 查找占用端口的進程
   netstat -tulpn | grep 8000  # Linux
   netstat -ano | findstr 8000  # Windows
   ```

2. **Python 包安裝失敗**
   ```bash
   # 升級 pip
   python -m pip install --upgrade pip
   
   # 清除緩存重新安裝
   pip cache purge
   pip install -r requirements.txt --no-cache-dir
   ```

3. **Milvus 連接失敗**
   - 確認 Milvus 服務器正在運行
   - 檢查網路連接和防火牆設置
   - 驗證主機地址和端口號

4. **DuckDB 文件上傳失敗**
   - 確認文件格式為 .db 或 .duckdb
   - 檢查文件大小是否超過限制
   - 確認文件權限正確

### 日誌檢查
```bash
# 查看應用程序日誌
tail -f logs/app.log
```

## 🔒 安全注意事項

1. **生產部署**
   - 設置強密碼和安全金鑰
   - 配置 HTTPS
   - 限制 CORS 來源域名
   - 設置適當的文件權限

2. **數據安全**
   - 定期清理臨時文件
   - 限制上傳文件大小
   - 驗證文件類型和內容

## 🚀 部署到生產環境

### 使用 Docker (推薦)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🤝 貢獻指南

1. Fork 本項目
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打開 Pull Request

## 📄 許可證

本項目採用 MIT 許可證。詳情請參閱 [LICENSE](LICENSE) 文件。

## 📞 支援

如果您遇到問題或需要幫助：

1. 查看 [故障排除](#故障排除) 部分
2. 檢查 [Issues](../../issues) 是否有類似問題
3. 創建新的 Issue 描述您的問題

## 🔄 更新日誌

### v1.0.0
- 初始版本發布
- 支援 Milvus 和 DuckDB
- 完整的 Web 界面
- RESTful API

---

**開發者**: [Your Name]  
**版本**: 1.0.0  
**最後更新**: 2025年9月20日