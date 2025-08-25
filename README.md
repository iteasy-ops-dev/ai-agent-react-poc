# ReAct Agent v2 🤖

**Reasoning-Acting-Observing** 패턴을 구현한 인텔리전트 시스템 관리 에이전트입니다. LLM의 추론 과정을 실시간으로 시각화하고, 원격 서버 관리 작업을 자동화합니다.

## 🌟 주요 특징

### 🧠 투명한 AI 추론
- **실시간 추론 표시**: AI의 사고 과정을 단계별로 실시간 확인
- **ReAct 패턴**: Reasoning(추론) → Acting(행동) → Observing(관찰) 순환
- **콜백 시스템**: 각 단계별 세밀한 상태 추적 및 UI 업데이트
- **추론 히스토리**: 모든 사고 과정과 의사결정 근거 저장

### 🔧 시스템 관리 도구
- **동적 도구 발견**: 새로운 도구 추가 시 자동 인식
- **원격 실행**: SSH를 통한 안전한 원격 명령 실행
- **다중 분석 도구**: 시스템, 프로세스, 네트워크, 서비스, 컨테이너 분석
- **확장 가능한 아키텍처**: BaseTool 상속으로 쉬운 도구 확장

### 🚀 LLM 통합
- **멀티 LLM 지원**: OpenAI API, 로컬 모델(Ollama), 추론 모델 지원
- **적응형 클라이언트**: 모델별 최적화된 파라미터 자동 설정
- **Function Calling**: 도구 호출을 위한 네이티브 함수 호출 지원
- **토큰 추적**: 실시간 토큰 사용량 모니터링

### 🔒 보안 강화
- **메모리 기반 저장**: 민감한 정보는 세션에만 저장
- **SSH 보안**: paramiko 라이브러리를 통한 안전한 연결
- **중앙화 관리**: 서버 접속 정보 중앙 관리로 보안성 향상
- **권한 분리**: 읽기 전용 작업과 실행 작업 분리

## 🚀 빠른 시작

### Docker를 이용한 실행 (권장)

#### 1. Docker Compose로 실행
```bash
# 환경 설정 및 컨테이너 빌드 후 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d --build
```

#### 2. 환경 설정 (선택사항)
```bash
# .env 파일 생성 (OpenAI API 키 설정 시)
cp .env.example .env

# .env 파일을 편집하여 OpenAI API 키 설정
# OPENAI_API_KEY=your_openai_api_key_here
```

### 로컬 개발 환경에서 실행

#### 1. 가상환경 생성 및 활성화
```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate.bat
```

#### 2. 패키지 설치
```bash
pip install -r requirements.txt
```

#### 3. 환경 설정
```bash
# .env 파일 생성
cp .env.example .env

# .env 파일을 편집하여 OpenAI API 키 설정 (선택사항)
# OPENAI_API_KEY=your_openai_api_key_here
```

#### 4. 앱 실행
```bash
streamlit run streamlit_app_v2.py
```

## 🔧 Docker 컨테이너 관리

### 컨테이너 중지
```bash
docker-compose down
```

### 로그 확인
```bash
docker-compose logs -f
```

### 컨테이너 재시작
```bash
docker-compose restart
```

## 📋 시스템 요구사항

### 🖥️ 최소 시스템 요구사항
- **Python**: 3.8 이상 (권장: 3.12)
- **메모리**: 512MB 이상 (권장: 2GB)
- **저장공간**: 200MB 이상
- **네트워크**: 인터넷 연결 (LLM API 사용시)

### 🌐 LLM 서비스 요구사항
- **OpenAI API**: API 키 및 크레딧 필요
- **Ollama 로컬**: 2GB+ RAM, GPU 권장
- **기타 로컬 모델**: 모델별 하드웨어 요구사항 상이

### 🔒 원격 서버 접속 요구사항
- **SSH 접근**: 대상 서버에 SSH 접근 권한
- **포트 접근**: SSH 포트(기본 22) 접근 가능
- **사용자 권한**: 시스템 정보 조회 권한 (sudo 불필요)

## 🛠️ 사용 가능한 도구

### 📊 시스템 분석 도구
1. **시스템 정보 분석기** (`system_info_analyzer.py`)
   - OS 정보, CPU, 메모리, 디스크 상태 분석
   - 하드웨어 사양 및 시스템 리소스 모니터링
   - 시스템 업타임, 로드 평균, 커널 정보

2. **프로세스 모니터** (`process_monitor_analyzer.py`)
   - 실행 중인 프로세스 및 리소스 사용량 분석
   - CPU/메모리 사용률 높은 프로세스 식별
   - 프로세스 트리 구조 및 부모-자식 관계 분석

3. **네트워크 상태 분석기** (`network_status_analyzer.py`)
   - 네트워크 인터페이스, 포트, 라우팅 테이블 분석
   - 활성 연결 상태 및 네트워크 트래픽 모니터링
   - 방화벽 규칙 및 보안 상태 검사

