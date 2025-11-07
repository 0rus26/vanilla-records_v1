import os
import subprocess
from pathlib import Path
from textwrap import dedent

PROJECT_NAME = "vanilla_records"
VENV_PATH = Path("venv")
DB_PATH = Path("vanilla_records.db")

def ensure_structure():
    print("🏗️ Verificando estructura del proyecto...\n")
    folders = [
        f"{PROJECT_NAME}/src/domain/entities",
        f"{PROJECT_NAME}/src/domain/services",
        f"{PROJECT_NAME}/src/application/use_cases",
        f"{PROJECT_NAME}/src/infrastructure/db",
        f"{PROJECT_NAME}/src/infrastructure/adapters",
        f"{PROJECT_NAME}/src/infrastructure/utils",
        f"{PROJECT_NAME}/src/config",
        f"{PROJECT_NAME}/tests",
    ]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        Path(folder, "__init__.py").touch()
        print(f"📁 OK {folder}")
    print("\n✅ Estructura verificada / actualizada.\n")

def write_schema_v3_2():
    print("🧱 Escribiendo schema v3.2...\n")
    schema = dedent("""\
    -- ================================
    -- Vanilla Records DB v3.2 (corregido)
    -- ================================

    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS proveedores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        telefono TEXT,
        correo TEXT,
        direccion TEXT
    );

    CREATE TABLE IF NOT EXISTS plantas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE NOT NULL,
        nombre_comun TEXT,
        especie TEXT,
        variedad TEXT,
        fecha_siembra TEXT,
        ubicacion TEXT,
        gps TEXT,
        proveedor_id INTEGER,
        observaciones TEXT,
        estado TEXT DEFAULT 'viva',
        FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
    );

    CREATE TABLE IF NOT EXISTS eventos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL,
        descripcion TEXT,
        fecha TEXT,
        costo_total REAL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS evento_planta (
        evento_id INTEGER,
        planta_id INTEGER,
        PRIMARY KEY (evento_id, planta_id),
        FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE,
        FOREIGN KEY (planta_id) REFERENCES plantas(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS insumos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        tipo TEXT,
        unidad TEXT,
        descripcion TEXT
    );

    CREATE TABLE IF NOT EXISTS lotes_insumo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        insumo_id INTEGER NOT NULL,
        proveedor_id INTEGER,
        cantidad_inicial REAL NOT NULL,
        cantidad_disponible REAL NOT NULL,
        unidad TEXT DEFAULT 'g',        -- ✅ nuevo campo agregado
        precio_unitario REAL,
        fecha_compra TEXT,
        fecha_vencimiento TEXT,
        observaciones TEXT,
        FOREIGN KEY (insumo_id) REFERENCES insumos(id),
        FOREIGN KEY (proveedor_id) REFERENCES proveedores(id),
        CHECK (cantidad_inicial >= 0),
        CHECK (cantidad_disponible >= 0)
    );

    CREATE TABLE IF NOT EXISTS lote_media (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lote_id INTEGER,
        file_path TEXT,
        file_type TEXT,
        drive_link TEXT,
        FOREIGN KEY (lote_id) REFERENCES lotes_insumo(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS evento_lote (
        evento_id INTEGER,
        lote_id INTEGER,
        cantidad_utilizada REAL NOT NULL,
        PRIMARY KEY (evento_id, lote_id),
        FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE,
        FOREIGN KEY (lote_id) REFERENCES lotes_insumo(id) ON DELETE CASCADE,
        CHECK (cantidad_utilizada > 0)
    );

    CREATE TRIGGER IF NOT EXISTS trg_evento_lote_check_stock
    BEFORE INSERT ON evento_lote
    FOR EACH ROW
    BEGIN
        SELECT CASE
            WHEN (SELECT cantidad_disponible FROM lotes_insumo WHERE id = NEW.lote_id) < NEW.cantidad_utilizada
            THEN RAISE(ABORT, 'Stock insuficiente en el lote')
        END;
    END;

    CREATE TRIGGER IF NOT EXISTS trg_evento_lote_descuenta
    AFTER INSERT ON evento_lote
    FOR EACH ROW
    BEGIN
        UPDATE lotes_insumo
        SET cantidad_disponible = cantidad_disponible - NEW.cantidad_utilizada
        WHERE id = NEW.lote_id;
    END;

    CREATE TABLE IF NOT EXISTS workers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        telefono TEXT,
        rol TEXT
    );

    CREATE TABLE IF NOT EXISTS actividades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        descripcion TEXT
    );

    CREATE TABLE IF NOT EXISTS actividad_evento (
        actividad_id INTEGER,
        evento_id INTEGER,
        worker_id INTEGER,
        costo REAL,
        PRIMARY KEY (actividad_id, evento_id, worker_id),
        FOREIGN KEY (actividad_id) REFERENCES actividades(id) ON DELETE CASCADE,
        FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE,
        FOREIGN KEY (worker_id) REFERENCES workers(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS evento_media (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        evento_id INTEGER,
        file_path TEXT,
        file_type TEXT,
        drive_link TEXT,
        FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS tipos_producto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT
    );

    CREATE TABLE IF NOT EXISTS cosechas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo_producto_id INTEGER NOT NULL,
        evento_id INTEGER,
        planta_id INTEGER,
        fecha_recoleccion TEXT NOT NULL,
        cantidad REAL,
        unidad TEXT,
        calidad TEXT,
        humedad_porcentaje REAL,
        observaciones TEXT,
        FOREIGN KEY (tipo_producto_id) REFERENCES tipos_producto(id),
        FOREIGN KEY (evento_id) REFERENCES eventos(id),
        FOREIGN KEY (planta_id) REFERENCES plantas(id)
    );

    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cosecha_id INTEGER,
        tipo_producto_id INTEGER,
        fecha TEXT NOT NULL,
        comprador TEXT,
        destino TEXT,
        cantidad_vendida REAL,
        unidad TEXT,
        precio_unitario REAL,
        moneda TEXT DEFAULT 'COP',
        metodo_pago TEXT,
        tipo_operacion TEXT DEFAULT 'venta',
        observaciones TEXT,
        FOREIGN KEY (cosecha_id) REFERENCES cosechas(id),
        FOREIGN KEY (tipo_producto_id) REFERENCES tipos_producto(id)
    );

    CREATE TABLE IF NOT EXISTS venta_media (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venta_id INTEGER,
        file_path TEXT,
        file_type TEXT,
        drive_link TEXT,
        FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE
    );
    """)
    path = Path(f"{PROJECT_NAME}/src/infrastructure/db/schema.sql")
    path.write_text(schema, encoding="utf-8")
    print(f"📄 Esquema v3.2 corregido escrito en {path}\n")

