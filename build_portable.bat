@echo off
echo ===================================
echo Voice Translator - Portable Build Script
echo ===================================
echo This script will build a portable version of the Voice Translator application
echo that can run without installation from a USB drive or any folder.
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in your PATH
    echo Please install Python 3.8 or newer and try again.
    pause
    exit /b 1
)

:: Check if required libraries are installed
echo Checking required libraries...
python -c "import speech_recognition, googletrans, pyaudio, langdetect" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required libraries...
    pip install SpeechRecognition googletrans==4.0.0-rc1 pyaudio langdetect
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install required libraries.
        echo Please run: pip install SpeechRecognition googletrans==4.0.0-rc1 pyaudio langdetect
        pause
        exit /b 1
    )
)

:: Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install PyInstaller.
        echo Please run: pip install pyinstaller
        pause
        exit /b 1
    )
)

:: Create data folder and sample database
if not exist "data" mkdir data
echo Data folder created/verified

:: Create a sample database file for better compatibility
echo Creating sample database file...
python -c "import sqlite3; conn = sqlite3.connect('data/translation_history.db'); cursor = conn.cursor(); cursor.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, source_text TEXT, source_lang TEXT, translated_text TEXT, target_lang TEXT)'); conn.commit(); conn.close(); print('Sample database created successfully.')"

:: Generate icon if needed
if not exist "icon-resource.ico" (
    if exist "icon-resource.svg" (
        echo Attempting to convert SVG icon to ICO...
        python -c "from cairosvg import svg2png; from PIL import Image; svg2png(url='icon-resource.svg', write_to='icon-resource.png', output_width=256, output_height=256); img = Image.open('icon-resource.png'); img.save('icon-resource.ico')" >nul 2>&1
        if exist "icon-resource.ico" (
            echo Icon successfully converted
        ) else (
            echo Could not convert icon, continuing without custom icon
        )
    )
)

:: Build options
echo.
echo Build options:
echo 1. Build portable app (recommended)
echo 2. Build portable app with console for debugging
echo 3. Build both versions
echo.
set /p build_option="Select build option (1-3): "

echo.
echo Building...

if "%build_option%"=="1" (
    pyinstaller --clean --noconfirm --onefile --windowed --add-data "data;data" --icon=icon-resource.ico voice_translator.py
) else if "%build_option%"=="2" (
    pyinstaller --clean --noconfirm --onefile --add-data "data;data" --icon=icon-resource.ico voice_translator.py
) else if "%build_option%"=="3" (
    echo Building windowed version...
    pyinstaller --clean --noconfirm --onefile --windowed --add-data "data;data" --icon=icon-resource.ico voice_translator.py -n VoiceTranslator
    echo Building console version...
    pyinstaller --clean --noconfirm --onefile --add-data "data;data" --icon=icon-resource.ico voice_translator.py -n VoiceTranslator_Debug
) else (
    echo Invalid option. Building default portable version...
    pyinstaller --clean --noconfirm --onefile --windowed --add-data "data;data" --icon=icon-resource.ico voice_translator.py
)

:: Copy data folder to dist directory for direct access
echo.
echo Copying data folder to dist directory...
if not exist "dist\data" mkdir dist\data
copy /Y data\*.* dist\data\

:: Create starter script in dist folder for better usability
echo @echo off > dist\Start_VoiceTranslator.bat
echo echo Starting Voice Translator... >> dist\Start_VoiceTranslator.bat
echo echo. >> dist\Start_VoiceTranslator.bat
echo echo If you encounter any issues: >> dist\Start_VoiceTranslator.bat
echo echo 1. Make sure the "data" folder exists in this directory >> dist\Start_VoiceTranslator.bat
echo echo 2. Try running as administrator if database errors occur >> dist\Start_VoiceTranslator.bat
echo echo. >> dist\Start_VoiceTranslator.bat
echo cd /d %%~dp0 >> dist\Start_VoiceTranslator.bat
echo start VoiceTranslator.exe >> dist\Start_VoiceTranslator.bat

echo.
echo ===================================
echo Build completed successfully!
echo.
echo Your portable Voice Translator app is in the "dist" folder.
echo.
echo How to use:
echo 1. Copy the entire "dist" folder to any location (USB drive, etc.)
echo 2. Run "VoiceTranslator.exe" or "Start_VoiceTranslator.bat"
echo 3. Make sure the "data" folder exists in the same directory
echo ===================================
echo.

pause