import pygame
from pynput import mouse, keyboard
from moviepy import AudioFileClip
import os
import time
import threading
import mss
import cv2
import numpy as np
import json
import sys
import ctypes

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

# --- AYARLAR (Buradan Kontrol Et) ---
DOSYA_ADI = "AlphaBoostSound.wav"
INTRO_BASLANGIC = 0.075 
LOOP_NOKTASI = 0.597    
SES_SEVIYESI = 0.38

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

# --- SES PARÇALAMA (YENİ SİSTEM: TEK PARÇA KESİNTİSİZ LOOP) ---
def sesleri_hazirla():
    if os.path.exists("full_boost.wav"):
        return True
    print("Sesler hazırlanıyor (Kusursuz Alpha Boost Hissiyatı İçin)...")
    try:
        from moviepy import AudioFileClip, concatenate_audioclips
        audio = AudioFileClip(DOSYA_ADI)
        intro = audio.subclipped(INTRO_BASLANGIC, LOOP_NOKTASI)
        loop_part = audio.subclipped(LOOP_NOKTASI, audio.duration)
        
        # 10 saniyelik kesintisiz boost oluştur (Python'daki gap'i sıfırlamak için)
        clips = [intro] + [loop_part] * 20
        full_audio = concatenate_audioclips(clips)
        full_audio.write_audiofile("full_boost.wav", logger=None)
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
s_full = pygame.mixer.Sound("full_boost.wav")

# Ses Seviyelerini Uygula
s_full.set_volume(SES_SEVIYESI)

# --- DURUM DEĞİŞKENLERİ ---
is_mouse_down = False
mouse_down_time = 0.0
FREEPLAY_MODE = False
active_channels = []

def is_rl_active():
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
    title = buf.value
    return "Rocket League" in title or "RocketLeague" in title

def play_sound_from_start():
    # Boş bir kanal bul ve sesi oynat
    ch = pygame.mixer.find_channel()
    if ch:
        ch.play(s_full)
        active_channels.append(ch)

def stop_sound():
    # Tüm aktif kanalları çok yumuşak bir fadeout ile kapat (Alpha Boost yankısı)
    for ch in active_channels:
        if ch.get_busy():
            ch.fadeout(200) # Gerçek yankı için 200ms
    active_channels.clear()

def monitor_logic():
    global is_mouse_down, mouse_down_time, FREEPLAY_MODE
    
    last_thresh_img = None
    last_change_time = time.time()
    is_sound_playing = False

    with mss.mss() as sct:
        while True:
            current_time = time.time()
            
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
            if is_cursor_visible():
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
            if FREEPLAY_MODE:
                print("\n" + "*"*50)
                print("  >>> SINIRSIZ BOOST MODU AKTİF (Freeplay için)")
                print("  (Geri sayım ve donuk boost kontrolü devre dışı)")
                print("*"*50 + "\n")
            else:
                print("\n" + "*"*50)
                print("  >>> NORMAL MAÇ MODU AKTİF (Sınırsız Boost Kapalı)")
                print("*"*50 + "\n")
    except AttributeError:
        pass

# Takip thread'ini başlat
threading.Thread(target=monitor_logic, daemon=True).start()

print("\n" + "="*50)
print("  ALPHA BOOST SİSTEMİ (PERFECT FEEL EDITION) AKTİF")
print(f"  Ses Seviyesi: %{int(SES_SEVIYESI*100)}")
print("  Çoklu Kanal Hissiyatı (Feathering): AÇIK")
print("  Sınırsız Boost (Freeplay) Modu için: F4 tuşuna basın!")
print("="*50)

# Mouse ve Keyboard'u aynı anda dinle
mouse_listener = mouse.Listener(on_click=on_click)
keyboard_listener = keyboard.Listener(on_press=on_press)

mouse_listener.start()
keyboard_listener.start()

mouse_listener.join()
keyboard_listener.join()