"""
Alpha Boost - Ses Hazırlama Aracı v2
=====================================
a_audio.wav dosyasından (gerçek oyun kaydı) mid_loop.wav çıkarır.

NEDEN a_audio.wav?
  - AlphaBoostSound.wav sürekli ivmelenen bir sestir (AGENTS.md uyarısı)
  - ZCR=0.130 ile supersonic hızdaki ses frekansına sahiptir
  - a_audio.wav'ın 11-15s bölgesi ise gerçek, sabit, supersonic OLMAYAN boost sesidir
  - ZCR=0.050-0.070 ile doğal boost frekansına sahiptir

UYARI: a_audio.wav'da motor sesi ve stadyum ambiyansı karışıktır.
  Bu kaçınılmazdır çünkü izole, non-supersonic bir Alpha Boost kaynağımız yoktur.
  Ancak oyun içinde zaten bu sesler mevcut olduğundan, karışıklık farkedilmeyecektir.

YASAK: moviepy, scipy, pydub. Sadece wave + numpy.
YASAK: float32 dtype karışıklığı. Kaynak 16-bit PCM, çıkış da öyle.
"""

import wave
import numpy as np
import os

def extract_mid_loop():
    """a_audio.wav'dan sabit (non-supersonic) mid-loop bölgesini çıkarır."""
    
    SOURCE = "a_audio.wav"
    OUTPUT = "mid_loop.wav"
    
    if not os.path.exists(SOURCE):
        print("HATA: %s bulunamadi!" % SOURCE)
        return False
    
    # Kaynak dosyayı oku
    with wave.open(SOURCE, 'rb') as w:
        sr = w.getframerate()
        n_channels = w.getnchannels()
        sampwidth = w.getsampwidth()
        n_frames = w.getnframes()
        raw_frames = w.readframes(n_frames)
    
    print("Kaynak: %s" % SOURCE)
    print("  Sample Rate: %d Hz" % sr)
    print("  Channels: %d" % n_channels)
    print("  Sample Width: %d bytes" % sampwidth)
    print("  Toplam Sure: %.3fs" % (n_frames/sr))
    
    # dtype belirleme
    if sampwidth == 2:
        dtype = np.int16
    elif sampwidth == 4:
        dtype = np.int32
    else:
        print("HATA: Desteklenmeyen sample width: %d" % sampwidth)
        return False
    
    audio = np.frombuffer(raw_frames, dtype=dtype).reshape(-1, n_channels)
    
    # Mid-loop bölgesi: 11.5s - 15.0s
    # Bu bölge analiz sonuçlarına göre:
    #   - ZCR: 0.050-0.075 (supersonic DEĞİL, AlphaBoost'un 0.130'una karşı)
    #   - RMS: 310-345 (sabit enerji)
    #   - Std: düşük (kararlı ses)
    LOOP_START = 11.5
    LOOP_END = 15.0
    
    start_frame = int(LOOP_START * sr)
    end_frame = int(LOOP_END * sr)
    
    loop_segment = audio[start_frame:end_frame]
    
    # Sıfır geçiş noktalarında kes (tıklama/pop önleme)
    mono_start = loop_segment[:1000, 0].astype(np.float64)
    zero_crossings_start = np.where(np.diff(np.sign(mono_start)) != 0)[0]
    if len(zero_crossings_start) > 0:
        trim_start = zero_crossings_start[0]
        loop_segment = loop_segment[trim_start:]
    
    mono_end = loop_segment[-1000:, 0].astype(np.float64)
    zero_crossings_end = np.where(np.diff(np.sign(mono_end)) != 0)[0]
    if len(zero_crossings_end) > 0:
        trim_end = zero_crossings_end[-1] - len(mono_end)
        if trim_end < 0:
            loop_segment = loop_segment[:trim_end]
    
    # Volume normalizasyonu: a_audio.wav daha düşük enerjili
    # RMS ~330 -> hedef RMS ~800 (AlphaBoostSound.wav ile eşleşsin)
    current_rms = np.sqrt(np.mean(loop_segment.astype(np.float64)**2))
    target_rms = 800.0
    gain = target_rms / current_rms
    
    # Gain uygula (clipping kontrolü ile)
    normalized = (loop_segment.astype(np.float64) * gain)
    max_val = np.abs(normalized).max()
    if max_val > 32000:  # int16 limitine yaklaşırsa ölçekle
        normalized = normalized * (32000 / max_val)
    loop_segment = normalized.astype(dtype)
    
    duration = len(loop_segment) / sr
    final_rms = np.sqrt(np.mean(loop_segment.astype(np.float64)**2))
    
    print()
    print("Mid-Loop segment:")
    print("  Bolge: %.1fs - %.1fs" % (LOOP_START, LOOP_END))
    print("  Gercek Sure: %.3fs" % duration)
    print("  Frame Sayisi: %d" % len(loop_segment))
    print("  Orijinal RMS: %.1f -> Normalize RMS: %.1f" % (current_rms, final_rms))
    print("  Gain: %.2fx" % gain)
    
    # Kaydet
    with wave.open(OUTPUT, 'wb') as w:
        w.setnchannels(n_channels)
        w.setsampwidth(sampwidth)
        w.setframerate(sr)
        w.writeframes(loop_segment.astype(dtype).tobytes())
    
    # Doğrulama
    with wave.open(OUTPUT, 'rb') as w:
        verify_frames = w.getnframes()
        verify_dur = verify_frames / w.getframerate()
    
    print()
    print("%s basariyla olusturuldu!" % OUTPUT)
    print("  Dogrulama - Sure: %.3fs" % verify_dur)
    print("  Dosya Boyutu: %.1f KB" % (os.path.getsize(OUTPUT) / 1024))
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("  ALPHA BOOST - SES HAZIRLAMA ARACI v2")
    print("  Kaynak: a_audio.wav (gercek oyun kaydı)")
    print("=" * 50)
    
    success = extract_mid_loop()
    
    if success:
        print("\nHazirlik tamamlandi! Artik main.py calistirabilirsiniz.")
    else:
        print("\nHATA: Ses hazirlama basarisiz!")
