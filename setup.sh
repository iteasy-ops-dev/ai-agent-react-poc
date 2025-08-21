#!/bin/bash

# ReAct Agent v2 자동 설정 및 실행 스크립트
# Linux/macOS 환경용

set -e  # 에러 발생 시 스크립트 종료

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수들
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 제목 출력
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}     ReAct Agent v2 자동 설정         ${NC}"
echo -e "${BLUE}========================================${NC}"
echo

# 1. Python 설치 확인
log_info "Python 설치 확인 중..."
if ! command -v python3 &> /dev/null; then
    log_error "Python3이 설치되지 않았습니다."
    echo "Python3를 설치하고 다시 실행해주세요."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
log_success "Python 설치 확인: $PYTHON_VERSION"

# 2. 가상환경 생성 및 활성화
log_info "가상환경 확인 중..."
if [ ! -d "venv" ]; then
    log_info "가상환경 생성 중..."
    python3 -m venv venv
    log_success "가상환경 생성 완료"
else
    log_success "기존 가상환경 발견"
fi

log_info "가상환경 활성화 중..."
source venv/bin/activate
log_success "가상환경 활성화 완료"

# 3. 패키지 설치
log_info "Python 패키지 설치 중..."
if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
    log_success "패키지 설치 완료"
else
    log_error "requirements.txt 파일을 찾을 수 없습니다."
    exit 1
fi

# 4. .env 파일 설정
log_info ".env 파일 설정 중..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        log_success ".env 파일을 .env.example에서 복사했습니다."
        
        echo
        log_warning "OpenAI API 키 설정이 필요합니다."
        echo "1. 로컬 모델만 사용하는 경우: Enter를 눌러 건너뛰기"
        echo "2. OpenAI API를 사용하는 경우: API 키를 입력하세요"
        echo
        read -p "OpenAI API 키를 입력하세요 (선택사항): " api_key
        
        if [ ! -z "$api_key" ]; then
            # .env 파일에서 API 키 업데이트
            sed -i.bak "s/your_openai_api_key_here/$api_key/" .env
            rm .env.bak 2>/dev/null || true
            log_success "OpenAI API 키가 설정되었습니다."
        else
            log_info "로컬 모델 모드로 설정되었습니다."
        fi
    else
        log_error ".env.example 파일을 찾을 수 없습니다."
        exit 1
    fi
else
    log_success "기존 .env 파일 발견"
fi

# 5. 포트 확인
PORT=8501
log_info "포트 $PORT 사용 가능 여부 확인 중..."
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null; then
    log_warning "포트 $PORT가 이미 사용 중입니다."
    PORT=8502
    log_info "대안 포트 $PORT 사용합니다."
fi

# 6. Streamlit 앱 실행
echo
log_success "모든 설정이 완료되었습니다!"
echo
log_info "Streamlit 앱을 시작합니다..."
echo -e "${GREEN}브라우저에서 http://localhost:$PORT 을 열어주세요${NC}"
echo -e "${YELLOW}앱을 중지하려면 Ctrl+C를 눌러주세요${NC}"
echo

# Streamlit 실행
streamlit run streamlit_app_v2.py --server.port $PORT --server.address 0.0.0.0