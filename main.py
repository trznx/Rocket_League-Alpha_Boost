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
import wave
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
    print("HATA: config.json veya template_0.png bulunamadi!")
    print("Lütfen önce 'kalibrasyon.py' dosyasini çalistirin.")
    sys.exit(1)

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

# --- KUSURSUZ CROSSFADE SES ÜRETİCİSİ ---
def crossfade_audio(clip1, clip2, crossfade_samples):
    if crossfade_samples == 0:
        return np.vstack((clip1, clip2))
    
    fade_out = np.linspace(1.0, 0.0, crossfade_samples).reshape(-1, 1)
    fade_in = np.linspace(0.0, 1.0, crossfade_samples).reshape(-1, 1)
    
    overlap1 = clip1[-crossfade_samples:] * fade_out
    overlap2 = clip2[:crossfade_samples] * fade_in
    mixed = overlap1 + overlap2
    
    return np.vstack((
        clip1[:-crossfade_samples],
        mixed,
        clip2[crossfade_samples:]
    ))

def sesleri_hazirla():
    if os.path.exists("full_boost.wav"):
        return True
    print("Orijinal Alpha Boost Sesi (Crossfade ile Pürüzsüzleştirilerek) Hazırlanıyor...")
    try:
        with wave.open(DOSYA_ADI, 'rb') as w:
            sr = w.getframerate()
            n_channels = w.getnchannels()
            sampwidth = w.getsampwidth()
            frames = w.readframes(w.getnframes())
            
        dtype = np.int16 if sampwidth == 2 else np.int32
        audio = np.frombuffer(frames, dtype=dtype)
        if n_channels > 1:
            audio = audio.reshape(-1, n_channels)
        else:
            audio = audio.reshape(-1, 1)
            
        intro_start = int(INTRO_BASLANGIC * sr)
        loop_start = int(LOOP_NOKTASI * sr)
        loop_end = int(LOOP_BITIS * sr)
        
        intro = audio[intro_start:loop_start]
        loop_piece = audio[loop_start:loop_end]
        
        crossfade_samples = int(0.03 * sr) # 30ms pürüzsüz geçiş
        
        # Helikopter vızıltısını önlemek için pürüzsüz (crossfade) loop oluştur
        loop_10s = loop_piece.copy()
        # Kullanıcının isteği: 1 dakikalık ses kaydı haline getir (yaklaşık 120 kez birleştir)
        for _ in range(120):
            loop_10s = crossfade_audio(loop_10s, loop_piece, crossfade_samples)
            
        full_audio = crossfade_audio(intro, loop_10s, crossfade_samples)
        
        with wave.open("full_boost.wav", 'wb') as w:
            w.setnchannels(n_channels)
            w.setsampwidth(sampwidth)
            w.setframerate(sr)
            w.writeframes(full_audio.astype(dtype).tobytes())
            
        with wave.open("loop_part.wav", 'wb') as w:
            w.setnchannels(n_channels)
            w.setsampwidth(sampwidth)
            w.setframerate(sr)
            w.writeframes(loop_10s.astype(dtype).tobytes())
            
        return True
    except Exception as e:
        print(f"Hata: {e}")
        return False

# --- SİSTEM BAŞLATMA ---
sesleri_hazirla()
pygame.mixer.pre_init(44100, -16, 2, 256) # En düşük gecikme
pygame.init()

# 8 Kanallı Çoklu Ses Sistemi (Feathering için)
pygame.mixer.set_num_channels(8)

# Sesleri ve Kanalı Yükle
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

# --- FİZİK VE DURUM DEĞİŞKENLERİ ---
is_mouse_down = False
estimated_speed = 0.0
MAX_SPEED = 2200.0
ACCELERATION = 1200.0
DECELERATION = 800.0
mouse_down_time = 0.0
active_channels = []

def is_rl_active():
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
    title = buf.value
    return "Rocket League" in title or "RocketLeague" in title

def play_sound_from_start():
    ch = pygame.mixer.find_channel()
    if ch:
        # Kademeli Hız Kontrolü (8 Adım - Ultra Yumuşak Geçiş)
        if estimated_speed < 275:
            ch.play(s_level1)
        elif estimated_speed < 550:
            ch.play(s_level2)
        elif estimated_speed < 825:
            ch.play(s_level3)
        elif estimated_speed < 1100:
            ch.play(s_level4)
        elif estimated_speed < 1375:
            ch.play(s_level5)
        elif estimated_speed < 1650:
            ch.play(s_level6)
        elif estimated_speed < 1925:
            ch.play(s_level7)
        else:
            ch.play(s_level8)
        active_channels.append(ch)

def stop_sound():
    for ch in active_channels:
        if ch.get_busy():
            ch.fadeout(150)
    active_channels.clear()

def monitor_logic():
    global is_mouse_down, mouse_down_time, FREEPLAY_MODE, estimated_speed, is_sound_playing
    
    last_thresh_img = None
    last_change_time = time.time()
    last_update_time = time.time()
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
            if not IS_ACTIVE:
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
                play_sound_from_start()
                is_sound_playing = True
            elif not should_play and is_sound_playing:
                stop_sound()
                is_sound_playing = False
                
            # --- FİZİK VE DİNAMİK SES YÖNETİMİ ---
            if should_play:
                estimated_speed += ACCELERATION * dt
                if estimated_speed > MAX_SPEED:
                    estimated_speed = MAX_SPEED
            else:
                estimated_speed -= DECELERATION * dt
                if estimated_speed < 0:
                    estimated_speed = 0

            time.sleep(0.005) # Saniyede ~200 kez kontrol

def on_click(x, y, button, pressed):
    global is_mouse_down, mouse_down_time
    if button == mouse.Button.left:
        # Sadece oyun aktifken çalışsın
        if not is_rl_active():
            return
            
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
    update_volumes()
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
root = tk.Tk()
root.title("Alpha Boost Engine")
root.geometry("350x250")
root.resizable(False, False)
root.attributes("-topmost", True) # Her zaman üstte kalsın

style = ttk.Style()
style.theme_use('clam')

frame = ttk.Frame(root, padding="20")
frame.pack(fill=tk.BOTH, expand=True)

ttk.Label(frame, text="🚀 Alpha Boost Engine", font=("Arial", 14, "bold")).pack(pady=10)

btn_active = ttk.Button(frame, text=f"Alpha Boost: {'ENABLED' if IS_ACTIVE else 'DISABLED'}", command=toggle_active)
btn_active.pack(fill=tk.X, pady=5)

btn_freeplay = ttk.Button(frame, text=f"Freeplay Mode (F4): {'ENABLED' if FREEPLAY_MODE else 'DISABLED'}", command=toggle_freeplay)
btn_freeplay.pack(fill=tk.X, pady=5)

lbl_volume = ttk.Label(frame, text=f"Volume Level: {int(SES_SEVIYESI*100)}%")
lbl_volume.pack(pady=(10,0))

slider_volume = ttk.Scale(frame, from_=0.0, to=1.0, orient='horizontal', command=on_volume_change)
slider_volume.set(SES_SEVIYESI)
slider_volume.pack(fill=tk.X, pady=5)

root.mainloop()

