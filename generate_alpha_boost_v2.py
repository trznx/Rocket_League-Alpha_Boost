from __future__ import annotations

import argparse
import json
import math
import wave
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.signal import butter, resample_poly, sosfiltfilt


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_SOURCE = PROJECT_ROOT / "assets" / "sounds" / "alpha_boost" / "Net_Alpha_Boost.wav"
DEFAULT_XML = (
    PROJECT_ROOT
    / "_archive"
    / "sources"
    / "alpha_boost_sounds"
    / "alpha_boost_xml"
    / "SFX_Boost_Alpha.bnk.xml"
)
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "alpha_boost_v2"

MAX_SPEED = 2300.0
LEVEL_WIDTH = 200.0
TARGET_SAMPLE_RATE = 44100
TARGET_DURATION_SEC = 10.0
INTRO_DURATION_SEC = 0.65
LOOP_SEARCH_START_SEC = 0.45
LOOP_SEARCH_DURATION_SEC = 8.0
CYCLE_DURATION_SEC = 0.95
SEAM_CROSSFADE_MS = 90
INTRO_TO_LOOP_CROSSFADE_MS = 180
LFE_CUTOFF_HZ = 100.0
PEAK_LIMIT = 0.98
PITCH_MAX_SEMITONES = 3.0


@dataclass(frozen=True)
class XmlTuning:
    pitch_max_semitones: float
    lfe_max_units: float
    bus_volume_max_db: float
    loop_makeup_gain_db: float
    loop_delay_ms: int
    loop_stop_transition_ms: int
    ignition_stop_transition_ms: int


@dataclass(frozen=True)
class LevelSpec:
    level_index: int
    start_speed: int
    end_speed: int
    midpoint_speed: int
    pitch_semitones: float
    pitch_ratio: float
    lfe_units: float
    lfe_db: float
    bus_volume_db: float
    makeup_gain_db: float
    total_gain_db: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a 12-level Alpha Boost library from Net_Alpha_Boost.wav and Wwise XML hints."
    )
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--xml", type=Path, default=DEFAULT_XML)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def load_wav(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path), "rb") as wav_file:
        sample_rate = wav_file.getframerate()
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        if sample_width != 2:
            raise ValueError(f"Only 16-bit PCM WAV is supported. Got sample width {sample_width}.")
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


def resample_audio(audio: np.ndarray, source_rate: int, target_rate: int) -> np.ndarray:
    if source_rate == target_rate:
        return audio.copy()
    ratio = Fraction(target_rate, source_rate).limit_denominator(2000)
    return resample_poly(audio, ratio.numerator, ratio.denominator, axis=0).astype(np.float32)


