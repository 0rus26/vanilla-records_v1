import os
from src.infrastructure.db.db_sqlite_repository import SQLiteRepository

DB = 'vanilla_records.db'

def setup_module():
    if os.path.exists(DB):
        os.remove(DB)

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

    # Lotes (precios/días distintos)
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

    # Evento: aplicación a 10 plantas (100 g cal, 2 g Safer, 200 g lombrinaza por planta)
    eid = repo.crear_evento('abonado','Aplicación trio','2025-11-07', planta_ids)
    repo.consumir_lote_en_evento(eid, lote_cal, 100*10)
    repo.consumir_lote_en_evento(eid, lote_safer, 2*10)
    repo.consumir_lote_en_evento(eid, lote_lombr, 200*10)

    stock = {r['lote_id']: r for r in repo.resumen_stock()}
    assert stock[lote_cal]['cantidad_disponible'] == 60000 - 1000
    assert stock[lote_safer]['cantidad_disponible'] == 1000 - 20
    assert stock[lote_lombr]['cantidad_disponible'] == 100000 - 2000

    # Validar asociaciones planta-evento
    filas = repo.query('SELECT count(*) as c FROM evento_planta WHERE evento_id=?',(eid,))
    assert filas[0]['c']==10

    repo.close()
