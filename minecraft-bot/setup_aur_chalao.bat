@echo off
echo ============================================
echo   Minecraft Guard Bot - Setup aur Chalao
echo ============================================
echo.

REM Python version check
python --version 2>nul
if errorlevel 1 (
    echo [ERROR] Python nahi mila! Python 3.10.0 install karo:
    echo         https://www.python.org/downloads/release/python-3100/
    pause
    exit /b 1
)

REM Node.js check (mineflayer ke liye zaroori hai)
node --version 2>nul
if errorlevel 1 (
    echo [ERROR] Node.js nahi mila! Node.js install karo:
    echo         https://nodejs.org/en/download  (LTS version lo)
    pause
    exit /b 1
)

echo [1/4] Python packages install ho rahe hain...
pip install -r requirements.txt

echo.
echo [2/4] Node.js packages install ho rahe hain...
call npm install mineflayer mineflayer-pathfinder mineflayer-pvp vec3

echo.
echo [3/4] Sab kuch ready hai! Bot start ho raha hai...
echo.
echo  Server : funark.aternos.me:57003
echo  Admin  : RealWangLing
echo  Bot    : GuardBot (offline mode - koi password nahi)
echo.
echo  Bot band karne ke liye: Ctrl+C dabao
echo.

python bot.py

pause
