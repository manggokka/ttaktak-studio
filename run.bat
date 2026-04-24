@echo off
chcp 65001 > nul
cls

echo.
echo ================================================================
echo   🔧 뚝딱공작소 - AI 이미지 업스케일러
echo ================================================================
echo.

REM Python 버전 확인
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았습니다!
    echo.
    echo Python을 설치해주세요: https://www.python.org/downloads/
    echo (설치 시 "Add Python to PATH" 체크하기)
    echo.
    pause
    exit /b 1
)

echo ✅ Python 찾음
echo.

REM 가상 환경 생성 (없으면)
if not exist venv (
    echo 📦 가상 환경 생성 중...
    python -m venv venv
    echo ✅ 가상 환경 생성 완료
    echo.
)

REM 가상 환경 활성화
call venv\Scripts\activate.bat

echo 📚 라이브러리 설치 중... (처음 한 번만 시간 걸림)
pip install -q -r requirements.txt

if errorlevel 1 (
    echo ❌ 라이브러리 설치 실패!
    pause
    exit /b 1
)

echo ✅ 라이브러리 설치 완료
echo.
echo ================================================================
echo   🌐 웹 서버 시작 중...
echo ================================================================
echo.
echo 아래 주소를 웹 브라우저에서 열어주세요:
echo.
echo   👉 http://localhost:5000
echo.
echo (Ctrl+C를 누르면 종료됩니다)
echo.
echo ================================================================
echo.

python app.py

pause
