import requests # type: ignore
import os # Dosya işlemleri için os modülünü import ediyoruz

url = "https://adresgezgini.com/" #Ancak asıl hedefimiz canlı site olduğu için adresgezini.com ile başlayalım.

dosya_adi = "adresgezgini_anasayfa.html"

try:
    print(f"{url} adresinden kaynak kodu çekiliyor...")
    response = requests.get(url)
    response.raise_for_status()  # HTTP hataları (4xx veya 5xx) için hata yükseltir

    kaynak_kodu = response.text

    # Kaynak kodunu bir dosyaya kaydetme
    with open(dosya_adi, "w", encoding="utf-8") as f:
        f.write(kaynak_kodu)

    print(f"Kaynak kodu '{dosya_adi}' dosyasına başarıyla kaydedildi.")
    print(f"Dosya boyutu: {os.path.getsize(dosya_adi)} bayt")


except requests.exceptions.HTTPError as http_err:
    print(f"HTTP Hatası oluştu: {http_err} (URL: {url})")
    print(f"Durum Kodu: {response.status_code}")
except requests.exceptions.ConnectionError as conn_err:
    print(f"Bağlantı Hatası oluştu: {conn_err}. İnternet bağlantınızı veya URL'yi kontrol edin.")
except requests.exceptions.Timeout as timeout_err:
    print(f"Zaman Aşımı Hatası oluştu: {timeout_err}. İstek çok uzun sürdü.")
except requests.exceptions.RequestException as req_err:
    print(f"Bir Hata oluştu: {req_err}")
except Exception as e:
    print(f"Beklenmeyen bir hata oluştu: {e}")