4. **서비스 상태 분석기** (`service_status_analyzer.py`)
   - systemd 서비스 상태 및 관리
   - 실패한 서비스 탐지 및 로그 분석
   - 부팅 시 자동 시작 서비스 관리

5. **컨테이너 분석기** (`container_analyzer.py`)
   - Docker 컨테이너 및 이미지 정보 분석
   - Kubernetes 클러스터 상태 모니터링
   - 컨테이너 리소스 사용량 및 헬스체크

### 🔧 원격 실행 도구
6. **원격 명령어 실행기** (`exec_command_remote_system.py`)
   - SSH를 통한 안전한 원격 시스템 명령어 실행
   - 명령어 결과 실시간 스트리밍
   - 에러 핸들링 및 타임아웃 관리

### 🔌 도구 확장 시스템
- **BaseTool 추상 클래스**: 모든 도구의 기본 인터페이스
- **동적 도구 발견**: `tools/` 디렉토리에 새 도구 파일 추가 시 자동 인식
- **ToolsManager**: 도구 라이프사이클 관리 및 메타데이터 추출

## ⚙️ 설정 방법

### 1. LLM 설정
- **로컬 모델 (Ollama)**: 기본 설정으로 바로 사용 가능
- **OpenAI API**: `.env` 파일에 `OPENAI_API_KEY` 설정 필요

### 2. 원격 서버 설정
웹 인터페이스의 사이드바에서 다음 정보를 입력:
- 서버 IP 주소
- SSH 포트 (기본: 22)
- 사용자명
- 비밀번호

## 🔒 보안 고려사항

- 서버 접속 정보는 메모리에만 저장되며 세션 종료시 삭제
- 민감한 정보는 LLM에 노출되지 않도록 중앙화된 관리
- SSH 연결은 안전한 paramiko 라이브러리 사용

## 🎯 사용 예시

1. **시스템 상태 확인**: "현재 시스템의 전반적인 상태를 분석해줘"
2. **성능 모니터링**: "CPU와 메모리 사용률이 높은 프로세스를 찾아줘"
3. **네트워크 진단**: "네트워크 연결 상태와 열린 포트를 확인해줘"
4. **서비스 관리**: "실패한 systemd 서비스가 있는지 확인하고 해결 방법을 제시해줘"
5. **컨테이너 관리**: "실행 중인 Docker 컨테이너 상태를 분석해줘"

## 🛡️ 문제 해결

### 포트 충돌
- 기본 포트 8501이 사용 중인 경우 자동으로 8502 포트 사용
- 수동으로 포트 지정: `streamlit run streamlit_app_v2.py --server.port 8503`

### 가상환경 문제
- Windows에서 실행 정책 오류 발생시: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### API 키 오류
- OpenAI 모델 사용시 `.env` 파일의 `OPENAI_API_KEY` 확인
- 로컬 모델 사용시에는 API 키 불필요

## 📁 프로젝트 구조

```
function_calling_react/
├── 📄 streamlit_app_v2.py          # 메인 Streamlit 웹 애플리케이션
├── 🤖 agent_v2.py                  # ReAct 에이전트 핵심 로직 구현
│
├── 🧠 core/                        # 핵심 LLM 통신 모듈
│   ├── __init__.py
│   ├── model.py                    # 멀티 LLM 클라이언트 (OpenAI, Ollama 지원)
│   └── _DO_NOT_TOUCH_REACT_WITH_PROMPT.py  # ReAct 프롬프트 템플릿
│
├── ⚙️ config/                      # 설정 관리 모듈
│   ├── __init__.py
│   └── server_config.py            # 원격 서버 접속 설정 관리
│
├── 🔧 tools/                       # 시스템 관리 도구 모음
│   ├── base_tool.py                # 도구 기본 추상 클래스
│   ├── tools_manager.py            # 동적 도구 발견 및 관리
│   ├── system_info_analyzer.py     # 시스템 정보 분석 도구
│   ├── process_monitor_analyzer.py # 프로세스 모니터링 도구
│   ├── network_status_analyzer.py  # 네트워크 상태 분석 도구
│   ├── service_status_analyzer.py  # systemd 서비스 관리 도구
│   ├── container_analyzer.py       # Docker/K8s 컨테이너 분석 도구
│   └── exec_command_remote_system.py # SSH 원격 명령 실행 도구
│
├── 🐳 Docker 설정
│   ├── Dockerfile                  # Python 3.12 기반 컨테이너 이미지
│   ├── docker-compose.yml          # Docker Compose 설정
│   └── README_DOCKER.md            # Docker 실행 가이드
│
├── 📦 의존성 및 설정
│   ├── requirements.txt            # Python 패키지 의존성
│   └── .env.example               # 환경변수 설정 템플릿
│
├── 📚 문서
│   ├── README.md                   # 프로젝트 메인 문서 (이 파일)
│   └── AI_도입_전략_제안서.md        # AI 도입 전략 제안서
│
└── 🗂️ 가상환경
    └── venv/                       # Python 가상환경 (로컬 개발용)
```

### 🏗️ 아키텍처 설계

