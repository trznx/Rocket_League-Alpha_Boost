import re

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Load 8 sounds
replacement1 = """# Sesleri ve Kanalı Yükle
s_level1 = pygame.mixer.Sound("full_boost.wav")
s_level2 = pygame.mixer.Sound("level_2.wav")
s_level3 = pygame.mixer.Sound("level_3.wav")
s_level4 = pygame.mixer.Sound("level_4.wav")
s_level5 = pygame.mixer.Sound("level_5.wav")
s_level6 = pygame.mixer.Sound("level_6.wav")
s_level7 = pygame.mixer.Sound("level_7.wav")
s_level8 = pygame.mixer.Sound("level_8.wav")

# Ses Seviyelerini Uygula
s_level1.set_volume(SES_SEVIYESI)
s_level2.set_volume(SES_SEVIYESI)
s_level3.set_volume(SES_SEVIYESI)
s_level4.set_volume(SES_SEVIYESI)
s_level5.set_volume(SES_SEVIYESI)
s_level6.set_volume(SES_SEVIYESI)
s_level7.set_volume(SES_SEVIYESI)
s_level8.set_volume(SES_SEVIYESI)

# --- FİZİK VE DURUM DEĞİŞKENLERİ ---"""

content = re.sub(r"# Sesleri ve Kanalı Yükle.*?# --- FİZİK VE DURUM DEĞİŞKENLERİ ---", replacement1, content, flags=re.DOTALL)

# Update playback logic
replacement2 = """def play_sound_from_start():
    ch = pygame.mixer.find_channel()
    if ch:
        # Kademeli Hız Kontrolü (8 Adım - Ultra Yumuşak Geçiş)
        if estimated_speed < 275:
            ch.play(s_level1)
        elif estimated_speed < 550:
            ch.play(s_level2)
        elif estimated_speed < 825:
            ch.play(s_level3)
        elif estimated_speed < 1100:
            ch.play(s_level4)
        elif estimated_speed < 1375:
            ch.play(s_level5)
        elif estimated_speed < 1650:
            ch.play(s_level6)
        elif estimated_speed < 1925:
            ch.play(s_level7)
        else:
            ch.play(s_level8)
        active_channels.append(ch)

def stop_sound():"""

content = re.sub(r"def play_sound_from_start\(\):.*?def stop_sound\(\):", replacement2, content, flags=re.DOTALL)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
