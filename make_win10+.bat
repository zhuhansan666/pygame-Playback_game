@echo off

start .\venv\Scripts\pyinstaller.exe -w update.py -i icon.ico -y
".\venv\Scripts\pyinstaller.exe" -w main.py -i icon.ico -y
del /f pygame����-������Ϸ.zip
"./��װ֧�ֿ�/7z.exe" a ./pygame����-������Ϸ.zip ./res
"./��װ֧�ֿ�/7z.exe" a ./pygame����-������Ϸ.zip ./dist/main/*
"./��װ֧�ֿ�/7z.exe" a ./pygame����-������Ϸ.zip ./dist/update/*
rmdir /s /q "dist"
rmdir /s /q "build"
del /f /q "main.spec"
del /f /q "update.spec"
".\venv\Scripts\python.exe" ./��װ֧�ֿ�/server_update.py
pause