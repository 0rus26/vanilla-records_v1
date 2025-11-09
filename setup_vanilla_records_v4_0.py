# setup_vanilla_records_v4_0_full.py
import os
import json
import subprocess
from pathlib import Path
from textwrap import dedent

# =========================
# Configuración general
# =========================
PROJECT_NAME = "vanilla_records"
VENV_PATH = Path("venv")
DB_PATH = Path("vanilla_records.db")

# Rutas clave dentro del proyecto
SRC_DIR = Path(f"{PROJECT_NAME}/src")
CONFIG_DIR = SRC_DIR / "config"
DB_DIR = SRC_DIR / "infrastructure" / "db"
DRIVE_DIR = SRC_DIR / "infrastructure" / "drive"
ADAPTERS_DIR = SRC_DIR / "infrastructure" / "adapters"
UTILS_DIR = SRC_DIR / "infrastructure" / "utils"
TESTS_DIR = Path(f"{PROJECT_NAME}/tests")
TESTS_UNIT_DIR = TESTS_DIR / "unit"
TESTS_INTEGRATION_DIR = TESTS_DIR / "integration"

CREDENTIALS_JSON = CONFIG_DIR / "google_drive_credentials.json"
DRIVE_CONFIG_JSON = CONFIG_DIR / "drive_config.json"
PYTEST_INI = Path(f"{PROJECT_NAME}/pytest.ini")
ROOT_GITIGNORE = Path(".gitignore")

# =========================
# Helpers
# =========================
def ensure_structure():
    print("🏗️ Verificando estructura del proyecto...\n")
    folders = [
        f"{PROJECT_NAME}",
        f"{PROJECT_NAME}/src",
        f"{PROJECT_NAME}/src/domain",
        f"{PROJECT_NAME}/src/domain/entities",
        f"{PROJECT_NAME}/src/domain/services",
        f"{PROJECT_NAME}/src/application",
        f"{PROJECT_NAME}/src/application/use_cases",
        f"{PROJECT_NAME}/src/infrastructure",
        f"{PROJECT_NAME}/src/infrastructure/db",
        f"{PROJECT_NAME}/src/infrastructure/drive",
        f"{PROJECT_NAME}/src/infrastructure/adapters",
        f"{PROJECT_NAME}/src/infrastructure/utils",
        f"{PROJECT_NAME}/src/config",
        f"{PROJECT_NAME}/tests",
        f"{PROJECT_NAME}/tests/unit",
        f"{PROJECT_NAME}/tests/integration",
    ]
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)
        # Crear __init__.py para que los imports relativos funcionen
        if folder.startswith(f"{PROJECT_NAME}/src"):
            init_py = Path(folder) / "__init__.py"
            if not init_py.exists():
                init_py.write_text("", encoding="utf-8")
        print(f"📁 OK {folder}")
    print("\n✅ Estructura verificada / actualizada.\n")


def write_gitignore():
    print("🛡️ Asegurando .gitignore...\n")
    base_lines = [
        "# === Vanilla Records ===",
        ".venv/",
        "venv/",
        "__pycache__/",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        "*.db",
        "*.sqlite",
        ".DS_Store",
        # Credenciales y configs sensibles
        f"{PROJECT_NAME}/src/config/google_drive_credentials.json",
        f"{PROJECT_NAME}/src/config/google_oauth_client_secret.json",
        f"{PROJECT_NAME}/src/config/google_oauth_token.json",
        # Artifacts de tests
        ".pytest_cache/",
        ".coverage",
        "htmlcov/",
    ]
    if ROOT_GITIGNORE.exists():
        current = ROOT_GITIGNORE.read_text(encoding="utf-8").splitlines()
    else:
        current = []
    # Merge conservador
    with ROOT_GITIGNORE.open("a", encoding="utf-8") as f:
        for line in base_lines:
            if line not in current:
                f.write(line + "\n")
    print("✅ .gitignore listo.\n")


