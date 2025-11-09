from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError
import io
import json

# ==========================================================
# CONFIGURACIÓN DEL BOT DE GOOGLE DRIVE
# ==========================================================

SERVICE_ACCOUNT_FILE = "vanilla_records/src/config/google_drive_credentials.json"
SCOPES = ["https://www.googleapis.com/auth/drive"]

# ID de la carpeta raíz en la UNIDAD COMPARTIDA (Shared Drive)
SHARED_DRIVE_ID = "0AGWFWZLNB-dXUk9PVA"

# ==========================================================
# AUTENTICACIÓN
# ==========================================================

print("🔐 Iniciando autenticación con Google Drive API...\n")

try:
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("drive", "v3", credentials=creds)

    about = service.about().get(fields="user, kind").execute()
    print("✅ Autenticación exitosa.")
    print(f"📊 Usuario actual del bot: {about['user']['emailAddress']}")
    print(f"🪣 Tipo de cuenta: {about.get('kind', 'N/A')}\n")

except Exception as e:
    print("❌ Error al autenticar con Google Drive:")
    print(e)
    exit(1)

# ==========================================================
# PRUEBA DE SUBIDA DE ARCHIVO
# ==========================================================

print("📤 Intentando subir archivo de prueba a la Shared Drive...\n")

try:
    file_metadata = {
        "name": "test_vanilla_records.txt",
        "parents": [SHARED_DRIVE_ID]
    }

    media = MediaIoBaseUpload(
        io.BytesIO(b"Archivo de prueba desde Python (Vanilla Records)"),
        mimetype="text/plain"
    )

    file = (
        service.files()
        .create(
            body=file_metadata,
            media_body=media,
            fields="id, name, webViewLink, driveId",
            supportsAllDrives=True
        )
        .execute()
    )

    print("✅ Archivo subido correctamente a la unidad compartida.")
    print(f"📄 Nombre: {file['name']}")
    print(f"🆔 ID: {file['id']}")
    print(f"🔗 Link: {file['webViewLink']}")
    print(f"🗂 Drive ID: {file.get('driveId', 'N/A')}")

except HttpError as e:
    try:
        error_content = json.loads(e.content.decode())
        details = error_content.get("error", {}).get("errors", [])
        print("⚠️ Error al subir el archivo:")
        print(f"  → Código: {e.resp.status}")
        print(f"  → Motivo: {details}")
    except Exception:
        print(f"❌ Error HTTP sin detalles: {e}")
except Exception as e:
    print("❌ Error inesperado:", e)
