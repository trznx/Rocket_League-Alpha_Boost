import re

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

replacement1 = """# Sesleri ve Kanalı Yükle
s_level1 = pygame.mixer.Sound("full_boost.wav")
s_level2 = pygame.mixer.Sound("full_boost_mid1.wav")
s_level3 = pygame.mixer.Sound("full_boost_mid2.wav")
s_level4 = pygame.mixer.Sound("full_boost_high.wav")

# Ses Seviyelerini Uygula
s_level1.set_volume(SES_SEVIYESI)
s_level2.set_volume(SES_SEVIYESI)
s_level3.set_volume(SES_SEVIYESI)
s_level4.set_volume(SES_SEVIYESI)

# --- FİZİK VE DURUM DEĞİŞKENLERİ ---"""

content = re.sub(r"# Sesleri ve Kanalı Yükle.*?# --- FİZİK VE DURUM DEĞİŞKENLERİ ---", replacement1, content, flags=re.DOTALL)

replacement2 = """def play_sound_from_start():
    ch = pygame.mixer.find_channel()
    if ch:
        # Kademeli Hız Kontrolü (4 Adım - Çok Yumuşak Geçiş)
        if estimated_speed < 550:
            ch.play(s_level1)
        elif estimated_speed < 1100:
            ch.play(s_level2)
        elif estimated_speed < 1650:
            ch.play(s_level3)
        else:
            ch.play(s_level4)
        active_channels.append(ch)

def stop_sound():"""

content = re.sub(r"def play_sound_from_start\(\):.*?def stop_sound\(\):", replacement2, content, flags=re.DOTALL)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
