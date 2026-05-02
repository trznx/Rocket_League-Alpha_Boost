import re

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update on_click to be pure O(1)
old_click = """def on_click(x, y, button, pressed):
    global is_mouse_down, mouse_down_time
    if button == mouse.Button.left:
        # Sadece oyun aktifken çalışsın
        if not is_rl_active():
            return
            
        is_mouse_down = pressed
        if pressed:
            mouse_down_time = time.time()"""

new_click = """def on_click(x, y, button, pressed):
    global is_mouse_down, mouse_down_time
    # Pynput callback MUST be as fast as possible to avoid input lag.
    if button == mouse.Button.left:
        is_mouse_down = pressed
        if pressed:
            mouse_down_time = time.time()"""
content = content.replace(old_click, new_click)

# 2. Add cached RL active check to monitor_logic and change sleep to 0.015
old_logic_start = """def monitor_logic():
    global is_mouse_down, mouse_down_time, FREEPLAY_MODE, estimated_speed, is_sound_playing
    
    last_thresh_img = None
    last_change_time = time.time()
    last_update_time = time.time()
    is_sound_playing = False"""

new_logic_start = """def monitor_logic():
    global is_mouse_down, mouse_down_time, FREEPLAY_MODE, estimated_speed, is_sound_playing
    
    last_thresh_img = None
    last_change_time = time.time()
    last_update_time = time.time()
    last_rl_check_time = 0
    cached_rl_active = False
    is_sound_playing = False"""
content = content.replace(old_logic_start, new_logic_start)

# Add logic check
old_sleep = "time.sleep(0.005) # Saniyede ~200 kez kontrol"
new_sleep = """            # Check if RL is active only twice a second to save CPU
            if current_time - last_rl_check_time > 0.5:
                cached_rl_active = is_rl_active()
                last_rl_check_time = current_time
                
            time.sleep(0.015) # ~66 FPS - ultra optimized"""
content = content.replace(old_sleep, new_sleep)

# Check cached_rl_active instead
old_should_play = """            if not IS_ACTIVE:
                should_play = False
            elif is_cursor_visible():
                should_play = False
            elif is_mouse_down and not currently_empty:"""
new_should_play = """            if not IS_ACTIVE or not cached_rl_active:
                should_play = False
            elif is_cursor_visible():
                should_play = False
            elif is_mouse_down and not currently_empty:"""
content = content.replace(old_should_play, new_should_play)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
