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
