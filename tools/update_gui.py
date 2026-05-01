import re

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update imports
replacement_imports = """import cv2
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
import wave
import tkinter as tk
from tkinter import ttk"""

content = re.sub(r"import cv2.*?import wave", replacement_imports, content, flags=re.DOTALL)

# 2. Add user settings logic and replace paths
replacement_paths = """# --- AYARLAR VE KAYIT ---
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

# --- KALİBRASYON VERİLERİNİ YÜKLE ---"""

content = re.sub(r"# --- AYARLAR \(Buradan Kontrol Et\) ---.*?# --- KALİBRASYON VERİLERİNİ YÜKLE ---", replacement_paths, content, flags=re.DOTALL)

# 3. Update Audio Paths
replacement_audio = """# Sesleri ve Kanalı Yükle
def get_path(filename):
    return os.path.join("assets", "sounds", filename)

try:
    s_level1 = pygame.mixer.Sound(get_path("full_boost.wav"))
    s_level2 = pygame.mixer.Sound(get_path("level_2.wav"))
    s_level3 = pygame.mixer.Sound(get_path("level_3.wav"))
    s_level4 = pygame.mixer.Sound(get_path("level_4.wav"))
    s_level5 = pygame.mixer.Sound(get_path("level_5.wav"))
    s_level6 = pygame.mixer.Sound(get_path("level_6.wav"))
    s_level7 = pygame.mixer.Sound(get_path("level_7.wav"))
    s_level8 = pygame.mixer.Sound(get_path("level_8.wav"))
except FileNotFoundError:
    print("HATA: Ses dosyaları 'assets/sounds' klasöründe bulunamadı!")
    sys.exit(1)

# Ses Seviyelerini Uygula
def update_volumes():
    s_level1.set_volume(SES_SEVIYESI)
    s_level2.set_volume(SES_SEVIYESI)
    s_level3.set_volume(SES_SEVIYESI)
    s_level4.set_volume(SES_SEVIYESI)
    s_level5.set_volume(SES_SEVIYESI)
    s_level6.set_volume(SES_SEVIYESI)
    s_level7.set_volume(SES_SEVIYESI)
    s_level8.set_volume(SES_SEVIYESI)

update_volumes()

# --- FİZİK VE DURUM DEĞİŞKENLERİ ---"""

content = re.sub(r"# Sesleri ve Kanalı Yükle.*?# --- FİZİK VE DURUM DEĞİŞKENLERİ ---", replacement_audio, content, flags=re.DOTALL)

# 4. Remove old FREEPLAY_MODE declaration (since it's now loaded from settings)
content = re.sub(r"FREEPLAY_MODE = False\n", "", content)

# 5. Add GUI Code at the end, replacing the direct run logic
replacement_gui = """
def toggle_freeplay():
    global FREEPLAY_MODE
    FREEPLAY_MODE = not FREEPLAY_MODE
    user_settings["freeplay_mode"] = FREEPLAY_MODE
    save_settings()
    btn_freeplay.config(text=f"Freeplay Modu: {'AÇIK' if FREEPLAY_MODE else 'KAPALI'}")

def toggle_active():
    global IS_ACTIVE
    IS_ACTIVE = not IS_ACTIVE
    user_settings["is_active"] = IS_ACTIVE
    save_settings()
    btn_active.config(text=f"Motor Durumu: {'ÇALIŞIYOR' if IS_ACTIVE else 'DURDURULDU'}")

def on_volume_change(val):
    global SES_SEVIYESI
    SES_SEVIYESI = float(val)
    user_settings["volume"] = SES_SEVIYESI
    save_settings()
    update_volumes()
    lbl_volume.config(text=f"Ses Seviyesi: {int(SES_SEVIYESI*100)}%")

# Dinleyici Threadleri Başlat
mouse_listener = mouse.Listener(on_click=on_click)
mouse_listener.start()

keyboard_listener = keyboard.Listener(on_press=on_press)
keyboard_listener.start()

monitor_thread = threading.Thread(target=monitor_logic)
monitor_thread.daemon = True
monitor_thread.start()

# --- TKINTER ARAYÜZ (GUI) ---
root = tk.Tk()
root.title("Alpha Boost Motoru")
root.geometry("350x250")
root.resizable(False, False)
root.attributes("-topmost", True) # Her zaman üstte kalsın

style = ttk.Style()
style.theme_use('clam')

frame = ttk.Frame(root, padding="20")
frame.pack(fill=tk.BOTH, expand=True)

ttk.Label(frame, text="🚀 Alpha Boost Control", font=("Arial", 14, "bold")).pack(pady=10)

btn_active = ttk.Button(frame, text=f"Motor Durumu: {'ÇALIŞIYOR' if IS_ACTIVE else 'DURDURULDU'}", command=toggle_active)
btn_active.pack(fill=tk.X, pady=5)

btn_freeplay = ttk.Button(frame, text=f"Freeplay Modu: {'AÇIK' if FREEPLAY_MODE else 'KAPALI'}", command=toggle_freeplay)
btn_freeplay.pack(fill=tk.X, pady=5)

lbl_volume = ttk.Label(frame, text=f"Ses Seviyesi: {int(SES_SEVIYESI*100)}%")
lbl_volume.pack(pady=(10,0))

slider_volume = ttk.Scale(frame, from_=0.0, to=1.0, orient='horizontal', command=on_volume_change)
slider_volume.set(SES_SEVIYESI)
slider_volume.pack(fill=tk.X, pady=5)

root.mainloop()
"""

# Find where to replace:
# mouse_listener = mouse.Listener(on_click=on_click) ... and below
content = re.sub(r"mouse_listener = mouse\.Listener\(on_click=on_click\).*?$", replacement_gui, content, flags=re.DOTALL)

# 6. Update on_press to update GUI button if possible, or just change variable.
# Wait, changing variable in terminal via F4 should ideally update GUI. 
replacement_onpress = """def on_press(key):
    global FREEPLAY_MODE
    try:
        if key == keyboard.Key.f4:
            FREEPLAY_MODE = not FREEPLAY_MODE
            user_settings["freeplay_mode"] = FREEPLAY_MODE
            save_settings()
            try:
                btn_freeplay.config(text=f"Freeplay Modu: {'AÇIK' if FREEPLAY_MODE else 'KAPALI'}")
            except:
                pass
    except AttributeError:
        pass"""
content = re.sub(r"def on_press\(key\):.*?except AttributeError:\n        pass", replacement_onpress, content, flags=re.DOTALL)

# 7. Apply IS_ACTIVE rule in monitor logic
replacement_monitor = """            # Eğer fare görünür durumdaysa (ESC menüsü, Ayarlar, Ana menü), sesi tamamen yasakla!
            if not IS_ACTIVE:
                should_play = False
            elif is_cursor_visible():"""
content = re.sub(r"            # Eğer fare görünür durumdaysa \(ESC menüsü, Ayarlar, Ana menü\), sesi tamamen yasakla!\n            if is_cursor_visible\(\):", replacement_monitor, content)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
