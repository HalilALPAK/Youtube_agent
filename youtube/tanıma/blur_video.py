import os
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from numpy.linalg import norm

# =======================
# AYARLAR
# =======================
VIDEO_IN = "video.mp4"
VIDEO_OUT = "output_blur.mp4"
ME_DIR = "me"

DEVICE = -1  # CPU

ME_STRICT = 0.42
FOREIGN_ONLY = 0.55

MIN_FACE_SIZE = 80
BLUR_KERNEL = (45, 45)

# =======================
# MODEL
# =======================
print("⚙️ InsightFace yükleniyor...")
app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=DEVICE, det_size=(640, 640))

# =======================
# YARDIMCI
# =======================
def cosine_distance(a, b):
    return 1 - np.dot(a, b) / (norm(a) * norm(b))

def get_largest_face(faces):
    return max(
        faces,
        key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]),
        default=None
    )

# =======================
# 🔁 VERİ ARTIRIMI
# =======================
def augment_image(img):
    h, w = img.shape[:2]
    out = [img]

    # Flip
    out.append(cv2.flip(img, 1))

    # Brightness
    for alpha in [0.8, 1.2]:
        bright = cv2.convertScaleAbs(img, alpha=alpha, beta=0)
        out.append(bright)

    # Gaussian blur
    out.append(cv2.GaussianBlur(img, (5, 5), 0))

    # Small rotation
    M = cv2.getRotationMatrix2D((w//2, h//2), 5, 1.0)
    rot = cv2.warpAffine(img, M, (w, h))
    out.append(rot)

    return out

# =======================
# ME EMBEDDINGS (ARTIRIMLI)
# =======================
def build_me_embeddings():
    embeddings = []

    files = [
        os.path.join(ME_DIR, f)
        for f in os.listdir(ME_DIR)
        if f.lower().endswith((".jpg", ".png", ".jpeg"))
    ]

    if not files:
        raise RuntimeError("❌ me/ klasörü boş")

    print(f"🔍 {len(files)} ME foto bulundu")

    for path in files:
        img = cv2.imread(path)
        if img is None:
            continue

        for aug in augment_image(img):
            faces = app.get(aug)
            if not faces:
                continue

            face = get_largest_face(faces)
            emb = face.embedding / norm(face.embedding)
            embeddings.append(emb.astype(np.float32))

    print(f"✅ Toplam {len(embeddings)} ME embedding (augmentation dahil)")
    return np.stack(embeddings)

# =======================
# VIDEO BLUR
# =======================
def blur_video(me_embeddings):
    cap = cv2.VideoCapture(VIDEO_IN)
    if not cap.isOpened():
        raise RuntimeError("❌ Video açılamadı")

    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out = cv2.VideoWriter(
        VIDEO_OUT,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (w, h)
    )

    print("🎬 Video işleniyor...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        faces = app.get(frame)

        for face in faces:
            x1, y1, x2, y2 = map(int, face.bbox)
            if (x2 - x1) < MIN_FACE_SIZE:
                continue

            emb = face.embedding / norm(face.embedding)
            min_dist = min(cosine_distance(emb, me) for me in me_embeddings)

            # 🔑 SAĞLAM KARAR
            if min_dist > FOREIGN_ONLY:
                roi = frame[y1:y2, x1:x2]
                if roi.size > 0:
                    roi = cv2.GaussianBlur(roi, BLUR_KERNEL, 0)
                    frame[y1:y2, x1:x2] = roi

        out.write(frame)

    cap.release()
    out.release()
    print("✅ TAMAMLANDI →", VIDEO_OUT)

# =======================
if __name__ == "__main__":
    me_embeddings = build_me_embeddings()
    blur_video(me_embeddings)
