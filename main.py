"""
Alpha Boost Engine - Main (Hybrid Edition)
============================================
Boost tespiti: Mouse tiklama (GetAsyncKeyState)
Hiz verisi: API'den gercek Speed (varsa), yoksa fizik tahmini
"""

import pygame
from pynput import keyboard
import os
import time
import threading
import sys
import json
import ctypes

from audio_engine import AlphaBoostAudioEngine
from api_client import RocketLeagueAPI

# ─── SETTINGS & PERSISTENCE ──────────────────────────────────────────────────
SETTINGS_FILE = "user_settings.json"

default_settings = {
    "volume": 0.4,
    "audio_delay_ms": 0,
    "is_active": True,
    "shortcuts_enabled": True,
    "unlimited_boost": False,
    "profile": "advanced",
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

def save_settings():
    with open(SETTINGS_FILE, "w") as f:
        json.dump(user_settings, f, indent=4)

SES_SEVIYESI = user_settings["volume"]
AUDIO_DELAY_MS = user_settings.get("audio_delay_ms", 0)
IS_ACTIVE = user_settings["is_active"]
SHORTCUTS_ENABLED = user_settings.get("shortcuts_enabled", True)
UNLIMITED_BOOST = user_settings.get("unlimited_boost", False)

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
mouse_down_time = 0.0
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
    
    Boost tespiti: HERZAMAN mouse tiklama ile (API'de bBoosting yok)
    Hiz verisi: API baglantisindan Speed (yoksa fizik tahmini)
    """
    global is_sound_playing, is_mouse_down, mouse_down_time, estimated_speed
    
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
        if current_mouse and not is_mouse_down:
            mouse_down_time = current_time
        is_mouse_down = current_mouse
        
        # Cursor gorunurse (menu acik) boost basmayi yoksay
        is_boosting = is_mouse_down and not is_cursor_visible()
        
        # ─── HIZ VERISI ──────────────────────────────────────────────────
        if api.connected:
            # API'den gercek hiz
            speed = api.speed
        else:
            # API yoksa fizik tahmini
            if is_boosting:
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
            # API bagliysa boost miktarini kontrol et
            if api.connected and not UNLIMITED_BOOST:
                # Boost 0 ise ses calma (boost yok!)
                if api.boost_amount > 0:
                    should_play = True
            else:
                # API yoksa veya sinirsiz boost aciksa her zaman cal
                should_play = True
        
        # ─── SES YONETIMI ────────────────────────────────────────────────
        delay_elapsed = (current_time - mouse_down_time) >= (AUDIO_DELAY_MS / 1000.0)
        
        if should_play and not is_sound_playing and delay_elapsed:
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

def toggle_unlimited_boost():
    global UNLIMITED_BOOST
    UNLIMITED_BOOST = not UNLIMITED_BOOST
    user_settings["unlimited_boost"] = UNLIMITED_BOOST
    save_settings()
    if app:
        app.update_unlimited_boost_state(UNLIMITED_BOOST)

def set_volume(val):
    global SES_SEVIYESI
    SES_SEVIYESI = float(val)
    user_settings["volume"] = SES_SEVIYESI
    save_settings()
    audio.set_volume(SES_SEVIYESI)

def set_delay(val):
    global AUDIO_DELAY_MS
    AUDIO_DELAY_MS = int(val)
    user_settings["audio_delay_ms"] = AUDIO_DELAY_MS
    save_settings()

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
        elif key == keyboard.Key.f4:
            toggle_unlimited_boost()
    except AttributeError:
        pass

# ─── START ────────────────────────────────────────────────────────────────────

threading.Thread(target=engine_loop, daemon=True).start()

print("\n" + "=" * 50)
print("  ALPHA BOOST ENGINE (v2.0 - HYBRID) AKTIF")
print(f"  Ses Seviyesi: %{int(SES_SEVIYESI * 100)}")
print(f"  Boost Tespiti: Mouse Tiklama")
print(f"  Hiz Verisi: {'API (Gercek)' if api.connected else 'Fizik Tahmini'}")
print(f"  Sinirsiz Boost: {'ACIK' if UNLIMITED_BOOST else 'KAPALI'}")
print("=" * 50, flush=True)

keyboard_listener = keyboard.Listener(on_press=on_press)
keyboard_listener.start()

# ─── LAUNCH GUI ──────────────────────────────────────────────────────────────

from interface import AlphaBoostApp

engine_callbacks = {
    "toggle_active": toggle_active,
    "toggle_shortcuts": toggle_shortcuts,
    "toggle_unlimited_boost": toggle_unlimited_boost,
    "get_active": lambda: IS_ACTIVE,
    "get_shortcuts": lambda: SHORTCUTS_ENABLED,
    "get_unlimited_boost": lambda: UNLIMITED_BOOST,
    "get_volume": lambda: SES_SEVIYESI,
    "set_volume": set_volume,
    "get_delay": lambda: AUDIO_DELAY_MS,
    "set_delay": set_delay,
    "get_api_status": lambda: api.connected,
    "get_profile": lambda: PROFILE,
    "set_profile": set_profile,
}

app = AlphaBoostApp(engine_callbacks)
app.mainloop()
