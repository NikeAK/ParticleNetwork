@echo off
cd /d "%~dp0"

echo Creating a virtual environment...
python -m venv Venv

echo Virtual Environment Activation...
call Venv/Scripts/activate.bat

echo Requirements Setup...
pip install -r requirements.txt

echo Delete "README.MD"
del "README.MD"

echo Delete "requirements.txt"
del "requirements.txt"

echo Delete "Setup.bat"
del "Setup.bat"
