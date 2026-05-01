import pygame
from pynput import mouse, keyboard
import os
import time
import threading
import mss
import cv2
import numpy as np
import json
import sys
import ctypes
import wave

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
LOOP_NOKTASI = 1.0       # Uzun başlangıç (Döngüye hemen girmemesi için wind-up)
LOOP_BITIS = 1.4         # Tam ortanın biraz altı (Kusursuz sabit loop aralığı)
SES_SEVIYESI = 0.3

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
s_full = pygame.mixer.Sound("full_boost.wav")
s_loop = pygame.mixer.Sound("loop_part.wav")

# Ses Seviyelerini Uygula
s_full.set_volume(SES_SEVIYESI)
s_loop.set_volume(SES_SEVIYESI)

# --- DURUM DEĞİŞKENLERİ ---
is_mouse_down = False
mouse_down_time = 0.0
last_sound_stop_time = 0.0
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
    ch = pygame.mixer.find_channel()
    if ch:
        ch.play(s_full)
        active_channels.append(ch)

def stop_sound():
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
print("  ALPHA BOOST SİSTEMİ (PURE AUDIO EDITION) AKTİF")
print(f"  Ses Seviyesi: %{int(SES_SEVIYESI*100)}")
print("  Orijinal Ses Tizleri: KORUNDU")
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
