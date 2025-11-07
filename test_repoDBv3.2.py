# ==============================================================
# Vanilla Records v3.2 – Prueba Integral de Población de Tablas
# ==============================================================

import os
from pprint import pprint
from datetime import datetime, timedelta
from vanilla_records.src.infrastructure.db.db_sqlite_repository import SQLiteRepository

DB_PATH = "vanilla_records.db"

# ==============================================================
# LIMPIEZA Y PREPARACIÓN
# ==============================================================

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("🗑️ Base de datos eliminada (reinicio de prueba)")

repo = SQLiteRepository(DB_PATH)
print("🌱 Iniciando prueba integral avanzada Vanilla Records v3.2...\n")

# ==============================================================
# 1️⃣ Proveedores
# ==============================================================

prov1 = repo.insert("proveedores", {"nombre": "Agroinsumos La Montaña", "telefono": "3201112233", "correo": "ventas@agromontana.co"})
prov2 = repo.insert("proveedores", {"nombre": "BioFertil SAS", "telefono": "3204446677", "correo": "info@biofertil.com"})
print(f"✅ Proveedores insertados: {prov1}, {prov2}")

# ==============================================================
# 2️⃣ Plantas (Vanilla planifolia y pompona)
# ==============================================================

planta_ids = []
for i in range(1, 11):
    planta_ids.append(repo.insert("plantas", {
        "codigo": f"VNL-{i:03d}",
        "nombre_comun": "Vainilla",
        "especie": "Vanilla planifolia" if i <= 6 else "Vanilla pompona",
        "variedad": "planifolia" if i <= 6 else "pompona",
        "fecha_siembra": f"2024-03-{10 + i:02d}",
        "ubicacion": "Bloque A" if i <= 5 else "Bloque B",
        "gps": "7.390N, -73.495W",
        "proveedor_id": prov1 if i <= 5 else prov2,
        "observaciones": "Planta en desarrollo"
    }))
print(f"🌿 Plantas registradas: {len(planta_ids)}")

# ==============================================================
# 3️⃣ Insumos y Lotes (Cal, Lombrinaza, Bocashi, Micorriza)
# ==============================================================

insumos = {
    "cal": repo.insert("insumos", {"nombre": "Cal agrícola", "tipo": "enmienda", "unidad": "g", "descripcion": "Neutraliza acidez del suelo"}),
    "lombrinaza": repo.insert("insumos", {"nombre": "Lombrinaza", "tipo": "abono", "unidad": "g", "descripcion": "Abono orgánico maduro"}),
    "bocashi": repo.insert("insumos", {"nombre": "Bocashi", "tipo": "abono fermentado", "unidad": "g", "descripcion": "Abono biológico fermentado"}),
    "micorriza": repo.insert("insumos", {"nombre": "Micorriza", "tipo": "bioinsumo", "unidad": "g", "descripcion": "Hongos simbióticos para raíces"})
}

# Lotes (dos fechas distintas por insumo)
hoy = datetime.now()
for nombre, iid in insumos.items():
    for offset in [0, 15]:
        fecha = (hoy - timedelta(days=offset)).strftime("%Y-%m-%d")
        repo.insert("lotes_insumo", {
            "insumo_id": iid,
            "proveedor_id": prov1 if offset == 0 else prov2,
            "cantidad_inicial": 50000 + (offset * 100),
            "cantidad_disponible": 50000 + (offset * 100),
            "unidad": "g",
            "precio_unitario": 45_000 / 1000,
            "fecha_compra": fecha,
            "observaciones": f"Lote de {nombre} recibido el {fecha}"
        })
print("📦 Lotes de insumos registrados (8 en total)")

# ==============================================================
# 4️⃣ Actividades y Trabajadores
# ==============================================================

workers = [
    repo.insert("workers", {"nombre": "Luis Pérez", "telefono": "3101234567", "rol": "Operario de campo"}),
    repo.insert("workers", {"nombre": "Ana Ríos", "telefono": "3127654321", "rol": "Técnico agrícola"})
]
actividades = [
    repo.insert("actividades", {"nombre": "Fertilización", "descripcion": "Aplicación de abonos y cal"}),
    repo.insert("actividades", {"nombre": "Riego", "descripcion": "Irrigación manual por goteo"})
]
print("👷‍♂️ Trabajadores y actividades creados")

