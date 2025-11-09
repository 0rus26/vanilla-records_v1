import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional

class SQLiteRepository:
    def __init__(self, db_path: str = 'vanilla_records.db', schema_path: str = None):
        self.db_path = Path(db_path)
        if schema_path is None:
            base = Path(__file__).resolve().parent
            schema_path = base / "schema.sql"
        else:
            schema_path = Path(schema_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema(schema_path)

    def _init_schema(self, schema_path: str):
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()
        cur = self.conn.cursor()
        cur.executescript(schema)
        self.conn.commit()

    # ---------- CRUD genéricos ----------
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        cols = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        sql = f'INSERT INTO {table} ({cols}) VALUES ({placeholders})'
        cur = self.conn.cursor()
        cur.execute(sql, tuple(data.values()))
        self.conn.commit()
        return cur.lastrowid

    def update(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        set_clause = ', '.join([f'{k}=?' for k in data])
        where_clause = ' AND '.join([f'{k}=?' for k in where])
        sql = f'UPDATE {table} SET {set_clause} WHERE {where_clause}'
        cur = self.conn.cursor()
        cur.execute(sql, tuple(data.values()) + tuple(where.values()))
        self.conn.commit()
        return cur.rowcount

    def delete(self, table: str, where: Dict[str, Any]) -> int:
        where_clause = ' AND '.join([f'{k}=?' for k in where])
        sql = f'DELETE FROM {table} WHERE {where_clause}'
        cur = self.conn.cursor()
        cur.execute(sql, tuple(where.values()))
        self.conn.commit()
        return cur.rowcount

    def fetch_all(self, table: str) -> List[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute(f'SELECT * FROM {table}')
        return [dict(r) for r in cur.fetchall()]

    def fetch_one(self, table: str, where: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        where_clause = ' AND '.join([f'{k}=?' for k in where])
        sql = f'SELECT * FROM {table} WHERE {where_clause}'
        cur = self.conn.cursor()
        cur.execute(sql, tuple(where.values()))
        row = cur.fetchone()
        return dict(row) if row else None

    def query(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]

    def execute(self, sql: str, params: tuple = ()) -> None:
        cur = self.conn.cursor()
        cur.execute(sql, params)
        self.conn.commit()

    # ---------- Helpers de dominio ----------
    def crear_evento(self, tipo: str, descripcion: str, fecha: str, planta_ids: List[int]) -> int:
        eid = self.insert('eventos', {'tipo': tipo, 'descripcion': descripcion, 'fecha': fecha})
        for pid in planta_ids:
            self.insert('evento_planta', {'evento_id': eid, 'planta_id': pid})
        return eid

    def consumir_lote_en_evento(self, evento_id: int, lote_id: int, cantidad: float):
        # triggers del schema validan stock y descuentan automáticamente
        self.insert('evento_lote', {'evento_id': evento_id, 'lote_id': lote_id, 'cantidad_utilizada': cantidad})

    def resumen_stock(self) -> List[Dict[str, Any]]:
        sql = '''
        SELECT li.id as lote_id, i.nombre as insumo, i.unidad,
               li.cantidad_inicial, li.cantidad_disponible,
               li.precio_unitario, li.fecha_compra
        FROM lotes_insumo li
        JOIN insumos i ON i.id = li.insumo_id
        ORDER BY i.nombre, li.fecha_compra
        '''
        return self.query(sql)

    def trazabilidad_insumo(self, insumo_id: int) -> List[Dict[str, Any]]:
        sql = '''
        SELECT i.nombre, li.id AS lote_id, li.cantidad_inicial, li.cantidad_disponible,
               li.precio_unitario, li.fecha_compra,
               el.evento_id, el.cantidad_utilizada
        FROM insumos i
        JOIN lotes_insumo li ON li.insumo_id = i.id
        LEFT JOIN evento_lote el ON el.lote_id = li.id
        WHERE i.id = ?
        ORDER BY li.fecha_compra
        '''
        return self.query(sql, (insumo_id,))

    def resumen_ventas(self) -> List[Dict[str, Any]]:
        sql = '''
        SELECT v.id, tp.nombre as producto, v.fecha, v.comprador, v.cantidad_vendida, v.unidad,
               v.precio_unitario, (COALESCE(v.cantidad_vendida,0)*COALESCE(v.precio_unitario,0)) AS ingreso
        FROM ventas v
        LEFT JOIN tipos_producto tp ON tp.id = v.tipo_producto_id
        ORDER BY v.fecha DESC, v.id DESC
        '''
        return self.query(sql)

    def close(self):
        self.conn.close()
