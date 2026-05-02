import re

with open("audio_engine.py", "r", encoding="utf-8") as f:
    content = f.read()

# Increase channel limit
content = content.replace("channels=32", "channels=64")

# Force channel allocation to prevent 'no sound'
content = content.replace("ch = pygame.mixer.find_channel()", "ch = pygame.mixer.find_channel(force=True)")

with open("audio_engine.py", "w", encoding="utf-8") as f:
    f.write(content)
