import wave
import numpy as np
import os

source_wav = os.path.join("_archive", "sources", "AlphaBoostSound.wav")
output_wav = os.path.join("assets", "sounds", "full_boost_new.wav")

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

    # Çok daha UZUN bir parça alarak "helikopter/dalgalanma" efektini azaltacağız
    # Eski kod sadece 0.3 saniye alıyordu, biz 2 saniye alacağız!
    start_idx = int(0.6 * sr)
    end_idx = int(2.6 * sr)
    core_chunk = audio[start_idx:end_idx].copy().astype(np.float32)
    chunk_len = len(core_chunk)

    crossfade_sec = 0.2
    fade_len = int(crossfade_sec * sr)

    fade_in = np.linspace(0.0, 1.0, fade_len).reshape(-1, 1)
    fade_out = np.linspace(1.0, 0.0, fade_len).reshape(-1, 1)

    target_len = int(42 * sr)
    out_audio = np.zeros((target_len, n_channels), dtype=np.float32)

    current_pos = 0
    # İlk parçayı yerleştir
    out_audio[0:chunk_len] = core_chunk
    current_pos = chunk_len - fade_len

    while current_pos + chunk_len < target_len:
        # Crossfade bölgesi
        out_audio[current_pos:current_pos+fade_len] = out_audio[current_pos:current_pos+fade_len] * fade_out + core_chunk[:fade_len] * fade_in
        # Geri kalan
        out_audio[current_pos+fade_len:current_pos+chunk_len] = core_chunk[fade_len:]
        current_pos += (chunk_len - fade_len)

    # Normalize et
    max_val = np.max(np.abs(out_audio))
    if max_val > 0:
        orig_max = np.max(np.abs(audio))
        out_audio = out_audio * (orig_max / max_val)

    with wave.open(output_wav, 'wb') as w:
        w.setnchannels(n_channels)
        w.setsampwidth(sampwidth)
        w.setframerate(sr)
        w.writeframes(out_audio.astype(dtype).tobytes())

    print(f"Başarıyla {output_wav} oluşturuldu! Dalgalanma azaltıldı.")
else:
    print(f"Dosya bulunamadı: {source_wav}")
