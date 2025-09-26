@echo off
echo 🚀 Setting up DHGate Scraper on Windows...

REM Check if Python 3 is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3 is not installed. Please install Python 3 first:
    echo    Download from https://www.python.org/downloads/
    echo    Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python 3 found:
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created.
) else (
    echo ℹ️  Virtual environment already exists.
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install setuptools first (fixes Python 3.13 compatibility)
echo 🔧 Installing setuptools for Python 3.13 compatibility...
python -m pip install --upgrade setuptools

REM Install dependencies
echo 📚 Installing dependencies...
python -m pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo 📝 Creating .env template file...
    copy config\env.template .env
    echo ✅ .env file created. Please edit it with your credentials.
) else (
    echo ℹ️  .env file already exists.
)

REM Create downloads directory
if not exist "downloads" (
    echo 📁 Creating downloads directory...
    mkdir downloads
    echo ✅ downloads directory created.
) else (
    echo ℹ️  downloads directory already exists.
)

echo.
echo ✅ Setup complete!
echo.
echo To activate the virtual environment in the future, run:
echo   venv\Scripts\activate.bat
echo.
echo To run the scraper:
echo   python main.py
echo.
echo Don't forget to edit the .env file with your DHGate credentials!
echo.
echo 📋 Next steps:
echo 1. Edit .env file with your DHGate username and password
echo 2. Run: venv\Scripts\activate.bat
echo 3. Run: python main.py
echo.
pause

