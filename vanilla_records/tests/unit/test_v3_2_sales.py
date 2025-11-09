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