def write_repo():
    print("💾 Escribiendo repositorio SQLite...\n")
    repo = dedent("""\
    import sqlite3
    from pathlib import Path
    from typing import Dict, Any, List, Optional

    class SQLiteRepository:
        def __init__(self, db_path: str = 'vanilla_records.db', schema_path: str = 'vanilla_records/src/infrastructure/db/schema.sql'):
            self.db_path = Path(db_path)
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
    """)
    path = Path(f"{PROJECT_NAME}/src/infrastructure/db/db_sqlite_repository.py")
    path.write_text(repo, encoding="utf-8")
    print(f"📄 Repositorio escrito en {path}\n")

def write_tests():
    print("🧪 Escribiendo pruebas v3.2...\n")
    tests_dir = Path(f"{PROJECT_NAME}/tests")
    tests_dir.mkdir(parents=True, exist_ok=True)

    # 1) Núcleo: proveedores/plantas/insumos/lotes/evento consumo múltiple
    (tests_dir / "test_v3_2_core.py").write_text(dedent("""\
    import os
    from src.infrastructure.db.db_sqlite_repository import SQLiteRepository

    DB = 'vanilla_records.db'

    def setup_module():
        if os.path.exists(DB):
            os.remove(DB)

    def test_core_flow():
        repo = SQLiteRepository(DB)
        # Proveedores
        prov1 = repo.insert('proveedores', {'nombre':'Agro A','telefono':'111'})
        prov2 = repo.insert('proveedores', {'nombre':'Agro B','telefono':'222'})
        # Plantas (10)
        planta_ids = []
        for i in range(1, 11):
            planta_ids.append(repo.insert('plantas', {
                'codigo': f'PLT{str(i).zfill(3)}',
                'nombre_comun': 'Vainilla',
                'especie': 'Vanilla sp.',
                'variedad': 'planifolia' if i<=3 else 'pompona',
                'fecha_siembra': '2025-03-10',
                'ubicacion': 'Lote 1' if i<=5 else 'Lote 2',
                'gps': '7.390N,-73.495W',
                'proveedor_id': prov2 if i<=3 else prov1,
                'observaciones': 'test'
            }))
        assert len(planta_ids)==10

        # Insumos
        cal = repo.insert('insumos', {'nombre':'Cal agrícola','tipo':'enmienda','unidad':'g','descripcion':'Neutraliza acidez'})
        safer = repo.insert('insumos', {'nombre':'SaferSoil','tipo':'bio','unidad':'g','descripcion':'Mejora suelo'})
        lombr = repo.insert('insumos', {'nombre':'Lombrinaza','tipo':'abono','unidad':'g','descripcion':'Orgánico'})

        # Lotes (precios/días distintos)
        lote_cal = repo.insert('lotes_insumo', {
            'insumo_id': cal, 'proveedor_id': prov1,
            'cantidad_inicial': 60000, 'cantidad_disponible': 60000,
            'precio_unitario': 60_000/1000, 'fecha_compra':'2025-11-06'
        })
        lote_safer = repo.insert('lotes_insumo', {
            'insumo_id': safer, 'proveedor_id': prov1,
            'cantidad_inicial': 1000, 'cantidad_disponible': 1000,
            'precio_unitario': 60_000/1000, 'fecha_compra':'2025-11-06'
        })
        lote_lombr = repo.insert('lotes_insumo', {
            'insumo_id': lombr, 'proveedor_id': prov2,
            'cantidad_inicial': 100000, 'cantidad_disponible': 100000,
            'precio_unitario': 40_000/1000, 'fecha_compra':'2025-11-06'
        })

        # Evento: aplicación a 10 plantas (100 g cal, 2 g Safer, 200 g lombrinaza por planta)
        eid = repo.crear_evento('abonado','Aplicación trio','2025-11-07', planta_ids)
        repo.consumir_lote_en_evento(eid, lote_cal, 100*10)
        repo.consumir_lote_en_evento(eid, lote_safer, 2*10)
        repo.consumir_lote_en_evento(eid, lote_lombr, 200*10)

        stock = {r['lote_id']: r for r in repo.resumen_stock()}
        assert stock[lote_cal]['cantidad_disponible'] == 60000 - 1000
        assert stock[lote_safer]['cantidad_disponible'] == 1000 - 20
        assert stock[lote_lombr]['cantidad_disponible'] == 100000 - 2000

        # Validar asociaciones planta-evento
        filas = repo.query('SELECT count(*) as c FROM evento_planta WHERE evento_id=?',(eid,))
        assert filas[0]['c']==10

        repo.close()
    """), encoding="utf-8")

    # 2) Inventario: overconsume debe fallar, media de lote, resumen de stock
    (tests_dir / "test_v3_2_inventory.py").write_text(dedent("""\
    import os
    import pytest
    from src.infrastructure.db.db_sqlite_repository import SQLiteRepository

    DB = 'vanilla_records.db'

    def setup_module():
        if os.path.exists(DB):
            os.remove(DB)

    def test_stock_and_media_and_overconsume():
        repo = SQLiteRepository(DB)
        prov = repo.insert('proveedores', {'nombre':'Prov','telefono':'999'})
        insu = repo.insert('insumos', {'nombre':'Cal','tipo':'enmienda','unidad':'g'})
        lote = repo.insert('lotes_insumo', {
            'insumo_id': insu, 'proveedor_id': prov,
            'cantidad_inicial': 5000, 'cantidad_disponible': 5000,
            'precio_unitario': 60_000/1000, 'fecha_compra':'2025-11-06'
        })
        # Media de lote (factura)
        repo.insert('lote_media', {'lote_id': lote, 'file_path':'facturas/cal_1106.pdf','file_type':'pdf'})
        # Evento de 1000g
        p = repo.insert('plantas', {'codigo':'P001'})
        e = repo.crear_evento('abonado','test','2025-11-07',[p])
        repo.consumir_lote_en_evento(e, lote, 1000)
        # Intento de consumo excesivo (debería fallar por trigger)
        with pytest.raises(Exception):
            repo.consumir_lote_en_evento(e, lote, 5000)  # queda 4000 disp; 5000 > 4000 => abort

        st = repo.resumen_stock()
        assert any(r['cantidad_disponible']==4000 for r in st)
        repo.close()
    """), encoding="utf-8")

    # 3) Producción/Ventas multi-producto
    (tests_dir / "test_v3_2_sales.py").write_text(dedent("""\
    import os
    from src.infrastructure.db.db_sqlite_repository import SQLiteRepository

    DB = 'vanilla_records.db'

    def setup_module():
        if os.path.exists(DB):
            os.remove(DB)

    def test_production_and_sales():
        repo = SQLiteRepository(DB)

        # Tipos de producto
        t_esqueje = repo.insert('tipos_producto', {'nombre':'Esqueje'})
        t_planta  = repo.insert('tipos_producto', {'nombre':'Planta'})
        t_verde   = repo.insert('tipos_producto', {'nombre':'Vaina verde'})
        t_curada  = repo.insert('tipos_producto', {'nombre':'Vaina curada'})

        # Plantas base
        p1 = repo.insert('plantas', {'codigo':'PLTX01'})
        p2 = repo.insert('plantas', {'codigo':'PLTX02'})

        # Cosechas
        c1 = repo.insert('cosechas', {
            'tipo_producto_id': t_verde, 'planta_id': p1,
            'fecha_recoleccion':'2025-12-10','cantidad': 1.2,'unidad':'kg','calidad':'A'
        })
        c2 = repo.insert('cosechas', {
            'tipo_producto_id': t_esqueje, 'planta_id': p2,
            'fecha_recoleccion':'2025-12-11','cantidad': 10,'unidad':'un','calidad':'B'
        })

        # Ventas: 1) parte de cosecha (verde) 2) venta directa por tipo (curada)
        v1 = repo.insert('ventas', {
            'cosecha_id': c1, 'fecha':'2025-12-15','comprador':'Cliente A',
            'cantidad_vendida': 0.5, 'unidad':'kg', 'precio_unitario': 1200000
        })
        v2 = repo.insert('ventas', {
            'tipo_producto_id': t_curada, 'fecha':'2026-01-02','comprador':'Cliente B',
            'cantidad_vendida': 0.3, 'unidad':'kg', 'precio_unitario': 3500000
        })
        # Evidencia
        repo.insert('venta_media', {'venta_id': v1, 'file_path':'docs/factura_v1.pdf','file_type':'pdf'})

        resumen = repo.resumen_ventas()
        assert len(resumen)>=2
        ingresos = sum([r['ingreso'] for r in resumen])
        assert ingresos > 0
        repo.close()
    """), encoding="utf-8")

    print("✅ Pruebas v3.2 generadas.\n")

