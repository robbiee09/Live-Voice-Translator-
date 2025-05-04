@echo off
echo Creating Voice Translator executable...

:: Make sure data directory exists and include it with the build
if not exist "data" mkdir data
echo Data folder ready

:: Show build options
echo.
echo Please select a build option:
echo.
echo 1. Build with hidden console (production)
echo 2. Build with visible console (easier debugging)
echo 3. Build with one-step process (simpler but less features)
echo.

set /p option="Enter option (1, 2, or 3): "

:: Check for icon file
set "icon_path=icon-resource.ico"
if not exist "%icon_path%" (
    echo Icon file not found. Attempting to generate one from SVG...
    
    :: Try to convert SVG to ICO using Python
    python -c "import cairosvg; cairosvg.svg2png(url='icon-resource.svg', write_to='icon-resource.png', output_width=256, output_height=256)" 2>nul
    
    if exist "icon-resource.png" (
        echo Generated PNG, attempting to convert to ICO...
        :: Try to convert PNG to ICO using PIL
        python -c "from PIL import Image; img = Image.open('icon-resource.png'); img.save('icon-resource.ico')" 2>nul
    )
    
    if not exist "%icon_path%" (
        echo Unable to generate icon. Will build without custom icon.
        set "icon_param="
    ) else (
        echo Icon generated successfully.
        set "icon_param=--icon=%icon_path%"
    )
) else (
    echo Icon file found at %icon_path%
    set "icon_param=--icon=%icon_path%"
)

:: Process based on selection
if "%option%"=="1" (
    echo.
    echo Building production version (hidden console)...
    echo.
    pyinstaller --onefile --noconsole --add-data "data;data" %icon_param% voice_translator.py
) else if "%option%"=="2" (
    echo.
    echo Building debug version (visible console)...
    echo.
    pyinstaller --onefile --add-data "data;data" %icon_param% voice_translator.py
) else if "%option%"=="3" (
    echo.
    echo Building with simple one-step process...
    echo.
    pyinstaller --onefile %icon_param% voice_translator.py
) else (
    echo.
    echo Invalid option. Using default (production build)
    echo.
    pyinstaller --onefile --noconsole --add-data "data;data" %icon_param% voice_translator.py
)

echo.
echo ===================================
echo Build process completed!
echo.
echo If successful, your executable should be in the "dist" folder.
echo.
echo IMPORTANT NOTES:
echo 1. If the app shows "SQLite database error", make sure you run the app as
echo    administrator, or use the "data" folder next to the executable.
echo 2. For debugging purposes, you can use option 2 to see any error messages.
echo ===================================
echo.

:: Copy data folder to dist for direct access
echo Copying data folder to dist for direct access...
if not exist "dist\data" mkdir dist\data

echo.
echo Press any key to exit
pause > nul