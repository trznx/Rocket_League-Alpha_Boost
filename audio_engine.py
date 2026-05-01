import pygame
import os

class AlphaBoostAudioEngine:
    def __init__(self, channels=16):
        pygame.mixer.pre_init(44100, -16, 2, 256)
        pygame.init()
        pygame.mixer.set_num_channels(channels)
        
        self.levels = {}
        self.active_channels = []
        self.master_volume = 0.3
        
        self.load_sounds()

    def get_path(self, filename):
        return os.path.join("assets", "sounds", filename)

    def load_sounds(self):
        try:
            self.levels[1] = pygame.mixer.Sound(self.get_path("full_boost.wav"))
            for i in range(2, 9):
                self.levels[i] = pygame.mixer.Sound(self.get_path(f"level_{i}.wav"))
            self.set_volume(self.master_volume)
        except Exception as e:
            print(f"  [AudioEngine HATA] Sesler yüklenirken hata oluştu: {e}")

    def set_volume(self, volume):
        self.master_volume = volume
        for sound in self.levels.values():
            sound.set_volume(volume)

    def trigger_start(self):
        pass # Eskiden sorun çıkaran transient kodunu tamamen iptal ettim

    def trigger_end(self):
        pass # Eskiden sorun çıkaran transient kodunu tamamen iptal ettim

    def play_loop(self, speed):
        """Eski orijinal, sorunsuz çalışan mantık: Boost anında tek ses oyna"""
        ch = pygame.mixer.find_channel()
        if not ch: return
        
        target_level = 1
        if speed < 275: target_level = 1
        elif speed < 550: target_level = 2
        elif speed < 825: target_level = 3
        elif speed < 1100: target_level = 4
        elif speed < 1375: target_level = 5
        elif speed < 1650: target_level = 6
        elif speed < 1925: target_level = 7
        else: target_level = 8
            
        ch.play(self.levels[target_level])
        self.active_channels.append(ch)

    def stop_loop(self):
        """Eski orijinal, sorunsuz çalışan mantık: 150ms fadeout ile yumuşak kapanış"""
        for ch in self.active_channels:
            if ch.get_busy():
                ch.fadeout(150)
        self.active_channels.clear()
