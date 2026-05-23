import pandas as pd
import numpy as np

def preprocess_data(data_dict):
    """
    Sensörlerden gelen ham veriyi alır, eksik verileri medyan ile doldurur,
    API tasarım kurallarına (domain knowledge) ve IQR istatistiksel 
    yöntemine göre aykırı değerleri (outlier) temizler.
    """
    df = pd.DataFrame(data_dict)
    
    # 1. Eksik Veri Tamamlama (Medyan Yöntemi)
    columns_to_fill = ['soil_moisture', 'temperature', 'humidity', 'ph_level']
    for col in columns_to_fill:
        df[col] = df[col].fillna(df[col].median())

    # 2. Aykırı Değer Tespiti - Adım A: Domain Kuralları (API Validation)
    df['temperature'] = np.clip(df['temperature'], -50, 70)
    df['humidity'] = np.clip(df['humidity'], 0, 100)
    df['ph_level'] = np.clip(df['ph_level'], 0, 14)
    df['soil_moisture'] = np.clip(df['soil_moisture'], 0, 100)

    # 3. Aykırı Değer Tespiti - Adım B: IQR (Interquartile Range) Yöntemi
    def apply_iqr_clipping(dataframe, column):
        Q1 = dataframe[column].quantile(0.25)
        Q3 = dataframe[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        dataframe[column] = np.clip(dataframe[column], lower_bound, upper_bound)
        return dataframe

    for col in columns_to_fill:
        df = apply_iqr_clipping(df, col)
        
    return df

# Test Çalıştırması (Sentetik Veri)
if __name__ == "__main__":
    test_data = {
        'timestamp': pd.date_range(start='2026-03-25T14:30:00Z', periods=10, freq='h'),
        'soil_moisture': [42.5, 45.0, np.nan, 41.2, 150.0, 43.1, 40.5, np.nan, 44.0, -10.0],
        'temperature': [24.8, 25.1, 24.5, 95.0, 23.9, np.nan, 22.1, -60.0, 24.2, 25.0],
        'humidity': [60, 62, 59, 61, np.nan, 65, 120, 58, 60, np.nan],
        'ph_level': [6.8, 6.9, 7.0, np.nan, 6.7, 14.5, 6.6, 6.8, np.nan, 6.5]
    }
    
    clean_df = preprocess_data(test_data)
    print("Temizlenmiş Veri Seti:\n", clean_df)
