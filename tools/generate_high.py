import wave
import numpy as np
from scipy.signal import resample_poly
import os

def generate():
    if not os.path.exists("full_boost.wav"):
        print("full_boost.wav bulunamadı!")
        return

    with wave.open("full_boost.wav", "rb") as w:
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

    # 1.25x hızlandırma (Pürüzsüz ve boğukluk olmadan)
    # up=4, down=5 -> 4/5 = 0.8 uzunluk -> 1.25x hız
    high_audio = resample_poly(audio, 4, 5, axis=0).astype(dtype)

    with wave.open("full_boost_high.wav", "wb") as w:
        w.setnchannels(n_channels)
        w.setsampwidth(sampwidth)
        w.setframerate(sr)
        w.writeframes(high_audio.tobytes())
        
    print("full_boost_high.wav başarıyla üretildi!")

if __name__ == "__main__":
    generate()
