from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import pymysql

app = FastAPI(title="Quran Explorer API")

# Enable CORS so frontend can communicate smoothly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MySQL connection configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "1234",
    "database": "quran_db",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

# Pydantic schemas for assignment completion (PUT/DELETE/POST support)
class AyahCreate(BaseModel):
    surah_number: int
    ayah_number_in_surah: int
    global_ayah_number: Optional[int] = None
    text_arabic: str
    text_urdu: str
    audio_url: Optional[str] = None

class AyahUpdate(BaseModel):
    text_arabic: Optional[str] = None
    text_urdu: Optional[str] = None
    audio_url: Optional[str] = None

# Step 8: GET APIs

@app.get("/api/surahs")
def get_all_surahs():
    """Retrieve all 114 surahs ordered by surah number."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM surahs ORDER BY surah_number ASC")
            return cursor.fetchall()
    finally:
        conn.close()

@app.get("/api/surahs/{surah_number}")
def get_surah_details(surah_number: int):
    """Retrieve metadata of a single surah."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM surahs WHERE surah_number = %s", (surah_number,))
            surah = cursor.fetchone()
            if not surah:
                raise HTTPException(status_code=404, detail="Surah not found")
            return surah
    finally:
        conn.close()

@app.get("/api/surahs/{surah_number}/ayahs")
def get_ayahs_by_surah(surah_number: int):
    """Retrieve all ayahs for a specific surah."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM ayahs 
                WHERE surah_number = %s 
                ORDER BY ayah_number_in_surah ASC
            """, (surah_number,))
            ayahs = cursor.fetchall()
            return ayahs
    finally:
        conn.close()

# Step 9: Search API

import re

def remove_arabic_diacritics(text: str) -> str:
    """Remove Arabic tashkeel/diacritics for flexible text matching."""
    arabic_diacritics = re.compile(r'[\u0617-\u061A\u064B-\u0652\u06D6-\u06ED\u0670\u0671]')
    return arabic_diacritics.sub('', text)

@app.get("/api/search")
def search_quran(q: str = Query(..., min_length=1)):
    """Search by surah number, surah name (Arabic/English), or ayah text (Arabic/Urdu)."""
    raw_query = q.strip()
    conn = get_db_connection()

    try:
        with conn.cursor() as cursor:
            # 1. Check if user entered a Surah Number (e.g., "1", "2", "36", "114")
            if raw_query.isdigit():
                surah_num = int(raw_query)
                if 1 <= surah_num <= 114:
                    cursor.execute("SELECT * FROM surahs WHERE surah_number = %s", (surah_num,))
                    matched_surah = cursor.fetchone()
                    return {
                        "type": "surah_redirect",
                        "surah_number": surah_num,
                        "surah": matched_surah,
                        "query": raw_query
                    }

            # 2. Check if user typed a Surah Name (English or Arabic without tashkeel)
            cursor.execute("SELECT * FROM surahs")
            all_surahs = cursor.fetchall()
            cleaned_query = remove_arabic_diacritics(raw_query).lower()
            user_clean = cleaned_query.replace('-', '').replace("'", "").replace(' ', '')
            if user_clean.startswith('al'):
                user_clean = user_clean[2:]
            if user_clean.endswith('h'):
                user_clean_alt = user_clean[:-1]
            else:
                user_clean_alt = user_clean

            for s in all_surahs:
                s_ar_clean = remove_arabic_diacritics(s['name_arabic']).lower().replace(' ', '')
                s_en_clean = s['name_english'].lower().replace('-', '').replace("'", "").replace(' ', '')
                if s_en_clean.startswith('al'):
                    s_en_clean_no_al = s_en_clean[2:]
                else:
                    s_en_clean_no_al = s_en_clean

                # Match Arabic name or English name or prefix
                if (user_clean in s_ar_clean) or \
                   (user_clean in s_en_clean) or (s_en_clean in user_clean) or \
                   (user_clean_alt in s_en_clean_no_al) or (s_en_clean_no_al in user_clean_alt):
                    return {
                        "type": "surah_redirect",
                        "surah_number": s['surah_number'],
                        "surah": s,
                        "query": raw_query
                    }

            # 3. Search in Ayahs (both Arabic text and Urdu translation)
            search_pattern = f"%{raw_query}%"
            cursor.execute("""
                SELECT a.*, s.name_arabic as surah_name_arabic, s.name_english as surah_name_english
                FROM ayahs a
                JOIN surahs s ON a.surah_number = s.surah_number
                WHERE a.text_arabic LIKE %s OR a.text_urdu LIKE %s
                LIMIT 50
            """, (search_pattern, search_pattern))
            ayah_results = cursor.fetchall()

            return {
                "type": "ayahs_list",
                "query": raw_query,
                "total_results": len(ayah_results),
                "results": ayah_results
            }
    finally:
        conn.close()

# Step 13: CRUD endpoints for assignment requirements (POST / PUT / DELETE)

@app.post("/api/ayahs", status_code=201)
def add_ayah(ayah: AyahCreate):
    """Add a new ayah record."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO ayahs (surah_number, ayah_number_in_surah, global_ayah_number, text_arabic, text_urdu, audio_url)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                ayah.surah_number,
                ayah.ayah_number_in_surah,
                ayah.global_ayah_number,
                ayah.text_arabic,
                ayah.text_urdu,
                ayah.audio_url
            ))
            conn.commit()
            return {"message": "Ayah created successfully", "id": cursor.lastrowid}
    finally:
        conn.close()

@app.put("/api/ayahs/{ayah_id}")
def update_ayah(ayah_id: int, ayah: AyahUpdate):
    """Update an existing ayah."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM ayahs WHERE id = %s", (ayah_id,))
            existing = cursor.fetchone()
            if not existing:
                raise HTTPException(status_code=404, detail="Ayah not found")

            new_arabic = ayah.text_arabic if ayah.text_arabic is not None else existing['text_arabic']
            new_urdu = ayah.text_urdu if ayah.text_urdu is not None else existing['text_urdu']
            new_audio = ayah.audio_url if ayah.audio_url is not None else existing['audio_url']

            sql = """
                UPDATE ayahs 
                SET text_arabic = %s, text_urdu = %s, audio_url = %s
                WHERE id = %s
            """
            cursor.execute(sql, (new_arabic, new_urdu, new_audio, ayah_id))
            conn.commit()
            return {"message": "Ayah updated successfully"}
    finally:
        conn.close()

@app.delete("/api/ayahs/{ayah_id}")
def delete_ayah(ayah_id: int):
    """Delete an ayah by ID."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM ayahs WHERE id = %s", (ayah_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Ayah not found")

            cursor.execute("DELETE FROM ayahs WHERE id = %s", (ayah_id,))
            conn.commit()
            return {"message": "Ayah deleted successfully"}
    finally:
        conn.close()

import requests
from fastapi.responses import StreamingResponse

@app.get("/api/audio/{global_ayah_number}")
def stream_ayah_audio(global_ayah_number: int):
    """Stream audio directly through backend to ensure 100% reliable browser playback."""
    audio_url = f"https://cdn.islamic.network/quran/audio/128/ar.alafasy/{global_ayah_number}.mp3"
    req = requests.get(audio_url, stream=True, headers={"User-Agent": "Mozilla/5.0"})
    if req.status_code == 200:
        return StreamingResponse(req.iter_content(chunk_size=4096), media_type="audio/mpeg")
    raise HTTPException(status_code=404, detail="Audio not found")

# Mount frontend static directory if exists
try:
    app.mount("/", StaticFiles(directory="D:/Quran_Program_01/static", html=True), name="static")
except Exception:
    pass