def write_credentials_template():
    print("🔐 Revisando plantilla de credenciales Google Drive...\n")
    if not CREDENTIALS_JSON.exists():
        template = {
            "type": "service_account",
            "project_id": "tu-proyecto",
            "private_key_id": "XXXX",
            "private_key": "-----BEGIN PRIVATE KEY-----\\nTU_LLAVE\\n-----END PRIVATE KEY-----\\n",
            "client_email": "service-account@tu-proyecto.iam.gserviceaccount.com",
            "client_id": "1234567890",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/service-account%40tu-proyecto.iam.gserviceaccount.com"
        }
        CREDENTIALS_JSON.write_text(json.dumps(template, indent=2), encoding="utf-8")
        print(f"🧾 Plantilla creada en {CREDENTIALS_JSON}")
    else:
        print("🔎 Ya existe google_drive_credentials.json (no se modifica).")
    print("✅ Plantilla de credenciales OK.\n")


def write_drive_config():
    print("⚙️ Revisando drive_config.json...\n")
    default_cfg = {
        "use_shared_drive": True,
        "shared_drive_id": "0AGWFWZLNB-dXUk9PVA",  # tu Shared Drive ID (ya validado)
        "default_folder_name": "VanillaRecords_Uploads",
        "default_mime_fallback": "application/octet-stream"
    }
    if not DRIVE_CONFIG_JSON.exists():
        DRIVE_CONFIG_JSON.write_text(json.dumps(default_cfg, indent=2), encoding="utf-8")
        print(f"🧾 Config creada en {DRIVE_CONFIG_JSON}")
    else:
        print("🔎 Ya existe drive_config.json (no se modifica).")
    print("✅ Config de Drive OK.\n")


def write_pytest_ini():
    print("🧪 Generando pytest.ini...\n")
    content = dedent(f"""\
    [pytest]
    addopts = -q
    testpaths = tests
    pythonpath = .
    """)
    PYTEST_INI.write_text(content, encoding="utf-8")
    print(f"✅ pytest.ini escrito en {PYTEST_INI}\n")


# =========================
# DB v3.2 (intacto)
# =========================
def write_schema_v3_2():
    print("🧱 Escribiendo schema v3.2 (intacto)...\n")
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
        unidad TEXT DEFAULT 'g',
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
    path = DB_DIR / "schema.sql"
    path.write_text(schema, encoding="utf-8")
    print(f"📄 Esquema v3.2 escrito en {path}\n")


def write_repo():
    print("💾 Escribiendo repositorio SQLite...\n")
    repo = dedent("""\
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
    """)
    (DB_DIR / "db_sqlite_repository.py").write_text(repo, encoding="utf-8")
    print(f"📄 Repositorio escrito en {DB_DIR / 'db_sqlite_repository.py'}\n")


