# Docker 실행 가이드

## 사전 요구사항
- Docker 및 Docker Compose 설치
- OpenAI API 키

## 실행 방법

### 1. 환경 변수 설정
`.env` 파일을 생성하고 OpenAI API 키를 추가:
```bash
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### 2. Docker Compose로 실행

#### 빌드 및 실행
```bash
# 이미지 빌드 및 컨테이너 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d --build
```

#### 실행 중인 컨테이너 확인
```bash
docker-compose ps
```

#### 로그 확인
```bash
docker-compose logs -f
```

#### 종료
```bash
docker-compose down
```

#### 컨테이너 및 볼륨 완전 삭제
```bash
docker-compose down -v
```

### 3. Docker 명령어로 직접 실행

#### 이미지 빌드
```bash
docker build -t function-calling-react .
```

#### 컨테이너 실행
```bash
docker run -d \
  --name function-calling-react \
  -p 8501:8501 \
  -e OPENAI_API_KEY=${OPENAI_API_KEY} \
  function-calling-react
```

## 접속 방법
브라우저에서 http://localhost:8501 접속

## 개발 모드
코드 변경사항을 실시간으로 반영하려면 `docker-compose.yml`의 volumes 섹션 주석을 해제하세요:

```yaml
volumes:
  - ./core:/app/core
  - ./streamlit_app_v2.py:/app/streamlit_app_v2.py
```

## 문제 해결

### 포트 충돌
8501 포트가 이미 사용 중인 경우, `docker-compose.yml`에서 포트 변경:
```yaml
ports:
  - "8502:8501"  # 로컬포트:컨테이너포트
```

### 메모리 부족
리소스 제한을 조정하려면 `docker-compose.yml`의 deploy 섹션 수정

### 컨테이너 재시작
```bash
docker-compose restart
```