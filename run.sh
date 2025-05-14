#!/bin/bash

# Aktifkan virtual environment jika ada
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Jalankan server Flask
python server.py