# ==============================================================
# 5️⃣ Evento de fertilización y consumo de insumos
# ==============================================================

eid = repo.crear_evento("abonado", "Aplicación de cal, lombrinaza y micorriza", hoy.strftime("%Y-%m-%d"), planta_ids[:6])
repo.insert("actividad_evento", {"actividad_id": actividades[0], "evento_id": eid, "worker_id": workers[0], "costo": 45000})
repo.insert("actividad_evento", {"actividad_id": actividades[1], "evento_id": eid, "worker_id": workers[1], "costo": 30000})

# Seleccionar algunos lotes y consumir insumos
lotes = repo.query("SELECT id, insumo_id FROM lotes_insumo LIMIT 4")
for lote in lotes:
    repo.consumir_lote_en_evento(eid, lote["id"], 1500)

print(f"🌾 Evento de fertilización {eid} registrado y consumo aplicado.")

# ==============================================================
# 6️⃣ Cosechas (vaina verde y esquejes)
# ==============================================================

tp_vaina = repo.insert("tipos_producto", {"nombre": "Vaina verde", "descripcion": "Cosecha fresca de vainilla"})
tp_esqueje = repo.insert("tipos_producto", {"nombre": "Esqueje", "descripcion": "Plántula para propagación"})

cosechas = [
    repo.insert("cosechas", {"tipo_producto_id": tp_vaina, "planta_id": planta_ids[0], "fecha_recoleccion": "2025-01-18", "cantidad": 1.8, "unidad": "kg", "calidad": "A"}),
    repo.insert("cosechas", {"tipo_producto_id": tp_esqueje, "planta_id": planta_ids[1], "fecha_recoleccion": "2025-02-10", "cantidad": 15, "unidad": "un", "calidad": "B"})
]
print("🌺 Cosechas registradas")

# ==============================================================
# 7️⃣ Ventas con evidencia
# ==============================================================

v1 = repo.insert("ventas", {
    "cosecha_id": cosechas[0],
    "fecha": "2025-02-20",
    "comprador": "Cliente Gourmet",
    "destino": "Bucaramanga",
    "cantidad_vendida": 1.0,
    "unidad": "kg",
    "precio_unitario": 1500000,
    "metodo_pago": "transferencia"
})
v2 = repo.insert("ventas", {
    "tipo_producto_id": tp_esqueje,
    "fecha": "2025-03-05",
    "comprador": "Vivero Los Andes",
    "destino": "Sabana de Torres",
    "cantidad_vendida": 10,
    "unidad": "un",
    "precio_unitario": 20000,
    "metodo_pago": "efectivo"
})
repo.insert("venta_media", {"venta_id": v1, "file_path": "docs/factura_v1.pdf", "file_type": "pdf"})
print("💰 Ventas registradas con evidencia")

# ==============================================================
# 8️⃣ Adjuntar medios a eventos y lotes
# ==============================================================

repo.insert("evento_media", {"evento_id": eid, "file_path": "media/evento_abonado.mp4", "file_type": "video"})
repo.insert("lote_media", {"lote_id": lotes[0]["id"], "file_path": "facturas/cal_enero.pdf", "file_type": "pdf"})
print("📸 Media asociada a eventos y lotes añadida")

# ==============================================================
# 9️⃣ Consultas y verificaciones
# ==============================================================

print("\n📊 Resumen de stock actual:")
pprint(repo.resumen_stock())

print("\n🔍 Trazabilidad de insumo (Cal agrícola):")
pprint(repo.trazabilidad_insumo(insumos["cal"]))

print("\n🧾 Resumen de ventas:")
pprint(repo.resumen_ventas())

eventos = repo.fetch_all("eventos")
print(f"\n📅 Total eventos registrados: {len(eventos)}")
pprint(eventos)

repo.close()
print("\n✅ Prueba integral completada con éxito. Base poblada y lista para inspección visual.")
