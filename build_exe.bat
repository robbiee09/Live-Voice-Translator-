@echo off
echo Creating Voice Translator executable...

:: Create data folder and sample database
if not exist "data" mkdir data
echo Data folder created/verified

:: Create a sample database file for better compatibility
echo Creating sample database file...
python -c "import sqlite3; conn = sqlite3.connect('data/translation_history.db'); cursor = conn.cursor(); cursor.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, source_text TEXT, source_lang TEXT, translated_text TEXT, target_lang TEXT)'); conn.commit(); conn.close(); print('Sample database created successfully.')"

:: Run PyInstaller with data included
echo Building executable with database included...
pyinstaller --clean --onefile --noconsole --add-data "data;data" voice_translator.py

:: Copy data folder to dist directory for direct access
echo Copying data folder to dist directory...
if not exist "dist\data" mkdir dist\data
copy /Y data\*.* dist\data\

echo Build completed! Check the "dist" folder for your executable.
echo.
echo IMPORTANT: When running the executable, either:
echo 1. Create a "data" folder in the same directory as the executable 
echo 2. Run the application as administrator
echo 3. The app will automatically use your Documents folder if both options fail
echo.
pause