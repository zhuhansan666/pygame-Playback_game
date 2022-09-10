@echo off

start .\venv\Scripts\pyinstaller.exe -w update.py -i ./fz/res/icon.ico -y
".\venv\Scripts\pyinstaller.exe" -w main.py -i ./fz/res/icon.ico -y
del /f ./.Releases/pygame-win10+.zip
"./fz/7z.exe" a ./.Releases/pygame-win10+.zip ./res
"./fz/7z.exe" a ./.Releases/pygame-win10+.zip ./dist/main/*
"./fz/7z.exe" a ./.Releases/pygame-win10+.zip ./dist/update/*
rmdir /s /q "dist"
rmdir /s /q "build"
del /f /q "main.spec"
del /f /q "update.spec"
".\venv\Scripts\python.exe" ./fz/server_update_win10.py
".\venv\Scripts\python.exe" ./fz/set_latest_version.py
pause
