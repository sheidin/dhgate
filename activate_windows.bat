@echo off
if exist "venv" (
    echo 🔧 Activating virtual environment...
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment activated!
    echo.
    echo To run the scraper:
    echo   python main.py
    echo.
    echo To deactivate:
    echo   deactivate
) else (
    echo ❌ Virtual environment not found. Please run setup_windows.bat first.
    pause
)
