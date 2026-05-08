# 24/7 Free Mein Bot Ko Alive Kaise Rakhe

## Option 1 — Oracle Cloud (SABSE ACCHA - Hamesha Free)

Oracle Cloud ka "Always Free" tier deta hai 2 virtual machines HAMESHA FREE mein — koi credit card expire nahi hoga.

### Steps:
1. https://cloud.oracle.com par account banao (free hai)
2. Compute > Instances > Create Instance karo
3. Shape: **VM.Standard.A1.Flex** (Always Free)
4. OS: Ubuntu 22.04
5. SSH key download karo

### VM mein commands:
```bash
# Node.js install karo
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Python 3.10 install karo
sudo apt install python3.10 python3-pip -y

# Bot upload karo (apne computer se)
scp -r minecraft-bot/ ubuntu@<TUMHARI_VM_IP>:~/

# VM mein jao
ssh ubuntu@<TUMHARI_VM_IP>
cd minecraft-bot

# Dependencies install karo
pip3 install -r requirements.txt
npm install mineflayer mineflayer-pathfinder mineflayer-pvp vec3

# Screen mein chalao (band hone ke baad bhi chalta rahega)
sudo apt install screen -y
screen -S mcbot
python3 bot.py

# Screen se bahar aao (bot chalta rahega):  Ctrl+A phir D
# Wapas screen mein jaane ke liye:
screen -r mcbot
```

---

## Option 2 — Replit (Simple - Seedha Yahan Chalao)

1. Replit pe is project ko open karo
2. Shell mein ye commands likho:

```bash
cd minecraft-bot
npm install mineflayer mineflayer-pathfinder mineflayer-pvp vec3
pip install javascript==1.1.1
python bot.py
```

3. Replit hamesha online rakhne ke liye: **UptimeRobot** (free) se ping karo

---

## Option 3 — Railway.app (Free Tier)

1. https://railway.app par account banao
2. New Project > Deploy from GitHub repo
3. `minecraft-bot/` folder deploy karo
4. Environment variables mein kuch set nahi karna

---

## Option 4 — Fly.io (Free)

```bash
# Apne computer mein flyctl install karo
# https://fly.io/docs/hands-on/install-flyctl/

fly auth signup
cd minecraft-bot
fly launch
fly deploy
```

---

## Sabse Recommended:

**Oracle Cloud Always Free** = Best, hamesha free, koi limit nahi
**Replit** = Sabse aasan, seedha yahan karo

