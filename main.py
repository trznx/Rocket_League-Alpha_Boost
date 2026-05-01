import pygame
from pynput import mouse
from moviepy import AudioFileClip
import os
import time
import threading

# --- AYARLAR (Buradan Kontrol Et) ---
DOSYA_ADI = "AlphaBoostSound.wav"
INTRO_BASLANGIC = 0.075 
LOOP_NOKTASI = 0.597    

# SES SEVİYESİ: 0.0 (Sessiz) ile 1.0 (Tam Ses) arası. 
# Oyun sesiyle uyuşması için 0.4 veya 0.5 idealdir.
SES_SEVIYESI = 0.38

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

is_pressed = False
loop_triggered = False

def monitor_logic():
    """Arka planda sadece loop geçişini yönetir"""
    global is_pressed, loop_triggered
    while True:
        # Eğer basılıysa ve intro bittiyse (kanal boşaldıysa) loop'u başlat
        if is_pressed and not channel.get_busy() and not loop_triggered:
            channel.play(s_loop, loops=-1)
            loop_triggered = True
        time.sleep(0.005)

def on_click(x, y, button, pressed):
    global is_pressed, loop_triggered
    if button == mouse.Button.left:
        if pressed:
            # ÖNEMLİ: Her basışta kanalı DURDUR ve her şeyi sıfırla. 
            # Bu, sesin gelmeme veya takılı kalma sorununu çözer.
            is_pressed = True
            loop_triggered = False
            channel.stop() 
            channel.play(s_intro)
        else:
            # Parmağını çektiğin an her şeyi kes
            is_pressed = False
            loop_triggered = False
            channel.fadeout(100) # 100ms sönme ile keskinliği yumuşat

# Takip thread'ini başlat
threading.Thread(target=monitor_logic, daemon=True).start()

print("\n" + "="*35)
print("  ALPHA BOOST SİSTEMİ AKTİF")
print(f"  Ses Seviyesi: %{int(SES_SEVIYESI*100)}")
print("  Bug-Fix Mode: ON")
print("="*35)

with mouse.Listener(on_click=on_click) as listener:
    listener.join()