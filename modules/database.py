
import sqlite3

DATABASE_NAME = "smartcrop.db"


def create_database():
    with sqlite3.connect(DATABASE_NAME) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS sensor_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                temperature REAL,
                humidity REAL,
                soil_moisture REAL,
                leaf_wetness REAL,
                system_status TEXT
            )
        """)


def save_sensor_data(data, status):
    with sqlite3.connect(DATABASE_NAME) as connection:
        connection.execute("""
            INSERT INTO sensor_records (
                timestamp,
                temperature,
                humidity,
                soil_moisture,
                leaf_wetness,
                system_status
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["timestamp"],
            data["temperature"],
            data["humidity"],
            data["soil_moisture"],
            data["leaf_wetness"],
            status
        ))


def get_latest_record():
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.execute("""
            SELECT * FROM sensor_records
            ORDER BY id DESC
            LIMIT 1
        """)
        return cursor.fetchone()


def get_record_count():
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.execute("""
            SELECT COUNT(*) FROM sensor_records
        """)
        return cursor.fetchone()[0]


def get_recent_records(limit=100):
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.execute("""
            SELECT * FROM sensor_records
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()


def get_all_records():
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.execute("""
            SELECT * FROM sensor_records
            ORDER BY id DESC
        """)
        return cursor.fetchall()
