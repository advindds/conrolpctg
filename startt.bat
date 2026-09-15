@echo off
REM Проверка, установлен ли Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python не установлен.
    goto check_arch
)

REM Проверка версии Python
for /f "tokens=2 delims= " %%i in ('python --version') do set PYTHON_VERSION=%%i

REM Если версия Python не совпадает с 3.12.6
if "%PYTHON_VERSION%" NEQ "3.12.6" (
    echo Установленная версия Python: %PYTHON_VERSION%
    goto check_arch
) else (
    echo Python 3.12.6 установлен. Ничего не делаем.
    goto execute
)

:check_arch
REM Проверка разрядности системы
if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    REM 64-битная система
    start "" "python\python-3.12.6_(64-bit).exe"
) else (
    REM 32-битная система
    start "" "python\python-3.12.6_(32-bit).exe"
)

echo Установите Python и перезапустите скрипт.
pause
exit

:execute
REM Общий код для активации виртуальной среды и установки библиотек
call .venv\Scripts\activate
pip install -r requirements.txt
python main.py

REM Удаляем временные файлы
del /Q "config.py"
del /Q "bot_script.spec"
rmdir /S /Q "build"

pause