# =========================
# Drive Adapter (CORREGIDO)
# =========================
def write_drive_adapter():
    print("☁️ Escribiendo DriveAdapter...\n")
    drive_adapter = dedent("""\
    from __future__ import annotations

    # ⚠️ Entornos corporativos con MITM/SSL: forzamos contexto sin verificación
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context

    import io
    import json
    from pathlib import Path
    from typing import Optional, Dict, Any

    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    from googleapiclient.http import MediaIoBaseUpload

    CONFIG_PATH = Path('vanilla_records/src/config/drive_config.json')
    CREDS_PATH = Path('vanilla_records/src/config/google_drive_credentials.json')

    class DriveAdapter:
        def __init__(self, creds_json: Path = CREDS_PATH, config_json: Path = CONFIG_PATH):
            if not creds_json.exists():
                raise FileNotFoundError(f'No se encontró credencial: {creds_json}')
            if not config_json.exists():
                raise FileNotFoundError(f'No se encontró config de Drive: {config_json}')
            cfg = json.loads(config_json.read_text(encoding='utf-8'))

            scopes = ['https://www.googleapis.com/auth/drive']
            creds = service_account.Credentials.from_service_account_file(str(creds_json), scopes=scopes)
            self.service = build('drive', 'v3', credentials=creds)
            self.use_shared_drive = bool(cfg.get('use_shared_drive', True))
            self.shared_drive_id = cfg.get('shared_drive_id')
            self.default_folder_name = cfg.get('default_folder_name', 'VanillaRecords_Uploads')

        def _list_params(self) -> Dict[str, Any]:
            # Solo los parámetros válidos para files().list
            params: Dict[str, Any] = {}
            if self.use_shared_drive and self.shared_drive_id:
                params.update({
                    'supportsAllDrives': True,
                    'includeItemsFromAllDrives': True,
                    'driveId': self.shared_drive_id,
                    'corpora': 'drive'
                })
            return params

        def ensure_folder(self, name: str, parent_id: Optional[str] = None) -> str:
            params = self._list_params()
            q = f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
            if parent_id:
                q += f" and '{parent_id}' in parents"

            results = self.service.files().list(q=q, fields='files(id, name)', **params).execute()
            files = results.get('files', [])
            if files:
                return files[0]['id']

            metadata = {'name': name, 'mimeType': 'application/vnd.google-apps.folder'}
            if parent_id:
                metadata['parents'] = [parent_id]
            # ⚠️ NOTA: files().create no acepta includeItemsFromAllDrives; solo supportsAllDrives
            created = self.service.files().create(
                body=metadata,
                fields='id',
                supportsAllDrives=True
            ).execute()
            return created['id']

        def upload_bytes(self, data: bytes, filename: str, parent_id: Optional[str] = None, mime_type: str = 'application/octet-stream') -> Dict[str, Any]:
            file_metadata = {'name': filename}
            if parent_id:
                file_metadata['parents'] = [parent_id]

            media = MediaIoBaseUpload(io.BytesIO(data), mimetype=mime_type)
            created = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink, name, parents',
                supportsAllDrives=True
            ).execute()
            return created

        def upload_path(self, path: Path, parent_id: Optional[str] = None, mime_type: Optional[str] = None) -> Dict[str, Any]:
            if not path.exists():
                raise FileNotFoundError(str(path))
            if mime_type is None:
                mime_type = 'application/octet-stream'
            return self.upload_bytes(path.read_bytes(), path.name, parent_id=parent_id, mime_type=mime_type)

        def get_about(self) -> Dict[str, Any]:
            # about().get no acepta supports/includeItems…: NO pasar kwargs adicionales
            return self.service.about().get(fields='user, storageQuota').execute()
    """)
    (DRIVE_DIR / "drive_adapter.py").write_text(drive_adapter, encoding="utf-8")
    print(f"📄 DriveAdapter escrito en {DRIVE_DIR / 'drive_adapter.py'}\n")


