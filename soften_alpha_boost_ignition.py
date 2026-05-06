from __future__ import annotations

import json
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfiltfilt


PROJECT_ROOT = Path(__file__).resolve().parent
AUDIO_DIR = PROJECT_ROOT / "assets" / "sounds" / "alpha_boost"
TARGET_LEVELS = [AUDIO_DIR / f"level_{i}.wav" for i in range(1, 7)]
REPORT_PATH = PROJECT_ROOT / "scratch" / "alpha_boost_ignition_soften_report.json"

IGNITION_SEC = 0.54
RECOVERY_END_SEC = 0.74
BAND_SPLIT_HZ = 4200.0
PEAK_LIMIT = 0.98

ATTACK_GAIN_DB = [-0.8, -1.0, -1.2, -1.5, -1.8, -2.0]
HIGH_BAND_GAIN = [0.90, 0.86, 0.82, 0.78, 0.74, 0.70]


def load_wav(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path), "rb") as wav_file:
        sample_rate = wav_file.getframerate()
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        if sample_width != 2:
            raise ValueError(f"Only 16-bit PCM WAV supported, got sample width {sample_width}")
        frames = wav_file.readframes(wav_file.getnframes())

    audio = np.frombuffer(frames, dtype=np.int16).reshape(-1, channels).astype(np.float32)
    audio /= 32768.0
    return audio, sample_rate


def save_wav(path: Path, audio: np.ndarray, sample_rate: int) -> None:
    clipped = np.clip(audio, -1.0, 1.0)
    pcm = np.round(clipped * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(pcm.shape[1])
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm.tobytes())


def db_to_amp(gain_db: float) -> float:
    return float(10.0 ** (gain_db / 20.0))


def design_lowpass(sample_rate: int, cutoff_hz: float):
    return butter(4, cutoff_hz, btype="low", fs=sample_rate, output="sos")


def make_attack_envelope(length: int, sample_rate: int, attack_gain_db: float) -> np.ndarray:
    attack_frames = max(1, int(round(0.08 * sample_rate)))
    release_frames = max(1, int(round(0.34 * sample_rate)))

    envelope = np.ones(length, dtype=np.float32)
    attack_amp = db_to_amp(attack_gain_db)

    attack_end = min(length, attack_frames)
    envelope[:attack_end] = np.linspace(attack_amp, attack_amp * 0.92, attack_end, dtype=np.float32)

    release_start = attack_end
    release_end = min(length, release_start + release_frames)
    if release_end > release_start:
        envelope[release_start:release_end] = np.linspace(
            envelope[release_start - 1],
            1.0,
            release_end - release_start,
            dtype=np.float32,
        )
    if release_end < length:
        envelope[release_end:] = 1.0

    return envelope.reshape(-1, 1)


def soften_ignition(audio: np.ndarray, sample_rate: int, level_index: int) -> tuple[np.ndarray, dict]:
    ignition_frames = min(len(audio), int(round(IGNITION_SEC * sample_rate)))
    recovery_end = min(len(audio), int(round(RECOVERY_END_SEC * sample_rate)))
    if ignition_frames <= 0 or recovery_end <= ignition_frames:
        return audio.copy(), {"ignition_frames": ignition_frames, "recovery_end": recovery_end}

    lowpass_sos = design_lowpass(sample_rate, BAND_SPLIT_HZ)

    ignition = audio[:ignition_frames].copy()
    ignition_mono = ignition.mean(axis=1)
    target_rms = float(np.sqrt(np.mean(ignition_mono**2)))
    target_peak = float(np.max(np.abs(ignition)))
    low_band = sosfiltfilt(lowpass_sos, ignition, axis=0).astype(np.float32)
    high_band = ignition - low_band
    treated = low_band + (high_band * HIGH_BAND_GAIN[level_index])
    treated *= make_attack_envelope(len(treated), sample_rate, ATTACK_GAIN_DB[level_index])

    treated_mono = treated.mean(axis=1)
    treated_rms = float(np.sqrt(np.mean(treated_mono**2)))
    if treated_rms > 1e-9 and target_rms > 1e-9:
        treated *= target_rms / treated_rms

    output = audio.copy()
    output[:ignition_frames] = treated

    # Blend back into the untouched body to avoid a seam.
    blend_length = recovery_end - ignition_frames
    fade = np.linspace(0.0, 1.0, blend_length, endpoint=False, dtype=np.float32).reshape(-1, 1)
    blend_original = audio[ignition_frames:recovery_end]
    blend_low = sosfiltfilt(lowpass_sos, blend_original, axis=0).astype(np.float32)
    blend_high = blend_original - blend_low
    blend_treated = blend_low + (blend_high * HIGH_BAND_GAIN[level_index])
    output[ignition_frames:recovery_end] = blend_treated * (1.0 - fade) + blend_original * fade

    current_peak = float(np.max(np.abs(output[:ignition_frames])))
    if current_peak > 1e-9 and target_peak > 1e-9:
        peak_ratio = target_peak / current_peak
        if peak_ratio < 1.0:
            output[:ignition_frames] *= peak_ratio
        elif peak_ratio > 1.03:
            output[:ignition_frames] *= min(peak_ratio, 1.12)

    peak = float(np.max(np.abs(output)))
    if peak > PEAK_LIMIT and peak > 0.0:
        output *= PEAK_LIMIT / peak

    mono_before = audio[:ignition_frames].mean(axis=1)
    mono_after = output[:ignition_frames].mean(axis=1)
    before_rms = float(np.sqrt(np.mean(mono_before**2)))
    after_rms = float(np.sqrt(np.mean(mono_after**2)))

    return output.astype(np.float32), {
        "ignition_sec": IGNITION_SEC,
        "recovery_end_sec": RECOVERY_END_SEC,
        "attack_gain_db": ATTACK_GAIN_DB[level_index],
        "high_band_gain": HIGH_BAND_GAIN[level_index],
        "target_rms": target_rms,
        "target_peak": target_peak,
        "before_rms": before_rms,
        "after_rms": after_rms,
    }


def main() -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report: dict[str, dict] = {}
    for level_index, path in enumerate(TARGET_LEVELS):
        audio, sample_rate = load_wav(path)
        softened, stats = soften_ignition(audio, sample_rate, level_index)
        save_wav(path, softened, sample_rate)
        report[path.name] = stats
        print(
            f"Softened {path.name} | attack={stats['attack_gain_db']:.1f} dB | "
            f"high_band={stats['high_band_gain']:.2f} | rms {stats['before_rms']:.4f}->{stats['after_rms']:.4f}"
        )

    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Report written to {REPORT_PATH}")


if __name__ == "__main__":
    main()
