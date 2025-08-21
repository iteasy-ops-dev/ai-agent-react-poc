#!/bin/bash

# ReAct Agent v2 실행 스크립트 (설정 완료 후 실행용)
# Linux/macOS 환경용

set -e

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}        ReAct Agent v2 실행           ${NC}"
echo -e "${BLUE}========================================${NC}"
echo

# 가상환경 확인 및 활성화
if [ ! -d "venv" ]; then
    echo -e "${RED}[ERROR]${NC} 가상환경이 설정되지 않았습니다."
    echo "먼저 setup.sh를 실행해주세요: ./setup.sh"
    exit 1
fi

echo -e "${BLUE}[INFO]${NC} 가상환경 활성화 중..."
source venv/bin/activate

# .env 파일 확인
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}[WARNING]${NC} .env 파일이 없습니다. .env.example에서 복사합니다."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}[SUCCESS]${NC} .env 파일이 생성되었습니다."
    fi
fi

# 포트 확인
PORT=8501
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null; then
    echo -e "${YELLOW}[WARNING]${NC} 포트 $PORT가 이미 사용 중입니다."
    PORT=8502
    echo -e "${BLUE}[INFO]${NC} 대안 포트 $PORT를 사용합니다."
fi

# Streamlit 앱 실행
echo -e "${GREEN}[SUCCESS]${NC} ReAct Agent v2 시작 중..."
echo -e "${GREEN}브라우저에서 http://localhost:$PORT 을 열어주세요${NC}"
echo -e "${YELLOW}앱을 중지하려면 Ctrl+C를 눌러주세요${NC}"
echo

streamlit run streamlit_app_v2.py --server.port $PORT --server.address 0.0.0.0