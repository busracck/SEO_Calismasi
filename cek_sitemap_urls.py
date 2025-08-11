import requests
from bs4 import BeautifulSoup
import time # İstekler arasına gecikme eklemek için

# Sitemizin sitemap URL'si
sitemap_url = "https://adresgezgini.com/sitemap.xml"



def get_urls_from_sitemap(sitemap_url):
    """
    Verilen sitemap URL'sinden tüm <loc> etiketlerindeki URL'leri çeker.
    """
    urls = []
    try:
        print(f"Sitemap çekiliyor: {sitemap_url}")
        response = requests.get(sitemap_url, timeout=10) # 10 saniye zaman aşımı
        response.raise_for_status() # HTTP hatalarını kontrol et

        soup = BeautifulSoup(response.text, 'xml') # XML olarak ayrıştırıyoruz

        # <loc> etiketlerini bul
        for loc_tag in soup.find_all('loc'):
            url = loc_tag.text.strip()
            if url:
                urls.append(url)

        # Eğer sitemap bir sitemap index dosyası ise (diğer sitemap'lere referans veriyorsa)
        # <sitemap> etiketlerini kontrol edelim
        for sitemap_tag in soup.find_all('sitemap'):
            sub_sitemap_url = sitemap_tag.loc.text.strip()
            if sub_sitemap_url:
                print(f"Alt sitemap bulundu: {sub_sitemap_url}. İçindeki URL'ler çekiliyor...")
                urls.extend(get_urls_from_sitemap(sub_sitemap_url)) # Özyinelemeli olarak alt sitemap'leri de çek

    except requests.exceptions.RequestException as e:
        print(f"Sitemap çekme hatası: {sitemap_url} - {e}")
    except Exception as e:
        print(f"Sitemap ayrıştırma hatası: {sitemap_url} - {e}")
    return urls

if __name__ == "__main__":
    all_urls = get_urls_from_sitemap(sitemap_url)
    print(f"\nToplam {len(all_urls)} URL sitemap'ten bulundu.")

    # İlk 10 URL'i göster (test amaçlı)
    # for i, url in enumerate(all_urls[:10]):
    #     print(f"{i+1}. {url}")

    # Bu URL'leri daha sonra kullanmak üzere bir dosyaya kaydedelim
    with open("sitemap_urls.txt", "w", encoding="utf-8") as f:
        for url in all_urls:
            f.write(url + "\n")
    print("Bulunan tüm URL'ler 'sitemap_urls.txt' dosyasına kaydedildi.")