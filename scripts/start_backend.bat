@echo off
echo Starting Smart Order Routing Backend...

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt

REM Set environment variables
set PYTHONPATH=%CD%\src

REM Start the API server
echo Starting FastAPI server...
python src/api/main.py

pause
