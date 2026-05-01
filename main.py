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
    BOOST_REGION = json.load(f)

template_0 = cv2.imread("template_0.png", 0) # Grayscale olarak oku

if np.mean(template_0) == 0:
    print("HATA: template_0.png tamamen SİYAH (boş)! Kalibrasyon sırasında '0' rakamı düzgün alınamamış veya eşik değeri çok yüksek.")
    print("Lütfen kalibrasyon.py dosyasını tekrar çalıştırın.")
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
is_boost_empty = False
loop_triggered = False

def is_rl_active():
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
    title = buf.value
    # Bakkesmod veya normal oyun başlığında Rocket League geçer
    return "Rocket League" in title or "RocketLeague" in title

def play_sound_from_start():
    global loop_triggered
    loop_triggered = False
    channel.stop()
    channel.play(s_intro)

def stop_sound():
    channel.fadeout(50) # 50ms ile daha keskin ama doğal kesilme

def monitor_logic():
    """Arka planda ekranı tarar ve loop/boost geçişlerini yönetir"""
    global is_mouse_down, is_boost_empty, loop_triggered
    
    with mss.mss() as sct:
        while True:
            # Görüntü alma ve işleme
            img = np.array(sct.grab(BOOST_REGION))
            gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            # DİKKAT: kalibrasyon.py ile aynı eşik değerini (100) kullanmalıyız!
            _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
            
            # Şablon eşleştirme
            res = cv2.matchTemplate(thresh, template_0, cv2.TM_CCOEFF_NORMED)
            match_val = np.max(res)
            
            # Eğer eşleşme 0.80'den büyükse, ekranda net bir şekilde 0 yazıyordur.
            currently_empty = (match_val > 0.80)
            
            if currently_empty != is_boost_empty:
                is_boost_empty = currently_empty
                
                # Boost MİKTARI DEĞİŞTİ (Sıfırlandı veya Pad Alındı)
                if is_boost_empty:
                    # Boost 0 oldu, sesi hemen kes (mouse basılı olsa bile)
                    stop_sound()
                else:
                    # Boost 0'dan büyük bir değere çıktı (Örn: 12'lik Pad alındı)
                    # SİZİN İSTEĞİNİZ: Eğer sol tıka hala basılıyorsa, ses en baştan başlasın!
                    if is_mouse_down:
                        play_sound_from_start()
            
            # Normal Loop mantığı: Intro bitince loop'a geçiş (Boost varsa ve fare basılıysa)
            if is_mouse_down and not is_boost_empty and not channel.get_busy() and not loop_triggered:
                channel.play(s_loop, loops=-1)
                loop_triggered = True
                
            time.sleep(0.005) # Saniyede ~200 kez kontrol

def on_click(x, y, button, pressed):
    global is_mouse_down, is_boost_empty
    if button == mouse.Button.left:
        # Sadece oyun penceresi aktifken çalışsın (Masaüstünde ses çıkmasını engeller)
        if not is_rl_active():
            return
            
        is_mouse_down = pressed
        if pressed:
            # Tıkladığımızda boost'umuz varsa sesi baştan çal
            if not is_boost_empty:
                play_sound_from_start()
        else:
            # Parmağımızı çektiğimizde sesi kes
            stop_sound()

# Takip thread'ini başlat
threading.Thread(target=monitor_logic, daemon=True).start()

print("\n" + "="*45)
print("  ALPHA BOOST SİSTEMİ (CV EDITION) AKTİF")
print(f"  Ses Seviyesi: %{int(SES_SEVIYESI*100)}")
print("  Gecikmesiz Görüntü İşleme: AÇIK")
print("="*45)

with mouse.Listener(on_click=on_click) as listener:
    listener.join()