def parse_xml_tuning(xml_path: Path) -> XmlTuning:
    root = ET.parse(xml_path).getroot()

    rtpcs: list[dict] = []
    for rtpc in root.iter("object"):
        if rtpc.attrib.get("name") != "RTPC":
            continue
        entry = {"param": None, "rtpc_id": None, "points": []}
        for child in rtpc:
            if child.tag == "field":
                name = child.attrib.get("name")
                if name == "RTPCID":
                    entry["rtpc_id"] = child.attrib.get("value")
                elif name == "ParamID":
                    entry["param"] = child.attrib.get("valuefmt")
            elif child.tag == "list" and child.attrib.get("name") == "pRTPCMgr":
                for point in child:
                    point_data = {}
                    for field in point:
                        if field.tag == "field":
                            point_data[field.attrib["name"]] = field.attrib.get("value")
                            point_data[field.attrib["name"] + "_fmt"] = field.attrib.get("valuefmt")
                    entry["points"].append(point_data)
        rtpcs.append(entry)

    def pick_rtpc(param_name: str, point_count: int, x_end: float, y_end: float) -> dict:
        for entry in rtpcs:
            if entry["param"] != param_name or len(entry["points"]) != point_count:
                continue
            last = entry["points"][-1]
            if math.isclose(float(last["From"]), x_end, rel_tol=1e-6, abs_tol=1e-6) and math.isclose(
                float(last["To"]), y_end, rel_tol=1e-6, abs_tol=1e-6
            ):
                return entry
        raise ValueError(f"Could not find RTPC {param_name} with {point_count} points ending at {x_end}->{y_end}.")

    pitch_rtpc = pick_rtpc("0x02 [Pitch]", 2, 5.0, 18.0)
    lfe_rtpc = pick_rtpc("0x01 [LFE]", 2, 2300.0, 611.0)
    bus_volume_rtpc = pick_rtpc("0x05 [BusVolume]", 2, 5.0, -0.2056717723608017)

    sound_props: dict[str, dict[str, float]] = {}
    for sound in root.iter("object"):
        if sound.attrib.get("name") != "CAkSound":
            continue
        sound_id = None
        props: dict[str, float] = {}
        for field in sound.iter("field"):
            name = field.attrib.get("name")
            if name == "ulID":
                sound_id = field.attrib.get("value")
            elif name == "pID":
                props["_last_prop_id"] = field.attrib.get("value")
                props["_last_prop_fmt"] = field.attrib.get("valuefmt", "")
            elif name == "pValue" and props.get("_last_prop_id") == "5":
                props["MakeUpGain"] = float(field.attrib.get("value"))
        if sound_id is not None:
            sound_props[sound_id] = props

    loop_action = None
    loop_stop_action = None
    ignition_stop_action = None
    for action in root.iter("object"):
        name = action.attrib.get("name")
        if name not in {"CAkActionPlay", "CAkActionStop"}:
            continue
        fields = {field.attrib.get("name"): field.attrib for field in action.iter("field")}
        target = fields.get("idExt", {}).get("value")
        delay = None
        transition = None
        for prop in action.iter("object"):
            if prop.attrib.get("name") != "AkPropBundle":
                continue
            values = {field.attrib.get("name"): field.attrib for field in prop if field.tag == "field"}
            prop_name = values.get("pID", {}).get("valuefmt", "")
            if prop_name.endswith("[DelayTime]"):
                delay = int(float(values["pValue"]["value"]))
            elif prop_name.endswith("[TransitionTime]"):
                transition = int(float(values["pValue"]["value"]))
        if name == "CAkActionPlay" and delay == 300:
            loop_action = {"target": target, "delay_ms": delay}
        elif name == "CAkActionStop" and transition == 100:
            loop_stop_action = {"target": target, "transition_ms": transition}
        elif name == "CAkActionStop" and transition == 300:
            ignition_stop_action = {"target": target, "transition_ms": transition}

    if loop_action is None or loop_stop_action is None or ignition_stop_action is None:
        raise ValueError("Could not identify loop/stop actions from the XML.")

    loop_makeup_gain = sound_props.get(loop_action["target"], {}).get("MakeUpGain", -2.0)

    return XmlTuning(
        pitch_max_semitones=float(pitch_rtpc["points"][-1]["To"]),
        lfe_max_units=float(lfe_rtpc["points"][-1]["To"]),
        bus_volume_max_db=float(bus_volume_rtpc["points"][-1]["To"]),
        loop_makeup_gain_db=loop_makeup_gain,
        loop_delay_ms=int(loop_action["delay_ms"]),
        loop_stop_transition_ms=int(loop_stop_action["transition_ms"]),
        ignition_stop_transition_ms=int(ignition_stop_action["transition_ms"]),
    )


