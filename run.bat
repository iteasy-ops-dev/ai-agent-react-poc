@echo off
rem ReAct Agent v2 실행 스크립트 (설정 완료 후 실행용)
rem Windows 환경용

setlocal enabledelayedexpansion

echo ========================================
echo         ReAct Agent v2 실행
echo ========================================
echo.

rem 가상환경 확인 및 활성화
if not exist "venv" (
    echo [ERROR] 가상환경이 설정되지 않았습니다.
    echo 먼저 setup.bat을 실행해주세요: setup.bat
    pause
    exit /b 1
)

echo [INFO] 가상환경 활성화 중...
call venv\Scripts\activate.bat

rem .env 파일 확인
if not exist ".env" (
    echo [WARNING] .env 파일이 없습니다. .env.example에서 복사합니다.
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [SUCCESS] .env 파일이 생성되었습니다.
    )
)

rem 포트 확인
set PORT=8501
netstat -an | find ":%PORT%" >nul
if not errorlevel 1 (
    echo [WARNING] 포트 %PORT%가 이미 사용 중입니다.
    set PORT=8502
    echo [INFO] 대안 포트 !PORT!를 사용합니다.
)

rem Streamlit 앱 실행
echo [SUCCESS] ReAct Agent v2 시작 중...
echo 브라우저에서 http://localhost:!PORT! 을 열어주세요
echo 앱을 중지하려면 Ctrl+C를 눌러주세요
echo.

streamlit run streamlit_app_v2.py --server.port !PORT! --server.address 0.0.0.0