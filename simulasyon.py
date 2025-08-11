import pandas as pd
from sklearn.preprocessing import LabelEncoder
import joblib # Modeli yüklemek için

# Etiketlenmiş verinin bulunduğu CSV dosyası (LabelEncoder'ı fit etmek için)
input_labeled_csv_file = "seo_analiz_etiketli.csv"
# Kaydedilmiş modeli ve LabelEncoder'ı yüklemek için dosya isimleri
model_path = 'random_forest_model.pkl'
label_encoder_path = 'label_encoder.pkl'

def load_model_and_encoder():
    """Kaydedilmiş modeli ve LabelEncoder'ı yükler."""
    try:
        model = joblib.load(model_path)
        label_encoder = joblib.load(label_encoder_path)
        print("Model ve LabelEncoder başarıyla yüklendi.")
        return model, label_encoder
    except FileNotFoundError:
        print(f"Hata: '{model_path}' veya '{label_encoder_path}' bulunamadı.")
        print("Lütfen 'model_egitimi.py' dosyasını çalıştırarak modeli ve encoder'ı kaydettiğinizden emin olun.")
        return None, None

def get_features_for_prediction(data_row, feature_columns):
    """Tahmin için uygun formatta özellik vektörü oluşturur."""
    # Tek bir satırı DataFrame'e dönüştür ve sütunları doğru sırada sırala
    df_row = pd.DataFrame([data_row])
    # Modelin beklediği sütunları ve sıralamayı sağlamak için yeniden indeksleme
    return df_row[feature_columns]

if __name__ == "__main__":
    # Model ve LabelEncoder'ı kaydetme adımı (eğer daha önce kaydetmediyseniz)
    # model_egitimi.py dosyasının sonuna eklenebilir veya ayrı bir betikte yapılabilir.
    # Bu kısmı sadece bir kere çalıştırmanız yeterli.
    # from sklearn.ensemble import RandomForestClassifier
    # from sklearn.preprocessing import LabelEncoder
    # X ve y_encoded'ı model_egitimi.py'deki gibi oluşturmanız gerekir
    # model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    # model.fit(X_train, y_train) # varsayalım X_train, y_train daha önce eğitildi
    # joblib.dump(model, model_path)
    # joblib.dump(label_encoder, label_encoder_path)
    # print("Model ve LabelEncoder kaydedildi.")

    model, label_encoder = load_model_and_encoder()
    if model is None or label_encoder is None:
        exit() # Yükleme başarısız olursa çık

    # Modelin eğitildiği özellik sütunlarının listesini manuel olarak tanımlıyoruz
    # Bu listenin model_egitimi.py'deki 'features' listesiyle AYNI sırada ve İÇERİKTE olması GEREKİR.
    model_features = [
        'Title_Length', 'Meta_Description_Length', 'H1_Length', 'Total_Images',
        'Missing_Alt_Images', 'Total_Links', 'Internal_Links', 'External_Links',
        'Nofollow_Links', 'CSS_Files_Count', 'JS_Files_Count', 'H2_Count',
        'H3_Count', 'H4_Count', 'H5_Count', 'H6_Count', 'Visible_Text_Length',
        'HTTP_Status_Code', 'HTML_File_Size_KB', 'Canonical_Tag_Exists', 'Missing_Alt_Images_Ratio'
    ]

    # --- Mevcut (Kötü) Sayfa Verileri (seo_analiz_etiketli.csv'den alınmıştır) ---
    # Bu verileri OnlyOffice Calc'tan veya csv'den kopyalayıp buraya yapıştırabilirsiniz.
    # Her satır bir sayfanın verisi olmalı.
    
    current_page_data = {
    'Title_Length': 37,
    'Meta_Description_Length': 155,
    'H1_Length': 10,
    'Total_Images': 132,
    'Missing_Alt_Images': 83,
    'Total_Links': 150,
    'Internal_Links': 72,
    'External_Links': 14,
    'Nofollow_Links': 0,
    'CSS_Files_Count': 0,
    'JS_Files_Count': 9,
    'H2_Count': 3,
    'H3_Count': 4,
    'H4_Count': 0,
    'H5_Count': 0,
    'H6_Count': 0,
    'Visible_Text_Length': 9232,
    'HTTP_Status_Code': 200,
    'HTML_File_Size_KB': 238.875977,
    'Canonical_Tag_Exists': 1, # Varsayılan olarak 1 (var) kabul edelim
}
# Missing_Alt_Images_Ratio'yu hesapla (bu değer otomatik hesaplanmalı)
    current_page_data['Missing_Alt_Images_Ratio'] = current_page_data['Missing_Alt_Images'] / current_page_data['Total_Images'] if current_page_data['Total_Images'] > 0 else 0
    # Missing_Alt_Images_Ratio'yu hesapla


    # --- İyileştirilmiş Senaryo İçin Yeni Sayfa Verileri ---
    # Yaptığınız iyileştirmelere göre değiştirdiğiniz değerler
    improved_page_data = {
    'Title_Length': 37, # Değişmedi
    'Meta_Description_Length': 140, # İyileştirildi!
    'H1_Length': 45, # İyileştirildi!
    'Total_Images': 132, # Değişmediğini varsayalım
    'Missing_Alt_Images': 0, # İyileştirildi!
    'Total_Links': 150, # Değişmedi
    'Internal_Links': 80, # İyileştirildi!
    'External_Links': 14, # Değişmedi
    'Nofollow_Links': 0, # Değişmedi
    'CSS_Files_Count': 0, # Değişmedi
    'JS_Files_Count': 9, # Değişmedi
    'H2_Count': 3, # Değişmedi
    'H3_Count': 4, # Değişmedi
    'H4_Count': 0, # Değişmedi
    'H5_Count': 0, # Değişmedi
    'H6_Count': 0, # Değişmedi
    'Visible_Text_Length': 9232, # Değişmedi
    'HTTP_Status_Code': 200, # Değişmedi
    'HTML_File_Size_KB': 238.875977, # Değişmedi
    'Canonical_Tag_Exists': 1, # Değişmedi
}
# Missing_Alt_Images_Ratio'yu hesapla (yeni Missing_Alt_Images değerine göre otomatik hesaplanmalı)
    improved_page_data['Missing_Alt_Images_Ratio'] = improved_page_data['Missing_Alt_Images'] / improved_page_data['Total_Images'] if improved_page_data['Total_Images'] > 0 else 0
 

    # Mevcut sayfa için tahmin yapma
    X_current = get_features_for_prediction(current_page_data, model_features)
    pred_current_encoded = model.predict(X_current)
    pred_current_category = label_encoder.inverse_transform(pred_current_encoded)[0]
    print(f"\nMevcut Sayfa İçin Tahmin Edilen Kategori: {pred_current_category}")

    # İyileştirilmiş sayfa için tahmin yapma
    X_improved = get_features_for_prediction(improved_page_data, model_features)
    pred_improved_encoded = model.predict(X_improved)
    pred_improved_category = label_encoder.inverse_transform(pred_improved_encoded)[0]
    print(f"İyileştirilmiş Sayfa İçin Tahmin Edilen Kategori: {pred_improved_category}")

    if pred_improved_category != pred_current_category:
        print("\nTEBRİKLER! İyileştirmelerinizin tahmini SEO kategorisini değiştirmesi bekleniyor!")
        print(f"'{pred_current_category}' durumundan '{pred_improved_category}' durumuna geçiş.")
    else:
        print("\nTahmini kategori değişmedi. Daha fazla iyileştirme veya farklı bir strateji düşünün.")