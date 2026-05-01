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

    # resample
    resampled = resample_poly(audio, up, down, axis=0).astype(dtype)

    with wave.open(output_file, "wb") as w:
        w.setnchannels(n_channels)
        w.setsampwidth(sampwidth)
        w.setframerate(sr)
        w.writeframes(resampled.tobytes())
    print(f"{output_file} başarıyla üretildi! (Hız: {down/up}x)")

def main():
    if not os.path.exists("full_boost.wav"):
        print("full_boost.wav bulunamadı!")
        return

    # 1.08x -> 27 / 25
    generate_speed("full_boost.wav", "full_boost_mid1.wav", 25, 27)
    
    # 1.16x -> 29 / 25
    generate_speed("full_boost.wav", "full_boost_mid2.wav", 25, 29)
    
    # 1.25x -> 5 / 4
    generate_speed("full_boost.wav", "full_boost_high.wav", 4, 5)

if __name__ == "__main__":
    main()