def build_level_specs(tuning: XmlTuning) -> list[LevelSpec]:
    specs: list[LevelSpec] = []
    for level_index in range(1, 13):
        start = int((level_index - 1) * LEVEL_WIDTH)
        end = 2300 if level_index == 12 else int(level_index * LEVEL_WIDTH)
        midpoint = 2250 if level_index == 12 else start + 100
        speed_ratio = midpoint / MAX_SPEED
        pitch_semitones = PITCH_MAX_SEMITONES * speed_ratio
        pitch_ratio = 2.0 ** (pitch_semitones / 12.0)
        lfe_units = tuning.lfe_max_units * (speed_ratio ** 3)
        lfe_db = (tuning.lfe_max_units / 100.0) * (speed_ratio ** 3)
        bus_volume_db = tuning.bus_volume_max_db * speed_ratio
        makeup_gain_db = tuning.loop_makeup_gain_db
        total_gain_db = bus_volume_db + makeup_gain_db
        specs.append(
            LevelSpec(
                level_index=level_index,
                start_speed=start,
                end_speed=end,
                midpoint_speed=midpoint,
                pitch_semitones=pitch_semitones,
                pitch_ratio=pitch_ratio,
                lfe_units=lfe_units,
                lfe_db=lfe_db,
                bus_volume_db=bus_volume_db,
                makeup_gain_db=makeup_gain_db,
                total_gain_db=total_gain_db,
            )
        )
    return specs


def extract_window(audio: np.ndarray, sample_rate: int, start_sec: float, duration_sec: float) -> tuple[np.ndarray, int, int]:
    start = max(0, int(round(start_sec * sample_rate)))
    frames = max(1, int(round(duration_sec * sample_rate)))
    end = min(len(audio), start + frames)
    return audio[start:end].copy(), start, end


def pitch_shift_by_resample(audio: np.ndarray, pitch_ratio: float) -> np.ndarray:
    if math.isclose(pitch_ratio, 1.0, rel_tol=1e-9, abs_tol=1e-9):
        return audio.copy()
    ratio = Fraction(pitch_ratio).limit_denominator(1000)
    shifted = resample_poly(audio, ratio.denominator, ratio.numerator, axis=0)
    return shifted.astype(np.float32)


