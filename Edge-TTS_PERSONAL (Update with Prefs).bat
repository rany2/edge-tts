@echo off

Rem For this version you can frankenstein parts from the All In One version based on your needs. This is intended for those who know what they're doing and just want a faster script with less questions. It's currently set up as my defaults.

echo ***************
echo.
:Start
echo --------------------------------
echo.
echo The script has just been started or reset.
echo.
echo --------------------------------
echo.
echo Before we get converting, here is the list of voices for your convenience. 
echo.
echo Type "yes" to see the list. Type "no" to skip.
echo.
set /p "CHOICE=Your answer: "
if /i "%CHOICE%"=="yes" py -m edge_tts --list-voices
if /i "%CHOICE%"=="no" goto :SkipSection

:SkipSection
echo.
echo ***************
echo.
echo.
echo Your input is required for each question even if it is the default option. Remember that negative values are possible.

echo.
echo.

echo Question [1 of 2]
echo ------------------------------
echo Paste the full path to your text file:
echo.
set /p "FILOC=Your answer: "
set "FILOC=%FILOC:"=%"

echo.
echo.

echo Question [2 of 2]
echo ------------------------------
echo What should the MP3 file be called?
echo.
set /p "TIT=Your answer: "

echo.
echo.

echo Converting text file to audio...
echo.
echo.

py -m edge_tts --voice en-US-ChristopherNeural --pitch -5Hz --file "%FILOC%" --write-media "C:\Users\Cait\Desktop\Edge-TTS\Output\%TIT%.mp3"

echo.
echo.
echo Done!
echo.
echo --------------------------------
echo.
echo.
echo Are you finished converting files? Type "no" to continue, "yes" to exit.
echo.
set /p "CHOICE=Your answer: "
if /i "%CHOICE%"=="no" (
    cls
    goto :Start
)
if /i "%CHOICE%"=="yes" (
    echo ***************
    echo.
    echo Thank you! Make sure to hydrate and get a snack!!
    echo.
    echo ***************
    echo.
    echo.
    pause
    exit /b 0
)