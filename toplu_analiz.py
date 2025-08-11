import requests
from bs4 import BeautifulSoup
import os
import time
import pandas as pd # type: ignore # Verileri DataFrame'e alıp CSV'ye kaydetmek için

# Analiz edilecek URL'lerin bulunduğu dosya
urls_file = "sitemap_urls.txt"
# Çıktı CSV dosyası
output_csv_file = "seo_analiz_sonuclari.csv"

# Her istek arasına eklenecek gecikme (saniye cinsinden)
REQUEST_DELAY = 0.5 # 0.5 saniye

def analyze_html_content(html_content): # URL artık burada alınmıyor
    """
    HTML içeriğini ayrıştırır ve SEO özelliklerini bir sözlük olarak döndürür.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    features = {
        # 'URL' ve diğer çekme ile ilgili bilgiler burada DEĞİL, dış döngüde eklenecek
        'Title_Tag': 'Yok',
        'Title_Length': 0,
        'Meta_Description': 'Yok',
        'Meta_Description_Length': 0,
        'H1_Tag': 'Yok',
        'H1_Length': 0,
        'Total_Images': 0,
        'Missing_Alt_Images': 0,
        'Total_Links': 0,
        'Internal_Links': 0,
        'External_Links': 0,
        'Nofollow_Links': 0,
        # 'HTML_File_Size_KB', 'Download_Success', 'HTTP_Status_Code', 'Error_Message'
        # bu fonksiyonun dışında doldurulacak.
        'CSS_Files_Count': 0,
        'JS_Files_Count': 0,
        'Meta_Viewport_Exists': False,
        'Canonical_Tag': 'Yok',
        'Noindex_Tag_Exists': False,
        'H2_Count': 0,
        'H3_Count': 0,
        'H4_Count': 0,
        'H5_Count': 0,
        'H6_Count': 0,
        'Visible_Text_Length': 0
    }

    try:
        # Başlık Etiketi
        title_tag = soup.title
        if title_tag:
            features['Title_Tag'] = title_tag.string.strip()
            features['Title_Length'] = len(features['Title_Tag'])

        # Meta Açıklama
        meta_description = soup.find('meta', attrs={'name': 'description'})
        if meta_description:
            features['Meta_Description'] = meta_description.get('content', '').strip()
            features['Meta_Description_Length'] = len(features['Meta_Description'])

        # H1 Etiketi
        h1_tag = soup.find('h1')
        if h1_tag:
            features['H1_Tag'] = h1_tag.get_text().strip()
            features['H1_Length'] = len(features['H1_Tag'])

        # Resimler ve Alt Etiketleri
        img_tags = soup.find_all('img')
        features['Total_Images'] = len(img_tags)
        alt_eksik_resimler = 0
        for img in img_tags:
            if not img.get('alt') or img.get('alt').strip() == "":
                alt_eksik_resimler += 1
        features['Missing_Alt_Images'] = alt_eksik_resimler

        # Bağlantılar
        a_tags = soup.find_all('a')
        features['Total_Links'] = len(a_tags)
        for a in a_tags:
            href = a.get('href')
            rel = a.get('rel')
            if href:
                # Dahili/Harici Link Kontrolü (Kendi domaininizi güncelleyin)
                if "adresgezgini.com" in href or href.startswith('/'):
                    features['Internal_Links'] += 1
                elif href.startswith('http') or href.startswith('//'):
                    features['External_Links'] += 1

                # Nofollow kontrolü
                if rel and 'nofollow' in rel:
                    features['Nofollow_Links'] += 1

        # CSS Dosyası Sayısı
        css_links = soup.find_all('link', rel='stylesheet')
        features['CSS_Files_Count'] = len(css_links)

        # JavaScript Dosyası Sayısı
        js_scripts = soup.find_all('script', src=True)
        features['JS_Files_Count'] = len(js_scripts)

        # Meta Viewport
        meta_viewport = soup.find('meta', attrs={'name': 'viewport'})
        features['Meta_Viewport_Exists'] = True if meta_viewport else False

        # Canonical Tag
        canonical_tag = soup.find('link', rel='canonical')
        features['Canonical_Tag'] = canonical_tag.get('href') if canonical_tag else "Yok"

        # Noindex Meta Tag
        noindex_tag = soup.find('meta', attrs={'name': 'robots', 'content': lambda x: x and 'noindex' in x.lower()})
        features['Noindex_Tag_Exists'] = True if noindex_tag else False

        # H2-H6 Başlık Sayıları
        for i in range(2, 7):
            tag_name = f'h{i}'
            features[f'H{i}_Count'] = len(soup.find_all(tag_name))

        # Toplam Metin Uzunluğu (Görünür metin)
        for script_or_style in soup(["script", "style", "header", "footer", "nav"]):
            script_or_style.extract()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        features['Visible_Text_Length'] = len(text)

    except Exception as e:
        # Eğer ayrıştırmada hata olursa, hata mesajını kaydet
        features['Error_Message_Parsing'] = f"Ayrıştırma Hatası: {e}"

    return features

if __name__ == "__main__":
    all_site_data = []

    if not os.path.exists(urls_file):
        print(f"Hata: '{urls_file}' dosyası bulunamadı. Lütfen önce cek_sitemap_urls.py'yi çalıştırdığınızdan emin olun.")
    else:
        with open(urls_file, "r", encoding="utf-8") as f:
            urls_to_analyze = [line.strip() for line in f if line.strip()]

        print(f"'{urls_file}' dosyasından {len(urls_to_analyze)} URL okunuyor.")

        for i, url in enumerate(urls_to_analyze):
            print(f"({i+1}/{len(urls_to_analyze)}) {url} adresinden veri çekiliyor...")
            
            page_features = { # Her sayfa için temel çekme bilgileri
                'URL': url,
                'HTTP_Status_Code': 0,
                'HTML_File_Size_KB': 0,
                'Download_Success': False,
                'Error_Message': 'Yok', # İstek/bağlantı hataları için
                'Error_Message_Parsing': 'Yok' # Ayrıştırma hataları için
            }

            try:
                response = requests.get(url, timeout=15)
                page_features['HTTP_Status_Code'] = response.status_code
                page_features['HTML_File_Size_KB'] = len(response.content) / 1024
                page_features['Download_Success'] = True # Başlangıçta başarılı varsayılır
                response.raise_for_status() # HTTP hatalarını yakala (4xx, 5xx)

                # HTML içeriğini analiz et
                extracted_features = analyze_html_content(response.text) # URL parametresi kaldırıldı
                page_features.update(extracted_features) # Çekilen özelliklerle güncelleyin

            except requests.exceptions.HTTPError as http_err:
                print(f"  HTTP Hatası: {http_err} (Durum Kodu: {response.status_code})")
                page_features['Download_Success'] = False
                page_features['Error_Message'] = f"HTTP Hatası: {http_err}"
            except requests.exceptions.ConnectionError as conn_err:
                print(f"  Bağlantı Hatası: {conn_err}")
                page_features['Download_Success'] = False
                page_features['Error_Message'] = f"Bağlantı Hatası: {conn_err}"
            except requests.exceptions.Timeout as timeout_err:
                print(f"  Zaman Aşımı Hatası: {timeout_err}")
                page_features['Download_Success'] = False
                page_features['Error_Message'] = f"Zaman Aşımı Hatası: {timeout_err}"
            except requests.exceptions.RequestException as req_err:
                print(f"  Genel İstek Hatası: {req_err}")
                page_features['Download_Success'] = False
                page_features['Error_Message'] = f"Genel İstek Hatası: {req_err}"
            except Exception as e:
                print(f"  Beklenmeyen Hata (Ana Döngü): {e}")
                page_features['Download_Success'] = False
                page_features['Error_Message'] = f"Beklenmeyen Hata (Ana Döngü): {e}"

            all_site_data.append(page_features)

            time.sleep(REQUEST_DELAY)

        df = pd.DataFrame(all_site_data)
        df.to_csv(output_csv_file, index=False, encoding='utf-8')
        print(f"\nAnaliz tamamlandı. Sonuçlar '{output_csv_file}' dosyasına kaydedildi.")
        print(f"Toplam {len(df)} sayfa işlendi.")