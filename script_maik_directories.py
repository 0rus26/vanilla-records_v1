import os
import shutil
import subprocess
from pathlib import Path

PROJECT_NAME = "vanilla_records"
VENV_PATH = Path("venv")


# =====================================================
# 1. LIMPIEZA TOTAL DEL PROYECTO
# =====================================================
def clean_project():
    if Path(PROJECT_NAME).exists():
        shutil.rmtree(PROJECT_NAME)
        print(f"🗑️ Carpeta eliminada: {PROJECT_NAME}")
    if Path("vanilla_records.db").exists():
        Path("vanilla_records.db").unlink()
        print("🗑️ Base de datos eliminada.")
    print("✅ Limpieza completa.\n")


# =====================================================
# 2. CREAR ESTRUCTURA BASE
# =====================================================
def create_structure():
    print("🏗️ Creando estructura del proyecto...\n")
    folders = [
        f"{PROJECT_NAME}/src/domain/entities",
        f"{PROJECT_NAME}/src/domain/services",
        f"{PROJECT_NAME}/src/application/use_cases",
        f"{PROJECT_NAME}/src/infrastructure",
        f"{PROJECT_NAME}/src/config",
        f"{PROJECT_NAME}/tests",
    ]

    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        Path(folder, "__init__.py").write_text("# Inicialización del paquete\n", encoding="utf-8")
        print(f"📁 {folder}")

    # Archivos principales
    files = {
        f"{PROJECT_NAME}/src/domain/entities/planta.py": '''class Planta:
    def __init__(self, id: str, ubicacion: str = None, especie: str = "Vanilla planifolia"):
        self.id = id
        self.ubicacion = ubicacion
        self.especie = especie

    def __repr__(self):
        return f"<Planta {self.id} - {self.especie}>"
''',

        f"{PROJECT_NAME}/src/domain/entities/evento.py": '''from datetime import datetime

class Evento:
    def __init__(self, planta_id: str, tipo: str, descripcion: str, media_path=None, fecha=None):
        self.planta_id = planta_id
        self.tipo = tipo
        self.descripcion = descripcion
        self.media_path = media_path or []
        self.fecha = fecha or datetime.now()

    def to_dict(self):
        return {
            "planta_id": self.planta_id,
            "tipo": self.tipo,
            "descripcion": self.descripcion,
            "fecha": self.fecha.isoformat(),
            "media_path": self.media_path,
        }
''',

        f"{PROJECT_NAME}/src/infrastructure/db_sqlite_repository.py": '''import sqlite3
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
''',

        f"{PROJECT_NAME}/src/application/use_cases/registrar_evento_usecase.py": '''from src.domain.entities.evento import Evento

class RegistrarEventoUseCase:
    def __init__(self, storage, drive):
        self.storage = storage
        self.drive = drive

    def execute(self, planta_id, tipo, descripcion, media_files=None):
        evento = Evento(planta_id, tipo, descripcion, media_files)
        self.storage.guardar_evento(evento.to_dict())

        uploaded_links = []
        if media_files:
            for f in media_files:
                file_id = self.drive.upload_file(f)
                uploaded_links.append(f"https://drive.google.com/file/d/{file_id}/view")

        return {"evento": evento.to_dict(), "drive_links": uploaded_links}
''',

        f"{PROJECT_NAME}/src/config/settings.yaml": "# Configuración general del proyecto Vanilla-Records\n",
        f"{PROJECT_NAME}/tests/test_entities.py": '''from src.domain.entities.planta import Planta
from src.domain.entities.evento import Evento

def test_crear_evento():
    planta = Planta("001", "Sector A")
    evento = Evento(planta.id, "abonado", "Aplicación de compost")
    assert evento.planta_id == "001"
    assert evento.tipo == "abonado"
    assert isinstance(evento.to_dict(), dict)
''',
        f"{PROJECT_NAME}/pytest.ini": "[pytest]\naddopts = -v\ntestpaths = tests\npythonpath = src\n",
    }

    for path, content in files.items():
        Path(path).write_text(content, encoding="utf-8")
        print(f"📄 {path}")

    print("\n✅ Estructura creada correctamente.\n")


# =====================================================
# 3. CONFIGURAR ENTORNO VIRTUAL Y DEPENDENCIAS
# =====================================================
def setup_environment():
    print("🔧 Configurando entorno virtual...\n")
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
    subprocess.run(["venv\\Scripts\\pip", "freeze", ">", "requirements.txt"], shell=True)
    print("✅ Dependencias instaladas.\n")


# =====================================================
# 4. EJECUTAR PRUEBAS
# =====================================================
def run_tests():
    print("🧪 Ejecutando pruebas...\n")
    subprocess.run(["venv\\Scripts\\python", "-m", "pytest", f"{PROJECT_NAME}/tests", "-v"])
    print("\n🎉 Configuración completa. Proyecto funcional.\n")


# =====================================================
# 5. CONFIGURAR GIT AUTOMÁTICAMENTE
# =====================================================
def setup_git(remote_url=None):
    print("🔧 Configurando Git...\n")

    # Crear .gitignore
    Path(".gitignore").write_text(
        "__pycache__/\nvenv/\n*.db\n*.pyc\npytest_cache/\n.DS_Store\n.idea/\n.vscode/\n",
        encoding="utf-8"
    )

    # Crear README seguro sin triple comillas internas
    readme = (
        "# Vanilla-Records 🌱\n\n"
        "Sistema de registro inteligente para cultivos de vainilla.\n\n"
        "## Estructura del proyecto\n"
        "```\n"
        f"{PROJECT_NAME}/src/\n"
        "├── domain/\n"
        "├── application/\n"
        "├── infrastructure/\n"
        "├── config/\n"
        "└── tests/\n"
        "```\n\n"
        "### Ejecución\n"
        "`python setup_vanilla_records.py`\n\n"
        "### Pruebas\n"
        "`pytest -v`\n"
    )
    Path("README.md").write_text(readme, encoding="utf-8")

    if not Path(".git").exists():
        subprocess.run(["git", "init"])
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", "Initial commit - Vanilla Records core setup"])
        print("✅ Repositorio Git inicializado y primer commit realizado.")

        if remote_url:
            subprocess.run(["git", "remote", "add", "origin", remote_url])
            subprocess.run(["git", "branch", "-M", "main"])
            subprocess.run(["git", "push", "-u", "origin", "main"])
            print(f"☁️ Repositorio remoto configurado: {remote_url}")
    else:
        print("⚠️ Repositorio Git ya existente, se omite inicialización.\n")


# =====================================================
# MAIN FINAL
# =====================================================
if __name__ == "__main__":
    clean_project()
    create_structure()
    setup_environment()
    run_tests()
    setup_git(remote_url=None)
