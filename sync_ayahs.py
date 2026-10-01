import pymysql
import requests

# Fetch and store ayahs for popular surahs to ensure full testability out-of-the-box
POPULAR_SURAHS = [1, 36, 55, 67, 112, 113, 114]

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "1234",
    "database": "quran_db",
    "charset": "utf8mb4"
}

def sync_popular_surahs():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    for s_num in POPULAR_SURAHS:
        cursor.execute("SELECT COUNT(*) FROM ayahs WHERE surah_number = %s", (s_num,))
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"Surah {s_num} already populated ({count} ayahs). Skipping.")
            continue

        print(f"Fetching ayahs for Surah {s_num} from API...")
        url = f"https://api.alquran.cloud/v1/surah/{s_num}/editions/quran-uthmani,ur.jalandhry,ar.alafasy"
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()["data"]
            arabic_ayahs = data[0]["ayahs"]
            urdu_ayahs = data[1]["ayahs"]
            audio_ayahs = data[2]["ayahs"]

            records = []
            for i in range(len(arabic_ayahs)):
                records.append((
                    s_num,
                    arabic_ayahs[i]["numberInSurah"],
                    arabic_ayahs[i]["number"],
                    arabic_ayahs[i]["text"].replace('\ufeff', '').strip(),
                    urdu_ayahs[i]["text"].replace('\ufeff', '').strip(),
                    audio_ayahs[i]["audio"].strip()
                ))

            insert_sql = """
                INSERT INTO ayahs (surah_number, ayah_number_in_surah, global_ayah_number, text_arabic, text_urdu, audio_url)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(insert_sql, records)
            conn.commit()
            print(f"Inserted {len(records)} ayahs for Surah {s_num}.")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    sync_popular_surahs()
