#!/usr/bin/env python3
"""
資料庫檢視器啟動腳本
"""
import os
import sys
import subprocess
import uvicorn
from pathlib import Path

def check_python_version():
    """檢查 Python 版本"""
    if sys.version_info < (3, 8):
        print("❌ 需要 Python 3.8 或更高版本")
        sys.exit(1)
    print(f"✅ Python 版本: {sys.version}")

def setup_directories():
    """創建必要的目錄"""
    directories = [
        "uploads",
        "temp", 
        "logs",
        "static/css",
        "static/js", 
        "static/assets",
        "templates",
        "api",
        "utils",
        "tests"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        # 為 Python 包創建 __init__.py 文件
        if directory in ["api", "utils", "tests"]:
            init_file = Path(directory) / "__init__.py"
            if not init_file.exists():
                init_file.write_text("# -*- coding: utf-8 -*-\n")
    
    print("✅ 目錄結構創建完成")

def check_dependencies():
    """檢查依賴項是否已安裝"""
    required_packages = [
        "fastapi",
        "uvicorn", 
        "pymilvus",
        "duckdb",
        "python-multipart"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依賴項: {', '.join(missing_packages)}")
        print("正在自動安裝依賴項...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ])
            print("✅ 依賴項安裝完成")
        except subprocess.CalledProcessError:
            print("❌ 依賴項安裝失敗，請手動執行: pip install -r requirements.txt")
            return False
    else:
        print("✅ 所有依賴項已安裝")
    
    return True

def create_basic_files():
    """創建基本文件（如果不存在）"""
    # 創建 .env 文件
    if not Path(".env").exists():
        env_content = """# Milvus 配置
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
"""
        Path(".env").write_text(env_content)
        print("✅ 創建 .env 配置文件")

def main():
    """主啟動函數"""
    print("🚀 啟動資料庫檢視器...")
    print("=" * 50)
    
    # 檢查 Python 版本
    check_python_version()
    
    # 檢查依賴項
    if not check_dependencies():
        sys.exit(1)
    
    # 設置目錄結構
    setup_directories()
    
    # 創建基本文件
    create_basic_files()
    
    print("=" * 50)
    print("🌐 啟動 FastAPI 服務器...")
    print("📍 服務器地址: http://localhost:8000")
    print("📚 API 文檔: http://localhost:8000/docs")
    print("🏥 健康檢查: http://localhost:8000/health")
    print("=" * 50)
    
    # 啟動服務器
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 服務器已停止")
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()