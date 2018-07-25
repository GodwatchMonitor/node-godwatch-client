pyinstaller -F --hidden-import=win32timezone --icon=base.ico main.py
cd dist
copy main.exe %~dp0clientinstaller\main.exe
cd ..
