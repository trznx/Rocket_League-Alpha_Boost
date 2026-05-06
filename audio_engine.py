"""
Alpha Boost Engine - Audio Engine (Profile Edition)
=====================================================
İki profil destekler:

  Advanced  – Araç hızına göre 4 farklı ses dosyası:
      0-500   uu/s  →  0_gr.wav
      501-1000 uu/s →  750_gr.wav
      1001-1500 uu/s → 1400_gr.wav
      1501-2000 uu/s → 1700_gr.wav

  Normal    – Her zaman Classic.wav
"""

import pygame
import os
import sys


class AlphaBoostAudioEngine:
    """Profil tabanlı Alpha Boost ses motoru.
    
    Advanced profilde araç hızına göre doğru ses dosyası seçilir.
    Normal profilde her zaman aynı ses dosyası çalar.
    """

    # Advanced profil: hız aralıkları ve dosya isimleri
    ADVANCED_RANGES = [
        (   0,  500, "0_gr.wav"),
        ( 501, 1000, "750_gr.wav"),
        (1001, 1500, "1400_gr.wav"),
        (1501, 2000, "1700_gr.wav"),
    ]

    NORMAL_FILE = "Classic.wav"

    def __init__(self, channels=8):
        pygame.mixer.pre_init(48000, -16, 2, 512)
        pygame.mixer.init()
        pygame.mixer.set_num_channels(channels)

        self._channel = pygame.mixer.Channel(0)

        self._profile = "advanced"       # "advanced" veya "normal"
        self._master_volume = 0.1
        self._current_sound = None       # Şu an yüklü Sound nesnesi
        self._current_file = None        # Şu an yüklü dosya adı

        # Ses dosyalarını önceden yükle
        self._advanced_sounds = {}       # {dosya_adı: Sound}
        self._normal_sound = None        # Classic.wav Sound nesnesi

        self._load_all_sounds()

    # ─── PATH HELPERS ────────────────────────────────────────────────────────

    def _get_base_path(self):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, "assets", "sounds")
        return os.path.join("assets", "sounds")

    def _get_advanced_path(self, filename):
        return os.path.join(self._get_base_path(), "alpha_boost_advanced", filename)

    def _get_normal_path(self, filename):
        return os.path.join(self._get_base_path(), "alpha_boost_normal", filename)

    # ─── SOUND LOADING ───────────────────────────────────────────────────────

    def _load_all_sounds(self):
        """Tüm ses dosyalarını önceden belleğe yükler."""
        # Advanced profil sesleri
        for _, _, filename in self.ADVANCED_RANGES:
            path = self._get_advanced_path(filename)
            try:
                self._advanced_sounds[filename] = pygame.mixer.Sound(path)
            except Exception as e:
                print(f"  [AudioEngine HATA] {filename} yüklenemedi: {e}")

        # Normal profil sesi
        path = self._get_normal_path(self.NORMAL_FILE)
        try:
            self._normal_sound = pygame.mixer.Sound(path)
        except Exception as e:
            print(f"  [AudioEngine HATA] {self.NORMAL_FILE} yüklenemedi: {e}")

        adv_count = len(self._advanced_sounds)
        norm_ok = "OK" if self._normal_sound else "HATA"
        print(f"  [AudioEngine] Sesler yüklendi — Advanced: {adv_count} dosya, Normal: {norm_ok}")

    # ─── PROFILE ─────────────────────────────────────────────────────────────

    def set_profile(self, profile_name):
        """Profili değiştirir ("advanced" veya "normal").
        
        Eğer ses çalıyorsa önce durdurur.
        """
        profile_name = profile_name.lower()
        if profile_name not in ("advanced", "normal"):
            return

        if profile_name != self._profile:
            # Çalan sesi durdur
            self.stop_loop()
            self._profile = profile_name
            self._current_sound = None
            self._current_file = None
            print(f"  [AudioEngine] Profil değiştirildi: {profile_name}")

    def get_profile(self):
        return self._profile

    # ─── VOLUME ──────────────────────────────────────────────────────────────

    def set_volume(self, volume):
        """Master ses seviyesini ayarlar (0.0 - 1.0)."""
        self._master_volume = max(0.0, min(1.0, volume))
        if self._channel.get_busy():
            self._channel.set_volume(self._master_volume)

    # ─── SPEED → SOUND MAPPING ───────────────────────────────────────────────

    def _get_sound_for_speed(self, speed):
        """Hıza göre doğru ses dosyasını döndürür (Advanced profil).
        
        Returns: (filename, Sound) tuple
        """
        for v_min, v_max, filename in self.ADVANCED_RANGES:
            if v_min <= speed <= v_max:
                sound = self._advanced_sounds.get(filename)
                return filename, sound

        # 2000 üzeri hızlar → son aralık
        last_file = self.ADVANCED_RANGES[-1][2]
        return last_file, self._advanced_sounds.get(last_file)

    # ─── PLAYBACK ────────────────────────────────────────────────────────────

    def play_loop(self, speed=0.0):
        """Boost başladığında çağrılır. Hıza göre doğru sesi başlatır."""
        if self._profile == "normal":
            target_file = self.NORMAL_FILE
            target_sound = self._normal_sound
        else:
            target_file, target_sound = self._get_sound_for_speed(speed)

        if target_sound is None:
            return

        # Zaten aynı ses çalıyorsa tekrar başlatma
        if self._current_file == target_file and self._channel.get_busy():
            return

        # Farklı ses veya ses çalmıyor → yeni ses başlat
        self._channel.stop()
        self._channel.set_volume(self._master_volume)
        self._channel.play(target_sound, loops=-1)
        self._current_file = target_file
        self._current_sound = target_sound

    def update_speed(self, speed):
        """Boost basılıyken çağrılır ama ses değişikliği yapmaz.
        
        Ses dosyası yalnızca boost'a basıldığı anda (play_loop) belirlenir.
        Boost basılı tutulurken hız değişse bile ses dosyası değişmez.
        Kullanıcı boost'u bırakıp tekrar bastığında yeni hıza göre ses seçilir.
        """
        pass

    def stop_loop(self):
        """Sesi yumuşak bir şekilde kapatır (150ms fadeout)."""
        if self._channel.get_busy():
            self._channel.fadeout(150)
        self._current_file = None
        self._current_sound = None

    def trigger_start(self):
        """Ses başlamadan önce çağrılır (opsiyonel hook)."""
        pass

    def trigger_end(self):
        """Ses bittikten sonra çağrılır (opsiyonel hook)."""
        pass
