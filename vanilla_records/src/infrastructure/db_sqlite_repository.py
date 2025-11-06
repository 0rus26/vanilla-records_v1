import sqlite3
from pathlib import Path

DB_PATH = Path("vanilla_records.db")

class SQLiteRepository:
    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        cur = self.conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            planta_id TEXT,
            tipo TEXT,
            descripcion TEXT,
            fecha TEXT,
            media_path TEXT
        )
        """)
        self.conn.commit()

    def guardar_evento(self, evento_dict):
        cur = self.conn.cursor()
        cur.execute("""
        INSERT INTO eventos (planta_id, tipo, descripcion, fecha, media_path)
        VALUES (?, ?, ?, ?, ?)
        """, (
            evento_dict["planta_id"],
            evento_dict["tipo"],
            evento_dict["descripcion"],
            evento_dict["fecha"],
            ",".join(evento_dict["media_path"])
        ))
        self.conn.commit()

    def listar_eventos(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM eventos")
        return cur.fetchall()
