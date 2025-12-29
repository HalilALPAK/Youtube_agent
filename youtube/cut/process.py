import os
import json
import subprocess
import whisper
import re

# ================== AYARLAR ==================
INPUT_VIDEO = "input.mp4"
AUDIO_FILE = "audio.wav"
OUTPUT_VIDEO = "output_clean.mp4"

LANGUAGE = "tr"

MODEL_PATH = r"C:\Users\User\Desktop\whisper_models\small.pt"

FILLERS = {"ıı", "ııı", "eee", "ee", "şey", "hmm", "ıhm"}

# Sessizlik ayarları
SILENCE_DB = "-35dB"
MIN_SILENCE = 0.4   # saniye

BUFFER = 0.05
MERGE_GAP = 0.35
# =============================================


def extract_audio():
    print("🔊 Ses çıkarılıyor...")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", INPUT_VIDEO,
        "-ac", "1",
        "-ar", "16000",
        AUDIO_FILE
    ], check=True)


def detect_silence():
    print("🤫 Sessizlikler algılanıyor...")

    cmd = [
        "ffmpeg", "-i", AUDIO_FILE,
        "-af", f"silencedetect=noise={SILENCE_DB}:d={MIN_SILENCE}",
        "-f", "null", "-"
    ]

    process = subprocess.run(
        cmd,
        stderr=subprocess.PIPE,
        text=True
    )

    silences = []
    silence_start = None

    for line in process.stderr.splitlines():
        if "silence_start" in line:
            silence_start = float(re.findall(r"silence_start: ([0-9.]+)", line)[0])
        elif "silence_end" in line and silence_start is not None:
            silence_end = float(re.findall(r"silence_end: ([0-9.]+)", line)[0])
            silences.append((silence_start, silence_end))
            silence_start = None

    return silences


def transcribe():
    print("🧠 Whisper modeli yükleniyor (Desktop)...")

    model = whisper.load_model(MODEL_PATH)

    result = model.transcribe(
        AUDIO_FILE,
        language=LANGUAGE,
        word_timestamps=True,
        fp16=False
    )

    return result


def detect_filler_words(result):
    cuts = []
    last_end = -1

    words = []
    for seg in result["segments"]:
        if "words" in seg:
            words.extend(seg["words"])

    for w in words:
        word = w["word"].strip().lower()
        if word in FILLERS:
            s = w["start"] + BUFFER
            e = w["end"] + BUFFER

            if s > last_end + MERGE_GAP:
                cuts.append((s, e))
                last_end = e

    return cuts


def merge_cuts(cuts):
    if not cuts:
        return []

    cuts.sort()
    merged = [cuts[0]]

    for s, e in cuts[1:]:
        last_s, last_e = merged[-1]
        if s <= last_e + MERGE_GAP:
            merged[-1] = (last_s, max(last_e, e))
        else:
            merged.append((s, e))

    return merged


def invert_cuts(cuts, duration):
    keep = []
    last = 0.0

    for s, e in cuts:
        if s > last:
            keep.append((last, s))
        last = e

    if last < duration:
        keep.append((last, duration))

    return keep


def video_duration():
    r = subprocess.run(
        ["ffprobe", "-v", "error",
         "-show_entries", "format=duration",
         "-of", "default=nokey=1:noprint_wrappers=1",
         INPUT_VIDEO],
        stdout=subprocess.PIPE,
        text=True
    )
    return float(r.stdout.strip())


def build_video(segments):
    print("✂️ Video yeniden oluşturuluyor...")

    with open("segments.txt", "w") as f:
        for i, (s, e) in enumerate(segments):
            out = f"seg_{i}.mp4"
            subprocess.run([
                "ffmpeg", "-y",
                "-i", INPUT_VIDEO,
                "-ss", str(s),
                "-to", str(e),
                "-c", "copy",
                out
            ], check=True)
            f.write(f"file '{out}'\n")

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", "segments.txt",
        "-c", "copy",
        OUTPUT_VIDEO
    ], check=True)

    print("✅ ÇIKTI:", OUTPUT_VIDEO)


if __name__ == "__main__":
    extract_audio()

    silence_cuts = detect_silence()
    whisper_result = transcribe()
    filler_cuts = detect_filler_words(whisper_result)

    all_cuts = merge_cuts(silence_cuts + filler_cuts)

    duration = video_duration()
    keep_segments = invert_cuts(all_cuts, duration)

    build_video(keep_segments)

    print("🎉 BİTTİ — sessizlik + ıı temizlendi")
