@echo off
rem ReAct Agent v2 자동 설정 및 실행 스크립트
rem Windows 환경용

setlocal enabledelayedexpansion

echo ========================================
echo      ReAct Agent v2 자동 설정
echo ========================================
echo.

rem 1. Python 설치 확인
echo [INFO] Python 설치 확인 중...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python이 설치되지 않았습니다.
    echo Python을 설치하고 다시 실행해주세요.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [SUCCESS] Python 설치 확인: !PYTHON_VERSION!

rem 2. 가상환경 생성 및 활성화
echo [INFO] 가상환경 확인 중...
if not exist "venv" (
    echo [INFO] 가상환경 생성 중...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] 가상환경 생성에 실패했습니다.
        pause
        exit /b 1
    )
    echo [SUCCESS] 가상환경 생성 완료
) else (
    echo [SUCCESS] 기존 가상환경 발견
)

echo [INFO] 가상환경 활성화 중...
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] 가상환경 활성화 스크립트를 찾을 수 없습니다.
    pause
    exit /b 1
)
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] 가상환경 활성화에 실패했습니다.
    pause
    exit /b 1
)
echo [SUCCESS] 가상환경 활성화 완료

rem 3. 패키지 설치
echo [INFO] Python 패키지 설치 중...
if exist "requirements.txt" (
    echo [INFO] pip 업그레이드 중...
    python -m pip install --upgrade pip
    if errorlevel 1 (
        echo [WARNING] pip 업그레이드에 실패했지만 계속 진행합니다.
    )
    
    echo [INFO] requirements.txt 패키지들 설치 중...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] 패키지 설치에 실패했습니다.
        echo 인터넷 연결을 확인하고 다시 시도해주세요.
        pause
        exit /b 1
    )
    echo [SUCCESS] 패키지 설치 완료
) else (
    echo [ERROR] requirements.txt 파일을 찾을 수 없습니다.
    pause
    exit /b 1
)

rem 4. .env 파일 설정
echo [INFO] .env 파일 설정 중...
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [SUCCESS] .env 파일을 .env.example에서 복사했습니다.
        
        echo.
        echo [WARNING] OpenAI API 키 설정이 필요합니다.
        echo 1. 로컬 모델만 사용하는 경우: Enter를 눌러 건너뛰기
        echo 2. OpenAI API를 사용하는 경우: API 키를 입력하세요
        echo.
        set /p api_key="OpenAI API 키를 입력하세요 (선택사항): "
        
        if not "!api_key!"=="" (
            rem .env 파일에서 API 키 업데이트
            powershell -Command "(gc .env) -replace 'your_openai_api_key_here', '!api_key!' | Out-File -Encoding UTF8 .env"
            echo [SUCCESS] OpenAI API 키가 설정되었습니다.
        ) else (
            echo [INFO] 로컬 모델 모드로 설정되었습니다.
        )
    ) else (
        echo [ERROR] .env.example 파일을 찾을 수 없습니다.
        pause
        exit /b 1
    )
) else (
    echo [SUCCESS] 기존 .env 파일 발견
)

rem 5. 포트 확인
set PORT=8501
echo [INFO] 포트 %PORT% 사용 가능 여부 확인 중...
netstat -an | find ":%PORT%" >nul
if not errorlevel 1 (
    echo [WARNING] 포트 %PORT%가 이미 사용 중입니다.
    set PORT=8502
    echo [INFO] 대안 포트 !PORT! 사용합니다.
)

rem 6. Streamlit 설치 확인
echo [INFO] Streamlit 설치 확인 중...
streamlit --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Streamlit이 설치되지 않았습니다.
    echo 패키지 설치를 다시 확인해주세요.
    pause
    exit /b 1
)

rem 7. Streamlit 앱 실행
echo.
echo [SUCCESS] 모든 설정이 완료되었습니다!
echo.
echo [INFO] Streamlit 앱을 시작합니다...
echo 브라우저에서 http://localhost:!PORT! 을 열어주세요
echo 앱을 중지하려면 Ctrl+C를 눌러주세요
echo.
echo 잠시 후 Streamlit이 시작됩니다...
timeout /t 3 /nobreak >nul

rem Streamlit 실행
echo [INFO] Streamlit 실행 중...
streamlit run streamlit_app_v2.py --server.port !PORT! --server.address 0.0.0.0
if errorlevel 1 (
    echo.
    echo [ERROR] Streamlit 실행에 실패했습니다.
    echo 문제가 발생했습니다. 다음을 확인해주세요:
    echo 1. streamlit_app_v2.py 파일이 존재하는지 확인
    echo 2. 가상환경이 올바르게 활성화되었는지 확인
    echo 3. 포트 !PORT!가 사용 가능한지 확인
    echo.
    pause
    exit /b 1
) 