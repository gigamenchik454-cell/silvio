@echo off
REM Сборка exe-файла приложения Студия
cd /d "%~dp0"

echo Установка зависимостей...
pip install --user -r requirements.txt

echo Копирование ресурсов...
if not exist assets mkdir assets
copy /Y "..\leadsport-logo.png" assets\ 2>nul
copy /Y "..\tracksport-logo.png" assets\ 2>nul
copy /Y "..\intro.jpg" assets\ 2>nul

echo Сборка exe...
pyinstaller --noconfirm --onefile --windowed --name "Студия" ^
  --add-data "assets;assets" ^
  main.py

echo.
echo Готово! Файл: dist\Студия.exe
pause
