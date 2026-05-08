"""
Minecraft Guard Bot — Full AI Player
Server : funark.aternos.me:57003
Admin  : RealWangLing

States:
  FOLLOW  — admin online hai, uske saath rehta hai, mobs maarta hai
  IDLE    — admin offline hai, spawn ke paas items collect karta hai,
            mobs maarta hai, chhoti building karta hai
"""

import time
import math
import random
import threading
from javascript import require, On

# ── CONFIG ────────────────────────────────────────────────────────────────────
HOST         = "funark.aternos.me"
PORT         = 57003
BOT_USERNAME = "GuardBot"
ADMIN_NAME   = "RealWangLing"
FOLLOW_DIST  = 2       # admin se kitne blocks duri
MOB_RANGE    = 14      # mobs detect karne ki range (blocks)
IDLE_RANGE   = 30      # spawn se kitne blocks tak ghoomna
LOW_HEALTH   = 8       # is se kam HP ho to food khao
# ─────────────────────────────────────────────────────────────────────────────

HOSTILE_MOBS = {
    "zombie", "skeleton", "creeper", "spider", "cave_spider",
    "enderman", "witch", "pillager", "vindicator", "phantom",
    "drowned", "husk", "stray", "slime", "magma_cube", "blaze",
    "ghast", "wither_skeleton", "zombie_villager", "zombified_piglin",
    "hoglin", "zoglin", "piglin_brute", "silverfish", "ravager",
    "guardian", "elder_guardian", "shulker", "evoker", "vex",
}

# Blocks jo bot collect karta hai (idle mode)
COLLECT_BLOCKS = {
    "oak_log", "birch_log", "spruce_log", "jungle_log",
    "acacia_log", "dark_oak_log", "cherry_log",
    "coal_ore", "iron_ore", "stone", "cobblestone",
    "grass_block", "dirt",
}

print("=" * 55)
print("  Minecraft Guard Bot — Full AI Player")
print(f"  Server  : {HOST}:{PORT}")
print(f"  Bot     : {BOT_USERNAME}")
print(f"  Admin   : {ADMIN_NAME}")
print("=" * 55)

# ── LIBRARIES ─────────────────────────────────────────────────────────────────
mineflayer = require("mineflayer")
pathfinder  = require("mineflayer-pathfinder")
pvp_plugin  = require("mineflayer-pvp").plugin
Movements   = pathfinder.Movements
goals       = pathfinder.goals

# ── STATE ─────────────────────────────────────────────────────────────────────
bot         = None
running     = True
state       = "IDLE"      # "FOLLOW" ya "IDLE"
spawn_pos   = None        # pehli baar spawn hone ki jagah
tick        = 0

# ── BOT BANAO ─────────────────────────────────────────────────────────────────

def create_bot():
    global bot, state
    bot = mineflayer.createBot({
        "host":                 HOST,
        "port":                 PORT,
        "username":             BOT_USERNAME,
        "auth":                 "offline",
        "checkTimeoutInterval": 60000,
    })
    bot.loadPlugin(pathfinder.pathfinder)
    bot.loadPlugin(pvp_plugin)
    register_events()
    print("[~] Connect ho raha hai server se...")

def register_events():
    global spawn_pos, state

    @On(bot, "login")
    def on_login(*a):
        print("[+] Server se connected!")

    @On(bot, "spawn")
    def on_spawn(*a):
        global spawn_pos
        try:
            if spawn_pos is None:
                spawn_pos = {
                    "x": bot.entity.position.x,
                    "y": bot.entity.position.y,
                    "z": bot.entity.position.z,
                }
                print(f"[+] Spawn point save hua: {spawn_pos}")
            print("[+] Bot spawn ho gaya — khel raha hai!")
        except Exception as e:
            print(f"[spawn error] {e}")

    @On(bot, "death")
    def on_death(*a):
        print("[!] Bot mar gaya — respawn ho raha hai...")

    @On(bot, "respawn")
    def on_respawn(*a):
        print("[+] Bot respawn ho gaya!")

    @On(bot, "playerJoined")
    def on_player_join(this, player, *a):
        try:
            name = player.username if player.username else str(player)
            if name == ADMIN_NAME:
                print(f"[★] {ADMIN_NAME} server pe aa gaya! Follow mode ON.")
        except Exception:
            pass

    @On(bot, "playerLeft")
    def on_player_left(this, player, *a):
        try:
            name = player.username if player.username else str(player)
            if name == ADMIN_NAME:
                print(f"[~] {ADMIN_NAME} chala gaya. Idle/collect mode ON.")
        except Exception:
            pass

    @On(bot, "kicked")
    def on_kicked(this, reason, *a):
        print(f"[!] Kick hua: {reason} — 8s baad reconnect...")
        time.sleep(8)
        create_bot()

    @On(bot, "error")
    def on_error(this, err, *a):
        print(f"[!] Error: {err}")

    @On(bot, "end")
    def on_end(this, reason, *a):
        print(f"[!] Disconnect: {reason} — 8s baad reconnect...")
        time.sleep(8)
        create_bot()

