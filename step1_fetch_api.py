import requests
import json
import sys

# Ensure UTF-8 output in Windows terminal
sys.stdout.reconfigure(encoding='utf-8')

def fetch_surah_list():
    """
    مرحلہ 1 اور 2:
    تمام سورتوں کی فہرست (Metadata) API سے حاصل کرنا
    """
    url = "https://api.alquran.cloud/v1/surah"
    print(f"Connecting to API: {url} ...")
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print("✓ API سے ڈیٹا کامیابی کے ساتھ مل گیا!")
        
        surahs = data.get("data", [])
        print(f"کل سورتیں: {len(surahs)}")
        
        # پہلی 3 سورتوں کا نمونہ دیکھیں
        print("\n--- نمونہ ڈیٹا (پہلی 3 سورتیں) ---")
        for surah in surahs[:3]:
            print(f"نمبر: {surah['number']} | عربی نام: {surah['name']} | انگریزی: {surah['englishName']} | آیات: {surah['numberOfAyahs']}")
            
        return surahs
    else:
        print(f"API Error: Status Code {response.status_code}")
        return None

def fetch_single_surah_detail(surah_number=1):
    """
    ایک سورۃ کا عربی متن، اردو ترجمہ اور آڈیو ایک ساتھ لینا
    """
    url = f"https://api.alquran.cloud/v1/surah/{surah_number}/editions/quran-uthmani,ur.jalandhry,ar.alafasy"
    print(f"\nسورۃ نمبر {surah_number} کا مکمل ڈیٹا حاصل کیا جا رہا ہے...")
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()["data"]
        arabic_edition = data[0]   # عربی متن
        urdu_edition = data[1]     # اردو ترجمہ
        audio_edition = data[2]    # آڈیو تلاوت
        
        print(f"\nسورۃ: {arabic_edition['name']} ({arabic_edition['englishName']})")
        print(f"کل آیات: {len(arabic_edition['ayahs'])}")
        
        print("\n--- پہلی آیت کا ڈیٹا ---")
        ayah_1_ar = arabic_edition['ayahs'][0]['text']
        ayah_1_ur = urdu_edition['ayahs'][0]['text']
        ayah_1_audio = audio_edition['ayahs'][0]['audio']
        
        print(f"عربی متن: {ayah_1_ar}")
        print(f"اردو ترجمہ: {ayah_1_ur}")
        print(f"آڈیو لنک: {ayah_1_audio}")
    else:
        print("ڈیٹا لانے میں ناکامی۔")

if __name__ == "__main__":
    fetch_surah_list()
    fetch_single_surah_detail(1)
