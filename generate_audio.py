import os
import subprocess
import math

base_file = "assets/sounds/full_boost.wav"
out_dir = "assets/sounds/quiet_loop_2"

os.makedirs(out_dir, exist_ok=True)

# Generate 12 levels
for i in range(1, 13):
    v = (i - 1) / 11.0 * 2300.0
    
    # Pitch shift formula: P = 611/2300 * v (in cents)
    cents = (611.0 / 2300.0) * v
    
    # Multiplier: 2^(cents / 1200)
    multiplier = math.pow(2.0, cents / 1200.0)
    
    new_rate = int(44100 * multiplier)
    out_file = os.path.join(out_dir, f"level_{i}.wav")
    
    # ffmpeg command
    cmd = [
        "ffmpeg", "-y",
        "-i", base_file,
        "-filter:a", f"asetrate={new_rate},aresample=44100",
        "-t", "10",
        out_file
    ]
    print(f"Generating Level {i} with v={v:.1f}, multiplier={multiplier:.3f}")
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print("Finished generating 12 audio levels.")
