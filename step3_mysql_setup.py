import pymysql
import pandas as pd
import requests

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "1234",
    "charset": "utf8mb4"
}

DB_NAME = "quran_db"

def setup_database_and_tables():
    """Create database and tables with utf8mb4 charset for Arabic/Urdu support."""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Step 5: Create Database
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    cursor.execute(f"USE {DB_NAME};")

    # Drop existing tables to start fresh
    cursor.execute("DROP TABLE IF EXISTS ayahs;")
    cursor.execute("DROP TABLE IF EXISTS surahs;")

    # Table 1: surahs
    create_surahs_sql = """
    CREATE TABLE surahs (
        surah_number INT PRIMARY KEY,
        name_arabic VARCHAR(100) NOT NULL,
        name_english VARCHAR(100) NOT NULL,
        english_meaning VARCHAR(150),
        total_ayahs INT NOT NULL,
        revelation_type VARCHAR(20)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    cursor.execute(create_surahs_sql)

    # Table 2: ayahs (with foreign key referencing surahs)
    create_ayahs_sql = """
    CREATE TABLE ayahs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        surah_number INT NOT NULL,
        ayah_number_in_surah INT NOT NULL,
        global_ayah_number INT,
        text_arabic TEXT NOT NULL,
        text_urdu TEXT NOT NULL,
        audio_url VARCHAR(255),
        FOREIGN KEY (surah_number) REFERENCES surahs(surah_number) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    cursor.execute(create_ayahs_sql)

    conn.commit()
    cursor.close()
    conn.close()
    print("Database and tables created successfully.")

def populate_data():
    """Step 6: Insert cleaned Pandas DataFrame data into MySQL."""
    # Read cleaned dataframes
    surahs_df = pd.read_csv("D:/Quran_Program_01/surahs_cleaned.csv")
    ayahs_df = pd.read_csv("D:/Quran_Program_01/ayahs_cleaned.csv")

    conn = pymysql.connect(database=DB_NAME, **DB_CONFIG)
    cursor = conn.cursor()

    # Insert into surahs table
    insert_surah_sql = """
    INSERT INTO surahs (surah_number, name_arabic, name_english, english_meaning, total_ayahs, revelation_type)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    surah_records = [tuple(x) for x in surahs_df.to_numpy()]
    cursor.executemany(insert_surah_sql, surah_records)
    print(f"Inserted {len(surah_records)} surahs into MySQL.")

    # Insert into ayahs table
    insert_ayah_sql = """
    INSERT INTO ayahs (surah_number, ayah_number_in_surah, global_ayah_number, text_arabic, text_urdu, audio_url)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    ayah_records = [tuple(x) for x in ayahs_df.to_numpy()]
    cursor.executemany(insert_ayah_sql, ayah_records)
    print(f"Inserted {len(ayah_records)} ayahs into MySQL.")

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    setup_database_and_tables()
    populate_data()
