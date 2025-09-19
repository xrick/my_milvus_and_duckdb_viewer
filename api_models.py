# -*- coding: utf-8 -*-
"""
Pydantic 資料模型定義
用於 API 請求和響應的資料驗證和序列化
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import re

# ==================== 通用模型 ====================

class BaseResponse(BaseModel):
    """基礎響應模型"""
    status: str = Field(..., description="響應狀態")
    message: str = Field(..., description="響應消息")
    timestamp: datetime = Field(default_factory=datetime.now, description="時間戳")

class ErrorResponse(BaseResponse):
    """錯誤響應模型"""
    error_code: Optional[str] = Field(None, description="錯誤代碼")
    details: Optional[Dict[str, Any]] = Field(None, description="錯誤詳情")

class HealthResponse(BaseModel):
    """健康檢查響應模型"""
    status: str = Field(..., description="系統狀態")
    milvus_connected: bool = Field(..., description="Milvus 連接狀態")
    duckdb_loaded: bool = Field(..., description="DuckDB 載入狀態")
    temp_dir: str = Field(..., description="臨時目錄路徑")
    uptime: Optional[str] = Field(None, description="運行時間")

# ==================== Milvus 相關模型 ====================

class MilvusConnectionRequest(BaseModel):
    """Milvus 連接請求模型"""
    host: str = Field("localhost", description="Milvus 服務器主機地址")
    port: int = Field(19530, ge=1, le=65535, description="Milvus 服務器端口")
    
    @validator('host')
    def validate_host(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('主機地址不能為空')
        return v.strip()
    
    @validator('port')
    def validate_port(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError('端口必須在 1-65535 範圍內')
        return v

class MilvusConnectionResponse(BaseResponse):
    """Milvus 連接響應模型"""
    host: str = Field(..., description="連接的主機地址")
    port: int = Field(..., description="連接的端口")
    collections_count: int = Field(..., description="集合數量")

class MilvusCollectionsResponse(BaseModel):
    """Milvus 集合列表響應模型"""
    collections: List[str] = Field(..., description="集合名稱列表")
    total_count: int = Field(..., description="集合總數")

class MilvusFieldInfo(BaseModel):
    """Milvus 字段信息模型"""
    name: str = Field(..., description="字段名稱")
    type: str = Field(..., description="字段類型")
    is_primary: bool = Field(..., description="是否為主鍵")
    auto_id: bool = Field(..., description="是否自動生成ID")
    dimension: Optional[int] = Field(None, description="向量維度")

class MilvusSchemaInfo(BaseModel):
    """Milvus 集合架構信息模型"""
    description: str = Field(..., description="集合描述")
    fields: List[MilvusFieldInfo] = Field(..., description="字段列表")

class MilvusCollectionInfo(BaseModel):
    """Milvus 集合信息模型"""
    name: str = Field(..., description="集合名稱")
    schema: MilvusSchemaInfo = Field(..., description="集合架構")
    num_entities: int = Field(..., description="實體數量")
    is_empty: bool = Field(..., description="是否為空")
    compaction_state: str = Field(..., description="壓縮狀態")

class MilvusDataResponse(BaseModel):
    """Milvus 數據響應模型"""
    collection_name: str = Field(..., description="集合名稱")
    total_count: int = Field(..., description="總記錄數")
    returned_count: int = Field(..., description="返回記錄數")
    data: List[Dict[str, Any]] = Field(..., description="數據內容")

class MilvusSearchRequest(BaseModel):
    """Milvus 搜索請求模型"""
    collection_name: str = Field(..., description="集合名稱")
    vectors: List[List[float]] = Field(..., description="查詢向量")
    limit: int = Field(10, ge=1, le=1000, description="返回結果數量限制")
    search_params: Optional[Dict[str, Any]] = Field(None, description="搜索參數")
    
    @validator('vectors')
    def validate_vectors(cls, v):
        if not v or len(v) == 0:
            raise ValueError('查詢向量不能為空')
        
        # 檢查所有向量維度是否一致
        if len(v) > 1:
            first_dim = len(v[0])
            for i, vec in enumerate(v[1:], 1):
                if len(vec) != first_dim:
                    raise ValueError(f'向量 {i} 的維度與第一個向量不一致')
        
        return v

class MilvusSearchResponse(BaseModel):
    """Milvus 搜索響應模型"""
    collection_name: str = Field(..., description="集合名稱")
    search_results: List[List[Dict[str, Any]]] = Field(..., description="搜索結果")

# ==================== DuckDB 相關模型 ====================

class DuckDBUploadResponse(BaseResponse):
    """DuckDB 上傳響應模型"""
    filename: str = Field(..., description="上傳的文件名")
    file_size: int = Field(..., description="文件大小（位元組）")
    tables_count: int = Field(..., description="包含的表格數量")

class DuckDBTablesResponse(BaseModel):
    """DuckDB 表格列表響應模型"""
    tables: List[str] = Field(..., description="表格名稱列表")
    total_count: int = Field(..., description="表格總數")

class DuckDBColumnInfo(BaseModel):
    """DuckDB 表格列信息模型"""
    name: str = Field(..., description="列名")
    type: str = Field(..., description="資料類型")
    null: str = Field(..., description="是否允許NULL")
    key: Optional[str] = Field(None, description="鍵類型")
    default: Optional[str] = Field(None, description="預設值")

class DuckDBTableInfo(BaseModel):
    """DuckDB 表格信息模型"""
    table_name: str = Field(..., description="表格名稱")
    row_count: int = Field(..., description="行數")
    columns: List[DuckDBColumnInfo] = Field(..., description="列信息")

class DuckDBDataResponse(BaseModel):
    """DuckDB 數據響應模型"""
    table_name: Optional[str] = Field(None, description="表格名稱")
    total_count: Optional[int] = Field(None, description="總記錄數")
    returned_count: int = Field(..., description="返回記錄數")
    data: List[Dict[str, Any]] = Field(..., description="數據內容")

class SQLQueryRequest(BaseModel):
    """SQL 查詢請求模型"""
    query: str = Field(..., min_length=1, description="SQL 查詢語句")
    
    @validator('query')
    def validate_query(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('SQL 查詢語句不能為空')
        
        # 簡單的 SQL 注入檢查
        dangerous_patterns = [
            r';\s*drop\s+',
            r';\s*delete\s+',
            r';\s*truncate\s+',
            r';\s*alter\s+',
            r';\s*create\s+',
            r'--\s*$',
            r'/\*.*\*/',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError('檢測到潛在的危險 SQL 語句')
        
        return v

class SQLQueryResponse(BaseModel):
    """SQL 查詢響應模型"""
    query: str = Field(..., description="執行的查詢語句")
    execution_time: Optional[float] = Field(None, description="執行時間（秒）")
    returned_count: Optional[int] = Field(None, description="返回記錄數")
    affected_rows: Optional[int] = Field(None, description="影響行數")
    data: List[Dict[str, Any]] = Field(..., description="查詢結果數據")
    message: Optional[str] = Field(None, description="執行消息")

# ==================== 文件上傳相關模型 ====================

class FileUploadResponse(BaseResponse):
    """文件上傳響應模型"""
    filename: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小")
    content_type: str = Field(..., description="文件類型")
    upload_path: str = Field(..., description="上傳路徑")

# ==================== 統計和監控模型 ====================

class SystemStats(BaseModel):
    """系統統計信息模型"""
    cpu_usage: Optional[float] = Field(None, description="CPU 使用率")
    memory_usage: Optional[float] = Field(None, description="記憶體使用率")
    disk_usage: Optional[float] = Field(None, description="磁碟使用率")
    active_connections: int = Field(..., description="活動連接數")
    upload_files_count: int = Field(..., description="上傳文件數量")
    temp_files_size: int = Field(..., description="臨時文件大小")

class APIUsageStats(BaseModel):
    """API 使用統計模型"""
    total_requests: int = Field(..., description="總請求數")
    successful_requests: int = Field(..., description="成功請求數")
    failed_requests: int = Field(..., description="失敗請求數")
    avg_response_time: float = Field(..., description="平均響應時間")
    most_used_endpoints: Dict[str, int] = Field(..., description="最常使用的端點")

# ==================== 驗證器和工具函數 ====================

def validate_table_name(table_name: str) -> str:
    """驗證表格名稱"""
    if not table_name or not table_name.strip():
        raise ValueError('表格名稱不能為空')
    
    # 檢查表格名稱是否包含危險字符
    if re.search(r'[;"\'\\]', table_name):
        raise ValueError('表格名稱包含非法字符')
    
    return table_name.strip()

def validate_collection_name(collection_name: str) -> str:
    """驗證集合名稱"""
    if not collection_name or not collection_name.strip():
        raise ValueError('集合名稱不能為空')
    
    return collection_name.strip()

# ==================== 配置模型 ====================

class AppConfig(BaseModel):
    """應用程序配置模型"""
    debug: bool = Field(False, description="調試模式")
    host: str = Field("0.0.0.0", description="服務器主機")
    port: int = Field(8000, ge=1, le=65535, description="服務器端口")
    max_file_size: int = Field(104857600, description="最大文件大小")
    cors_origins: List[str] = Field([], description="CORS 允許的來源")
    log_level: str = Field("INFO", description="日誌級別")
    
    class Config:
        env_prefix = "APP_"