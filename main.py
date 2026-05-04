"""
Alpha Boost Engine - Main (API Edition)
========================================
Rocket League'in WebSocket API'sinden gelen gercek zamanli veriyle
(hiz + boost durumu) Alpha Boost sesini senkronize eder.

Eski OCR/ekran tarama sistemi TAMAMEN kaldirilmistir.
Artik tek veri kaynagi: ws://localhost:49123
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
    "shortcuts_enabled": True
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

# ─── AUDIO ENGINE INIT ───────────────────────────────────────────────────────
audio = AlphaBoostAudioEngine()
audio.set_volume(SES_SEVIYESI)

# ─── API CLIENT INIT ─────────────────────────────────────────────────────────
api = RocketLeagueAPI()
api.start()

# ─── STATE VARIABLES ─────────────────────────────────────────────────────────
is_sound_playing = False

# ─── MAIN LOGIC LOOP ─────────────────────────────────────────────────────────

def engine_loop():
    """Ana motor dongusu.
    
    API'den gelen veriyi okur ve ses motorunu yonetir.
    Eski sistemdeki gibi ekran taramasi, OCR, piksel analizi,
    ivme hesaplamasi vs. YOKTUR. Sadece API verisi ve ses.
    """
    global is_sound_playing
    
    boost_start_time = 0.0
    
    while True:
        current_time = time.time()
        
        # API'den gercek verileri oku (thread-safe)
        speed = api.speed
        is_boosting = api.is_boosting
        api_connected = api.connected
        
        # --- DURUM KARARI ---
        # Ses calsin mi?
        should_play = False
        
        if IS_ACTIVE and api_connected and is_boosting:
            should_play = True
        
        # --- SES YONETIMI ---
        if should_play and not is_sound_playing:
            # Boost yeni basildi
            boost_start_time = current_time
            delay_ok = (AUDIO_DELAY_MS == 0)
            
            if delay_ok:
                audio.trigger_start()
                audio.play_loop(speed)
                is_sound_playing = True
                
        elif should_play and not is_sound_playing:
            # Gecikme suresi bekleniyor
            if (current_time - boost_start_time) >= (AUDIO_DELAY_MS / 1000.0):
                audio.trigger_start()
                audio.play_loop(speed)
                is_sound_playing = True
                
        elif not should_play and is_sound_playing:
            # Boost birakildi veya API baglantisi koptu
            audio.stop_loop()
            audio.trigger_end()
            is_sound_playing = False
        
        # --- HIZ GUNCELLEME ---
        # Ses caliyorsa, API'den gelen hiza gore level'i guncelle
        if is_sound_playing:
            audio.update_speed(speed)
        
        # ~120 FPS (API ile esit hizda)
        time.sleep(0.008)


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
    except AttributeError:
        pass

# ─── START BACKGROUND THREADS ────────────────────────────────────────────────

# Motor dongusu
threading.Thread(target=engine_loop, daemon=True).start()

print("\n" + "=" * 50)
print("  ALPHA BOOST ENGINE (API EDITION) AKTIF")
print(f"  Ses Seviyesi: %{int(SES_SEVIYESI * 100)}")
print(f"  API Baglantisi: {'BAGLI' if api.connected else 'BEKLENIYOR...'}")
print(f"  WebSocket: {RocketLeagueAPI.WS_URL}")
print("=" * 50, flush=True)

# Keyboard listener
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
    "get_delay": lambda: AUDIO_DELAY_MS,
    "set_delay": set_delay,
    "get_api_status": lambda: api.connected,
}

app = AlphaBoostApp(engine_callbacks)
app.mainloop()
