# ReAct Agent v2 🤖

LLM의 추론 과정을 실시간으로 확인할 수 있는 개선된 ReAct(Reasoning-Acting-Observing) 에이전트입니다.

## 🌟 주요 특징

- **실시간 추론 표시**: AI의 사고 과정을 단계별로 실시간 확인
- **다양한 시스템 관리 도구**: 원격 서버의 시스템 정보, 프로세스, 네트워크, 서비스, 컨테이너 분석
- **투명한 AI**: 사용자가 AI의 의사결정 과정을 완전히 이해할 수 있는 투명성 제공
- **안전한 원격 실행**: 중앙화된 서버 설정으로 보안 강화
- **다중 LLM 지원**: OpenAI API 및 로컬 모델(Ollama) 지원

## 🚀 빠른 시작

### 자동 설정 및 실행 (권장)

#### Linux/macOS
```bash
# 실행 권한 부여 (필요시)
chmod +x setup.sh

# 자동 설정 및 실행
./setup.sh
```

#### Windows
```cmd
# 자동 설정 및 실행
setup.bat
```

### 수동 설정

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

## 🔧 이미 설정된 환경에서 실행

### Linux/macOS
```bash
./run.sh
```

### Windows
```cmd
run.bat
```

## 📋 시스템 요구사항

- Python 3.8 이상
- 512MB 이상의 RAM
- 인터넷 연결 (LLM API 사용시)

## 🛠️ 사용 가능한 도구

1. **시스템 정보 분석기**: OS, CPU, 메모리, 디스크 정보
2. **프로세스 모니터**: 실행 중인 프로세스 및 리소스 사용량
3. **네트워크 상태 분석기**: 네트워크 인터페이스, 포트, 라우팅 정보
4. **서비스 상태 분석기**: systemd 서비스 상태 및 관리
5. **컨테이너 분석기**: Docker 컨테이너 및 Kubernetes 정보
6. **원격 명령어 실행**: SSH를 통한 원격 시스템 명령어 실행

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
├── streamlit_app_v2.py     # 메인 Streamlit 애플리케이션
├── agent_v2.py             # ReAct 에이전트 구현
├── core/
│   └── model.py            # LLM 클라이언트
├── config/
│   └── server_config.py    # 서버 설정 관리
├── tools/                  # 시스템 분석 도구들
│   ├── base_tool.py
│   ├── system_info_analyzer.py
│   ├── process_monitor_analyzer.py
│   ├── network_status_analyzer.py
│   ├── service_status_analyzer.py
│   ├── container_analyzer.py
│   └── exec_command_remote_system.py
├── setup.sh               # Linux/macOS 자동 설정 스크립트
├── setup.bat              # Windows 자동 설정 스크립트
├── run.sh                 # Linux/macOS 실행 스크립트
├── run.bat                # Windows 실행 스크립트
├── requirements.txt        # Python 패키지 의존성
├── .env.example           # 환경변수 템플릿
└── README.md              # 이 파일
```

## 🤝 기여하기

이 프로젝트는 ReAct 패턴과 LLM을 활용한 시스템 관리 도구의 PoC(Proof of Concept)입니다. 
기여하고 싶으시다면 이슈를 등록하거나 풀 리퀘스트를 보내주세요.

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.