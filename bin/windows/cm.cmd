@echo off
setlocal
python "%USERPROFILE%\.codex\scripts\codex_shared_cli.py" codex.cmd --yolo -c "model=\"gpt-6.2-sol\"" -c "model_reasoning_effort=\"max\"" %*
exit /b %errorlevel%
