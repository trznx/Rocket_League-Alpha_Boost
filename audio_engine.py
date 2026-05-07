"""
Alpha Boost Engine - Audio Engine
"""

import os
import sys

import pygame


class AlphaBoostAudioEngine:
    ADVANCED_RANGES = [
        (0, 500, "0_gr.wav"),
        (501, 1000, "750_gr.wav"),
        (1001, 1500, "1400_gr.wav"),
        (1501, 2000, "1700_gr.wav"),
    ]

    QUALITY_RANGES = [
        (0, 300, "gr_level_150.wav"),
        (301, 600, "gr_level_450.wav"),
        (601, 900, "gr_level_750.wav"),
        (901, 1200, "gr_level_1050.wav"),
        (1201, 1500, "gr_level_1350.wav"),
        (1501, 9999, "gr_level_1650.wav"),
    ]

    NORMAL_FILE = "Classic.wav"

    def __init__(self, channels=8):
        pygame.mixer.pre_init(48000, -16, 2, 512)
        pygame.mixer.init()
        pygame.mixer.set_num_channels(channels)

        self._channel = pygame.mixer.Channel(0)
        self._profile = "advanced"
        self._master_volume = 0.1
        self._current_sound = None
        self._current_file = None

        self._advanced_sounds = {}
        self._quality_sounds = {}
        self._normal_sound = None

        self._load_all_sounds()

    def _get_base_path(self):
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, "assets", "sounds")
        return os.path.join("assets", "sounds")

    def _get_advanced_path(self, filename):
        return os.path.join(self._get_base_path(), "alpha_boost_advanced", filename)

    def _get_quality_path(self, filename):
        return os.path.join(self._get_base_path(), "alpha_boost_quality", filename)

    def _get_normal_path(self, filename):
        return os.path.join(self._get_base_path(), "alpha_boost_normal", filename)

    def _load_all_sounds(self):
        for _, _, filename in self.ADVANCED_RANGES:
            path = self._get_advanced_path(filename)
            try:
                self._advanced_sounds[filename] = pygame.mixer.Sound(path)
            except Exception as exc:
                print(f"  [AudioEngine ERROR] {filename} could not be loaded: {exc}")

        for _, _, filename in self.QUALITY_RANGES:
            path = self._get_quality_path(filename)
            try:
                self._quality_sounds[filename] = pygame.mixer.Sound(path)
            except Exception as exc:
                print(f"  [AudioEngine ERROR] {filename} could not be loaded: {exc}")

        path = self._get_normal_path(self.NORMAL_FILE)
        try:
            self._normal_sound = pygame.mixer.Sound(path)
        except Exception as exc:
            print(f"  [AudioEngine ERROR] {self.NORMAL_FILE} could not be loaded: {exc}")

        advanced_count = len(self._advanced_sounds)
        quality_count = len(self._quality_sounds)
        normal_status = "OK" if self._normal_sound else "ERROR"
        print(
            f"  [AudioEngine] Sounds loaded - Advanced: {advanced_count}, "
            f"Quality: {quality_count}, Normal: {normal_status}"
        )

    def set_profile(self, profile_name):
        profile_name = profile_name.lower()
        if profile_name not in ("advanced", "quality", "normal"):
            return

        if profile_name != self._profile:
            self.stop_loop()
            self._profile = profile_name
            self._current_sound = None
            self._current_file = None
            print(f"  [AudioEngine] Profile changed: {profile_name}")

    def get_profile(self):
        return self._profile

    def set_volume(self, volume):
        self._master_volume = max(0.0, min(1.0, volume))
        if self._channel.get_busy():
            self._channel.set_volume(self._master_volume)

    def _get_sound_for_speed(self, speed, ranges, sound_bank):
        for v_min, v_max, filename in ranges:
            if v_min <= speed <= v_max:
                return filename, sound_bank.get(filename)

        last_file = ranges[-1][2]
        return last_file, sound_bank.get(last_file)

    def play_loop(self, speed=0.0):
        if self._profile == "normal":
            target_file = self.NORMAL_FILE
            target_sound = self._normal_sound
        elif self._profile == "quality":
            target_file, target_sound = self._get_sound_for_speed(
                speed, self.QUALITY_RANGES, self._quality_sounds
            )
        else:
            target_file, target_sound = self._get_sound_for_speed(
                speed, self.ADVANCED_RANGES, self._advanced_sounds
            )

        if target_sound is None:
            return

        if self._current_file == target_file and self._channel.get_busy():
            return

        self._channel.stop()
        self._channel.set_volume(self._master_volume)
        self._channel.play(target_sound, loops=-1)

        self._current_file = target_file
        self._current_sound = target_sound

    def update_speed(self, speed):
        pass

    def stop_loop(self):
        if self._channel.get_busy():
            self._channel.fadeout(360)

        self._current_file = None
        self._current_sound = None

    def trigger_start(self):
        pass

    def trigger_end(self):
        pass
