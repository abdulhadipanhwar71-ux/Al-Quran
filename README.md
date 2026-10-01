# القرآن الکریم - Quran Explorer & Study Web Application

A professional, high-performance Quran exploration web application built step-by-step using **Python, Pandas, MySQL, FastAPI**, and a responsive **Islamic-themed frontend** (HTML5, CSS3, JavaScript).

---

## 🌟 Key Features

- **Authentic Scripture:** Complete 114 Surahs and 6,236 Ayahs in Madinah Uthmani script (`quran-uthmani`).
- **Renowned Urdu Translation:** Authentic translation by Maulana Fateh Muhammad Jalandhry (`ur.jalandhry`).
- **High-Quality Audio Recitation:** Verse-by-verse recitation by Sheikh Mishary Rashid Alafasy.
- **Intelligent Search Engine:** 
  - Search by Surah number (e.g. `2`, `36`, `114`)
  - Search by Surah name in English (e.g. `Baqarah`, `Yaseen`, `Rahman`)
  - Search by Surah name in Arabic or Urdu (e.g. `البقرة`, `یس`, `رحمن`)
  - Full-text search across Quranic verses and translations (e.g. `جنت`, `صبر`).
- **Interactive Controls:** Seamless Surah selector dropdown, Next / Previous navigation, and audio playback bar.
- **Clean RESTful API:** Built on FastAPI with full GET, Search, and CRUD endpoints (`POST`, `PUT`, `DELETE`).
- **Interactive API Documentation:** Built-in Swagger UI at `/docs`.

---

## 🏗️ Architecture & Data Pipeline

```
[Al-Quran Cloud API] 
         │
         ▼ (Step 1 & 2: Requests / JSON Extraction)
[Pandas DataFrames] 
         │
         ▼ (Step 3 & 4: Data Cleaning, Structuring, Validation)
[MySQL Database] (quran_db: surahs & ayahs tables with utf8mb4)
         │
         ▼ (Step 5, 6 & 7: PyMySQL & Relational Queries)
[FastAPI Backend] 
         │
         ▼ (Step 8, 9 & 13: RESTful Endpoints & Audio Stream Proxy)
[Frontend UI] (HTML5, Responsive CSS3, Vanilla JS)
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- MySQL Server (Localhost)

### 2. Clone Repository & Install Dependencies
```bash
git clone https://github.com/your-username/your-quran-repo.git
cd Quran_Program_01
pip install -r requirements.txt
```

### 3. Database Setup & Data Ingestion
Make sure MySQL is running with your credentials, then execute:
```bash
python load_full_quran.py
```
*This populates all 114 Surahs and 6,236 Ayahs into MySQL database.*

### 4. Run the Application
```bash
python -m uvicorn main:app --reload
```

Open your browser at:
👉 **`http://127.0.0.1:8000`**

Explore API documentation at:
👉 **`http://127.0.0.1:8000/docs`**

---

## 📜 License & Acknowledgements
- Quranic text and translation provided via Al-Quran Cloud API.
- Recitation audio by Sheikh Mishary Rashid Alafasy.
- Built for educational, open-source, and authentic Quranic study.
