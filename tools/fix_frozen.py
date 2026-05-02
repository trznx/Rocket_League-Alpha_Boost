import re

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Increase the diff_count threshold from 5 to 25 to prevent background camera pans from triggering the audio
content = content.replace("if 5 < diff_count < 800:", "if 25 < diff_count < 800:")

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
