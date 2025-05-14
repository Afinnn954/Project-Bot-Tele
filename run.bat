@echo off
REM Aktifkan virtual environment jika ada
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Jalankan server Flask
python server.py
