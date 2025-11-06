import os
import subprocess
from pathlib import Path

print("🔧 Configurando entorno Vanilla-Records...\n")

# Crear entorno virtual
if not Path("venv").exists():
    subprocess.run(["python", "-m", "venv", "venv"])
    print("✅ Entorno virtual creado.")

# Activar pip e instalar dependencias
subprocess.run(["venv\\Scripts\\python", "-m", "pip", "install", "--upgrade", "pip"])
packages = [
    "pytest",
    "google-api-python-client",
    "google-auth",
    "google-auth-oauthlib",
    "google-auth-httplib2"
]
subprocess.run(["venv\\Scripts\\pip", "install", *packages])
print("✅ Dependencias instaladas.")

# Crear requirements.txt
subprocess.run(["venv\\Scripts\\pip", "freeze", ">", "requirements.txt"], shell=True)
print("📄 requirements.txt generado.")

# Ejecutar pruebas iniciales
print("\n🧪 Ejecutando pruebas unitarias...\n")
subprocess.run(["venv\\Scripts\\pytest", "-v"])

print("\n🎉 Configuración completa. Entorno Vanilla-Records listo.")
