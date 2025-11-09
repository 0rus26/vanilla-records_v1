# Vanilla-Records v4.0 🚀

**Qué hace este setup (full):**
- Reconstruye **toda** la estructura del proyecto desde cero.
- Mantiene el **esquema DB v3.2** (intacto) y el repositorio SQLite con helpers.
- Crea **tests unitarios** (core, inventario, ventas).
- Agrega **integración con Google Drive** (DriveAdapter) + config JSON.
- Genera **test de integración** con Drive (no se ejecuta automáticamente).
- Asegura **.gitignore** y plantillas de credenciales si no existen.

## Rutas clave
- DB schema: `vanilla_records\src\infrastructure\db\schema.sql`
- Repo DB: `vanilla_records\src\infrastructure\db\db_sqlite_repository.py`
- Drive Adapter: `vanilla_records\src\infrastructure\drive\drive_adapter.py`
- Config Drive: `vanilla_records\src\config\drive_config.json`
- Credenciales (plantilla): `vanilla_records\src\config\google_drive_credentials.json`
- Tests unit: `vanilla_records\tests\unit`
- Tests integration: `vanilla_records\tests\integration`

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
   venv\Scripts\activate
   ```
3. Colocar tus credenciales reales en:
   ```
   vanilla_records\src\config\google_drive_credentials.json
   ```
   (el .gitignore ya las excluye del repo)

4. (Opcional) Ajustar `shared_drive_id` en:
   ```
   vanilla_records\src\config\drive_config.json
   ```

5. Correr tests unitarios:
   ```
   cd vanilla_records
   pytest -q tests/unit
   ```

6. Correr test de integración Drive (si ya configuraste credenciales y permisos):
   ```
   cd vanilla_records
   pytest -q tests/integration/test_drive_integration.py
   ```

## Notas
- El test de integración crea un archivo de texto pequeño para validar el flujo de subida.
- En entornos corporativos con interceptación SSL, el `DriveAdapter` fuerza contexto sin verificación
  para permitir la conexión (ajústalo según políticas de tu organización).
