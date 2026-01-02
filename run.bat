@echo off
REM Supply Chain Guardian - Quick Run Script for Windows

echo ================================================
echo   Supply Chain Guardian - Quick Start
echo ================================================
echo.

REM Check if virtualenv exists
if not exist "virtualenv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv virtualenv
    echo.
)

REM Activate virtualenv
echo Activating virtual environment...
call virtualenv\Scripts\activate.bat
echo.

REM Check if requirements are installed
python -c "import vertexai" 2>nul
if errorlevel 1 (
    echo Installing requirements...
    pip install -r requirements.txt
    echo.
)

REM Check if database exists
if not exist "supply_chain.db" (
    echo Initializing database...
    python setup_database.py
    echo.
)

REM Check if .env exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please create .env file from .env.example
    echo.
    pause
)

REM Show menu
:menu
echo ================================================
echo   What would you like to do?
echo ================================================
echo.
echo   1. Test agents locally (python main.py)
echo   2. Launch Streamlit dashboard
echo   3. Run alert check
echo   4. Initialize/reset database
echo   5. Deploy to Google Cloud
echo   6. Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" (
    echo.
    echo Running agent tests...
    python main.py
    echo.
    pause
    goto menu
)

if "%choice%"=="2" (
    echo.
    echo Launching Streamlit dashboard...
    echo Access the UI at: http://localhost:8501
    echo Press Ctrl+C to stop
    echo.
    streamlit run ui/app.py
    goto end
)

if "%choice%"=="3" (
    echo.
    echo Running alert check...
    python alerting.py
    echo.
    pause
    goto menu
)

if "%choice%"=="4" (
    echo.
    echo Initializing database...
    python setup_database.py
    echo.
    pause
    goto menu
)

if "%choice%"=="5" (
    echo.
    echo Deploying to Google Cloud...
    echo Make sure GOOGLE_CLOUD_PROJECT and STAGING_BUCKET are set in .env
    echo.
    python deploy.py
    echo.
    pause
    goto menu
)

if "%choice%"=="6" goto end

echo Invalid choice. Please try again.
goto menu

:end
echo.
echo Thank you for using Supply Chain Guardian!
echo.
