"""
Alpha Boost Engine - Main (API + Manual Hybrid Edition)
========================================================
Iki calisma modu destekler:
  1. API Mode: Rocket League WebSocket API'sinden gercek veri okur.
  2. Manual Mode: Mouse tiklama + fizik tahmini ile calisir (API yoksa fallback).

Eski OCR/ekran tarama sistemi kaldirilmistir.
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
    "manual_mode": True,
    "unlimited_boost": False,
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
MANUAL_MODE = user_settings.get("manual_mode", True)
UNLIMITED_BOOST = user_settings.get("unlimited_boost", False)

# ─── AUDIO ENGINE INIT ───────────────────────────────────────────────────────
audio = AlphaBoostAudioEngine()
audio.set_volume(SES_SEVIYESI)

# ─── API CLIENT INIT ─────────────────────────────────────────────────────────
api = RocketLeagueAPI()
api.start()

# ─── STATE VARIABLES ─────────────────────────────────────────────────────────
is_sound_playing = False
is_mouse_down = False
mouse_down_time = 0.0
estimated_speed = 0.0

# Manuel mod fizik sabitleri
ACCELERATION = 911.0   # uu/s^2
DECELERATION = 800.0   # uu/s^2
MAX_SPEED = 2300.0      # uu/s

# ─── RL ACTIVE CHECK ─────────────────────────────────────────────────────────

def is_rl_active():
    """Rocket League penceresinin on planda olup olmadigini kontrol eder."""
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
    """Windows imlecinin gorunup gorunmedigini kontrol eder (menu tespiti)."""
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

# ─── MAIN LOGIC LOOP ─────────────────────────────────────────────────────────

def engine_loop():
    """Ana motor dongusu - hem API hem Manuel modu destekler."""
    global is_sound_playing, is_mouse_down, mouse_down_time, estimated_speed
    
    last_update_time = time.time()
    last_rl_check_time = 0.0
    cached_rl_active = False
    
    while True:
        current_time = time.time()
        dt = current_time - last_update_time
        last_update_time = current_time
        
        # RL aktif mi kontrolu (saniyede 2 kez)
        if current_time - last_rl_check_time > 0.5:
            cached_rl_active = is_rl_active()
            last_rl_check_time = current_time
        
        # ─── VERI KAYNAGI SECIMI ──────────────────────────────────────────
        speed = 0.0
        is_boosting = False
        
        if MANUAL_MODE:
            # Manuel Mod: Mouse tiklama + fizik tahmini
            current_mouse = (ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000) != 0
            if current_mouse and not is_mouse_down:
                mouse_down_time = current_time
            is_mouse_down = current_mouse
            
            # Cursor gorunurse (menu acik) boost basmayi yoksay
            mouse_boosting = is_mouse_down and not is_cursor_visible()
            
            # Fizik hesabi
            if mouse_boosting:
                estimated_speed += ACCELERATION * dt
                if estimated_speed > MAX_SPEED:
                    estimated_speed = MAX_SPEED
            else:
                estimated_speed -= DECELERATION * dt
                if estimated_speed < 0:
                    estimated_speed = 0
            
            speed = estimated_speed
            is_boosting = mouse_boosting
            
        else:
            # API Modu: WebSocket'ten gercek veri
            speed = api.speed
            is_boosting = api.is_boosting
        
        # ─── DURUM KARARI ─────────────────────────────────────────────────
        should_play = False
        
        if IS_ACTIVE and cached_rl_active and is_boosting:
            should_play = True
        
        # Sinirci boost modundaysa ve mouse basili ise her zaman cal
        if IS_ACTIVE and cached_rl_active and UNLIMITED_BOOST and MANUAL_MODE:
            if is_mouse_down and not is_cursor_visible():
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
        
        # Ses caliyorsa hizi guncelle
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

def toggle_manual_mode():
    global MANUAL_MODE
    MANUAL_MODE = not MANUAL_MODE
    user_settings["manual_mode"] = MANUAL_MODE
    save_settings()
    if app:
        app.update_manual_mode_state(MANUAL_MODE)

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

# ─── START BACKGROUND THREADS ────────────────────────────────────────────────

threading.Thread(target=engine_loop, daemon=True).start()

print("\n" + "=" * 50)
print("  ALPHA BOOST ENGINE (v2.0 - HYBRID) AKTIF")
print(f"  Ses Seviyesi: %{int(SES_SEVIYESI * 100)}")
print(f"  Mod: {'MANUEL (Mouse)' if MANUAL_MODE else 'API (WebSocket)'}")
print(f"  Sinirsiz Boost: {'ACIK' if UNLIMITED_BOOST else 'KAPALI'}")
print("=" * 50, flush=True)

# Keyboard listener
keyboard_listener = keyboard.Listener(on_press=on_press)
keyboard_listener.start()

# ─── LAUNCH GUI ──────────────────────────────────────────────────────────────

from interface import AlphaBoostApp

engine_callbacks = {
    "toggle_active": toggle_active,
    "toggle_shortcuts": toggle_shortcuts,
    "toggle_manual_mode": toggle_manual_mode,
    "toggle_unlimited_boost": toggle_unlimited_boost,
    "get_active": lambda: IS_ACTIVE,
    "get_shortcuts": lambda: SHORTCUTS_ENABLED,
    "get_manual_mode": lambda: MANUAL_MODE,
    "get_unlimited_boost": lambda: UNLIMITED_BOOST,
    "get_volume": lambda: SES_SEVIYESI,
    "set_volume": set_volume,
    "get_delay": lambda: AUDIO_DELAY_MS,
    "set_delay": set_delay,
    "get_api_status": lambda: api.connected,
}

app = AlphaBoostApp(engine_callbacks)
app.mainloop()
