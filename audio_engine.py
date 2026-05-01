import pygame
import os

class AlphaBoostAudioEngine:
    def __init__(self, channels=64):
        # En düşük gecikme için buffer=256
        pygame.mixer.pre_init(44100, -16, 2, 256)
        pygame.init()
        pygame.mixer.set_num_channels(channels)
        
        self.levels = {}
        self.active_groups = []
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
        # We don't update self.levels volumes directly here because volumes are dynamically managed by update_speed

    def trigger_start(self):
        pass # ADSR kullanılmıyor

    def trigger_end(self):
        pass # ADSR kullanılmıyor

    def play_loop(self, speed):
        """Boost basıldığı an 8 kanalın hepsini senkronize şekilde aynı anda başlatır"""
        
        target_level = self._get_level_from_speed(speed)
        current_group = []
        
        # 8 seviyenin hepsini aynı salisede oynatıyoruz ama 7 tanesinin sesi 0.0
        for i in range(1, 9):
            ch = pygame.mixer.find_channel(force=True)
            if ch:
                # Sadece hedef seviyenin sesi açık, diğerleri sessiz
                vol = self.master_volume if i == target_level else 0.0
                ch.set_volume(vol)
                ch.play(self.levels[i], loops=-1)
                current_group.append((i, ch))
                
        self.active_groups.append(current_group)

    def update_speed(self, speed):
        """Hız değiştikçe, o an çalan 8 kanallı grubun içindeki doğru kanalın sesini açıp diğerlerini kapatır."""
        target_level = self._get_level_from_speed(speed)
        
        for group in self.active_groups:
            for level_idx, ch in group:
                if ch.get_busy():
                    # Eğer kanal şu an çalması gereken kanalsa sesini aç, değilse 0 yap
                    vol = self.master_volume if level_idx == target_level else 0.0
                    ch.set_volume(vol)

    def stop_loop(self):
        """Boost bırakıldığında gruptaki tüm kanalları yumuşakça (fadeout) kapatır"""
        for group in self.active_groups:
            for _, ch in group:
                if ch.get_busy():
                    ch.fadeout(150)
        self.active_groups.clear()

    def _get_level_from_speed(self, speed):
        if speed < 275: return 1
        elif speed < 550: return 2
        elif speed < 825: return 3
        elif speed < 1100: return 4
        elif speed < 1375: return 5
        elif speed < 1650: return 6
        elif speed < 1925: return 7
        else: return 8
