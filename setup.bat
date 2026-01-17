@echo off
echo ========================================
echo Trading Tester - Setup Script
echo ========================================
echo.

echo Step 1: Creating virtual environment...
python3.14.exe -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    echo Make sure Python 3.14 is installed
    pause
    exit /b 1
)
echo Virtual environment created successfully
echo.

echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo Step 3: Upgrading pip...
python -m pip install --upgrade pip
echo.

echo Step 4: Installing dependencies...
pip install -e .
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully
echo.

echo Step 5: Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo .env file created
    echo.
    echo ========================================
    echo IMPORTANT: Edit .env and add your API key!
    echo ========================================
    echo.
    echo Open .env and set:
    echo ANTHROPIC_API_KEY=your_actual_api_key_here
    echo.
) else (
    echo .env file already exists
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To activate the environment later, run:
echo   venv\Scripts\activate
echo.
echo To test the installation, run:
echo   tradingtester --help
echo.
echo To run a demo, use:
echo   python demo.py 1
echo.
pause
