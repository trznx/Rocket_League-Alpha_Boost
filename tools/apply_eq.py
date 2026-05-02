"""
Alpha Boost - EQ Uygulama Araci
================================
Ses dosyalarinin frekans profilini orijinal Alpha Boost'a yaklastirir.

SORUN: Kaynak sesimiz 4100 Hz spectral centroid'e sahip (parlak, tiz, metalik)
       Orijinal Alpha Boost ise ~3000 Hz (sicak, derin, dogal motor sesi)

COZUM: 3 asamali dijital EQ filtresi:
  1. Mid-boost: 1000 Hz merkezli, +2dB, Q=0.8 (sesin govdesini guclendirmek)
  2. Presence-cut: 5000 Hz merkezli, -4dB, Q=1.0 (metalik tiz vızıltıyı kesmek)
  3. Brilliance-cut: 8500 Hz merkezli, -2dB, Q=0.7 (ince parlakliği azaltmak)

SONUC: Centroid 4103 -> ~3000 Hz (orijinale esit)

Kullanim: python tools/apply_eq.py
"""

import wave
import numpy as np
from scipy.signal import sosfiltfilt
import os
import shutil

# ============================================================
# EQ PARAMETRELERI (Z6 konfigurasyonu - test ile optimize edildi)
# ============================================================
EQ_CONFIG = {
    "mid_boost": {"freq": 1000, "gain_db": 2.0, "Q": 0.8},
    "presence_cut": {"freq": 5000, "gain_db": -4.0, "Q": 1.0},
    "brilliance_cut": {"freq": 8500, "gain_db": -2.0, "Q": 0.7},
}

# Islenecek dosyalar
SOUND_DIR = os.path.join("assets", "sounds")
BACKUP_DIR = os.path.join("_archive", "sounds_backup")

SOUND_FILES = [
    "full_boost.wav",
    "level_2.wav",
    "level_3.wav",
    "level_4.wav",
    "level_5.wav",
    "level_6.wav",
    "level_7.wav",
    "level_8.wav",
    "boost_start.wav",
    "boost_end.wav",
]


def peaking_eq_sos(f0, gain_db, Q, fs):
    """Audio EQ Cookbook - Peaking EQ biquad filtresi (SOS formati)"""
    A = 10 ** (gain_db / 40.0)
    w0 = 2 * np.pi * f0 / fs
    alpha = np.sin(w0) / (2 * Q)
    
    b0 = 1 + alpha * A
    b1 = -2 * np.cos(w0)
    b2 = 1 - alpha * A
    a0 = 1 + alpha / A
    a1 = -2 * np.cos(w0)
    a2 = 1 - alpha / A
    
    # SOS formati: [b0, b1, b2, a0, a1, a2] (a0 normalize edilmis)
    return np.array([[b0/a0, b1/a0, b2/a0, 1.0, a1/a0, a2/a0]])


def spectral_centroid(mono, fs):
    """Sesin frekans agirlik merkezini hesaplar"""
    fft = np.abs(np.fft.rfft(mono))
    freqs = np.fft.rfftfreq(len(mono), 1/fs)
    return np.sum(freqs * fft) / (np.sum(fft) + 1e-10)


def band_energy(mono, fs, f_low, f_high):
    """Belirli bir frekans bandinin toplam enerjiye oranini hesaplar"""
    fft = np.abs(np.fft.rfft(mono))
    freqs = np.fft.rfftfreq(len(mono), 1/fs)
    total = np.sum(fft**2)
    mask = (freqs >= f_low) & (freqs < f_high)
    return 100 * np.sum(fft[mask]**2) / total


def apply_eq_to_channel(channel_data, fs):
    """Tek bir ses kanalina EQ zincirini uygular"""
    result = channel_data.copy()
    
    # 1. Mid-boost
    cfg = EQ_CONFIG["mid_boost"]
    sos = peaking_eq_sos(cfg["freq"], cfg["gain_db"], cfg["Q"], fs)
    result = sosfiltfilt(sos, result)
    
    # 2. Presence-cut
    cfg = EQ_CONFIG["presence_cut"]
    sos = peaking_eq_sos(cfg["freq"], cfg["gain_db"], cfg["Q"], fs)
    result = sosfiltfilt(sos, result)
    
    # 3. Brilliance-cut
    cfg = EQ_CONFIG["brilliance_cut"]
    sos = peaking_eq_sos(cfg["freq"], cfg["gain_db"], cfg["Q"], fs)
    result = sosfiltfilt(sos, result)
    
    return result


