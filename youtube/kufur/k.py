import os
import cv2
import subprocess
import whisper
import numpy as np
from insightface.app import FaceAnalysis
from rapidfuzz import fuzz

# ====================== AYARLAR ======================
VIDEO_IN = "input.mp4"
VIDEO_OUT = "output_censored.mp4"
AUDIO_FILE = "audio.wav"
TRANSCRIPT_FILE = "transcript.txt"
LANG = "tr"
MODEL_PATH = "small"
THRESHOLD = 70
FILLERS = ["siktir", "orospu", "lan", "bok", "amk","oruspu çocuğu","oros bu çocuğu","yarrak","piç","göt","sik","amına koyim","amcık","sikiyim","yavşak","pezevenk","kahpe","mal","salak","aptal","gerizekalı"]

DEVICE = -1
MIN_FACE_SIZE = 50

# ====================== SES ÇIKAR ======================
print("🔊 Ses çıkarılıyor...")
subprocess.run([
    "ffmpeg", "-y",
    "-i", VIDEO_IN,
    "-ac", "1",
    "-ar", "16000",
    AUDIO_FILE
], check=True)

# ====================== TRANSKRİPT ======================
print("🧠 Whisper modeli yükleniyor...")
model = whisper.load_model(MODEL_PATH)
result = model.transcribe(AUDIO_FILE, language=LANG, word_timestamps=True, fp16=False)

# ====================== TRANSKRİPT DOSYAYA ======================
with open(TRANSCRIPT_FILE, "w", encoding="utf-8") as f:
    for seg in result["segments"]:
        f.write(f"[{seg['start']:.2f} - {seg['end']:.2f}] {seg['text']}\n")
print(f"📝 Transkript kaydedildi → {TRANSCRIPT_FILE}")

# ====================== KÜFÜR SEGMENTLERİ ======================
curse_times = []
print("🔍 Küfür tespiti başlıyor...")
for seg in result["segments"]:
    text = seg["text"].lower()
    found = False
    for curse in FILLERS:
        score = fuzz.partial_ratio(text, curse)
        if score >= THRESHOLD:
            curse_times.append((seg["start"], seg["end"]))
            print(f"💢 Küfür bulundu: '{curse}' in segment '{text}' | Benzerlik: {score}% | {seg['start']:.2f}-{seg['end']:.2f}s")
            found = True
            break
    if not found:
        print(f"⚪ Küfür yok: '{text}'")

if not curse_times:
    print("⚠️ Küfür bulunamadı!")

# ====================== FRAME LİSTESİ ======================
cap = cv2.VideoCapture(VIDEO_IN)
fps = cap.get(cv2.CAP_PROP_FPS)
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(VIDEO_OUT, fourcc, fps, (w, h))

curse_frames = set()
for start, end in curse_times:
    s_idx = int(start * fps)
    e_idx = int(end * fps)
    curse_frames.update(range(s_idx, e_idx + 1))

print(f"💢 {len(curse_frames)} frame küfür içeriyor, ağız kutusu eklenecek...")

# ====================== FACE MODEL ======================
print("⚙️ InsightFace yükleniyor...")
app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=DEVICE, det_size=(640, 640))

# ====================== VIDEO İŞLE ======================
frame_idx = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break

    if frame_idx in curse_frames:
        faces = app.get(frame)
        if not faces:
            print(f"⚠️ Frame {frame_idx} yüz bulunamadı!")
        for face in faces:
            x1, y1, x2, y2 = map(int, face.bbox)
            if (x2 - x1) < MIN_FACE_SIZE:
                print(f"⚠️ Frame {frame_idx} yüz küçük, atlandı!")
                continue

            # Dudak landmark varsa normal çizim
            if face.landmark is not None and len(face.landmark) >= 68:
                lips_x = face.landmark[48:68, 0].astype(int)
                lips_y = face.landmark[48:68, 1].astype(int)
                lx1, ly1 = lips_x.min(), lips_y.min()
                lx2, ly2 = lips_x.max(), lips_y.max()
            else:
                # Landmark yoksa yüz alt kısmını kapat
                lx1 = x1
                lx2 = x2
                ly1 = int(y1 + (y2 - y1) * 0.6)
                ly2 = y2

            cv2.rectangle(frame, (lx1, ly1), (lx2, ly2), (0, 0, 0), -1)
            print(f"✅ Frame {frame_idx} ağız kapandı: {lx1},{ly1}-{lx2},{ly2}")

    out.write(frame)
    frame_idx += 1

cap.release()
out.release()
print("✅ Çıktı oluşturuldu →", VIDEO_OUT)
