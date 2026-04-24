@echo off
chcp 65001 > nul
cls

echo.
echo ================================================================
echo   🔧 뚝딱공작소 - EXE 자동 빌드
echo ================================================================
echo.
echo 이 스크립트가 자동으로 EXE 파일을 만들어줍니다.
echo.
echo 아래 단계를 따릅니다:
echo   1. Python 확인
echo   2. 라이브러리 설치 (처음만, 5-10분)
echo   3. EXE 생성 (1-3분)
echo.

REM Python 확인
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았습니다!
    echo.
    echo https://www.python.org/downloads/ 에서 설치해주세요.
    echo (설치 시 "Add Python to PATH" 반드시 체크!)
    echo.
    pause
    exit /b 1
)

echo ✅ Python 찾음
echo.

REM 라이브러리 설치
echo 📦 필요한 라이브러리 설치 중...
pip install --quiet Flask Werkzeug Pillow opencv-python numpy pyinstaller

if errorlevel 1 (
    echo ❌ 라이브러리 설치 실패!
    echo.
    echo 관리자 권한으로 다시 실행해주세요.
    echo.
    pause
    exit /b 1
)

echo ✅ 라이브러리 설치 완료
echo.

REM EXE 빌드
echo 🔨 EXE 파일 빌드 중... (1-3분 소요)
echo.

pyinstaller --onefile ^
  --name "뚝딱공작소" ^
  --add-data "templates:templates" ^
  --add-data "uploads:uploads" ^
  --hidden-import=flask ^
  --hidden-import=cv2 ^
  --hidden-import=numpy ^
  --console ^
  app.py

if errorlevel 1 (
    echo.
    echo ❌ EXE 빌드 실패!
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo   ✅ EXE 파일 생성 완료!
echo ================================================================
echo.
echo 📍 파일 위치:
echo.
echo   dist\뚝딱공작소.exe
echo.
echo 🎉 이 파일을 다른 사람에게 배포하면 됩니다!
echo.
echo ================================================================
echo.

pause
