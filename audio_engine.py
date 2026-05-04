import pygame
import os

class AlphaBoostAudioEngine:
    """6e991ff commit'indeki mantığın BİREBİR aynısı.
    
    TEK FARK: find_channel(force=True) yerine dedike kanallar kullanılıyor.
    Bu, kanal çapma riskini ortadan kaldırır.
    """
    
    def __init__(self, channels=16, profile="classic"):
        pygame.mixer.pre_init(44100, -16, 2, 256)
        pygame.mixer.init()
        pygame.mixer.set_num_channels(channels)
        
        self.ch_loops = [pygame.mixer.Channel(i) for i in range(12)]
        
        self.levels = {}
        self.master_volume = 0.3
        self.profile = profile
        
        self.load_sounds()

    def get_path(self, filename):
        import sys
        if hasattr(sys, '_MEIPASS'):
            base_path = os.path.join(sys._MEIPASS, "assets", "sounds", self.profile)
            if not os.path.exists(base_path):
                base_path = os.path.join(sys._MEIPASS, "assets", "sounds")
        else:
            base_path = os.path.join("assets", "sounds", self.profile)
            if not os.path.exists(base_path):
                base_path = os.path.join("assets", "sounds")
        return os.path.join(base_path, filename)

    def load_sounds(self, new_profile=None):
        if new_profile:
            self.profile = new_profile
            
        self.levels.clear()
        try:
            if self.profile == "quiet_loop_2":
                for i in range(1, 13):
                    self.levels[i] = pygame.mixer.Sound(self.get_path(f"level_{i}.wav"))
            else:
                self.levels[1] = pygame.mixer.Sound(self.get_path("full_boost.wav"))
                for i in range(2, 9):
                    self.levels[i] = pygame.mixer.Sound(self.get_path(f"level_{i}.wav"))
            self.set_volume(self.master_volume)
            print(f"  [AudioEngine] '{self.profile}' profili başarıyla yüklendi!")
        except Exception as e:
            print(f"  [AudioEngine HATA] Sesler yüklenirken hata oluştu: {e}")

    def set_volume(self, volume):
        self.master_volume = volume

    def trigger_start(self):
        pass

    def trigger_end(self):
        pass

    def play_loop(self, speed):
        target_level = self._get_level_from_speed(speed)
        
        for i in range(1, 13 if self.profile == "quiet_loop_2" else 9):
            if self.levels.get(i) is None:
                continue
            ch = self.ch_loops[i-1]
            ch.stop()
            vol = self.master_volume if i == target_level else 0.0
            ch.set_volume(vol)
            ch.play(self.levels[i], loops=-1)

    def update_speed(self, speed):
        target_level = self._get_level_from_speed(speed)
        
        for i in range(1, 13 if self.profile == "quiet_loop_2" else 9):
            if self.levels.get(i) is None:
                continue
            ch = self.ch_loops[i-1]
            if ch.get_busy():
                vol = self.master_volume if i == target_level else 0.0
                ch.set_volume(vol)

    def stop_loop(self):
        for ch in self.ch_loops:
            if ch.get_busy():
                ch.fadeout(150)

    def _get_level_from_speed(self, speed):
        if self.profile == "quiet_loop_2":
            level = int((speed / 2300.0) * 12) + 1
            return max(1, min(12, level))
        else:
            if speed < 275: return 1
            elif speed < 550: return 2
            elif speed < 825: return 3
            elif speed < 1100: return 4
            elif speed < 1375: return 5
            elif speed < 1650: return 6
            elif speed < 1925: return 7
            else: return 8
