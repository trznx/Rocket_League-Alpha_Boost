import pygame
from pynput import mouse
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

# --- SES PARÇALAMA ---
def sesleri_hazirla():
    if os.path.exists("intro.wav") and os.path.exists("loop_part.wav"):
        return True
    print("Sesler parçalanıyor...")
    try:
        audio = AudioFileClip(DOSYA_ADI)
        audio.subclipped(INTRO_BASLANGIC, LOOP_NOKTASI).write_audiofile("intro.wav", logger=None)
        audio.subclipped(LOOP_NOKTASI, audio.duration).write_audiofile("loop_part.wav", logger=None)
        return True
    except Exception as e:
        print(f"Hata: {e}")
        return False

# --- SİSTEM BAŞLATMA ---
sesleri_hazirla()
pygame.mixer.pre_init(44100, -16, 2, 256) # En düşük gecikme
pygame.init()

# Sesleri ve Kanalı Yükle
channel = pygame.mixer.Channel(0)
s_intro = pygame.mixer.Sound("intro.wav")
s_loop = pygame.mixer.Sound("loop_part.wav")

# Ses Seviyelerini Uygula
s_intro.set_volume(SES_SEVIYESI)
s_loop.set_volume(SES_SEVIYESI)

# --- DURUM DEĞİŞKENLERİ ---
is_mouse_down = False
mouse_down_time = 0.0

def is_rl_active():
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
    title = buf.value
    return "Rocket League" in title or "RocketLeague" in title

def play_sound_from_start():
    channel.stop()
    channel.play(s_intro)

def stop_sound():
    channel.fadeout(50) # 50ms ile doğal kesilme

def monitor_logic():
    global is_mouse_down, mouse_down_time
    
    last_thresh_img = None
    last_change_time = time.time()
    is_sound_playing = False
    loop_triggered = False

    with mss.mss() as sct:
        while True:
            current_time = time.time()
            
            # Görüntü alma ve işleme
            img = np.array(sct.grab(BOOST_REGION))
            gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            _, thresh = cv2.threshold(gray, THRESHOLD_VALUE, 255, cv2.THRESH_BINARY)
            
            # 1. KONTROL: Rakam Değişimi (Frozen Boost tespiti)
            if last_thresh_img is not None:
                diff = cv2.absdiff(thresh, last_thresh_img)
                # Ufak piksel oynamalarını yoksaymak için eşik 5 piksel
                if cv2.countNonZero(diff) > 5:
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
            # Boost rakamı son 150ms içinde hiç değişmediyse "donuk" sayılır (Geri sayım)
            is_frozen = (current_time - last_change_time) > 0.15
            # Sol tıka basılalı henüz 150ms olmadıysa tolerans tanınır (0 gecikme için)
            in_grace_period = (current_time - mouse_down_time) < 0.15
            
            should_play = False
            
            if is_mouse_down and not currently_empty:
                if is_frozen and not in_grace_period:
                    # Rakam donmuş ve tolerans süresi bitmiş -> Geri sayımdasın, sesi kes.
                    should_play = False
                else:
                    # Her şey yolunda, boost harcanıyor veya yeni basıldı.
                    should_play = True
            
            # Sesi Yönet
            if should_play and not is_sound_playing:
                play_sound_from_start()
                is_sound_playing = True
                loop_triggered = False
            elif not should_play and is_sound_playing:
                stop_sound()
                is_sound_playing = False
                loop_triggered = False
                
            # Loop geçişi
            if is_sound_playing and not channel.get_busy() and not loop_triggered:
                channel.play(s_loop, loops=-1)
                loop_triggered = True
                
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

# Takip thread'ini başlat
threading.Thread(target=monitor_logic, daemon=True).start()

print("\n" + "="*50)
print("  ALPHA BOOST SİSTEMİ (TEMPORAL EDITION) AKTİF")
print(f"  Ses Seviyesi: %{int(SES_SEVIYESI*100)}")
print("  Donuk Boost Koruması (Geri Sayım): AÇIK")
print("="*50)

with mouse.Listener(on_click=on_click) as listener:
    listener.join()