import wave
import numpy as np
import os

source_wav = os.path.join("_archive", "sources", "AlphaBoostSound.wav")
start_wav = os.path.join("assets", "sounds", "boost_start.wav")
end_wav = os.path.join("assets", "sounds", "boost_end.wav")

if os.path.exists(source_wav):
    with wave.open(source_wav, 'rb') as w:
        sr = w.getframerate()
        n_channels = w.getnchannels()
        sampwidth = w.getsampwidth()
        frames = w.readframes(w.getnframes())
        
    dtype = np.int16 if sampwidth == 2 else np.int32
    audio = np.frombuffer(frames, dtype=dtype)
    if n_channels > 1:
        audio = audio.reshape(-1, n_channels)
    else:
        audio = audio.reshape(-1, 1)

    # 1. Extract the Start (Attack) - First 0.12 seconds (the sharp "CHUFF")
    start_samples = int(0.12 * sr)
    attack_audio = audio[:start_samples].copy()
    
    # Add a tiny 10ms fade out to the attack so it doesn't pop when ending
    fade_out_samples = int(0.01 * sr)
    fade_out = np.linspace(1.0, 0.0, fade_out_samples).reshape(-1, 1)
    attack_audio[-fade_out_samples:] = attack_audio[-fade_out_samples:] * fade_out
    
    with wave.open(start_wav, 'wb') as w:
        w.setnchannels(n_channels)
        w.setsampwidth(sampwidth)
        w.setframerate(sr)
        w.writeframes(attack_audio.astype(dtype).tobytes())

    # 2. Extract the End (Tail) - We'll take the very end of the original sound, or create a synthetic tail 
    # The original AlphaBoostSound.wav has a fade out at the end. We'll grab the last 0.3 seconds.
    end_samples = int(0.3 * sr)
    tail_audio = audio[-end_samples:].copy()
    
    # Add a quick fade in to the tail so it blends perfectly
    fade_in_samples = int(0.05 * sr)
    fade_in = np.linspace(0.0, 1.0, fade_in_samples).reshape(-1, 1)
    tail_audio[:fade_in_samples] = tail_audio[:fade_in_samples] * fade_in
    
    with wave.open(end_wav, 'wb') as w:
        w.setnchannels(n_channels)
        w.setsampwidth(sampwidth)
        w.setframerate(sr)
        w.writeframes(tail_audio.astype(dtype).tobytes())
        
    print("Transients extracted successfully.")
else:
    print(f"Source file not found at {source_wav}")
