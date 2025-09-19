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
        
        # 測試連接
        collections = utility.list_collections()
        logger.info(f"成功連接到 Milvus，找到 {len(collections)} 個集合")
        
        return {
            "status": "success",
            "message": f"成功連接到 Milvus ({connection.host}:{connection.port})",
            "collections_count": len(collections)
        }
        
    except Exception as e:
        logger.error(f"連接 Milvus 失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"連接失敗: {str(e)}")

@app.get("/milvus/collections")
async def get_collections():
    """獲取所有集合列表"""
    try:
        from pymilvus import utility
        collections = utility.list_collections()
        return {"collections": collections}
    except Exception as e:
        logger.error(f"獲取集合列表失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"獲取集合列表失敗: {str(e)}")

@app.get("/milvus/collection/{collection_name}/info")
async def get_collection_info(collection_name: str):
    """獲取指定集合的詳細信息"""
    try:
        from pymilvus import Collection, utility
        
        # 檢查集合是否存在
        if not utility.has_collection(collection_name):
            raise HTTPException(status_code=404, detail=f"集合 '{collection_name}' 不存在")
        
        collection = Collection(collection_name)
        
        # 獲取集合統計信息
        collection.load()
        stats = collection.get_compaction_state()
        
        info = {
            "name": collection_name,
            "schema": {
                "description": collection.description,
                "fields": []
            },
            "num_entities": collection.num_entities,
            "is_empty": collection.is_empty,
            "compaction_state": stats.state.name if hasattr(stats, 'state') else str(stats)
        }
        
        # 獲取字段信息
        for field in collection.schema.fields:
            field_info = {
                "name": field.name,
                "type": str(field.dtype),
                "is_primary": field.is_primary,
                "auto_id": field.auto_id,
            }
            if hasattr(field, 'dim'):
                field_info["dimension"] = field.dim
            info["schema"]["fields"].append(field_info)
        
        return info
        
    except Exception as e:
        logger.error(f"獲取集合信息失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"獲取集合信息失敗: {str(e)}")

@app.get("/milvus/collection/{collection_name}/data")
async def get_collection_data(collection_name: str, limit: int = Query(100, ge=1, le=1000)):
    """獲取集合中的數據"""
    try:
        from pymilvus import Collection, utility
        
        if not utility.has_collection(collection_name):
            raise HTTPException(status_code=404, detail=f"集合 '{collection_name}' 不存在")
        
        collection = Collection(collection_name)
        collection.load()
        
        # 獲取所有字段名
        field_names = [field.name for field in collection.schema.fields]
        
        # 查詢數據
        results = collection.query(
            expr="",  # 空表達式表示查詢所有數據
            output_fields=field_names,
            limit=limit
        )
        
        return {
            "collection_name": collection_name,
            "total_count": collection.num_entities,
            "returned_count": len(results),
            "data": results
        }
        
    except Exception as e:
        logger.error(f"獲取集合數據失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"獲取集合數據失敗: {str(e)}")

@app.post("/milvus/collection/{collection_name}/search")
async def search_collection(collection_name: str, search_request: MilvusSearchRequest):
    """在集合中搜索相似向量"""
    try:
        from pymilvus import Collection, utility
        
        if not utility.has_collection(collection_name):
            raise HTTPException(status_code=404, detail=f"集合 '{collection_name}' 不存在")
        
        collection = Collection(collection_name)
        collection.load()
        
        # 找到向量字段
        vector_field = None
        for field in collection.schema.fields:
            if field.dtype.name in ['FLOAT_VECTOR', 'BINARY_VECTOR']:
                vector_field = field.name
                break
        
        if not vector_field:
            raise HTTPException(status_code=400, detail="集合中沒有找到向量字段")
        
        # 執行搜索
        search_params = search_request.search_params or {"metric_type": "L2", "params": {"nprobe": 10}}
        
        results = collection.search(
            data=search_request.vectors,
            anns_field=vector_field,
            param=search_params,
            limit=search_request.limit,
            output_fields=[field.name for field in collection.schema.fields if not field.dtype.name.endswith('_VECTOR')]
        )
        
        # 格式化結果
        formatted_results = []
        for hits in results:
            hit_results = []
            for hit in hits:
                hit_data = {
                    "id": hit.id,
                    "distance": hit.distance,
                    "entity": hit.entity._row_data if hasattr(hit.entity, '_row_data') else {}
                }
                hit_results.append(hit_data)
            formatted_results.append(hit_results)
        
        return {
            "collection_name": collection_name,
            "search_results": formatted_results
        }
        
    except Exception as e:
        logger.error(f"搜索失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"搜索失敗: {str(e)}")

# ==================== DuckDB 相關端點 ====================

@app.post("/duckdb/upload")
async def upload_duckdb_file(file: UploadFile = File(...)):
    """上傳 DuckDB 文件"""
    global current_duckdb_path
    
    if not file.filename.endswith(('.db', '.duckdb')):
        raise HTTPException(status_code=400, detail="只支持 .db 或 .duckdb 文件格式")
    
    try:
        # 保存文件到臨時目錄
        file_path = os.path.join(temp_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 測試文件是否有效
        conn = duckdb.connect(file_path)
        tables = conn.execute("SHOW TABLES").fetchall()
        conn.close()
        
        current_duckdb_path = file_path
        logger.info(f"成功上傳 DuckDB 文件: {file.filename}，包含 {len(tables)} 個表")
        
        return {
            "status": "success",
            "message": f"成功上傳文件: {file.filename}",
            "tables_count": len(tables),
            "filename": file.filename
        }
        
    except Exception as e:
        logger.error(f"上傳文件失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上傳文件失敗: {str(e)}")

@app.get("/duckdb/tables")
async def get_tables():
    """獲取 DuckDB 中的所有表"""
    if not current_duckdb_path or not os.path.exists(current_duckdb_path):
        raise HTTPException(status_code=400, detail="請先上傳 DuckDB 文件")
    
    try:
        conn = duckdb.connect(current_duckdb_path)
        tables = conn.execute("SHOW TABLES").fetchall()
        table_names = [table[0] for table in tables]
        conn.close()
        
        return {"tables": table_names}
        
    except Exception as e:
        logger.error(f"獲取表列表失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"獲取表列表失敗: {str(e)}")

@app.get("/duckdb/table/{table_name}/info")
async def get_table_info(table_name: str):
    """獲取表的結構信息"""
    if not current_duckdb_path or not os.path.exists(current_duckdb_path):
        raise HTTPException(status_code=400, detail="請先上傳 DuckDB 文件")
    
    try:
        conn = duckdb.connect(current_duckdb_path)
        
        # 獲取表結構
        schema_info = conn.execute(f"DESCRIBE {table_name}").fetchall()
        
        # 獲取行數
        row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        
        conn.close()
        
        columns = []
        for col in schema_info:
            columns.append({
                "name": col[0],
                "type": col[1],
                "null": col[2],
                "key": col[3] if len(col) > 3 else None,
                "default": col[4] if len(col) > 4 else None
            })
        
        return {
            "table_name": table_name,
            "row_count": row_count,
            "columns": columns
        }
        
    except Exception as e:
        logger.error(f"獲取表信息失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"獲取表信息失敗: {str(e)}")

@app.get("/duckdb/table/{table_name}/data")
async def get_table_data(table_name: str, limit: int = Query(100, ge=1, le=10000)):
    """獲取表中的數據"""
    if not current_duckdb_path or not os.path.exists(current_duckdb_path):
        raise HTTPException(status_code=400, detail="請先上傳 DuckDB 文件")
    
    try:
        conn = duckdb.connect(current_duckdb_path)
        
        # 獲取數據
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        results = conn.execute(query).fetchall()
        
        # 獲取列名
        columns = [desc[0] for desc in conn.description]
        
        # 獲取總行數
        total_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        
        conn.close()
        
        # 轉換為字典列表
        data = []
        for row in results:
            row_dict = {}
            for i, col in enumerate(columns):
                row_dict[col] = row[i]
            data.append(row_dict)
        
        return {
            "table_name": table_name,
            "total_count": total_count,
            "returned_count": len(data),
            "data": data
        }
        
    except Exception as e:
        logger.error(f"獲取表數據失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"獲取表數據失敗: {str(e)}")

@app.post("/duckdb/query")
async def execute_sql_query(query_request: SQLQueryRequest):
    """執行自定義 SQL 查詢"""
    if not current_duckdb_path or not os.path.exists(current_duckdb_path):
        raise HTTPException(status_code=400, detail="請先上傳 DuckDB 文件")
    
    try:
        conn = duckdb.connect(current_duckdb_path)
        
        # 執行查詢
        result = conn.execute(query_request.query)
        
        # 檢查是否有結果
        try:
            rows = result.fetchall()
            columns = [desc[0] for desc in result.description] if result.description else []
        except:
            # 對於 INSERT, UPDATE, DELETE 等語句
            conn.close()
            return {
                "message": "查詢執行成功",
                "data": [],
                "affected_rows": result.rowcount if hasattr(result, 'rowcount') else 0
            }
        
        conn.close()
        
        # 轉換為字典列表
        data = []
        for row in rows:
            row_dict = {}
            for i, col in enumerate(columns):
                row_dict[col] = row[i]
            data.append(row_dict)
        
        return {
            "query": query_request.query,
            "returned_count": len(data),
            "data": data
        }
        
    except Exception as e:
        logger.error(f"執行查詢失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"執行查詢失敗: {str(e)}")

# ==================== 通用端點 ====================

@app.get("/")
async def serve_frontend():
    """提供前端頁面"""
    return FileResponse("index.html")

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "milvus_connected": milvus_client is not None,
        "duckdb_loaded": current_duckdb_path is not None,
        "temp_dir": temp_dir
    }

@app.on_event("shutdown")
async def shutdown_event():
    """應用關閉時清理資源"""
    try:
        # 斷開 Milvus 連接
        if milvus_client:
            from pymilvus import connections
            connections.disconnect("default")
        
        # 清理臨時文件
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            
        logger.info("應用關閉，資源清理完成")
    except Exception as e:
        logger.error(f"清理資源時出錯: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # 創建前端文件
    frontend_content = '''<!DOCTYPE html>
<html>
<head>
    <title>資料庫檢視器</title>
    <meta charset="UTF-8">
</head>
<body>
    <h1>資料庫檢視器</h1>
    <p>請使用前端界面訪問此應用程序。</p>
    <p>API 文檔請訪問: <a href="/docs">/docs</a></p>
</body>
</html>'''
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(frontend_content)
    
    # 啟動服務器
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )