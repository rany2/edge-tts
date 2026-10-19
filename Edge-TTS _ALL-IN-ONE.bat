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

echo Question [1 of 7]
echo ------------------------------
echo What voice will you use?
echo.
set /p "VOI=Your answer: "

echo.
echo.

echo Question [2 of 7]
echo ------------------------------
echo How fast do you want the voice to speak? (Example: +0%% for normal rate)
echo.
set /p "RAT=Your answer: "

echo.
echo.

echo Question [3 of 7]
echo ------------------------------
echo What should the volume be? (Example: +0%% for normal volume)
echo.
set /p "VOL=Your answer: "

echo.
echo.

echo Question [4 of 7]
echo ------------------------------
echo What Hz will the pitch of the voice be? (Example: +0Hz for no change.)
echo.
set /p "PIT=Your answer: "

echo.
echo.

echo Question [5 of 7]
echo ------------------------------
echo Paste the full path to your text file:
echo.
set /p "FILOC=Your answer: "
set "FILOC=%FILOC:"=%"

echo.
echo.

echo Question [6 of 7]
echo ------------------------------
echo Paste the folder where you want the MP3 saved:
echo.
set /p "EXPLCN=Your answer: "
set "EXPLCN=%EXPLCN:"=%"

echo.
echo.

echo Question [7 of 7]
echo ------------------------------
echo What should the MP3 file be called?
echo.
set /p "TIT=Your answer: "

echo.
echo.

echo Converting text file to audio...
echo.
echo.

py -m edge_tts --voice "%VOI%" --rate "%RAT%" --volume "%VOL%" --pitch "%PIT%" --file "%FILOC%" --write-media "%EXPLCN%\%TIT%.mp3"

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