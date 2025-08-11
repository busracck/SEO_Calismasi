import pandas as pd
import numpy as np # Rastgele sayılar için eklendi

# Analiz sonuçlarının bulunduğu CSV dosyası
input_csv_file = "seo_analiz_sonuclari.csv"

# Etiketlenmiş verinin kaydedileceği CSV dosyası
output_labeled_csv_file = "seo_analiz_etiketli.csv"

def assign_seo_category(row):
    """
    Her sayfa için belirli kurallara göre bir SEO uyumluluk kategorisi atar.
    MUVERA algoritması prensiplerini de dikkate alır.
    """
    
    # 1. Temel Hata Kontrolleri (Öncelikli ve Kritik - Teknik SEO)
    if row['Download_Success'] == False or row['HTTP_Status_Code'] >= 400:
        return 'Kötü' # İndirme başarısız veya hata kodu varsa direkt kötü

    # 2. Kritik SEO Unsurları Kontrolleri (Teknik SEO)
    # Başlık Etiketi
    if row['Title_Tag'] == 'Yok' or row['Title_Length'] < 20 or row['Title_Length'] > 70:
        return 'Kötü' # Başlık yoksa veya çok kısa/uzunsa

    # Meta Açıklama
    if row['Meta_Description'] == 'Yok' or row['Meta_Description_Length'] < 80 or row['Meta_Description_Length'] > 170:
        return 'Kötü' # Meta açıklama yoksa veya çok kısa/uzunsa

    # H1 Etiketi
    if row['H1_Tag'] == 'Yok' or row['H1_Length'] < 5: # H1 yoksa veya çok kısaysa
        return 'Kötü'

    # Missing Alt Images (Özellikle çok sayıdaysa)
    if row['Missing_Alt_Images'] > 0 and (row['Missing_Alt_Images'] / row['Total_Images'] > 0.1): # Toplam resimlerin %10'undan fazlasında alt eksikse
        return 'Kötü'

    # Noindex Tag (Eğer istenmeyen bir sayfa değilse)
    if row['Noindex_Tag_Exists'] == True:
        return 'Kötü'

    # Yeni: MUVERA Odaklı Kritik İçerik ve UX Kontrolleri (Bu kısım isteğe bağlı, eğer çok kritikse 'Kötü'ye atabiliriz)
    # Bu metriklerin "seo_analiz_sonuclari.csv" içinde var olduğunu varsayıyoruz.
    
    # Örnek: Eğer içerik derinliği çok düşükse (MUVERA kapsamlılığı vurgular)
    if 'Content_Depth_Score' in row and row['Content_Depth_Score'] < 0.2: # Çok sığ içerik
        return 'Kötü'
    
    """
    içeriğinin ne kadar derin, detaylı ve kullanıcıya gerçekten yardımcı olduğunu gösteren bir göstergedir. 
    Kaliteli içerik = yüksek puan = daha iyi sıralama.

    """

    # Eğer kullanıcı niyetiyle alaka aşırı düşükse
    if 'User_Intent_Alignment_Score' in row and row['User_Intent_Alignment_Score'] < 0.1: # Alakasız içerik
        return 'Kötü'

    # Eğer okunabilirlik çok kötü ise (jargon dolu, karmaşık)
    if 'Readability_Score' in row and row['Readability_Score'] < 40: # Okunabilirlik çok düşükse
        return 'Kötü'


    # 3. İyi SEO Kriterleri (Teknik ve MUVERA Odaklı Kombinasyon)
    # Eğer yukarıdaki kritik "Kötü" durumlarından hiçbiri yoksa ve
    # Hem temel teknik kriterler hem de MUVERA'nın vurguladığı kriterler ideal aralıklardaysa:
    
    # Temel Teknik İyiler
    basic_tech_good = (row['Title_Length'] >= 40 and row['Title_Length'] <= 60) and \
                      (row['Meta_Description_Length'] >= 120 and row['Meta_Description_Length'] <= 150) and \
                      (row['H1_Tag'] != 'Yok' and row['H1_Length'] >= 10) and \
                      (row['Missing_Alt_Images'] == 0)

    # MUVERA Odaklı İyiler (Yeni metriklerin varlığını ve uygun değerlerini kontrol edin)
    muvera_good = True
    
    # Her bir MUVERA metriği için ayrı ayrı kontrol yapıyoruz.
    # Eğer bu metrik sütunları yoksa veya değerleri koşulları sağlamıyorsa muvera_good = False olur.
    
    if 'Content_Depth_Score' not in row or row['Content_Depth_Score'] < 0.7:
        muvera_good = False
    if 'User_Intent_Alignment_Score' not in row or row['User_Intent_Alignment_Score'] < 0.6:
        muvera_good = False
    if 'Readability_Score' not in row or row['Readability_Score'] < 60:
        muvera_good = False
    if 'Natural_Language_Quality_Score' not in row or row['Natural_Language_Quality_Score'] < 0.7:
        muvera_good = False
    if 'FAQ_Section_Exists' not in row or not row['FAQ_Section_Exists']: # FAQ bölümü yoksa iyi değil
        muvera_good = False
    
    # Örneğin 'UX_Score' in row and row['UX_Score'] > 0.7 gibi

    if basic_tech_good and muvera_good:
        return 'İyi'
    
    # Yukarıdaki "İyi" koşullarını sağlamıyorsa ama "Kötü" de değilse "Orta"
    return 'Orta'

