@echo off

start .\venv\Scripts\pyinstaller.exe -w update.py -i icon.ico -y
".\venv\Scripts\pyinstaller.exe" -w main.py -i icon.ico -y
del /f pygame练手-弹球游戏.zip
"./封装支持库/7z.exe" a ./pygame练手-弹球游戏.zip ./res
"./封装支持库/7z.exe" a ./pygame练手-弹球游戏.zip ./dist/main/*
"./封装支持库/7z.exe" a ./pygame练手-弹球游戏.zip ./dist/update/*
rmdir /s /q "dist"
rmdir /s /q "build"
del /f /q "main.spec"
del /f /q "update.spec"
".\venv\Scripts\python.exe" ./封装支持库/server_update.py
pause
