@echo off
cd /d "%~dp0"

echo Virtual Environment Activation...
call Venv/Scripts/activate.bat

echo Launching the app...
python main.py
