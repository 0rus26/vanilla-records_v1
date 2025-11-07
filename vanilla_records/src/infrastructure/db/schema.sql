-- ================================
-- Vanilla Records DB v3.2 (corregido)
-- ================================

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS proveedores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    telefono TEXT,
    correo TEXT,
    direccion TEXT
);

CREATE TABLE IF NOT EXISTS plantas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    nombre_comun TEXT,
    especie TEXT,
    variedad TEXT,
    fecha_siembra TEXT,
    ubicacion TEXT,
    gps TEXT,
    proveedor_id INTEGER,
    observaciones TEXT,
    estado TEXT DEFAULT 'viva',
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
);

CREATE TABLE IF NOT EXISTS eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    descripcion TEXT,
    fecha TEXT,
    costo_total REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS evento_planta (
    evento_id INTEGER,
    planta_id INTEGER,
    PRIMARY KEY (evento_id, planta_id),
    FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE,
    FOREIGN KEY (planta_id) REFERENCES plantas(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS insumos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    tipo TEXT,
    unidad TEXT,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS lotes_insumo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    insumo_id INTEGER NOT NULL,
    proveedor_id INTEGER,
    cantidad_inicial REAL NOT NULL,
    cantidad_disponible REAL NOT NULL,
    unidad TEXT DEFAULT 'g',        -- ✅ nuevo campo agregado
    precio_unitario REAL,
    fecha_compra TEXT,
    fecha_vencimiento TEXT,
    observaciones TEXT,
    FOREIGN KEY (insumo_id) REFERENCES insumos(id),
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id),
    CHECK (cantidad_inicial >= 0),
    CHECK (cantidad_disponible >= 0)
);

CREATE TABLE IF NOT EXISTS lote_media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lote_id INTEGER,
    file_path TEXT,
    file_type TEXT,
    drive_link TEXT,
    FOREIGN KEY (lote_id) REFERENCES lotes_insumo(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS evento_lote (
    evento_id INTEGER,
    lote_id INTEGER,
    cantidad_utilizada REAL NOT NULL,
    PRIMARY KEY (evento_id, lote_id),
    FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE,
    FOREIGN KEY (lote_id) REFERENCES lotes_insumo(id) ON DELETE CASCADE,
    CHECK (cantidad_utilizada > 0)
);

CREATE TRIGGER IF NOT EXISTS trg_evento_lote_check_stock
BEFORE INSERT ON evento_lote
FOR EACH ROW
BEGIN
    SELECT CASE
        WHEN (SELECT cantidad_disponible FROM lotes_insumo WHERE id = NEW.lote_id) < NEW.cantidad_utilizada
        THEN RAISE(ABORT, 'Stock insuficiente en el lote')
    END;
END;

CREATE TRIGGER IF NOT EXISTS trg_evento_lote_descuenta
AFTER INSERT ON evento_lote
FOR EACH ROW
BEGIN
    UPDATE lotes_insumo
    SET cantidad_disponible = cantidad_disponible - NEW.cantidad_utilizada
    WHERE id = NEW.lote_id;
END;

CREATE TABLE IF NOT EXISTS workers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    telefono TEXT,
    rol TEXT
);

CREATE TABLE IF NOT EXISTS actividades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS actividad_evento (
    actividad_id INTEGER,
    evento_id INTEGER,
    worker_id INTEGER,
    costo REAL,
    PRIMARY KEY (actividad_id, evento_id, worker_id),
    FOREIGN KEY (actividad_id) REFERENCES actividades(id) ON DELETE CASCADE,
    FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE,
    FOREIGN KEY (worker_id) REFERENCES workers(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS evento_media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evento_id INTEGER,
    file_path TEXT,
    file_type TEXT,
    drive_link TEXT,
    FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tipos_producto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS cosechas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_producto_id INTEGER NOT NULL,
    evento_id INTEGER,
    planta_id INTEGER,
    fecha_recoleccion TEXT NOT NULL,
    cantidad REAL,
    unidad TEXT,
    calidad TEXT,
    humedad_porcentaje REAL,
    observaciones TEXT,
    FOREIGN KEY (tipo_producto_id) REFERENCES tipos_producto(id),
    FOREIGN KEY (evento_id) REFERENCES eventos(id),
    FOREIGN KEY (planta_id) REFERENCES plantas(id)
);

CREATE TABLE IF NOT EXISTS ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cosecha_id INTEGER,
    tipo_producto_id INTEGER,
    fecha TEXT NOT NULL,
    comprador TEXT,
    destino TEXT,
    cantidad_vendida REAL,
    unidad TEXT,
    precio_unitario REAL,
    moneda TEXT DEFAULT 'COP',
    metodo_pago TEXT,
    tipo_operacion TEXT DEFAULT 'venta',
    observaciones TEXT,
    FOREIGN KEY (cosecha_id) REFERENCES cosechas(id),
    FOREIGN KEY (tipo_producto_id) REFERENCES tipos_producto(id)
);

CREATE TABLE IF NOT EXISTS venta_media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venta_id INTEGER,
    file_path TEXT,
    file_type TEXT,
    drive_link TEXT,
    FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE
);
