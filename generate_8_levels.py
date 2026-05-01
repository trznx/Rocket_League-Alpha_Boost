import wave
import numpy as np
from scipy.signal import resample_poly
import os

def generate_speed(input_file, output_file, up, down):
    with wave.open(input_file, "rb") as w:
        n_channels = w.getnchannels()
        sampwidth = w.getsampwidth()
        sr = w.getframerate()
        frames = w.readframes(w.getnframes())

    dtype = np.int16 if sampwidth == 2 else np.int32
    audio = np.frombuffer(frames, dtype=dtype)
    
    if n_channels > 1:
        audio = audio.reshape(-1, n_channels)
    else:
        audio = audio.reshape(-1, 1)

    resampled = resample_poly(audio, up, down, axis=0).astype(dtype)

    with wave.open(output_file, "wb") as w:
        w.setnchannels(n_channels)
        w.setsampwidth(sampwidth)
        w.setframerate(sr)
        w.writeframes(resampled.tobytes())
    
    speed = down / up
    print(f"{output_file} başarıyla üretildi! (Hız: {speed:.3f}x)")

def main():
    if not os.path.exists("full_boost.wav"):
        print("full_boost.wav bulunamadı!")
        return

    # L1: 1.000x (Orijinal, üretmeye gerek yok)
    # L2: 1.035x -> down=207, up=200
    generate_speed("full_boost.wav", "level_2.wav", 200, 207)
    # L3: 1.071x -> down=15, up=14
    generate_speed("full_boost.wav", "level_3.wav", 14, 15)
    # L4: 1.107x -> down=31, up=28
    generate_speed("full_boost.wav", "level_4.wav", 28, 31)
    # L5: 1.142x -> down=8, up=7
    generate_speed("full_boost.wav", "level_5.wav", 7, 8)
    # L6: 1.178x -> down=33, up=28
    generate_speed("full_boost.wav", "level_6.wav", 28, 33)
    # L7: 1.214x -> down=17, up=14
    generate_speed("full_boost.wav", "level_7.wav", 14, 17)
    # L8: 1.250x -> down=5, up=4
    generate_speed("full_boost.wav", "level_8.wav", 4, 5)

if __name__ == "__main__":
    main()
