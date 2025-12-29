Cut — Video Kesme

- Amaç: Videoları önceden belirlenmiş segmentlere göre kesmek.
- İçerik: `process.py` kesme işlemini yapar; `segments.txt` segment listesini tutar.
- Kullanılan: Python (script), dış araçlar olarak genellikle `ffmpeg` (video kesme/işleme) kullanılır.
- Çalıştırma (örnek):
  - `python process.py` (script parametrelerine göre çalışır)
  - `segments.txt` her satırda bir segment tanımı içerir (ör. başlangıç-bitiş)

Not: Kesme mantarı ve parametreler için `process.py` içindeki yorumlara bakın.