def reset_database():
    if DB_PATH.exists():
        DB_PATH.unlink()
        print("🗑️ Base de datos eliminada (reset).")
    print("🧩 Se recreará al instanciar el repositorio.\n")

def setup_environment():
    print("🔧 Verificando entorno virtual y deps...\n")
    if not VENV_PATH.exists():
        subprocess.run(["python", "-m", "venv", "venv"])
        print("✅ Entorno virtual creado.")
    subprocess.run(["venv\\Scripts\\python", "-m", "pip", "install", "--upgrade", "pip"])
    packages = ["pytest"]
    subprocess.run(["venv\\Scripts\\pip", "install", *packages])
    print("✅ Dependencias listas.\n")

def write_readme_notes():
    readme = dedent(f"""\
    # Vanilla-Records v3.2 🌿

    Esta versión añade:
    - Inventario por **lotes** con **evidencias** (facturas/fotos/videos).
    - **Cosechas** (producción) y **ventas** (salidas del sistema).
    - Triggers de control de stock y helpers de consultas.

    ## Cómo ejecutar
    1. `python setup_vanilla_records_v3_2.py`
    2. Activar venv si hace falta (Windows CMD): `venv\\Scripts\\activate`
    3. `pytest -q vanilla_records/tests`
    """)
    Path("README.md").write_text(readme, encoding="utf-8")
    print("📝 README actualizado.\n")

if __name__ == "__main__":
    ensure_structure()
    write_schema_v3_2()
    write_repo()
    write_tests()
    reset_database()
    setup_environment()
    write_readme_notes()
    print("🎉 Vanilla-Records v3.2 listo. Ejecuta:  venv\\Scripts\\python -m pytest -q vanilla_records/tests")
