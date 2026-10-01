import pymysql
import sys

sys.stdout.reconfigure(encoding='utf-8')

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "1234",
    "charset": "utf8mb4"
}

def test_connection():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        print("MySQL connected successfully!")
        conn.close()
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
