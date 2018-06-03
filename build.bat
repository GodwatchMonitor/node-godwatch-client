pyinstaller --onefile --noconsole --icon ico/base.ico main.py
cd dist
copy main.exe %~dp0clientinstaller\main.exe