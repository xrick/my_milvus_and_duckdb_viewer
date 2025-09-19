#!/bin/bash

# 設置顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "================================================"
echo "          🚀 資料庫檢視器啟動程序"  
echo "================================================"
echo -e "${NC}"

# 檢查 Python 是否安裝
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安裝${NC}"
    echo "請先安裝 Python 3.8 或更高版本"
    exit 1
fi

echo -e "${GREEN}✅ 找到 Python3${NC}"

# 檢查 Python 版本
python_version=$(python3 -c "import sys; print(sys.version_info[:2])")
if [[ "$python_version" < "(3, 8)" ]]; then
    echo -e "${RED}❌ 需要 Python 3.8 或更高版本${NC}"
    exit 1
fi

# 檢查並激活虛擬環境
if [ -d "venv" ]; then
    echo -e "${YELLOW}🔧 發現虛擬環境，正在激活...${NC}"
    source venv/bin/activate
    echo -e "${GREEN}✅ 虛擬環境已激活${NC}"
else
    echo -e "${YELLOW}ℹ️  未找到虛擬環境，使用全局 Python 環境${NC}"
    echo "建議創建虛擬環境: python3 -m venv venv"
fi

# 檢查必要文件
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ 找不到 requirements.txt 文件${NC}"
    exit 1
fi

if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ 找不到 main.py 文件${NC}" 
    exit 1
fi

if [ ! -f "start.py" ]; then
    echo -e "${RED}❌ 找不到 start.py 文件${NC}"
    exit 1
fi

# 給腳本執行權限
chmod +x "$0"

# 安裝/更新依賴項
echo ""
echo -e "${YELLOW}📦 檢查並安裝依賴項...${NC}"
if ! pip install -r requirements.txt; then
    echo -e "${RED}❌ 依賴項安裝失敗${NC}"
    exit 1
fi

# 創建必要目錄
echo -e "${GREEN}📁 創建必要目錄...${NC}"
mkdir -p uploads temp logs static/{css,js,assets} templates api utils tests

# 啟動應用程序
echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}🌐 正在啟動服務器...${NC}"
echo -e "${BLUE}📍 服務器地址: http://localhost:8000${NC}"
echo -e "${BLUE}📚 API 文檔: http://localhost:8000/docs${NC}"
echo -e "${BLUE}🏥 健康檢查: http://localhost:8000/health${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止服務器${NC}"
echo ""

# 啟動服務器
python3 start.py

echo ""
echo -e "${GREEN}👋 服務器已停止${NC}"