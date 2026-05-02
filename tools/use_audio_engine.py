import re

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Remove pygame imports if we want, but let's just add the import
content = content.replace("from tkinter import messagebox", "from tkinter import messagebox\nfrom audio_engine import AlphaBoostAudioEngine")

# Find the old audio initialization and remove it
old_init_start = """# --- SİSTEM BAŞLATMA ---"""
old_init_end = """        active_channels.append(ch)

def stop_sound():
    for ch in active_channels:
        if ch.get_busy():
            ch.fadeout(150)
    active_channels.clear()"""

# We'll use regex to remove the old system initialization up to stop_sound
pattern_remove_audio = r"# --- SİSTEM BAŞLATMA ---.*?active_channels\.clear\(\)"
content = re.sub(pattern_remove_audio, "# --- SES MOTORU BAŞLATMA ---\naudio = AlphaBoostAudioEngine()", content, flags=re.DOTALL)

# Now we need to update the places where audio is played/stopped and volume changed
content = content.replace("update_volumes()", "audio.set_volume(SES_SEVIYESI)")

# Update monitor_logic audio calls
content = content.replace("play_sound_from_start()", "audio.trigger_start()\n                audio.play_loop(estimated_speed)")
content = content.replace("stop_sound()", "audio.stop_loop()\n                audio.trigger_end()")

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