if __name__ == "__main__":
    try:
        df = pd.read_csv(input_csv_file)
        print(f"'{input_csv_file}' dosyasından {len(df)} satır veri okundu.")

     
        # *** BURASI SADECE TEST AMAÇLI GEÇİCİ DEĞERLER ATIYOR! ***
       
        
        # Bu sütunların varlığını kontrol edip, yoksa ekliyoruz
        if 'Content_Depth_Score' not in df.columns:
            # Örnek: visible_text_length'e göre basit bir derinlik skoru
            df['Content_Depth_Score'] = df['Visible_Text_Length'].apply(lambda x: min(x / 5000, 1.0) if x > 0 else 0.1)
        
        if 'User_Intent_Alignment_Score' not in df.columns:
            # Örnek: Rastgele ama makul bir aralıkta değerler
            df['User_Intent_Alignment_Score'] = np.random.uniform(0.3, 0.9, len(df))
            
        if 'Readability_Score' not in df.columns:
            # Örnek: visible_text_length'e göre basit bir okunabilirlik skoru
            df['Readability_Score'] = df['Visible_Text_Length'].apply(lambda x: 75 if x > 2000 else (60 if x > 500 else 45))
            
        if 'Natural_Language_Quality_Score' not in df.columns:
            # Örnek: Rastgele değerler
            df['Natural_Language_Quality_Score'] = np.random.uniform(0.4, 0.9, len(df))
            
        if 'FAQ_Section_Exists' not in df.columns:
            # Örnek: Rastgele True/False
            df['FAQ_Section_Exists'] = np.random.choice([True, False], size=len(df), p=[0.3, 0.7]) # %30'u True olsun
            
        # --------------------------------------------------------------------
        
        df['SEO_Score_Category'] = df.apply(assign_seo_category, axis=1)

        df.to_csv(output_labeled_csv_file, index=False, encoding='utf-8')
        print(f"SEO kategorileri başarıyla atandı ve '{output_labeled_csv_file}' dosyasına kaydedildi.")
        
        print("\nSEO Kategori Dağılımı:")
        print(df['SEO_Score_Category'].value_counts())

        print("\nEtiketlenmiş Verinin İlk 5 Satırı:")
        # Yeni sütunları da göstermek için DataFrame'in tüm başlıklarını dahil ediyoruz
        print(df[['URL', 'Title_Length', 'Meta_Description_Length', 'H1_Tag', 'Missing_Alt_Images', 
                  'Content_Depth_Score', 'User_Intent_Alignment_Score', 'Readability_Score', 
                  'Natural_Language_Quality_Score', 'FAQ_Section_Exists', # Yeni eklenenler
                  'SEO_Score_Category']].head())

    except FileNotFoundError:
        print(f"Hata: '{input_csv_file}' dosyası bulunamadı. Lütfen 'toplu_analiz.py'yi çalıştırdığınızdan ve dosyanın doğru yolda olduğundan emin olun.")
    except KeyError as ke:
        print(f"Hata: DataFrame'de beklenen bir sütun bulunamadı: {ke}. Lütfen 'seo_analiz_sonuclari.csv' dosyasının tüm gerekli sütunları içerdiğinden veya yeni metrikleri hesapladığınızdan emin olun.")
    except Exception as e:
        print(f"Bir hata oluştu: {e}")