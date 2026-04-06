@echo off
cd /d %~dp0
call .venv\Scripts\activate
celery -A myproject beat --loglevel=info
pause