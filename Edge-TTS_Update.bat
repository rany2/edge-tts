@echo off

echo ***************
echo.
echo Checking for an Edge-TTS update...
echo.
echo ***************
echo.
py -m pip install --upgrade edge-tts
if errorlevel 1 (
    echo Update failed.
    pause
    exit /b 1
)
echo.
echo ***************
echo.
echo Current Edge-TTS version:
echo.
py -m edge_tts --version
echo.
echo ***************
echo.
echo Thank you! Make sure to hydrate and get a snack!!
echo.
echo ***************
echo.
echo.
pause
exit /b 0