# ── HELPER FUNCTIONS ──────────────────────────────────────────────────────────

def get_admin_entity():
    try:
        pl = bot.players.get(ADMIN_NAME)
        if pl and pl.entity:
            return pl.entity
    except Exception:
        pass
    return None

def dist3(a_pos, b_pos):
    return math.sqrt(
        (a_pos.x - b_pos.x) ** 2 +
        (a_pos.y - b_pos.y) ** 2 +
        (a_pos.z - b_pos.z) ** 2
    )

def set_path_goal(goal):
    try:
        mvmt = Movements(bot)
        bot.pathfinder.setMovements(mvmt)
        bot.pathfinder.setGoal(goal, True)
    except Exception as e:
        print(f"  [path error] {e}")

def stop_path():
    try:
        bot.pathfinder.setGoal(None)
    except Exception:
        pass

def stop_pvp():
    try:
        bot.pvp.stop()
    except Exception:
        pass

# ── COMBAT ────────────────────────────────────────────────────────────────────

def find_nearest_mob(center_pos, radius):
    nearest, nearest_d = None, radius
    try:
        for eid in bot.entities:
            ent = bot.entities[eid]
            if not ent or not ent.name:
                continue
            if ent.type != "mob":
                continue
            if ent.name.lower().replace(" ", "_") not in HOSTILE_MOBS:
                continue
            d = dist3(center_pos, ent.position)
            if d < nearest_d:
                nearest, nearest_d = ent, d
    except Exception:
        pass
    return nearest

def attack_mob(mob):
    try:
        bot.pvp.attack(mob)
    except Exception:
        try:
            bot.attack(mob)
        except Exception:
            pass

# ── HEALTH / FOOD ─────────────────────────────────────────────────────────────

def maybe_eat():
    try:
        if bot.food is not None and bot.food < LOW_HEALTH:
            bot.consume()
    except Exception:
        pass

# ── ITEM PICKUP ───────────────────────────────────────────────────────────────

def pick_up_nearby_items():
    """Gire hue items (drops) ki taraf jao"""
    try:
        nearest, nearest_d = None, 10
        for eid in bot.entities:
            ent = bot.entities[eid]
            if not ent:
                continue
            try:
                etype = str(ent.type).lower()
            except Exception:
                continue
            if "item" not in etype and "object" not in etype:
                continue
            try:
                d = dist3(bot.entity.position, ent.position)
            except Exception:
                continue
            if d < nearest_d:
                nearest, nearest_d = ent, d
        if nearest:
            set_path_goal(goals.GoalBlock(
                int(nearest.position.x),
                int(nearest.position.y),
                int(nearest.position.z),
            ))
            return True
    except Exception:
        pass
    return False

# ── BLOCK COLLECTING ─────────────────────────────────────────────────────────

def find_and_mine_block():
    """Nazdiki mine-karne wala block dhundo aur pathfind karo"""
    try:
        block_names = ["oak_log", "birch_log", "spruce_log",
                       "coal_ore", "iron_ore", "stone", "cobblestone"]
        for bname in block_names:
            try:
                btype = bot.registry.blocksByName[bname]
            except Exception:
                continue
            if not btype:
                continue
            try:
                block = bot.findBlock({
                    "matching": int(btype.id),
                    "maxDistance": 20,
                })
            except Exception:
                continue
            if not block:
                continue
            # Pathfind to block
            set_path_goal(goals.GoalBlock(
                int(block.position.x),
                int(block.position.y),
                int(block.position.z),
            ))
            time.sleep(2)
            # Try to dig
            try:
                current = bot.blockAt(block.position)
                if current and current.name == bname:
                    bot.dig(current)
                    print(f"  [mine] '{bname}' khoda!")
            except Exception:
                pass
            return True
    except Exception as e:
        if tick % 20 == 0:
            print(f"  [mine error] {e}")
    return False