def find_best_cycle_offset(audio: np.ndarray, cycle_frames: int, fade_frames: int) -> tuple[int, float]:
    raw_frames = cycle_frames + fade_frames
    if len(audio) < raw_frames:
        raise ValueError(f"Need at least {raw_frames} frames to build a cycle, got {len(audio)}.")

    coarse_step = max(1, fade_frames // 6)
    best_offset = 0
    best_score = float("inf")
    upper = len(audio) - raw_frames

    for offset in range(0, upper + 1, coarse_step):
        candidate = audio[offset : offset + raw_frames]
        score = float(np.mean(np.abs(candidate[:fade_frames] - candidate[-fade_frames:])))
        if score < best_score:
            best_score = score
            best_offset = offset

    refine_start = max(0, best_offset - coarse_step)
    refine_end = min(upper, best_offset + coarse_step)
    for offset in range(refine_start, refine_end + 1):
        candidate = audio[offset : offset + raw_frames]
        score = float(np.mean(np.abs(candidate[:fade_frames] - candidate[-fade_frames:])))
        if score < best_score:
            best_score = score
            best_offset = offset

    return best_offset, best_score


def build_wrapped_cycle(audio: np.ndarray, sample_rate: int, cycle_duration_sec: float, crossfade_ms: int) -> tuple[np.ndarray, float]:
    cycle_frames = int(round(cycle_duration_sec * sample_rate))
    fade_frames = int(round((crossfade_ms / 1000.0) * sample_rate))
    offset, seam_score = find_best_cycle_offset(audio, cycle_frames, fade_frames)
    raw = audio[offset : offset + cycle_frames + fade_frames].copy()

    fade_in = np.linspace(0.0, 1.0, fade_frames, endpoint=False, dtype=np.float32).reshape(-1, 1)
    fade_out = 1.0 - fade_in

    cycle = np.empty((cycle_frames, raw.shape[1]), dtype=np.float32)
    cycle[:fade_frames] = raw[:fade_frames] * fade_in + raw[-fade_frames:] * fade_out
    cycle[fade_frames:] = raw[fade_frames:cycle_frames]
    return cycle, seam_score


def stitch_intro_and_loop(
    intro: np.ndarray,
    cycle: np.ndarray,
    sample_rate: int,
    duration_sec: float,
    crossfade_ms: int,
) -> np.ndarray:
    target_frames = int(round(duration_sec * sample_rate))
    crossfade_frames = min(
        int(round((crossfade_ms / 1000.0) * sample_rate)),
        len(intro) - 1,
        len(cycle) - 1,
    )
    if crossfade_frames <= 0:
        body = tile_to_duration(cycle, sample_rate, max(0.0, duration_sec - (len(intro) / sample_rate)))
        return np.vstack([intro, body])[:target_frames].astype(np.float32)

    intro_keep = intro[:-crossfade_frames].copy()
    intro_tail = intro[-crossfade_frames:].copy()
    loop_head = cycle[:crossfade_frames].copy()

    fade_in = np.linspace(0.0, 1.0, crossfade_frames, endpoint=False, dtype=np.float32).reshape(-1, 1)
    fade_out = 1.0 - fade_in
    bridge = intro_tail * fade_out + loop_head * fade_in

    remaining_frames = target_frames - len(intro_keep) - len(bridge)
    if remaining_frames < 0:
        return np.vstack([intro_keep, bridge])[:target_frames].astype(np.float32)

    repeat_count = int(math.ceil((remaining_frames + crossfade_frames) / len(cycle)))
    loop_body = np.tile(cycle, (repeat_count, 1))
    loop_body = loop_body[crossfade_frames : crossfade_frames + remaining_frames]
    return np.vstack([intro_keep, bridge, loop_body]).astype(np.float32)


def apply_low_band_boost(audio: np.ndarray, sample_rate: int, gain_db: float, cutoff_hz: float) -> np.ndarray:
    if gain_db <= 0.0:
        return audio.copy()
    sos = butter(4, cutoff_hz, btype="low", fs=sample_rate, output="sos")
    low = sosfiltfilt(sos, audio, axis=0).astype(np.float32)
    high = audio - low
    boosted_low = low * db_to_amp(gain_db)
    return (high + boosted_low).astype(np.float32)


def db_to_amp(gain_db: float) -> float:
    return float(10.0 ** (gain_db / 20.0))


def apply_gain(audio: np.ndarray, gain_db: float) -> np.ndarray:
    return (audio * db_to_amp(gain_db)).astype(np.float32)


def tile_to_duration(audio: np.ndarray, sample_rate: int, duration_sec: float) -> np.ndarray:
    target_frames = int(round(duration_sec * sample_rate))
    repeat_count = int(math.ceil(target_frames / len(audio)))
    tiled = np.tile(audio, (repeat_count, 1))
    return tiled[:target_frames].astype(np.float32)


def limit_peak(audio: np.ndarray, peak_limit: float) -> np.ndarray:
    peak = float(np.max(np.abs(audio)))
    if peak > peak_limit and peak > 0.0:
        audio = audio * (peak_limit / peak)
    return audio.astype(np.float32)


def render_library(source_path: Path, xml_path: Path, output_dir: Path) -> list[dict]:
    tuning = parse_xml_tuning(xml_path)
    source_audio, source_rate = load_wav(source_path)
    source_audio = resample_audio(source_audio, source_rate, TARGET_SAMPLE_RATE)
    intro_window, intro_start, intro_end = extract_window(
        source_audio,
        TARGET_SAMPLE_RATE,
        0.0,
        INTRO_DURATION_SEC,
    )
    loop_window, loop_start, loop_end = extract_window(
        source_audio,
        TARGET_SAMPLE_RATE,
        LOOP_SEARCH_START_SEC,
        LOOP_SEARCH_DURATION_SEC,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []

    for spec in build_level_specs(tuning):
        pitched_intro = pitch_shift_by_resample(intro_window, spec.pitch_ratio)
        pitched_loop = pitch_shift_by_resample(loop_window, spec.pitch_ratio)
        cycle, seam_score = build_wrapped_cycle(
            pitched_loop,
            TARGET_SAMPLE_RATE,
            CYCLE_DURATION_SEC,
            SEAM_CROSSFADE_MS,
        )
        cycle = apply_low_band_boost(cycle, TARGET_SAMPLE_RATE, spec.lfe_db, LFE_CUTOFF_HZ)
        pitched_intro = apply_low_band_boost(pitched_intro, TARGET_SAMPLE_RATE, spec.lfe_db * 0.35, LFE_CUTOFF_HZ)
        cycle = apply_gain(cycle, spec.total_gain_db)
        pitched_intro = apply_gain(pitched_intro, spec.total_gain_db * 0.7)
        rendered = stitch_intro_and_loop(
            pitched_intro,
            cycle,
            TARGET_SAMPLE_RATE,
            TARGET_DURATION_SEC,
            INTRO_TO_LOOP_CROSSFADE_MS,
        )
        rendered = limit_peak(rendered, PEAK_LIMIT)

        output_path = output_dir / f"level_{spec.level_index}.wav"
        save_wav(output_path, rendered, TARGET_SAMPLE_RATE)

        peak = float(np.max(np.abs(rendered)))
        rms = float(np.sqrt(np.mean(np.square(rendered), dtype=np.float64)))
        manifest.append(
            {
                **asdict(spec),
                "output_file": str(output_path),
                "sample_rate": TARGET_SAMPLE_RATE,
                "duration_sec": TARGET_DURATION_SEC,
                "intro_window_start_sec": intro_start / TARGET_SAMPLE_RATE,
                "intro_window_end_sec": intro_end / TARGET_SAMPLE_RATE,
                "loop_window_start_sec": loop_start / TARGET_SAMPLE_RATE,
                "loop_window_end_sec": loop_end / TARGET_SAMPLE_RATE,
                "cycle_duration_sec": CYCLE_DURATION_SEC,
                "crossfade_ms": SEAM_CROSSFADE_MS,
                "intro_to_loop_crossfade_ms": INTRO_TO_LOOP_CROSSFADE_MS,
                "loop_delay_ms": tuning.loop_delay_ms,
                "loop_stop_transition_ms": tuning.loop_stop_transition_ms,
                "ignition_stop_transition_ms": tuning.ignition_stop_transition_ms,
                "peak": peak,
                "rms": rms,
                "seam_abs_mean": seam_score,
            }
        )
        print(
            f"Rendered level_{spec.level_index}.wav | "
            f"mid={spec.midpoint_speed} uu/s | "
            f"pitch={spec.pitch_semitones:.3f} st | "
            f"lfe={spec.lfe_db:.3f} dB | "
            f"gain={spec.total_gain_db:.3f} dB"
        )

    notes = {
        "source_file": str(source_path),
        "xml_file": str(xml_path),
        "notes": [
            "Net_Alpha_Boost.wav was treated as a steady raw hold source, not a speed sweep.",
            "Each level keeps the source ignition at the front and then transitions into a loop body.",
            "Pitch scaling was intentionally reduced to a conservative 3 semitones max so the result stays near the older Alpha Boost set.",
            "XML loop MakeUpGain belongs to the loop sound node, not a confirmed global master bus.",
            "LFE 611 was interpreted as 6.11 dB of low-band boost under 100 Hz to avoid destructive gain.",
            "The XML contains both 100 ms and 300 ms stop transitions; loop seam and intro handoff use shorter practical crossfades for cleaner offline assets.",
        ],
        "xml_tuning": asdict(tuning),
        "levels": manifest,
    }
    (output_dir / "manifest.json").write_text(json.dumps(notes, indent=2), encoding="utf-8")
    print(f"Manifest written to {output_dir / 'manifest.json'}")
    return manifest


def main() -> None:
    args = parse_args()
    render_library(
        source_path=args.source.resolve(),
        xml_path=args.xml.resolve(),
        output_dir=args.output_dir.resolve(),
    )


if __name__ == "__main__":
    main()
