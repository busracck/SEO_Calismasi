from bs4 import BeautifulSoup
import os

dosya_adi = "adresgezgini_anasayfa.html" # Çektiğimiz dosyanın adı

try:
    if not os.path.exists(dosya_adi):
        print(f"Hata: '{dosya_adi}' dosyası bulunamadı. Lütfen önce cek_kaynak.py'yi çalıştırdığınızdan emin olun.")
    else:
        with open(dosya_adi, "r", encoding="utf-8") as f:
            html_icerigi = f.read()

        soup = BeautifulSoup(html_icerigi, 'html.parser')

        print(f"\n--- HTML Analiz Sonuçları ({dosya_adi}) ---")

        # 1. Başlık Etiketi (Title Tag)
        title_tag = soup.title
        title_text = title_tag.string.strip() if title_tag else "Yok"
        print(f"Başlık Etiketi: '{title_text}'")
        print(f"Başlık Uzunluğu: {len(title_text)} karakter")

        # 2. Meta Açıklama (Meta Description)
        meta_description = soup.find('meta', attrs={'name': 'description'})
        description_content = meta_description.get('content', '').strip() if meta_description else "Yok"
        print(f"Meta Açıklama: '{description_content}'")
        print(f"Meta Açıklama Uzunluğu: {len(description_content)} karakter")

        # 3. H1 Etiketi (Ana Başlık)
        h1_tag = soup.find('h1')
        h1_text = h1_tag.get_text().strip() if h1_tag else "Yok"
        print(f"H1 Başlık: '{h1_text}'")
        print(f"H1 Uzunluğu: {len(h1_text)} karakter")

        # 4. Resimler ve Alt Etiketleri
        img_tags = soup.find_all('img')
        print(f"Toplam Resim Sayısı: {len(img_tags)}")
        alt_eksik_resimler = 0
        for img in img_tags:
            # alt niteliği yoksa veya boşsa eksik say
            if not img.get('alt') or img.get('alt').strip() == "":
                alt_eksik_resimler += 1
        print(f"Alt etiketi eksik resim sayısı: {alt_eksik_resimler}")

        # 5. Bağlantılar (Linkler)
        a_tags = soup.find_all('a')
        print(f"Toplam Bağlantı Sayısı: {len(a_tags)}")
        dahili_linkler = 0
        harici_linkler = 0
        nofollow_linkler = 0
        for a in a_tags:
            href = a.get('href')
            rel = a.get('rel') # rel niteliğini al
            if href:
                # Dahili/Harici Link Kontrolü (Kendi domaininizi güncelleyin)
                if "adresgezgini.com" in href or href.startswith('/'):
                    dahili_linkler += 1
                elif href.startswith('http') or href.startswith('//'):
                    harici_linkler += 1

                # Nofollow kontrolü
                if rel and 'nofollow' in rel:
                    nofollow_linkler += 1
        print(f"Dahili Bağlantı Sayısı: {dahili_linkler}")
        print(f"Harici Bağlantı Sayısı: {harici_linkler}")
        print(f"Nofollow Bağlantı Sayısı: {nofollow_linkler}")

        # --- Yeni Eklenen Özellikler ---

        # 6. HTML Boyutu (Çekilen dosyanın boyutu)
        html_file_size = os.path.getsize(dosya_adi) # cek_kaynak.py'den gelen dosya boyutu
        print(f"HTML Dosya Boyutu: {html_file_size / 1024:.2f} KB") # KB cinsinden gösterelim

        # 7. CSS Dosyası Sayısı
        css_links = soup.find_all('link', rel='stylesheet')
        print(f"CSS Dosyası Sayısı: {len(css_links)}")

        # 8. JavaScript Dosyası Sayısı
        js_scripts = soup.find_all('script', src=True) # src niteliği olan scriptleri sayarız
        print(f"JavaScript Dosyası Sayısı: {len(js_scripts)}")

        # 9. Head etiketindeki meta viewport
        meta_viewport = soup.find('meta', attrs={'name': 'viewport'})
        print(f"Meta Viewport Var mı: {'Evet' if meta_viewport else 'Hayır'}")

        # 10. Canonical Tag
        canonical_tag = soup.find('link', rel='canonical')
        canonical_href = canonical_tag.get('href') if canonical_tag else "Yok"
        print(f"Canonical Etiketi: {canonical_href}")

        # 11. Noindex Meta Tag
        noindex_tag = soup.find('meta', attrs={'name': 'robots', 'content': lambda x: x and 'noindex' in x})
        print(f"Noindex Etiketi Var mı: {'Evet' if noindex_tag else 'Hayır'}")

        # 12. H2-H6 Başlık Sayıları
        h_tags_counts = {}
        for i in range(2, 7): # h2'den h6'ya kadar
            tag_name = f'h{i}'
            h_tags_counts[tag_name] = len(soup.find_all(tag_name))
        print(f"H2-H6 Başlık Sayıları: {h_tags_counts}")

        # 13. Toplam Metin Uzunluğu (Sadece görünür metin)
        # script, style, head, [document], html gibi etiketleri dışlayarak metni alalım
        for script in soup(["script", "style"]):
            script.extract() # komut dosyalarını ve stil etiketlerini kaldır
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines()) # Satır satır işleyelim
        chunks = (phrase.strip() for line in lines for phrase in line.split("  ")) # Fazla boşlukları kaldır
        text = ' '.join(chunk for chunk in chunks if chunk) # Boş öbekleri atla
        print(f"Görünür Metin Uzunluğu: {len(text)} karakter")


except FileNotFoundError:
    print(f"Hata: '{dosya_adi}' dosyası bulunamadı. Lütfen cek_kaynak.py'yi çalıştırıp dosyayı oluşturduğunuzdan emin olun.")
except Exception as e:
    print(f"Bir hata oluştu: {e}")