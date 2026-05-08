"""
Alpha Boost Engine - Main (Hybrid Edition)
============================================
Boost tespiti: Mouse tiklama + API dogrulamasi
Hiz verisi: API'den gercek Speed (varsa), yoksa fizik tahmini
"""

from pynput import keyboard
import os
import time
import threading
import json
import ctypes

from audio_engine import AlphaBoostAudioEngine
from api_client import RocketLeagueAPI

# ─── SETTINGS & PERSISTENCE ──────────────────────────────────────────────────
SETTINGS_FILE = "user_settings.json"

default_settings = {
    "volume": 0.45,
    "is_active": True,
    "shortcuts_enabled": True,
    "profile": "quality",
}

if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "r") as f:
        try:
            user_settings = json.load(f)
            for k, v in default_settings.items():
                if k not in user_settings:
                    user_settings[k] = v
        except Exception:
            user_settings = default_settings.copy()
else:
    user_settings = default_settings.copy()

legacy_settings_removed = False
for legacy_key in ("audio_delay_ms", "unlimited_boost"):
    if user_settings.pop(legacy_key, None) is not None:
        legacy_settings_removed = True

def save_settings():
    with open(SETTINGS_FILE, "w") as f:
        json.dump(user_settings, f, indent=4)

if legacy_settings_removed:
    save_settings()

SES_SEVIYESI = user_settings["volume"]
IS_ACTIVE = user_settings["is_active"]
SHORTCUTS_ENABLED = user_settings.get("shortcuts_enabled", True)

# ─── AUDIO ENGINE INIT ───────────────────────────────────────────────────────
PROFILE = user_settings.get("profile", "advanced")
audio = AlphaBoostAudioEngine()
audio.set_volume(SES_SEVIYESI)
audio.set_profile(PROFILE)

# ─── API CLIENT INIT ─────────────────────────────────────────────────────────
api = RocketLeagueAPI()
api.start()

# ─── STATE VARIABLES ─────────────────────────────────────────────────────────
is_sound_playing = False
is_mouse_down = False
estimated_speed = 0.0

# Fizik sabitleri (API baglantisi yokken kullanilir)
ACCELERATION = 911.0
DECELERATION = 800.0
MAX_SPEED = 2300.0

# ─── HELPER FUNCTIONS ────────────────────────────────────────────────────────

def is_rl_active():
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
        title = buf.value
        return "Rocket League" in title or "RocketLeague" in title
    except Exception:
        return False

def is_cursor_visible():
    try:
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        class CURSORINFO(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.c_uint), ("flags", ctypes.c_uint),
                        ("hCursor", ctypes.c_void_p), ("ptScreenPos", POINT)]
        info = CURSORINFO()
        info.cbSize = ctypes.sizeof(CURSORINFO)
        ctypes.windll.user32.GetCursorInfo(ctypes.byref(info))
        return info.flags == 1
    except Exception:
        return False

# ─── MAIN ENGINE LOOP ────────────────────────────────────────────────────────