# ── SIMPLE BUILDING ──────────────────────────────────────────────────────────

def try_place_block():
    """Inventory mein cobblestone/dirt hai to ek block place karo"""
    try:
        for item_name in ["cobblestone", "dirt", "stone", "oak_planks"]:
            item_type = bot.registry.itemsByName.get(item_name)
            if not item_type:
                continue
            item = bot.inventory.findInventoryItem(item_type.id, None)
            if item:
                ref_pos = bot.entity.position
                # Bot ke paas ek random direction mein block place karo
                offsets = [(1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1)]
                ox, oz = random.choice(offsets)
                place_x = int(ref_pos.x) + ox
                place_y = int(ref_pos.y) - 1
                place_z = int(ref_pos.z) + oz
                ref_block = bot.blockAt({"x": place_x, "y": place_y, "z": place_z})
                if ref_block and ref_block.name == "air":
                    below = bot.blockAt({"x": place_x, "y": place_y - 1, "z": place_z})
                    if below and below.name != "air":
                        bot.equip(item, "hand")
                        bot.placeBlock(below, {"x": 0, "y": 1, "z": 0})
                        print(f"  [build] '{item_name}' place kiya ({place_x},{place_y},{place_z})")
                        return True
    except Exception:
        pass
    return False

# ── IDLE ROAM ────────────────────────────────────────────────────────────────

def idle_roam():
    """Admin offline hai — spawn ke paas randomly ghoomna"""
    if spawn_pos is None:
        return
    try:
        rx = spawn_pos["x"] + random.randint(-IDLE_RANGE, IDLE_RANGE)
        rz = spawn_pos["z"] + random.randint(-IDLE_RANGE, IDLE_RANGE)
        ry = spawn_pos["y"]
        set_path_goal(goals.GoalXZ(int(rx), int(rz)))
    except Exception as e:
        print(f"  [roam error] {e}")

# ── MAIN GAME LOOP ────────────────────────────────────────────────────────────

def game_loop():
    global tick, state

    idle_action_timer = 0    # idle actions ke beech gap
    build_timer       = 0    # building ka timer

    while running:
        time.sleep(1)
        tick += 1

        if bot is None:
            continue

        try:
            # ── Entity check ──────────────────────────────────────
            if not bot.entity:
                continue

            maybe_eat()

            admin = get_admin_entity()
            is_admin_online = admin is not None

            # ── State update ──────────────────────────────────────
            if is_admin_online and state != "FOLLOW":
                state = "FOLLOW"
                stop_pvp()
                print("[★] FOLLOW mode: admin ke paas ja raha hun!")

            elif not is_admin_online and state != "IDLE":
                state = "IDLE"
                stop_pvp()
                stop_path()
                print("[~] IDLE mode: spawn ke paas ghoom raha hun.")

            # ── Combat (dono states mein) ─────────────────────────
            center = admin.position if is_admin_online else bot.entity.position
            mob = find_nearest_mob(center, MOB_RANGE)
            if mob:
                if tick % 4 == 0:
                    print(f"  [⚔] '{mob.name}' ko maar raha hun!")
                attack_mob(mob)
            else:
                stop_pvp()

            # ── FOLLOW mode actions ───────────────────────────────
            if state == "FOLLOW" and is_admin_online:
                d = dist3(bot.entity.position, admin.position)
                if d > FOLLOW_DIST + 1:
                    set_path_goal(goals.GoalFollow(admin, FOLLOW_DIST))
                else:
                    stop_path()

            # ── IDLE mode actions ─────────────────────────────────
            elif state == "IDLE":
                idle_action_timer -= 1
                build_timer       -= 1

                if idle_action_timer <= 0:
                    # Priority: drops > mining > roam
                    picked = pick_up_nearby_items()
                    if not picked:
                        mined = find_and_mine_block()
                        if not mined:
                            idle_roam()
                    idle_action_timer = random.randint(4, 8)

                if build_timer <= 0:
                    try_place_block()
                    build_timer = random.randint(20, 40)

        except Exception as e:
            if tick % 15 == 0:
                print(f"[loop error] {e}")

# ── START ─────────────────────────────────────────────────────────────────────

create_bot()

t = threading.Thread(target=game_loop, daemon=True)
t.start()

print("[*] Bot chal raha hai — hamesha connected rahega!")
try:
    while True:
        time.sleep(5)
except KeyboardInterrupt:
    running = False
    print("[*] Bot band kiya.")
