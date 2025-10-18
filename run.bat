@echo off
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo Kalshi Trading Algorithm - Virtual Environment Activated
echo =====================================================
echo.
echo Available commands:
echo   python test_system.py          - Test the system
echo   python main.py --mode dashboard - Launch web dashboard
echo   python main.py --mode run      - Start automated trading
echo   python main.py --mode test     - Run single test cycle
echo.
echo To deactivate: deactivate
echo.
cmd /k
