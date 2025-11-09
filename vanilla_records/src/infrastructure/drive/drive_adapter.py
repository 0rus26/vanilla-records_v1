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