def process_wav_file(filepath):
    """Bir WAV dosyasina EQ uygular ve sonuclari dondurur"""
    
    # Oku
    with wave.open(filepath, 'rb') as w:
        fs = w.getframerate()
        n_channels = w.getnchannels()
        sampwidth = w.getsampwidth()
        n_frames = w.getnframes()
        raw = w.readframes(n_frames)
    
    if sampwidth == 2:
        dtype = np.int16
    elif sampwidth == 4:
        dtype = np.int32
    else:
        print("    UYARI: Desteklenmeyen sample width %d, atlaniyor" % sampwidth)
        return None, None, None
    
    audio = np.frombuffer(raw, dtype=dtype).reshape(-1, n_channels).astype(np.float64)
    
    # ONCEKI analiz (ilk 3 saniye veya tum dosya)
    analyze_len = min(len(audio), 3 * fs)
    before_centroid = spectral_centroid(audio[:analyze_len, 0], fs)
    
    # EQ uygula (her kanal icin ayri)
    processed = np.zeros_like(audio)
    for ch in range(n_channels):
        processed[:, ch] = apply_eq_to_channel(audio[:, ch], fs)
    
    # Clipping kontrolu (int16 limitleri)
    max_val = np.abs(processed).max()
    if max_val > 32000:
        scale = 32000 / max_val
        processed = processed * scale
    
    # SONRAKI analiz
    after_centroid = spectral_centroid(processed[:analyze_len, 0], fs)
    
    # Kaydet
    output_data = processed.astype(dtype)
    with wave.open(filepath, 'wb') as w:
        w.setnchannels(n_channels)
        w.setsampwidth(sampwidth)
        w.setframerate(fs)
        w.writeframes(output_data.tobytes())
    
    return before_centroid, after_centroid, len(audio) / fs


def main():
    print("=" * 60)
    print("  ALPHA BOOST - EQ UYGULAMA ARACI")
    print("  Hedef: Spectral Centroid ~3000 Hz (Original ile esit)")
    print("=" * 60)
    
    # Backup klasoru olustur
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Orijinal dosyalari yedekle
    print("\n[1/3] Orijinal dosyalar yedekleniyor...")
    for fname in SOUND_FILES:
        src = os.path.join(SOUND_DIR, fname)
        dst = os.path.join(BACKUP_DIR, fname)
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copy2(src, dst)
            print("    %s -> %s" % (fname, BACKUP_DIR))
        elif os.path.exists(dst):
            print("    %s (yedek zaten mevcut)" % fname)
        else:
            print("    UYARI: %s bulunamadi!" % src)
    
    # EQ uygula
    print("\n[2/3] EQ uygulanıyor...")
    print("  EQ Parametreleri:")
    for name, cfg in EQ_CONFIG.items():
        print("    %s: %d Hz, %+.1f dB, Q=%.1f" % (name, cfg["freq"], cfg["gain_db"], cfg["Q"]))
    print()
    
    results = []
    for fname in SOUND_FILES:
        filepath = os.path.join(SOUND_DIR, fname)
        if not os.path.exists(filepath):
            print("    UYARI: %s bulunamadi, atlaniyor" % filepath)
            continue
        
        before, after, duration = process_wav_file(filepath)
        if before is not None:
            results.append((fname, before, after, duration))
            print("    %s (%.1fs): Centroid %.0f -> %.0f Hz" % (fname, duration, before, after))
    
    # Dogrulama
    print("\n[3/3] Dogrulama...")
    print("  %-20s  %8s  %8s  %8s" % ("Dosya", "Onceki", "Sonraki", "Hedef"))
    print("  " + "-" * 50)
    
    all_ok = True
    for fname, before, after, dur in results:
        diff = abs(after - 3000)
        status = "OK" if diff < 500 else "DIKKAT"
        if diff >= 500:
            all_ok = False
        print("  %-20s  %6.0f Hz  %6.0f Hz  ~3000 Hz  %s" % (fname, before, after, status))
    
    print()
    if all_ok:
        print("  TAMAMLANDI! Tum dosyalar basariyla islendi.")
        print("  Yedekler: %s" % BACKUP_DIR)
    else:
        print("  UYARI: Bazi dosyalar hedeften uzak. Manuel kontrol oneriliyor.")
    
    print()
    print("  Geri donmek icin: %s klasorundeki dosyalari %s'e kopyalayin." % (BACKUP_DIR, SOUND_DIR))


if __name__ == "__main__":
    main()
