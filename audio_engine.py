"""
Alpha Boost Engine - Audio Engine (API Edition)
================================================
Sadece 'alpha_boost' profili uzerinden calisan, 5 seviyeli (5-Level)
Pygame tabanli ses motoru.

5 Level Sistemi:
  Level 1: 0-460 uu/s     (Dusuk hiz / Rolanti)
  Level 2: 461-920 uu/s   (Hizlanma baslangici)
  Level 3: 921-1380 uu/s  (Orta hiz yirtilmasi)
  Level 4: 1381-1840 uu/s (Yuksek hiz tinisi)
  Level 5: 1841-2300 uu/s (Supersonic / Limit)
"""

import pygame
import os
import sys


class AlphaBoostAudioEngine:
    """5 seviyeli, Pygame tabanli Alpha Boost ses motoru.
    
    Her seviye farkli bir pitch'e sahip ayni ses dosyasinin varyasyonudur.
    API'den gelen hiz verisine gore anlik olarak dogru seviye secilir.
    """
    
    NUM_LEVELS = 5
    MAX_SPEED = 2300.0
    
    # Her level'in hiz araliklari (alt sinir, ust sinir)
    LEVEL_RANGES = [
        (   0,  460),  # Level 1
        ( 461,  920),  # Level 2
        ( 921, 1380),  # Level 3
        (1381, 1840),  # Level 4
        (1841, 2300),  # Level 5
    ]
    
    def __init__(self, channels=8):
        pygame.mixer.pre_init(44100, -16, 2, 256)
        pygame.mixer.init()
        pygame.mixer.set_num_channels(channels)
        
        # Her level icin bir kanal ayir
        self.ch_loops = [pygame.mixer.Channel(i) for i in range(self.NUM_LEVELS)]
        
        self.levels = {}       # {1: Sound, 2: Sound, ...}
        self.master_volume = 0.3
        
        self._load_sounds()
    
    def _get_sound_path(self, filename):
        """Ses dosyasinin yolunu dondurur (PyInstaller uyumlu)."""
        if hasattr(sys, '_MEIPASS'):
            base = os.path.join(sys._MEIPASS, "assets", "sounds", "alpha_boost")
        else:
            base = os.path.join("assets", "sounds", "alpha_boost")
        return os.path.join(base, filename)
    
    def _load_sounds(self):
        """5 level ses dosyasini yukler."""
        self.levels.clear()
        try:
            for i in range(1, self.NUM_LEVELS + 1):
                path = self._get_sound_path(f"level_{i}.wav")
                self.levels[i] = pygame.mixer.Sound(path)
            print(f"  [AudioEngine] Alpha Boost profili yuklendi ({self.NUM_LEVELS} level)")
        except Exception as e:
            print(f"  [AudioEngine HATA] Sesler yuklenirken hata: {e}")
    
    def set_volume(self, volume):
        """Master ses seviyesini ayarlar (0.0 - 1.0)."""
        self.master_volume = max(0.0, min(1.0, volume))
    
    def _get_level_from_speed(self, speed):
        """Hiza gore dogru level numarasini dondurur (1-5).
        
        0 uu/s      -> Level 1
        460 uu/s    -> Level 1
        461 uu/s    -> Level 2
        ...
        2300 uu/s   -> Level 5
        """
        for i, (v_min, v_max) in enumerate(self.LEVEL_RANGES):
            if speed <= v_max:
                return i + 1
        return self.NUM_LEVELS  # Maksimum hizin uzerinde -> Level 5
    
    def play_loop(self, speed=0.0):
        """Tum kanallari baslatir. Sadece hedef level'in sesi acik olur.
        
        Bu fonksiyon ses BASLADIGINDA bir kere cagirilir.
        Ardindan update_speed() ile surekli guncellenir.
        """
        target = self._get_level_from_speed(speed)
        
        for i in range(1, self.NUM_LEVELS + 1):
            sound = self.levels.get(i)
            if sound is None:
                continue
            ch = self.ch_loops[i - 1]
            ch.stop()
            vol = self.master_volume if i == target else 0.0
            ch.set_volume(vol)
            ch.play(sound, loops=-1)
    
    def update_speed(self, speed):
        """API'den gelen hiza gore aktif level'i degistirir.
        
        Saniyede 120 kez cagrilabilir. Sadece kanal volume'u degistirir,
        ses dosyasini yeniden baslatmaz (puruzsuz gecis).
        """
        target = self._get_level_from_speed(speed)
        
        for i in range(1, self.NUM_LEVELS + 1):
            ch = self.ch_loops[i - 1]
            if ch.get_busy():
                vol = self.master_volume if i == target else 0.0
                ch.set_volume(vol)
    
    def stop_loop(self):
        """Tum kanallari yumusak bir sekilde kapatir (150ms fadeout)."""
        for ch in self.ch_loops:
            if ch.get_busy():
                ch.fadeout(150)
    
    def trigger_start(self):
        """Ses baslamadan once cagirilir (opsiyonel hook)."""
        pass
    
    def trigger_end(self):
        """Ses bittikten sonra cagirilir (opsiyonel hook)."""
        pass
