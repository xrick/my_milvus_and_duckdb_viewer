# main.py
from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import duckdb
import os
import tempfile
import shutil
from pathlib import Path
import json
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建 FastAPI 應用
app = FastAPI(
    title="資料庫集合檢視器",
    description="支持 Milvus 和 DuckDB 的 web 應用程序",
    version="1.0.0"
)

# 添加 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生產環境中應該設置具體的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局變量
milvus_client = None
current_duckdb_path = None
temp_dir = tempfile.mkdtemp()

# Pydantic 模型
class MilvusConnectionRequest(BaseModel):
    host: str = "localhost"
    port: int = 19530

class SQLQueryRequest(BaseModel):
    query: str

class MilvusSearchRequest(BaseModel):
    collection_name: str
    vectors: List[List[float]]
    limit: int = 10
    search_params: Optional[Dict] = None

# ==================== Milvus 相關端點 ====================

@app.post("/milvus/connect")
async def connect_milvus(connection: MilvusConnectionRequest):
    """連接到 Milvus 服務器"""
    global milvus_client
    try:
        from pymilvus import connections, utility
        
        # 斷開現有連接
        try:
            connections.disconnect("default")
        except:
            pass
        
        # 建立新連接
        connections.connect(
            alias="default",
            host=connection.host,
            port=str(connection.port)
        )
        
        # 測試