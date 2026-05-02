import wave
import numpy as np
import os
import scipy.signal

source_wav = os.path.join("_archive", "sources", "AlphaBoostSound.wav")

with wave.open(source_wav, 'rb') as w:
    sr = w.getframerate()
    n_channels = w.getnchannels()
    sampwidth = w.getsampwidth()
    frames = w.readframes(w.getnframes())

dtype = np.int16
audio = np.frombuffer(frames, dtype=dtype).reshape(-1, n_channels)

# Maksimum volume (Normalize)
audio_float = audio.astype(np.float32)
max_amp = np.max(np.abs(audio_float))
if max_amp > 0:
    audio = (audio_float * (32767.0 / max_amp)).astype(np.int16)

# 1. ÇUFF KISMINI AL (0.0s - 0.597s)
# Bu kısım orijinal patlamanın tamamını içerir, asla bozulmaz veya yavaşlatılmaz.
chuff_end_idx = int(0.597 * sr)
chuff_audio = audio[:chuff_end_idx].copy().astype(np.float32)

# BİTİŞ KISMINI AL (TAIL/RÜZGAR) - Gerek kalmadı ama bulunsun
end_frames = int(0.6 * sr)
end_audio = audio[-end_frames:].copy().astype(np.float32)
fade_in = np.linspace(0.0, 1.0, int(0.1*sr)).reshape(-1, 1)
end_audio[:int(0.1*sr)] = end_audio[:int(0.1*sr)] * fade_in
with wave.open(os.path.join("assets", "sounds", "boost_end.wav"), 'wb') as w:
    w.setnchannels(n_channels)
    w.setsampwidth(sampwidth)
    w.setframerate(sr)
    w.writeframes(np.clip(end_audio, -32767, 32767).astype(dtype).tobytes())

# 2. DÖNGÜ (LOOP) KESİTİ (0.597s - 2.6s)
# Uzun kesit (2 saniye) çok daha doğal bir motor uğultusu sağlar.
loop_start_idx = int(0.597 * sr)
loop_end_idx = int(2.6 * sr)
core_chunk_orig = audio[loop_start_idx:loop_end_idx].copy().astype(np.float32)

# YENİ DÜŞÜK DEVİR (LOW-RPM) EĞRİSİ
# Level 1 (Hız=0): %65 devir (Derin homurtu)
# Level 8 (Son Hız): %100 devir (Orijinal çığlık)
speed_factors = {
    1: 0.65,
    2: 0.70,
    3: 0.75,
    4: 0.80,
    5: 0.85,
    6: 0.90,
    7: 0.95,
    8: 1.00
}

merge_fade_sec = 0.010 # Çuff ile Loop birleşiminde patlamayı önleyen 10ms crossfade
merge_fade_len = int(merge_fade_sec * sr)

print("Mükemmel Low-RPM (Düşük Devir) Motor Sesleri üretiliyor...")

for level in range(1, 9):
    speed_factor = speed_factors[level]
    num_samples = int(len(core_chunk_orig) / speed_factor)
    
    # Döngü kesitini yavaşlat (Pitch-Down)
    if speed_factor == 1.0:
        core_chunk = core_chunk_orig
    else:
        if n_channels == 2:
            left = scipy.signal.resample(core_chunk_orig[:, 0], num_samples)
            right = scipy.signal.resample(core_chunk_orig[:, 1], num_samples)
            core_chunk = np.column_stack((left, right)).astype(np.float32)
        else:
            core_chunk = scipy.signal.resample(core_chunk_orig[:, 0], num_samples).reshape(-1, 1).astype(np.float32)
            
    chunk_len = len(core_chunk)
    # Loop için crossfade süresi
    crossfade_sec = 0.2
    fade_len = int(crossfade_sec * sr)
    
    if fade_len > chunk_len // 2:
        fade_len = chunk_len // 2
        
    fade_in_arr = np.linspace(0.0, 1.0, fade_len).reshape(-1, 1)
    fade_out_arr = np.linspace(1.0, 0.0, fade_len).reshape(-1, 1)

    target_len = int(40 * sr)
    out_audio = np.zeros((target_len, n_channels), dtype=np.float32)
    out_audio[0:chunk_len] = core_chunk
    current_pos = chunk_len - fade_len

    # Döngüyü 40 saniyeye uzat
    while current_pos + chunk_len < target_len:
        out_audio[current_pos:current_pos+fade_len] = out_audio[current_pos:current_pos+fade_len] * fade_out_arr + core_chunk[:fade_len] * fade_in_arr
        out_audio[current_pos+fade_len:current_pos+chunk_len] = core_chunk[fade_len:]
        current_pos += (chunk_len - fade_len)

    # 3. ÇUFF İLE YENİ PITCH-DOWN DÖNGÜYÜ KAYNAŞTIR
    v2_target_len = len(chuff_audio) + len(out_audio) - merge_fade_len
    v2_audio = np.zeros((v2_target_len, n_channels), dtype=np.float32)

    merge_fade_in = np.linspace(0.0, 1.0, merge_fade_len).reshape(-1, 1)
    merge_fade_out = np.linspace(1.0, 0.0, merge_fade_len).reshape(-1, 1)

    v2_audio[:len(chuff_audio)] = chuff_audio

    curr_p = len(chuff_audio) - merge_fade_len
    v2_audio[curr_p:curr_p+merge_fade_len] = (
        v2_audio[curr_p:curr_p+merge_fade_len] * merge_fade_out + 
        out_audio[:merge_fade_len] * merge_fade_in
    )
    v2_audio[curr_p+merge_fade_len:] = out_audio[merge_fade_len:]

    v2_audio = np.clip(v2_audio, -32767, 32767).astype(dtype)

    file_name = "full_boost.wav" if level == 1 else f"level_{level}.wav"
    with wave.open(os.path.join("assets", "sounds", file_name), 'wb') as w:
        w.setnchannels(n_channels)
        w.setsampwidth(sampwidth)
        w.setframerate(sr)
        w.writeframes(v2_audio.tobytes())
        
    print(f"  - {file_name} üretildi. (Hız: {speed_factor}x)")

print("Tüm devir sesleri orijinal geniş döngü ile başarıyla tamamlandı!")
