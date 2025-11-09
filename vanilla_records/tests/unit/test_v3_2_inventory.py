import os
import pytest
from src.infrastructure.db.db_sqlite_repository import SQLiteRepository

DB = 'vanilla_records.db'

def setup_module():
    try:
        if os.path.exists(DB):
            os.remove(DB)
    except (PermissionError, FileNotFoundError):
        pass

def test_stock_and_media_and_overconsume():
    repo = SQLiteRepository(DB)
    prov = repo.insert('proveedores', {'nombre':'Prov','telefono':'999'})
    insu = repo.insert('insumos', {'nombre':'Cal','tipo':'enmienda','unidad':'g'})
    lote = repo.insert('lotes_insumo', {
        'insumo_id': insu, 'proveedor_id': prov,
        'cantidad_inicial': 5000, 'cantidad_disponible': 5000,
        'precio_unitario': 60_000/1000, 'fecha_compra':'2025-11-06'
    })
    # media de lote (factura)
    repo.insert('lote_media', {'lote_id': lote, 'file_path':'facturas/cal_1106.pdf','file_type':'pdf'})
    # evento 1000g
    p = repo.insert('plantas', {'codigo':'P001'})
    e = repo.crear_evento('abonado','test','2025-11-07',[p])
    repo.consumir_lote_en_evento(e, lote, 1000)
    # intento de sobreconsumo (debe fallar por trigger)
    with pytest.raises(Exception):
        repo.consumir_lote_en_evento(e, lote, 5000)

    st = repo.resumen_stock()
    assert any(r['cantidad_disponible']==4000 for r in st)
    repo.close()