def engine_loop():
    """Hibrit motor dongusu.
    
    Boost tespiti: Mouse tiklamasi ile oyuncu girdisi okunur.
    API bagliysa ses ancak gercek boost harcamasi dogrulaninca calar.
    Hiz verisi: API baglantisindan Speed (yoksa fizik tahmini)
    """
    global is_sound_playing, is_mouse_down, estimated_speed
    
    last_update_time = time.time()
    last_rl_check_time = 0.0
    cached_rl_active = False
    
    while True:
        current_time = time.time()
        dt = current_time - last_update_time
        last_update_time = current_time
        
        # RL aktif mi? (saniyede 2 kez kontrol)
        if current_time - last_rl_check_time > 0.5:
            # API bagliysa RL kesinlikle aktif
            if api.connected:
                cached_rl_active = True
            else:
                cached_rl_active = is_rl_active()
            last_rl_check_time = current_time
        
        # ─── BOOST TESPITI (Mouse) ────────────────────────────────────────
        current_mouse = (ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000) != 0
        is_mouse_down = current_mouse
        
        # Cursor gorunurse (menu acik) boost basmayi yoksay
        input_boosting = is_mouse_down and not is_cursor_visible()

        if api.connected:
            # Mouse tek basina yeterli degil; API de boost'un gercekten harcandigini
            # dogrulamali. Bu sayede kickoff gibi anlarda sahte ses tetiklenmez.
            is_boosting = input_boosting and api.is_boosting
        else:
            is_boosting = input_boosting

        # ─── HIZ VERISI ──────────────────────────────────────────────────
        if api.connected:
            # API'den gercek hiz
            speed = api.speed
        else:
            # API yoksa fizik tahmini
            if input_boosting:
                estimated_speed += ACCELERATION * dt
                if estimated_speed > MAX_SPEED:
                    estimated_speed = MAX_SPEED
            else:
                estimated_speed -= DECELERATION * dt
                if estimated_speed < 0:
                    estimated_speed = 0
            speed = estimated_speed
        
        # ─── DURUM KARARI ─────────────────────────────────────────────────
        should_play = False
        
        if IS_ACTIVE and cached_rl_active and is_boosting:
            if api.connected:
                # Boost 0 ise ses calma (boost yok!)
                if api.boost_amount > 0:
                    should_play = True
            else:
                # API yoksa her zaman cal
                should_play = True
        
        # ─── SES YONETIMI ────────────────────────────────────────────────
        if should_play and not is_sound_playing:
            audio.trigger_start()
            audio.play_loop(speed)
            is_sound_playing = True
            
        elif not should_play and is_sound_playing:
            audio.stop_loop()
            audio.trigger_end()
            is_sound_playing = False
            estimated_speed = 0.0
        
        # Ses caliyorsa hizi guncelle (level gecisleri)
        if is_sound_playing:
            audio.update_speed(speed)
        
        time.sleep(0.008)  # ~120 FPS


# ─── GUI CALLBACK FUNCTIONS ──────────────────────────────────────────────────

app = None

def toggle_active():
    global IS_ACTIVE
    IS_ACTIVE = not IS_ACTIVE
    user_settings["is_active"] = IS_ACTIVE
    save_settings()
    if app:
        app.update_active_state(IS_ACTIVE)

def toggle_shortcuts():
    global SHORTCUTS_ENABLED
    SHORTCUTS_ENABLED = not SHORTCUTS_ENABLED
    user_settings["shortcuts_enabled"] = SHORTCUTS_ENABLED
    save_settings()
    if app:
        app.update_shortcuts_state(SHORTCUTS_ENABLED)

def set_volume(val):
    global SES_SEVIYESI
    SES_SEVIYESI = float(val)
    user_settings["volume"] = SES_SEVIYESI
    save_settings()
    audio.set_volume(SES_SEVIYESI)

def set_profile(profile_name):
    global PROFILE
    PROFILE = profile_name
    user_settings["profile"] = PROFILE
    save_settings()
    audio.set_profile(PROFILE)

def on_press(key):
    if not SHORTCUTS_ENABLED:
        return
    try:
        if key == keyboard.Key.f5:
            toggle_active()
    except AttributeError:
        pass

# ─── START ────────────────────────────────────────────────────────────────────

threading.Thread(target=engine_loop, daemon=True).start()

print("\n" + "=" * 50)
print("  ALPHA BOOST ENGINE (v2.0 - HYBRID) AKTIF")
print(f"  Ses Seviyesi: %{int(SES_SEVIYESI * 100)}")
print(f"  Boost Tespiti: Mouse + API Dogrulamasi")
print(f"  Hiz Verisi: {'API (Gercek)' if api.connected else 'Fizik Tahmini'}")
print("=" * 50, flush=True)

keyboard_listener = keyboard.Listener(on_press=on_press)
keyboard_listener.start()

# ─── LAUNCH GUI ──────────────────────────────────────────────────────────────

from interface import AlphaBoostApp

engine_callbacks = {
    "toggle_active": toggle_active,
    "toggle_shortcuts": toggle_shortcuts,
    "get_active": lambda: IS_ACTIVE,
    "get_shortcuts": lambda: SHORTCUTS_ENABLED,
    "get_volume": lambda: SES_SEVIYESI,
    "set_volume": set_volume,
    "get_api_status": lambda: api.connected,
    "get_profile": lambda: PROFILE,
    "set_profile": set_profile,
}

app = AlphaBoostApp(engine_callbacks)
app.mainloop()
