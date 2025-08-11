import pandas as pd
from sklearn.model_selection import train_test_split # type: ignore
from sklearn.ensemble import RandomForestClassifier # type: ignore
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score # type: ignore
from sklearn.preprocessing import LabelEncoder # type: ignore
import numpy as np # Missing Alt Images yüzdesi için
import joblib


# Etiketlenmiş verinin bulunduğu CSV dosyası
input_labeled_csv_file = "seo_analiz_etiketli.csv"

if __name__ == "__main__":
    try:
        df = pd.read_csv(input_labeled_csv_file)
        print(f"'{input_labeled_csv_file}' dosyasından {len(df)} satır etiketli veri okundu.")

        # train_test_split fonksiyonunda stratify parametresinin çalışabilmesi için her sınıfta
        # en az 2 örnek bulunması gerekir. Veri setindeki az sayıda örneğe sahip sınıfları
        # eğitimden önce çıkararak bu hatayı giderelim.
        class_counts = df['SEO_Score_Category'].value_counts()
        min_samples = 2
        rare_classes = class_counts[class_counts < min_samples].index

        if len(rare_classes) > 0:
            print(f"\nUyarı: Veri setinde {min_samples}'den az örneğe sahip olan şu sınıflar bulundu ve kaldırıldı: {list(rare_classes)}")
            df = df[~df['SEO_Score_Category'].isin(rare_classes)]
            print(f"Veri setinin yeni boyutu: {len(df)} satır.")

        # Eğer model eğitimi için yeterli sayıda (en az 2) sınıf kalmadıysa, programı durdur.
        if len(df['SEO_Score_Category'].unique()) < 2:
            print("\nHata: Model eğitimi için en az 2 farklı sınıf gereklidir. Lütfen veri setinizi kontrol edin.")
            exit()


        # --- 1. Veri Ön İşleme ---

        # Kullanılacak özellikler (X) ve hedef değişken (y) seçimi
        # URL, Title_Tag, Meta_Description, H1_Tag gibi metin tabanlı sütunları doğrudan KULLANMIYORUZ.
        # Bunun yerine, bunların sayısal türevlerini (uzunluk, sayım) kullanıyoruz.
        features = [
            'Title_Length',
            'Meta_Description_Length',
            'H1_Length',
            'Total_Images',
            'Missing_Alt_Images',
            'Total_Links',
            'Internal_Links',
            'External_Links',
            'Nofollow_Links',
            'CSS_Files_Count',
            'JS_Files_Count',
            'H2_Count',
            'H3_Count',
            'H4_Count',
            'H5_Count',
            'H6_Count',
            'Visible_Text_Length',
            'HTTP_Status_Code', # Önceki düzeltmeyle artık doğru değerler olmalı
            'HTML_File_Size_KB' # Önceki düzeltmeyle artık doğru değerler olmalı
        ]

        # Kategorik (True/False) özellikleri sayısal (0/1) dönüştürme
        # Bu sütunlar zaten True/False olduğu için int() ile doğrudan 1/0'a dönüşür.
        df['Meta_Viewport_Exists'] = df['Meta_Viewport_Exists'].astype(int)
        df['Noindex_Tag_Exists'] = df['Noindex_Tag_Exists'].astype(int)
        df['Download_Success'] = df['Download_Success'].astype(int)
        
        # Canonical_Tag için: "Yok" ise 0, URL varsa 1
        df['Canonical_Tag_Exists'] = df['Canonical_Tag'].apply(lambda x: 0 if x == 'Yok' else 1)
        features.append('Canonical_Tag_Exists')

        # 'Missing_Alt_Images' / 'Total_Images' oranını ekleyebiliriz. Bu, hata oranını daha iyi gösterir.
        # Payda sıfır olmaması için kontrol ekliyoruz.
        df['Missing_Alt_Images_Ratio'] = df.apply(
            lambda row: row['Missing_Alt_Images'] / row['Total_Images'] if row['Total_Images'] > 0 else 0,
            axis=1
        )
        features.append('Missing_Alt_Images_Ratio')


        # Özellik matrisi (X) ve hedef vektörü (y) oluşturma
        X = df[features]
        y = df['SEO_Score_Category']

        # Hedef değişkeni sayısal değerlere dönüştürme (Örn: 'Kötü': 0, 'Orta': 1, 'İyi': 2)
        label_encoder = LabelEncoder()
        y_encoded = label_encoder.fit_transform(y)
        # Hangi kategorinin hangi sayıya denk geldiğini görmek için:
        print("\nSEO Kategori Kodlaması:")
        for i, category in enumerate(label_encoder.classes_):
            print(f"  '{category}': {i}")

        # Veriyi eğitim ve test setlerine ayırma
        # stratify=y_encoded, hedef değişken dağılımını eğitim ve test setleri arasında dengeli tutar.
        # random_state, sonuçların her çalıştırmada aynı olmasını sağlar.
        X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)

        print(f"\nEğitim seti boyutu (X_train): {X_train.shape}")
        print(f"Test seti boyutu (X_test): {X_test.shape}")
        print(f"Eğitim hedef seti boyutu (y_train): {y_train.shape}")
        print(f"Test hedef seti boyutu (y_test): {y_test.shape}")

        # --- 2. Makine Öğrenimi Modeli Eğitimi ---

        # Random Forest Sınıflandırıcısı modelini oluşturma
        # n_estimators: Ağaç sayısı
        # random_state: Tekrarlanabilirlik için
        # class_weight: Sınıf dengesizliğini gidermek için (İyi kategori çok az olduğu için önemli)
        #    'balanced' seçeneği, sınıfların ters frekansları ile ağırlıkları otomatik olarak ayarlar.
        model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')

        print("\nRandom Forest model eğitiliyor...")
        model.fit(X_train, y_train)
        print("Model eğitimi tamamlandı.")

        # --- 3. Model Değerlendirmesi ---

        # Test seti üzerinde tahmin yapma
        y_pred = model.predict(X_test)

        # Tahminleri orijinal kategori isimlerine geri dönüştürme
        y_test_decoded = label_encoder.inverse_transform(y_test)
        y_pred_decoded = label_encoder.inverse_transform(y_pred)

        print("\nModel Performansı (Test Seti Üzerinde):")
        print(f"Doğruluk (Accuracy): {accuracy_score(y_test, y_pred):.2f}")

        print("\nSınıflandırma Raporu:")
        # target_names parametresi ile orijinal kategori isimlerini gösteririz.
        print(classification_report(y_test_decoded, y_pred_decoded, target_names=label_encoder.classes_))

        print("\nKarmaşıklık Matrisi:")
        # Karmaşıklık Matrisi, modelin doğru ve yanlış tahminlerini detaylı gösterir.
        # Satırlar gerçek sınıfları, sütunlar tahmin edilen sınıfları temsil eder.
        # Örneğin, [0, 1] hücresi, gerçekte sınıf 0 olan ancak sınıf 1 olarak tahmin edilen örnek sayısını gösterir.
        print(confusion_matrix(y_test_decoded, y_pred_decoded, labels=label_encoder.classes_))

        # --- 4. Özellik Önemliliği (Feature Importance) ---
        # Hangi özelliklerin model için daha önemli olduğunu gösterir.
        feature_importances = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)
        print("\nÖzellik Önemliliği (En Yüksekten En Düşüğe):")
        print(feature_importances)

        joblib.dump(model, 'random_forest_model.pkl')
        joblib.dump(label_encoder, 'label_encoder.pkl')
        print("Model ve LabelEncoder kaydedildi.")

    except FileNotFoundError:
        print(f"Hata: '{input_labeled_csv_file}' dosyası bulunamadı. Lütfen 'veri_hazirlama_ve_etiketleme.py'yi çalıştırdığınızdan ve dosyanın doğru yolda olduğundan emin olun.")
    except Exception as e:
        print(f"Bir hata oluştu: {e}")
        raise e
