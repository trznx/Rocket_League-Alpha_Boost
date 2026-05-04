import pygame
from pynput import mouse, keyboard
import os
import time
import threading
import mss
import cv2
import numpy as np
import sys
import json
import ctypes
from audio_engine import AlphaBoostAudioEngine
import kalibrasyon

# ─── WINDOWS STRUCTURES ──────────────────────────────────────────────────────

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class CURSORINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint),
                ("flags", ctypes.c_uint),
                ("hCursor", ctypes.c_void_p),
                ("ptScreenPos", POINT)]

def is_cursor_visible():
    info = CURSORINFO()
    info.cbSize = ctypes.sizeof(CURSORINFO)
    ctypes.windll.user32.GetCursorInfo(ctypes.byref(info))
    # flags == 1 means cursor is showing
    return info.flags == 1

# ─── SETTINGS & PERSISTENCE ──────────────────────────────────────────────────
SETTINGS_FILE = "user_settings.json"

default_settings = {
    "volume": 0.4,
    "sound_profile": "quiet_loop",
    "audio_delay_ms": 0,
    "freeplay_mode": False,
    "is_active": True,
    "shortcuts_enabled": True
}

if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "r") as f:
        try:
            user_settings = json.load(f)
            # Eksik anahtarları tamamla
            for k, v in default_settings.items():
                if k not in user_settings:
                    user_settings[k] = v
        except:
            user_settings = default_settings.copy()
else:
    user_settings = default_settings.copy()

def save_settings():
    with open(SETTINGS_FILE, "w") as f:
        json.dump(user_settings, f, indent=4)

SES_SEVIYESI = user_settings["volume"]
SOUND_PROFILE = user_settings.get("sound_profile", "classic")
AUDIO_DELAY_MS = user_settings.get("audio_delay_ms", 40)
FREEPLAY_MODE = user_settings["freeplay_mode"]
IS_ACTIVE = user_settings["is_active"]
SHORTCUTS_ENABLED = user_settings.get("shortcuts_enabled", True)

# ─── CALIBRATION DATA ────────────────────────────────────────────────────────

if not os.path.exists("config.json") or not os.path.exists("template_0.png"):
    print("Warning: config.json or template_0.png missing. Please run calibration from GUI.")
    BOOST_REGION = {"left": 0, "top": 0, "width": 100, "height": 100, "threshold": 128}
    template_0 = np.zeros((50, 50), dtype=np.uint8)
else:
    with open("config.json", "r") as f:
        config_data = json.load(f)
        BOOST_REGION = {
            "left": config_data["left"],
            "top": config_data["top"],
            "width": config_data["width"],
            "height": config_data["height"]
        }
        THRESHOLD_VALUE = config_data.get("threshold", 120)

    template_0 = cv2.imread("template_0.png", 0) # Grayscale olarak oku

    if np.mean(template_0) == 0:
        print("HATA: template_0.png tamamen SİYAH (boş)! Kalibrasyon sırasında '0' rakamı düzgün alınamamış.")

# ─── AUDIO ENGINE INIT ───────────────────────────────────────────────────────
audio = AlphaBoostAudioEngine(profile=SOUND_PROFILE)

# ─── PHYSICS & STATE VARIABLES ───────────────────────────────────────────────
is_mouse_down = False
estimated_speed = 0.0
MAX_SPEED = 2200.0
ACCELERATION = 1200.0
DECELERATION = 800.0
mouse_down_time = 0.0

def is_rl_active():
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
    title = buf.value
    return "Rocket League" in title or "RocketLeague" in title

