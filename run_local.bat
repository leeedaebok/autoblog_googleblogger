@echo off
chcp 65001 > nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d D:\claude_workspace\autoblog\autoblog_googleblogger
python run_local.py
