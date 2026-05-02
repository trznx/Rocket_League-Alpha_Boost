import re

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Add audio.update_speed(estimated_speed) when should_play is true
pattern = r"""            # --- FİZİK VE DİNAMİK SES YÖNETİMİ ---
            if should_play:
                estimated_speed \+= ACCELERATION \* dt
                if estimated_speed > MAX_SPEED:
                    estimated_speed = MAX_SPEED"""

replacement = """            # --- FİZİK VE DİNAMİK SES YÖNETİMİ ---
            if should_play:
                estimated_speed += ACCELERATION * dt
                if estimated_speed > MAX_SPEED:
                    estimated_speed = MAX_SPEED
                audio.update_speed(estimated_speed)"""

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
