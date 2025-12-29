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

Notlar:

- `onemlı_anlar.json` (repo kökünde): Proje genelinde tespit edilen "önemli anlar"ı saklar. Bu repoda `onemlı_anlar.json` içinde bir `n8n` workflow tanımı bulunmaktadır — `nodes`, `connections` ve `meta` bölümleriyle birlikte.
  - İçerik: n8n `code` node'larında JavaScript kodları, `httpRequest` node'ları ve bir LangChain/agent node'u örneği gibi workflow öğeleri bulunur. Dosya aynı zamanda `highlights` veya `start`/`end` alanları üreten kodlar içerir.
  - Kullanım: Bu JSON n8n'e import edilerek workflow olarak çalıştırılabilir; veya `nodes` içindeki kod parçaları çıkarılarak lokal script akışlarında tekrar kullanılabilir.
- Her klasördeki çalıştırma örnekleri ve detaylar ilgili README dosyalarında bulunmaktadır; daha fazla parametre veya kurulum gereksinimi için bu dosyalara bakın.