#### 1. 📱 프레젠테이션 계층 (Streamlit UI)
- **StreamlitReasoningCallback**: 실시간 추론 과정 시각화
- **반응형 UI**: 추론 단계별 확장 가능한 섹션
- **상태 관리**: 세션 기반 대화 히스토리 및 실행 기록

#### 2. 🤖 비즈니스 로직 계층 (ReAct Agent)
- **ReactAgentV2**: 추론-행동-관찰 순환 실행 엔진
- **ReasoningCallback**: 각 단계별 콜백 인터페이스
- **상태 추적**: 반복 횟수, 도구 호출, 결과 관찰

#### 3. 🧠 LLM 통신 계층 (Core)
- **LLMClient**: 멀티 모델 지원 통합 클라이언트
- **동적 라이브러리 선택**: 모델명 기반 자동 라이브러리 매핑
- **Function Calling**: 도구 호출을 위한 네이티브 지원

#### 4. 🔧 도구 실행 계층 (Tools)
- **ToolsManager**: 동적 도구 발견 및 라이프사이클 관리
- **BaseTool**: 모든 도구의 표준 인터페이스
- **도구 확장성**: 새 파일 추가만으로 자동 인식

#### 5. ⚙️ 설정 관리 계층 (Config)
- **ServerConfig**: 원격 서버 접속 정보 중앙 관리
- **보안 저장**: 메모리 기반 세션 저장으로 보안성 강화

## 🚀 기술 스택

### 🐍 Python 생태계
- **Streamlit**: 웹 UI 프레임워크
- **OpenAI**: LLM API 클라이언트
- **paramiko**: SSH 통신 라이브러리
- **python-dotenv**: 환경변수 관리

### 🤖 AI/ML 스택
- **ReAct Pattern**: Reasoning-Acting-Observing 순환
- **Function Calling**: LLM 네이티브 도구 호출
- **Multi-LLM**: OpenAI, Ollama, 추론 모델 지원
- **Dynamic Tool Discovery**: 런타임 도구 자동 발견

### 🐳 컨테이너 및 배포
- **Docker**: Python 3.12 slim 기반 컨테이너화
- **Docker Compose**: 단일 명령어 배포
- **Health Check**: 컨테이너 상태 모니터링

## 🎯 사용 사례 및 시나리오

### 🔍 시스템 진단 및 모니터링
```
사용자: "서버 성능이 느려진 것 같은데 원인을 분석해줘"
→ AI가 시스템 정보, 프로세스, 네트워크 순차 분석
→ 병목지점 식별 및 개선 방안 제시
```

### 🐛 문제 해결 자동화
```
사용자: "웹서버가 응답하지 않는다"
→ AI가 서비스 상태, 포트 상태, 로그 확인
→ 문제 진단 및 재시작 방법 제시
```

### 📊 시스템 리포트 생성
```
사용자: "월말 시스템 현황 보고서 작성해줘"
→ AI가 모든 도구 실행하여 종합 분석
→ 구조화된 리포트와 권장사항 생성
```

### 🔧 유지보수 작업 가이드
```
사용자: "Docker 컨테이너 최적화 방법 알려줘"
→ AI가 컨테이너 상태 분석
→ 리소스 사용량 기반 최적화 가이드 제공
```

## 🤝 기여하기

이 프로젝트는 **ReAct 패턴과 LLM을 활용한 지능형 시스템 관리 도구**의 실증 연구(PoC)입니다.

### 🎯 기여 방향
- **새로운 분석 도구 개발**: `tools/` 디렉토리에 BaseTool 상속 클래스 추가
- **LLM 모델 지원 확장**: `core/model.py`에 새로운 LLM 제공업체 지원 추가
- **UI/UX 개선**: Streamlit 인터페이스 사용성 향상
- **보안 강화**: SSH 연결 및 데이터 처리 보안성 향상

### 📝 기여 과정
1. **이슈 등록**: 버그 리포트 또는 기능 요청 등록
2. **포크 및 브랜치**: 개발용 브랜치 생성
3. **개발 및 테스트**: 로컬 환경에서 개발 및 검증
4. **풀 리퀘스트**: 코드 리뷰 및 머지 요청

## 📊 성능 및 확장성

### ⚡ 성능 특성
- **응답 시간**: 로컬 도구 실행 < 1초, 원격 도구 실행 < 5초
- **동시 사용자**: Streamlit 기본 설정으로 10-50명 지원
- **메모리 사용량**: 기본 실행 시 50-100MB
- **토큰 효율성**: ReAct 패턴으로 불필요한 LLM 호출 최소화

### 🔄 확장성 고려사항
- **수평 확장**: Docker 컨테이너 기반 로드밸런싱 지원
- **도구 확장**: 플러그인 아키텍처로 무제한 도구 추가 가능
- **LLM 확장**: 새로운 모델 제공업체 쉽게 통합
- **데이터베이스 연동**: 세션 상태를 영구 저장소로 확장 가능

## 📄 라이선스

이 프로젝트는 **MIT 라이선스** 하에 배포됩니다.

```
MIT License

Copyright (c) 2024 ReAct Agent v2 Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```