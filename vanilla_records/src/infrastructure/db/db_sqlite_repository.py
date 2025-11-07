import sqlite3
from pathlib import Path

class SQLiteRepository:
    def __init__(self, db_path='vanilla_records.db', schema_path='src/infrastructure/db/schema.sql'):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_schema(schema_path)

    def _create_schema(self, schema_path):
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()
        cur = self.conn.cursor()
        cur.executescript(schema)
        self.conn.commit()

    def insert(self, table: str, data: dict):
        cols = ', '.join(data.keys())
        vals = tuple(data.values())
        placeholders = ', '.join(['?'] * len(data))
        sql = f'INSERT INTO {table} ({cols}) VALUES ({placeholders})'
        cur = self.conn.cursor()
        cur.execute(sql, vals)
        self.conn.commit()
        return cur.lastrowid

    def update(self, table: str, data: dict, where: dict):
        set_clause = ', '.join([f'{k}=?' for k in data.keys()])
        where_clause = ' AND '.join([f'{k}=?' for k in where.keys()])
        sql = f'UPDATE {table} SET {set_clause} WHERE {where_clause}'
        cur = self.conn.cursor()
        cur.execute(sql, tuple(data.values()) + tuple(where.values()))
        self.conn.commit()

    def delete(self, table: str, where: dict):
        where_clause = ' AND '.join([f'{k}=?' for k in where.keys()])
        sql = f'DELETE FROM {table} WHERE {where_clause}'
        cur = self.conn.cursor()
        cur.execute(sql, tuple(where.values()))
        self.conn.commit()

    def fetch_all(self, table: str):
        cur = self.conn.cursor()
        cur.execute(f'SELECT * FROM {table}')
        return [dict(row) for row in cur.fetchall()]

    def fetch_one(self, table: str, where: dict):
        where_clause = ' AND '.join([f'{k}=?' for k in where.keys()])
        sql = f'SELECT * FROM {table} WHERE {where_clause}'
        cur = self.conn.cursor()
        cur.execute(sql, tuple(where.values()))
        row = cur.fetchone()
        return dict(row) if row else None

    def close(self):
        self.conn.close()
