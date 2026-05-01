import pygame
from pynput import mouse, keyboard
import os
import time
import threading
import mss
import cv2
import mss
import numpy as np
import time
import pygame
import threading
from pynput import mouse, keyboard
import sys
import os
import json
import ctypes
from tkinter import messagebox
from audio_engine import AlphaBoostAudioEngine
import kalibrasyon
import tkinter as tk
from tkinter import ttk

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

# --- AYARLAR VE KAYIT ---
SETTINGS_FILE = "user_settings.json"

default_settings = {
    "volume": 0.3,
    "freeplay_mode": False,
    "is_active": True
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
FREEPLAY_MODE = user_settings["freeplay_mode"]
IS_ACTIVE = user_settings["is_active"]

# --- KALİBRASYON VERİLERİNİ YÜKLE ---
if not os.path.exists("config.json") or not os.path.exists("template_0.png"):
    print("Warning: config.json or template_0.png missing. Please run calibration from GUI.")
    BOOST_REGION = {"left": 0, "top": 0, "width": 100, "height": 100, "threshold": 128}
    template_0 = np.zeros((50, 50), dtype=np.uint8)

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
    sys.exit(1)

# --- SES MOTORU BAŞLATMA ---
audio = AlphaBoostAudioEngine()

# --- FİZİK VE DURUM DEĞİŞKENLERİ ---
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

    with mss.mss() as sct:
        while True:
            current_time = time.time()
            dt = current_time - last_update_time
            last_update_time = current_time
            
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
                if 5 < diff_count < 800:
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
            if should_play and not is_sound_playing:
                audio.trigger_start()
                audio.play_loop(estimated_speed)
                is_sound_playing = True
            elif not should_play and is_sound_playing:
                audio.stop_loop()
                audio.trigger_end()
                is_sound_playing = False
                
            # --- FİZİK VE DİNAMİK SES YÖNETİMİ ---
            if should_play:
                estimated_speed += ACCELERATION * dt
                if estimated_speed > MAX_SPEED:
                    estimated_speed = MAX_SPEED
                audio.update_speed(estimated_speed)
            else:
                estimated_speed -= DECELERATION * dt
                if estimated_speed < 0:
                    estimated_speed = 0

                        # Check if RL is active only twice a second to save CPU
            if current_time - last_rl_check_time > 0.5:
                cached_rl_active = is_rl_active()
                last_rl_check_time = current_time
                
            time.sleep(0.015) # ~66 FPS - ultra optimized

def on_click(x, y, button, pressed):
    global is_mouse_down, mouse_down_time
    # Pynput callback MUST be as fast as possible to avoid input lag.
    if button == mouse.Button.left:
        is_mouse_down = pressed
        if pressed:
            mouse_down_time = time.time()

def on_press(key):
    global FREEPLAY_MODE
    try:
        if key == keyboard.Key.f4:
            FREEPLAY_MODE = not FREEPLAY_MODE
            user_settings["freeplay_mode"] = FREEPLAY_MODE
            save_settings()
            try:
                btn_freeplay.config(text=f"Freeplay Mode (F4): {'ENABLED' if FREEPLAY_MODE else 'DISABLED'}")
            except:
                pass
    except AttributeError:
        pass

# Takip thread'ini başlat
threading.Thread(target=monitor_logic, daemon=True).start()

print("\n" + "="*50)
print("  ALPHA BOOST SİSTEMİ (PURE AUDIO EDITION) AKTİF")
print(f"  Ses Seviyesi: %{int(SES_SEVIYESI*100)}")
print("  Orijinal Ses Tizleri: KORUNDU")
print("  Çoklu Kanal Hissiyatı (Feathering): AÇIK")
print("  Sınırsız Boost (Freeplay) Modu için: F4 tuşuna basın!")
print("="*50)

# Mouse ve Keyboard'u aynı anda dinle

def toggle_freeplay():
    global FREEPLAY_MODE
    FREEPLAY_MODE = not FREEPLAY_MODE
    user_settings["freeplay_mode"] = FREEPLAY_MODE
    save_settings()
    btn_freeplay.config(text=f"Freeplay Mode (F4): {'ENABLED' if FREEPLAY_MODE else 'DISABLED'}")

def toggle_active():
    global IS_ACTIVE
    IS_ACTIVE = not IS_ACTIVE
    user_settings["is_active"] = IS_ACTIVE
    save_settings()
    btn_active.config(text=f"Alpha Boost: {'ENABLED' if IS_ACTIVE else 'DISABLED'}")

def on_volume_change(val):
    global SES_SEVIYESI
    SES_SEVIYESI = float(val)
    user_settings["volume"] = SES_SEVIYESI
    save_settings()
    audio.set_volume(SES_SEVIYESI)
    lbl_volume.config(text=f"Volume Level: {int(SES_SEVIYESI*100)}%")

# Dinleyici Threadleri Başlat
mouse_listener = mouse.Listener(on_click=on_click)
mouse_listener.start()

keyboard_listener = keyboard.Listener(on_press=on_press)
keyboard_listener.start()

monitor_thread = threading.Thread(target=monitor_logic)
monitor_thread.daemon = True
monitor_thread.start()

# --- TKINTER ARAYÜZ (GUI) ---

def on_calibration_callback(msg):
    root.after(0, lambda: lbl_status.config(text=msg))

def start_calibration():
    res = messagebox.askyesno("Warning", "Are you sure you want to recalibrate?\n\nMake sure you are in Freeplay, your boost is at 0, and the game is Borderless/Windowed.")
    if not res: return
    
    lbl_status.config(text="Calibration starting...")
    calib_thread = threading.Thread(target=kalibrasyon.run_calibration, args=(on_calibration_callback,))
    calib_thread.daemon = True
    calib_thread.start()

root = tk.Tk()
root.title("Alpha Boost Engine")
root.geometry("400x520")
root.resizable(False, False)
root.attributes("-topmost", True)

style = ttk.Style()
style.theme_use('clam')

frame = ttk.Frame(root, padding="15")
frame.pack(fill=tk.BOTH, expand=True)

ttk.Label(frame, text="🚀 Alpha Boost Engine", font=("Arial", 16, "bold")).pack(pady=5)

# Controls
frame_controls = ttk.LabelFrame(frame, text="Controls", padding="10")
frame_controls.pack(fill=tk.X, pady=5)

btn_active = ttk.Button(frame_controls, text=f"Alpha Boost: {'ENABLED' if IS_ACTIVE else 'DISABLED'}", command=toggle_active)
btn_active.pack(fill=tk.X, pady=2)

btn_freeplay = ttk.Button(frame_controls, text=f"Freeplay Mode (F4): {'ENABLED' if FREEPLAY_MODE else 'DISABLED'}", command=toggle_freeplay)
btn_freeplay.pack(fill=tk.X, pady=2)

lbl_volume = ttk.Label(frame_controls, text=f"Volume Level: {int(SES_SEVIYESI*100)}%")
lbl_volume.pack(pady=(5,0))
slider_volume = ttk.Scale(frame_controls, from_=0.0, to=1.0, orient='horizontal', command=on_volume_change)
slider_volume.set(SES_SEVIYESI)
slider_volume.pack(fill=tk.X, pady=2)

# Calibration Section
frame_calib = ttk.LabelFrame(frame, text="Setup", padding="10")
frame_calib.pack(fill=tk.X, pady=5)

btn_calibrate = ttk.Button(frame_calib, text="🔧 Run Calibration", command=start_calibration)
btn_calibrate.pack(fill=tk.X, pady=2)

lbl_status = ttk.Label(frame_calib, text="Status: Ready", foreground="blue", wraplength=330, justify="center")
lbl_status.pack(pady=5)

# Info/Tips Section
frame_tips = ttk.LabelFrame(frame, text="Tips & Info", padding="10")
frame_tips.pack(fill=tk.X, pady=5)

tips_text = "• Freeplay Mode: Enable ONLY when using Unlimited Boost.\n\n• Note: Pressing boost during goal replays or countdowns may trigger short sounds. This is normal.\n\n• Calibration: Ensure game is Borderless/Windowed."
ttk.Label(frame_tips, text=tips_text, wraplength=340, font=("Arial", 8)).pack(fill=tk.X)

root.mainloop()
