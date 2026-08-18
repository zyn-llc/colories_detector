@echo off
REM Launches the Central Asian Food AI web app.
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found. Run these once before using this script:
    echo   python -m venv .venv
    echo   .venv\Scripts\pip install -r requirements-dev.txt
    pause
    exit /b 1
)

.venv\Scripts\python.exe -m streamlit run app/streamlit_app.py
pause
