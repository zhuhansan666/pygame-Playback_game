@echo off

start pyinstaller.exe -w update.py -i ./fz/res/icon.ico -y
pyinstaller.exe -w main.py -i ./fz/res/icon.ico -y
del /f ./.Releases/pygame-win7.zip
"./fz/7z.exe" a ./.Releases/pygame-win7.zip ./res
"./fz/7z.exe" a ./.Releases/pygame-win7.zip ./dist/main/*
"./fz/7z.exe" a ./.Releases/pygame-win7.zip ./dist/update/*
rmdir /s /q "dist"
rmdir /s /q "build"
del /f /q "main.spec"
del /f /q "update.spec"
python.exe ./fz/server_update_win7.py
pause
