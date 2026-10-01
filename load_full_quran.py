import pymysql
import requests
import sys

# Configure stdout
sys.stdout.reconfigure(encoding='utf-8')

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "1234",
    "database": "quran_db",
    "charset": "utf8mb4"
}

def sync_all_114_surahs():
    print("Connecting to MySQL...")
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Step 1: Ensure Tables exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS surahs (
            surah_number INT PRIMARY KEY,
            name_arabic VARCHAR(100) NOT NULL,
            name_english VARCHAR(100) NOT NULL,
            english_meaning VARCHAR(150),
            total_ayahs INT NOT NULL,
            revelation_type VARCHAR(20)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ayahs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            surah_number INT NOT NULL,
            ayah_number_in_surah INT NOT NULL,
            global_ayah_number INT,
            text_arabic TEXT NOT NULL,
            text_urdu TEXT NOT NULL,
            audio_url VARCHAR(255),
            KEY (surah_number),
            FOREIGN KEY (surah_number) REFERENCES surahs(surah_number) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    # Check how many ayahs already exist
    cursor.execute("SELECT COUNT(*) FROM ayahs")
    current_count = cursor.fetchone()[0]
    print(f"Current ayahs in database: {current_count}")

    if current_count >= 6236:
        print("All 6,236 ayahs already loaded! No download needed.")
        cursor.close()
        conn.close()
        return

    print("Fetching Arabic text of all 114 Surahs...")
    res_ar = requests.get("https://api.alquran.cloud/v1/quran/quran-uthmani")
    surahs_ar = res_ar.json()["data"]["surahs"]

    print("Fetching Urdu translation of all 114 Surahs...")
    res_ur = requests.get("https://api.alquran.cloud/v1/quran/ur.jalandhry")
    surahs_ur = res_ur.json()["data"]["surahs"]

    # Clear old partial ayahs to avoid duplicates
    cursor.execute("DELETE FROM ayahs")
    conn.commit()

    # Insert Surahs metadata if empty
    cursor.execute("SELECT COUNT(*) FROM surahs")
    if cursor.fetchone()[0] < 114:
        cursor.execute("DELETE FROM surahs")
        surah_tuples = []
        for s in surahs_ar:
            surah_tuples.append((
                s["number"],
                s["name"],
                s["englishName"],
                s["englishNameTranslation"],
                len(s["ayahs"]),
                s["revelationType"]
            ))
        cursor.executemany("""
            INSERT INTO surahs (surah_number, name_arabic, name_english, english_meaning, total_ayahs, revelation_type)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, surah_tuples)
        conn.commit()
        print("Surahs metadata loaded (114 surahs).")

    # Build and bulk insert all 6,236 ayahs
    print("Preparing all 6,236 ayahs with Arabic, Urdu and Audio links...")
    all_ayah_records = []

    for s_idx in range(len(surahs_ar)):
        s_ar = surahs_ar[s_idx]
        s_ur = surahs_ur[s_idx]
        s_num = s_ar["number"]

        for a_idx in range(len(s_ar["ayahs"])):
            ayah_ar = s_ar["ayahs"][a_idx]
            ayah_ur = s_ur["ayahs"][a_idx]
            global_num = ayah_ar["number"]
            num_in_surah = ayah_ar["numberInSurah"]

            # Reliable high-speed CDN audio URL (Alafasy)
            audio_link = f"https://cdn.islamic.network/quran/audio/128/ar.alafasy/{global_num}.mp3"

            ar_text = ayah_ar["text"].replace('\ufeff', '').strip()
            ur_text = ayah_ur["text"].replace('\ufeff', '').strip()

            all_ayah_records.append((
                s_num,
                num_in_surah,
                global_num,
                ar_text,
                ur_text,
                audio_link
            ))

    print(f"Total ayahs prepared: {len(all_ayah_records)}")
    print("Inserting into MySQL database...")

    insert_sql = """
        INSERT INTO ayahs (surah_number, ayah_number_in_surah, global_ayah_number, text_arabic, text_urdu, audio_url)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    cursor.executemany(insert_sql, all_ayah_records)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM ayahs")
    final_count = cursor.fetchone()[0]
    print(f"SUCCESS: Total {final_count} ayahs successfully stored in MySQL database!")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    sync_all_114_surahs()