# =========================
# Tests (unit)
# =========================
def write_unit_tests():
    print("🧪 Escribiendo tests unitarios (core, inventory, sales)...\n")

    test_core = dedent("""\
    import os
    from src.infrastructure.db.db_sqlite_repository import SQLiteRepository

    DB = 'vanilla_records.db'

    def setup_module():
        try:
            if os.path.exists(DB):
                os.remove(DB)
        except (PermissionError, FileNotFoundError):
            pass  # Ignora si otro test ya la está usando o ya se eliminó

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

        # Lotes
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

        # Evento: aplicación a 10 plantas (100g cal, 2g safer, 200g lombrinaza por planta)
        eid = repo.crear_evento('abonado','Aplicación trio','2025-11-07', planta_ids)
        repo.consumir_lote_en_evento(eid, lote_cal, 100*10)
        repo.consumir_lote_en_evento(eid, lote_safer, 2*10)
        repo.consumir_lote_en_evento(eid, lote_lombr, 200*10)

        stock = {r['lote_id']: r for r in repo.resumen_stock()}
        assert stock[lote_cal]['cantidad_disponible'] == 60000 - 1000
        assert stock[lote_safer]['cantidad_disponible'] == 1000 - 20
        assert stock[lote_lombr]['cantidad_disponible'] == 100000 - 2000

        filas = repo.query('SELECT count(*) as c FROM evento_planta WHERE evento_id=?',(eid,))
        assert filas[0]['c']==10

        repo.close()
    """)
    (TESTS_UNIT_DIR / "test_v3_2_core.py").write_text(test_core, encoding="utf-8")

    test_inventory = dedent("""\
    import os
    import pytest
    from src.infrastructure.db.db_sqlite_repository import SQLiteRepository

    DB = 'vanilla_records.db'

    def setup_module():
        try:
            if os.path.exists(DB):
                os.remove(DB)
        except (PermissionError, FileNotFoundError):
            pass

    def test_stock_and_media_and_overconsume():
        repo = SQLiteRepository(DB)
        prov = repo.insert('proveedores', {'nombre':'Prov','telefono':'999'})
        insu = repo.insert('insumos', {'nombre':'Cal','tipo':'enmienda','unidad':'g'})
        lote = repo.insert('lotes_insumo', {
            'insumo_id': insu, 'proveedor_id': prov,
            'cantidad_inicial': 5000, 'cantidad_disponible': 5000,
            'precio_unitario': 60_000/1000, 'fecha_compra':'2025-11-06'
        })
        # media de lote (factura)
        repo.insert('lote_media', {'lote_id': lote, 'file_path':'facturas/cal_1106.pdf','file_type':'pdf'})
        # evento 1000g
        p = repo.insert('plantas', {'codigo':'P001'})
        e = repo.crear_evento('abonado','test','2025-11-07',[p])
        repo.consumir_lote_en_evento(e, lote, 1000)
        # intento de sobreconsumo (debe fallar por trigger)
        with pytest.raises(Exception):
            repo.consumir_lote_en_evento(e, lote, 5000)

        st = repo.resumen_stock()
        assert any(r['cantidad_disponible']==4000 for r in st)
        repo.close()
    """)
    (TESTS_UNIT_DIR / "test_v3_2_inventory.py").write_text(test_inventory, encoding="utf-8")

    test_sales = dedent("""\
    import os
    from src.infrastructure.db.db_sqlite_repository import SQLiteRepository

    DB = 'vanilla_records.db'

    def setup_module():
        try:
            if os.path.exists(DB):
                os.remove(DB)
        except (PermissionError, FileNotFoundError):
            pass

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

        # Ventas
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
    """)
    (TESTS_UNIT_DIR / "test_v3_2_sales.py").write_text(test_sales, encoding="utf-8")

    print("✅ Tests unitarios creados.\n")


# =========================
# Tests (integration) – Drive
# =========================
def write_integration_tests():
    print("🔗 Escribiendo test de integración con Google Drive (rutas robustas)...\n")
    test_drive = dedent("""\
    import json
    from pathlib import Path
    from src.infrastructure.drive.drive_adapter import DriveAdapter

    def test_drive_upload_smoke():
        # 📌 Define una ruta base robusta (2 niveles arriba del archivo actual)
        BASE_DIR = Path(__file__).resolve().parents[2]
        CONFIG_PATH = BASE_DIR / 'src' / 'config' / 'drive_config.json'
        CREDS_PATH = BASE_DIR / 'src' / 'config' / 'google_drive_credentials.json'

        assert CONFIG_PATH.exists(), f"❌ No se encontró {CONFIG_PATH}"
        assert CREDS_PATH.exists(), f"❌ No se encontró {CREDS_PATH}"

        cfg = json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
        use_shared = cfg.get('use_shared_drive', True)

        # 🔧 Instancia el adaptador con rutas absolutas
        drive = DriveAdapter(creds_json=CREDS_PATH, config_json=CONFIG_PATH)

        about = drive.get_about()
        assert 'user' in about

        # 🗂️ Crear/Asegurar carpeta raíz para pruebas
        root_folder_name = cfg.get('default_folder_name', 'VanillaRecords_Uploads')
        root_id = drive.ensure_folder(root_folder_name) if use_shared else None

        # 📤 Subir archivo de prueba en memoria
        content = b'Archivo de prueba de integracion - Vanilla Records'
        result = drive.upload_bytes(content, 'test_integration_vr.txt', parent_id=root_id)
        assert 'id' in result and 'webViewLink' in result
    """)
    (TESTS_INTEGRATION_DIR / "test_drive_integration.py").write_text(test_drive, encoding="utf-8")
    print("✅ Test de integración Drive creado con rutas absolutas.\n")


