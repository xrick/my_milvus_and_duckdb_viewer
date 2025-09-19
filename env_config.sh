# Milvus 配置
MILVUS_HOST=localhost
MILVUS_PORT=19530

# 服務器配置
HOST=0.0.0.0
PORT=8000
DEBUG=True

# 文件上傳配置
MAX_FILE_SIZE=104857600
UPLOAD_DIR=./uploads

# 日誌配置
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log

# 數據庫配置
TEMP_DIR=./temp

# CORS 配置
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:8000"]

# 安全配置
SECRET_KEY=your-secret-key-here-change-in-production