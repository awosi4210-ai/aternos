#!/bin/bash
echo "============================================"
echo "  Minecraft Guard Bot - Setup aur Chalao"
echo "============================================"
echo ""

# Python check
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 nahi mila!"
    exit 1
fi

# Node.js check
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js nahi mila! Install karo:"
    echo "        https://nodejs.org/en/download"
    exit 1
fi

echo "[1/4] Python packages install ho rahe hain..."
pip3 install -r requirements.txt

echo ""
echo "[2/4] Node.js packages install ho rahe hain..."
npm install mineflayer mineflayer-pathfinder mineflayer-pvp vec3

echo ""
echo "[3/4] Sab kuch ready! Bot start ho raha hai..."
echo ""
echo " Server : funark.aternos.me:57003"
echo " Admin  : RealWangLing"
echo " Bot    : GuardBot (offline mode)"
echo ""
echo " Bot band karne ke liye: Ctrl+C"
echo ""

python3 bot.py
