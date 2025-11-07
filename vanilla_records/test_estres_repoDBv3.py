from src.infrastructure.db.db_sqlite_repository import SQLiteRepository

repo = SQLiteRepository()

# Insertar proveedor
prov_id = repo.insert("proveedores", {
    "nombre": "BioVainilla Orgánica",
    "telefono": "3105678910",
    "correo": "contacto@biovainilla.com",
    "direccion": "Sabana de Torres"
})
print(f"Proveedor insertado con ID: {prov_id}")

# Insertar planta asociada al proveedor
planta_id = repo.insert("plantas", {
    "codigo": "PLT001",
    "nombre_comun": "Vainilla",
    "especie": "Vanilla planifolia",
    "fecha_siembra": "2025-03-10",
    "ubicacion": "Lote 1",
    "gps": "7.390N, -73.495W",
    "proveedor_id": prov_id,
    "observaciones": "Esqueje de primera generación"
})
print(f"Planta insertada con ID: {planta_id}")

# Consultar todas las plantas
plantas = repo.fetch_all("plantas")
print("\n🌱 Plantas registradas:")
for p in plantas:
    print(p)

repo.close()
