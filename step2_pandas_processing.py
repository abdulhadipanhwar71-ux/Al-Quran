import requests
import pandas as pd
import sys

# Windows terminal UTF-8 encoding support
sys.stdout.reconfigure(encoding='utf-8')

def build_surahs_dataframe():
    """
    مرحلہ 3: سورتوں کا ڈیٹا لے کر Pandas DataFrame بنانا
    مرحلہ 4: ڈیٹا کو صاف اور درست کالمز میں منظم کرنا
    """
    print("API سے سورتوں کی معلومات لائی جا رہی ہیں...")
    url = "https://api.alquran.cloud/v1/surah"
    res = requests.get(url)
    
    if res.status_code != 200:
        raise Exception(f"API Error: {res.status_code}")
        
    raw_data = res.json()["data"]
    
    # خام JSON کو Pandas DataFrame میں تبدیل کرنا
    df = pd.DataFrame(raw_data)
    
    # مرحلہ 4: Data Cleaning & Renaming
    # کالمز کو واضح اور معیاری نام دینا جو ڈیٹا بیس کے لیے مناسب ہوں
    df = df.rename(columns={
        'number': 'surah_number',
        'name': 'name_arabic',
        'englishName': 'name_english',
        'englishNameTranslation': 'english_meaning',
        'numberOfAyahs': 'total_ayahs',
        'revelationType': 'revelation_type'
    })
    
    # ٹیکسٹ کی اضافی اسپیسز (whitespace) صاف کرنا
    df['name_arabic'] = df['name_arabic'].astype(str).str.strip()
    df['name_english'] = df['name_english'].astype(str).str.strip()
    df['english_meaning'] = df['english_meaning'].astype(str).str.strip()
    
    print("\n✓ سورتوں کا DataFrame کامیابی کے ساتھ بن گیا!")
    print(df.head(5)[['surah_number', 'name_arabic', 'name_english', 'total_ayahs', 'revelation_type']])
    
    return df

def build_ayahs_dataframe_for_surahs(surah_numbers=[1, 112, 113, 114]):
    """
    مرحلہ 3 اور 4: مخصوص سورتوں (یا تمام سورتوں) کی آیات، اردو ترجمہ اور آڈیو کا DataFrame بنانا
    ہم نمونے کے طور پر اہم سورتیں (جیسے سورۃ الفاتحہ، اخلاص، فلق، ناس) لے رہے ہیں
    تاکہ عمل تیز رہے، اور مکمل قرآن کے لیے بھی استعمال ہو سکے۔
    """
    print(f"\nآیات کا ڈیٹا حاصل کیا جا رہا ہے (سورتیں: {surah_numbers})...")
    
    all_ayahs = []
    
    for s_num in surah_numbers:
        url = f"https://api.alquran.cloud/v1/surah/{s_num}/editions/quran-uthmani,ur.jalandhry,ar.alafasy"
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()["data"]
            arabic_ayahs = data[0]["ayahs"]
            urdu_ayahs = data[1]["ayahs"]
            audio_ayahs = data[2]["ayahs"]
            
            for i in range(len(arabic_ayahs)):
                all_ayahs.append({
                    "surah_number": s_num,
                    "ayah_number_in_surah": arabic_ayahs[i]["numberInSurah"],
                    "global_ayah_number": arabic_ayahs[i]["number"],
                    "text_arabic": arabic_ayahs[i]["text"].strip(),
                    "text_urdu": urdu_ayahs[i]["text"].strip(),
                    "audio_url": audio_ayahs[i]["audio"].strip()
                })
        else:
            print(f"Error fetching surah {s_num}")
            
    df_ayahs = pd.DataFrame(all_ayahs)
    
    # Data Cleaning: کچھ عربی فونٹس میں شروع میں غیر ضروری کیریکٹرز یا BOM ہوتے ہیں انہیں صاف کرنا
    df_ayahs['text_arabic'] = df_ayahs['text_arabic'].str.replace('\ufeff', '', regex=False)
    df_ayahs['text_urdu'] = df_ayahs['text_urdu'].str.replace('\ufeff', '', regex=False)
    
    print("\n✓ آیات کا DataFrame کامیابی کے ساتھ بن گیا!")
    print(df_ayahs[['surah_number', 'ayah_number_in_surah', 'text_arabic', 'text_urdu']].head(4))
    
    return df_ayahs

if __name__ == "__main__":
    surahs_df = build_surahs_dataframe()
    ayahs_df = build_ayahs_dataframe_for_surahs([1, 112])
    
    # CSV فائلز میں محفوظ کرنا تاکہ تصدیق ہو سکے
    surahs_df.to_csv("D:/Quran_Program_01/surahs_cleaned.csv", index=False, encoding='utf-8-sig')
    ayahs_df.to_csv("D:/Quran_Program_01/ayahs_cleaned.csv", index=False, encoding='utf-8-sig')
    print("\n✓ صاف شدہ ڈیٹا CSV فائلز میں محفوظ ہو گیا!")
