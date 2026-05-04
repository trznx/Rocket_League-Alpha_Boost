"""
Alpha Boost — 5-Level Ses Dosyası Üretici

Net_Alpha_Boost.wav dosyasını baz alarak, Rocket League'in gerçek fizik
değerlerine dayalı 5 farklı pitch seviyesinde ses dosyası üretir.

Formül: PitchRatio = 1.0 + (v / 2300 * 0.42)
Her Level, belirli bir hız aralığının MERKEZ hızı üzerinden hesaplanır.
"""

import os
import subprocess
import math

# ─── KAYNAK DOSYA ─────────────────────────────────────────────────────────────
BASE_FILE = os.path.join("assets", "sounds", "alpha_boost", "Net_Alpha_Boost.wav")
OUT_DIR   = os.path.join("assets", "sounds", "alpha_boost")

os.makedirs(OUT_DIR, exist_ok=True)

# ─── 5-LEVEL TANIMLAMALARI ───────────────────────────────────────────────────
# Her tuple: (level_no, hız_aralığı_alt, hız_aralığı_üst, açıklama)
LEVELS = [
    (1,    0,  460, "Düşük hız / Rölanti"),
    (2,  461,  920, "Hızlanma başlangıcı"),
    (3,  921, 1380, "Orta hız yırtılması"),
    (4, 1381, 1840, "Yüksek hız tınısı"),
    (5, 1841, 2300, "Supersonic / Limit"),
]

ORIGINAL_SAMPLE_RATE = 44100
MAX_SPEED = 2300.0
MAX_PITCH_SHIFT = 0.42  # Maksimum pitch artışı (1.0x -> 1.42x)

print("=" * 60)
print("  Alpha Boost — 5-Level Ses Üretici")
print(f"  Kaynak: {BASE_FILE}")
print(f"  Formül: PitchRatio = 1.0 + (v / {MAX_SPEED} × {MAX_PITCH_SHIFT})")
print("=" * 60)

for level_no, v_min, v_max, desc in LEVELS:
    # Merkez hızı hesapla
    v_center = (v_min + v_max) / 2.0
    
    # Pitch formülü: PitchRatio = 1.0 + (v / 2300 * 0.42)
    pitch_ratio = 1.0 + (v_center / MAX_SPEED * MAX_PITCH_SHIFT)
    
    # FFmpeg'e vereceğimiz yeni sample rate
    new_rate = int(ORIGINAL_SAMPLE_RATE * pitch_ratio)
    
    out_file = os.path.join(OUT_DIR, f"level_{level_no}.wav")
    
    # FFmpeg: Önce sample rate'i değiştir (pitch shift), sonra 44100'e resample et
    cmd = [
        "ffmpeg", "-y",
        "-i", BASE_FILE,
        "-filter:a", f"asetrate={new_rate},aresample={ORIGINAL_SAMPLE_RATE}",
        "-t", "10",
        out_file
    ]
    
    print(f"\n  Level {level_no}: {desc}")
    print(f"    Hız Aralığı : {v_min:>4} - {v_max:>4} uu/s  (Merkez: {v_center:.0f})")
    print(f"    Pitch Ratio : {pitch_ratio:.4f}x")
    print(f"    Sample Rate : {ORIGINAL_SAMPLE_RATE} -> {new_rate} -> {ORIGINAL_SAMPLE_RATE}")
    print(f"    Cikti       : {out_file}")
    
    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if result.returncode == 0:
        print(f"    Durum       : BASARILI")
    else:
        print(f"    Durum       : HATA (FFmpeg returncode={result.returncode})")

print("\n" + "=" * 60)
print("  Tüm 5 level dosyası başarıyla oluşturuldu!")
print("=" * 60)
