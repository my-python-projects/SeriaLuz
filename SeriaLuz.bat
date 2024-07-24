@echo off
setlocal

set "diretorio=%~dp0"

if not exist "%diretorio%venv" (
    python -m venv "%diretorio%venv"
) 

cd /d "%diretorio%"

call venv\Scripts\activate

python -m pip install --upgrade pip

pip install pyserial

pip install matplotlib

python main.py

endlocal
