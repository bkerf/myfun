@echo off
setlocal
python "%USERPROFILE%\.codex\scripts\codex_shared_cli.py" codex.cmd --yolo -c "model_reasoning_effort=\"high\"" %*
exit /b %errorlevel%
