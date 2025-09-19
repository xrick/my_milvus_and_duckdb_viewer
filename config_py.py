import os
from typing import List
from pydantic import BaseSettings

class Settings(BaseSettings):
    """應用程序配置設置"""
    
    # Milvus 設置
    milvus_host: str = "localhost"
    milvus_port: int = 19530
    
    # 服務器設置
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # 文件上傳設置
    max_file_size: int = 104857600  # 100MB
    upload_dir: str = "./uploads"
    temp_dir: str = "./temp"
    
    # 日誌設置
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    
    # CORS 設置
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080", 
        "http://127.0.0.1:8000"
    ]
    
    # 安全設置
    secret_key: str = "your-secret-key-here-change-in-production"
    
    # 靜態文件設置
    static_dir: str = "./static"
    templates_dir: str = "./templates"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# 創建設置實例
settings = Settings()

# 創建必要目錄的函數
def create_directories():
    """創建應用程序所需的目錄"""
    directories = [
        settings.upload_dir,
        settings.temp_dir,
        os.path.dirname(settings.log_file),
        settings.static_dir,
        f"{settings.static_dir}/css",
        f"{settings.static_dir}/js",
        f"{settings.static_dir}/assets",
        settings.templates_dir
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ 所有必要目錄已創建")