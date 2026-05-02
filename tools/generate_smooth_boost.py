import wave
import numpy as np
import os
import random

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

    # Orijinal loop noktaları
    loop_start = int(0.597 * sr)
    loop_end = int(0.971 * sr)
    
    # Sadece döngü alınacak alanı kestiğimiz parça
    core_audio = audio[loop_start:loop_end].copy()
    
    # "Granular Synthesis" mantığı: Sesin içinden rastgele küçük parçalar (granüller) alıp
    # üst üste bindirerek "wobble/dalgalanma" periyodunu tamamen yok edeceğiz.
    
    grain_size = int(0.05 * sr) # 50 milisaniye parçalar
    overlap = int(0.02 * sr)    # 20 milisaniye üst üste binme
    
    # Çıktı için boş bir buffer (42 saniye)
    target_duration = int(42.0 * sr)
    output_audio = np.zeros((target_duration, n_channels), dtype=np.float32)
    
    current_pos = 0
    core_len = len(core_audio)
    
    # Çapraz geçiş (Crossfade) penceresi oluştur
    fade_in = np.linspace(0.0, 1.0, overlap).reshape(-1, 1)
    fade_out = np.linspace(1.0, 0.0, overlap).reshape(-1, 1)
    
    while current_pos < target_duration - grain_size:
        # Core audio içinden rastgele bir başlangıç noktası seç
        start_idx = random.randint(0, core_len - grain_size - 1)
        grain = core_audio[start_idx : start_idx + grain_size].astype(np.float32)
        
        # Eğer bu ilk parça değilse, başına fade_in uygula
        if current_pos > 0:
            grain[:overlap] *= fade_in
            
        # Sonuna fade_out uygula (Bir sonraki parça buraya binecek)
        grain[-overlap:] *= fade_out
        
        # Granülü output buffer'a ekle
        end_pos = current_pos + grain_size
        
        # Buffer taşmasını önle
        if end_pos > target_duration:
            break
            
        output_audio[current_pos : end_pos] += grain
        
        # Bir sonraki parçayı overlap kadar geri çekerek yerleştir ki boşluk kalmasın
        current_pos += (grain_size - overlap)
        
    # Sesi normalize et (Çok fazla üst üste binmeden dolayı patlamaması için)
    max_val = np.max(np.abs(output_audio))
    if max_val > 0:
        # Orijinal sesin genliğini koru
        orig_max = np.max(np.abs(core_audio))
        output_audio = output_audio * (orig_max / max_val)

    # Int16/Int32 formatına geri çevir
    output_audio = output_audio.astype(dtype)

    with wave.open(output_wav, 'wb') as w:
        w.setnchannels(n_channels)
        w.setsampwidth(sampwidth)
        w.setframerate(sr)
        w.writeframes(output_audio.tobytes())
        
    print(f"Başarıyla {output_wav} oluşturuldu! Dalgalanma giderildi.")
else:
    print(f"Dosya bulunamadı: {source_wav}")
