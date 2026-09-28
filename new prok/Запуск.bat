@echo off
chcp 65001 >nul
cd /d "%~dp0studio_app"
echo Запуск приложения Студия (PyQt)...
python main.py
if errorlevel 1 (
    echo.
    echo Ошибка. Установите зависимости:
    echo   pip install --user -r requirements.txt
    pause
)