def monitor_logic():
    global is_mouse_down, mouse_down_time, FREEPLAY_MODE, estimated_speed, is_sound_playing
    
    last_thresh_img = None
    last_change_time = time.time()
    last_update_time = time.time()
    last_rl_check_time = 0
    cached_rl_active = False
    is_sound_playing = False

    with mss.MSS() as sct:
        while True:
            current_time = time.time()
            dt = current_time - last_update_time
            last_update_time = current_time
            
            # --- MOUSE STATE POLLING ---
            current_mouse_state = (ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000) != 0
            if current_mouse_state and not is_mouse_down:
                mouse_down_time = current_time
            is_mouse_down = current_mouse_state
            
            # Görüntü alma ve işleme
            img = np.array(sct.grab(BOOST_REGION))
            gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            _, thresh = cv2.threshold(gray, THRESHOLD_VALUE, 255, cv2.THRESH_BINARY)
            
            # 1. KONTROL: Rakam Değişimi (Frozen Boost ve Gol Tekrarı tespiti)
            if last_thresh_img is not None:
                diff = cv2.absdiff(thresh, last_thresh_img)
                diff_count = cv2.countNonZero(diff)
                
                # Eğer değişim çok küçükse (titreme) veya çok büyükse (Gol tekrarında kameranın dönmesi)
                # Sadece mantıklı font değişimlerini (5 ile 800 piksel arası) kabul et.
                if 25 < diff_count < 800:
                    last_change_time = current_time
            
            last_thresh_img = thresh.copy()
            
            # 2. KONTROL: Menüde miyiz?
            white_pixels = cv2.countNonZero(thresh)
            in_menu = (white_pixels < 15)
            
            if in_menu:
                currently_empty = True
            else:
                # 3. KONTROL: Boost 0 mı?
                res = cv2.matchTemplate(thresh, template_0, cv2.TM_CCOEFF_NORMED)
                match_val = np.max(res)
                currently_empty = (match_val > 0.80)
            
            # --- DURUM MAKİNESİ (STATE MACHINE) ---
            is_frozen = (current_time - last_change_time) > 0.15
            
            # Sınırsız Boost Modu açıksa donukluk kontrolünü iptal et!
            if FREEPLAY_MODE:
                is_frozen = False
                
            in_grace_period = (current_time - mouse_down_time) < 0.15
            
            should_play = False
            
            # Eğer fare görünür durumdaysa (ESC menüsü, Ayarlar, Ana menü), sesi tamamen yasakla!
            if not IS_ACTIVE or not cached_rl_active:
                should_play = False
            elif is_cursor_visible():
                should_play = False
            elif is_mouse_down and not currently_empty:
                if is_frozen and not in_grace_period:
                    should_play = False
                else:
                    should_play = True
            
            # Sesi Yönet
            # Ses Başlama Gecikmesi: Boost basıldıktan AUDIO_DELAY_MS ms sonra ses başlar
            delay_elapsed = (current_time - mouse_down_time) >= (AUDIO_DELAY_MS / 1000.0)
            
            if should_play and not is_sound_playing and delay_elapsed:
                audio.trigger_start()
                audio.play_loop(estimated_speed)
                is_sound_playing = True
            elif not should_play and is_sound_playing:
                audio.stop_loop()
                audio.trigger_end()
                is_sound_playing = False
                
            # --- FİZİK VE DİNAMİK SES YÖNETİMİ ---
            if SOUND_PROFILE == "quiet_loop_2":
                if should_play:
                    estimated_speed += 911.0 * dt
                    if estimated_speed > 2300.0:
                        estimated_speed = 2300.0
                else:
                    estimated_speed -= 800.0 * dt
                    if estimated_speed < 0:
                        estimated_speed = 0
                if is_sound_playing:
                    audio.update_speed(estimated_speed)
            else:
                if should_play:
                    estimated_speed += ACCELERATION * dt
                    if estimated_speed > MAX_SPEED:
                        estimated_speed = MAX_SPEED
                else:
                    estimated_speed -= DECELERATION * dt
                    if estimated_speed < 0:
                        estimated_speed = 0
                if is_sound_playing:
                    audio.update_speed(estimated_speed)

                        # Check if RL is active only twice a second to save CPU
            if current_time - last_rl_check_time > 0.5:
                cached_rl_active = is_rl_active()
                last_rl_check_time = current_time
                
            time.sleep(0.015) # ~66 FPS - ultra optimized



# ─── GUI CALLBACK FUNCTIONS ──────────────────────────────────────────────────
# These are called by the interface when the user interacts with the GUI.

app = None  # Will be set after GUI is created

def toggle_freeplay():
    global FREEPLAY_MODE
    FREEPLAY_MODE = not FREEPLAY_MODE
    user_settings["freeplay_mode"] = FREEPLAY_MODE
    save_settings()
    if app:
        app.update_freeplay_state(FREEPLAY_MODE)

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

def set_profile(profile_code):
    global SOUND_PROFILE
    SOUND_PROFILE = profile_code
    user_settings["sound_profile"] = profile_code
    save_settings()
    audio.load_sounds(profile_code)

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

def start_calibration(status_callback):
    calib_thread = threading.Thread(
        target=kalibrasyon.run_calibration,
        args=(status_callback,)
    )
    calib_thread.daemon = True
    calib_thread.start()

def on_press(key):
    global FREEPLAY_MODE, SHORTCUTS_ENABLED
    if not SHORTCUTS_ENABLED:
        return
    try:
        if key == keyboard.Key.f4:
            toggle_freeplay()
        elif key == keyboard.Key.f5:
            toggle_active()
    except AttributeError:
        pass

# ─── START BACKGROUND THREADS ────────────────────────────────────────────────

# Monitor thread
threading.Thread(target=monitor_logic, daemon=True).start()

print("\n" + "="*50)
print("  ALPHA BOOST SİSTEMİ (PURE AUDIO EDITION) AKTİF")
print(f"  Ses Seviyesi: %{int(SES_SEVIYESI*100)}")
print("  Orijinal Ses Tizleri: KORUNDU")
print("  Çoklu Kanal Hissiyatı (Feathering): AÇIK")
print("  Sınırsız Boost (Freeplay) Modu için: F4 tuşuna basın!")
print("="*50)

# Keyboard listeners

keyboard_listener = keyboard.Listener(on_press=on_press)
keyboard_listener.start()

monitor_thread = threading.Thread(target=monitor_logic)
monitor_thread.daemon = True
monitor_thread.start()

# ─── LAUNCH GUI ──────────────────────────────────────────────────────────────

from interface import AlphaBoostApp

engine_callbacks = {
    "toggle_active": toggle_active,
    "toggle_freeplay": toggle_freeplay,
    "toggle_shortcuts": toggle_shortcuts,
    "get_active": lambda: IS_ACTIVE,
    "get_freeplay": lambda: FREEPLAY_MODE,
    "get_shortcuts": lambda: SHORTCUTS_ENABLED,
    "get_profile": lambda: SOUND_PROFILE,
    "set_profile": set_profile,
    "get_volume": lambda: SES_SEVIYESI,
    "set_volume": set_volume,
    "get_delay": lambda: AUDIO_DELAY_MS,
    "set_delay": set_delay,
    "start_calibration": start_calibration,
}

app = AlphaBoostApp(engine_callbacks)
app.mainloop()
