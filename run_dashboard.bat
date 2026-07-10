@echo off
cd /d "%~dp0"
venv\Scripts\python.exe -m streamlit run dashboard/dashboard.py --server.port 8501
pause
