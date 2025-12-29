Proje Özeti — Klasör İçeriklerinin Kısa Özeti

Bu depo üç ana alt klasör içerir: `cut`, `kufur`, `tanıma`. Aşağıda her bir klasörde ne yapıldığı ve hangi dosyaların bulunduğuna dair kısa bir özet bulabilirsiniz.

- cut:

  - Amaç: Videoları önceden tanımlı segmentlere göre kesmek.
  - Öne çıkan dosyalar: `process.py`, `segments.txt`.
  - Kullanılan: Python script; genelde `ffmpeg` ile birlikte çalışır.

- kufur:

  - Amaç: Transkript veya metin içindeki uygunsuz (küfür) kelimeleri tespit etmek.
  - Öne çıkan dosyalar: `k.py`, `transcript.txt`.
  - Kullanılan: Python, basit regex veya kelime listesi tabanlı filtreleme.

- tanıma:
  - Amaç: Videolarda nesne/kişi tespiti ve gizlilik için bulanıklaştırma uygulamak.
  - Öne çıkan dosyalar: `blur_video.py`, `yolov8n.pt`, `me/` (yardımcı görseller).
  - Kullanılan: Python, YOLOv8 (Ultralytics), OpenCV, PyTorch.
