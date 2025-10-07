@echo off
echo Starting Telegram Colorization Bot...
echo.

REM Set your bot token here
set BOT_TOKEN="8299632973:AAFkB6kcxRMfZQD0CE4NzZVJzkOuHSLWuW4"
set MODEL_PATH=models\colorization_release_v2.caffemodel
set PROTOTXT_PATH=models\colorization_deploy_v2.prototxt

REM Create models directory if it doesn't exist
if not exist "models" mkdir models

echo Bot Token: %BOT_TOKEN%
echo Model Path: %MODEL_PATH%
echo Prototxt Path: %PROTOTXT_PATH%
echo.

REM Run the bot
python bot.py

pause