# =========================
# README
# =========================
def write_readme_notes():
    print("📝 Actualizando README...\n")
    readme = dedent(f"""\
    # Vanilla-Records v4.0 🚀

    **Qué hace este setup (full):**
    - Reconstruye **toda** la estructura del proyecto desde cero.
    - Mantiene el **esquema DB v3.2** (intacto) y el repositorio SQLite con helpers.
    - Crea **tests unitarios** (core, inventario, ventas).
    - Agrega **integración con Google Drive** (DriveAdapter) + config JSON.
    - Genera **test de integración** con Drive (no se ejecuta automáticamente).
    - Asegura **.gitignore** y plantillas de credenciales si no existen.

    ## Rutas clave
    - DB schema: `{DB_DIR / "schema.sql"}`
    - Repo DB: `{DB_DIR / "db_sqlite_repository.py"}`
    - Drive Adapter: `{DRIVE_DIR / "drive_adapter.py"}`
    - Config Drive: `{DRIVE_CONFIG_JSON}`
    - Credenciales (plantilla): `{CREDENTIALS_JSON}`
    - Tests unit: `{TESTS_UNIT_DIR}`
    - Tests integration: `{TESTS_INTEGRATION_DIR}`

    ## Requisitos
    - Python 3.10+ recomendado
    - Cuenta de servicio con acceso a una Shared Drive (o carpeta) si `use_shared_drive=true`

    ## Pasos
    1. Ejecutar setup:
       ```
       python setup_vanilla_records_v4_0_full.py
       ```
    2. Activar venv (Windows):
       ```
       venv\\Scripts\\activate
       ```
    3. Colocar tus credenciales reales en:
       ```
       {CREDENTIALS_JSON}
       ```
       (el .gitignore ya las excluye del repo)

    4. (Opcional) Ajustar `shared_drive_id` en:
       ```
       {DRIVE_CONFIG_JSON}
       ```

    5. Correr tests unitarios:
       ```
       cd {PROJECT_NAME}
       pytest -q tests/unit
       ```

    6. Correr test de integración Drive (si ya configuraste credenciales y permisos):
       ```
       cd {PROJECT_NAME}
       pytest -q tests/integration/test_drive_integration.py
       ```

    ## Notas
    - El test de integración crea un archivo de texto pequeño para validar el flujo de subida.
    - En entornos corporativos con interceptación SSL, el `DriveAdapter` fuerza contexto sin verificación
      para permitir la conexión (ajústalo según políticas de tu organización).
    """)
    Path("README.md").write_text(readme, encoding="utf-8")
    print("✅ README actualizado.\n")


def reset_database():
    if DB_PATH.exists():
        try:
            DB_PATH.unlink()
            print("🗑️ Base de datos eliminada (reset).")
        except PermissionError:
            print("⚠️ No se pudo eliminar la DB (en uso). Se reutilizará.")
    print("🧩 Se recreará al instanciar el repositorio.\n")


def setup_environment():
    print("🔧 Verificando entorno virtual y dependencias...\n")
    if not VENV_PATH.exists():
        subprocess.run(["python", "-m", "venv", "venv"])
        print("✅ Entorno virtual creado.")

    subprocess.run(["venv\\Scripts\\python", "-m", "pip", "install", "--upgrade", "pip"])

    packages = [
        "pytest",
        "google-api-python-client",
        "google-auth",
        "google-auth-oauthlib",
        "google-auth-httplib2"
    ]
    subprocess.run(["venv\\Scripts\\pip", "install", *packages])
    print("✅ Dependencias instaladas correctamente.\n")


# =========================
# Main
# =========================
if __name__ == "__main__":
    ensure_structure()
    write_gitignore()
    write_credentials_template()
    write_drive_config()
    write_pytest_ini()

    write_schema_v3_2()
    write_repo()
    write_drive_adapter()

    write_unit_tests()
    write_integration_tests()

    reset_database()
    setup_environment()
    write_readme_notes()

    print("🎉 Vanilla-Records v4.0 listo.")
    print("👉 Activa el entorno y ejecuta tests unitarios:")
    print("   venv\\Scripts\\activate && cd vanilla_records && pytest -q tests/unit")
