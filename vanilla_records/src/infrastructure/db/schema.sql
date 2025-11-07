-- Base de datos Vanilla Records v3
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
    FOREIGN KEY (evento_id) REFERENCES eventos(id),
    FOREIGN KEY (planta_id) REFERENCES plantas(id)
);

CREATE TABLE IF NOT EXISTS insumos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    tipo TEXT,
    cantidad REAL,
    unidad TEXT,
    precio_unitario REAL,
    fecha_compra TEXT,
    proveedor_id INTEGER,
    fecha_vencimiento TEXT,
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
);

CREATE TABLE IF NOT EXISTS evento_insumo (
    evento_id INTEGER,
    insumo_id INTEGER,
    cantidad_utilizada REAL,
    PRIMARY KEY (evento_id, insumo_id),
    FOREIGN KEY (evento_id) REFERENCES eventos(id),
    FOREIGN KEY (insumo_id) REFERENCES insumos(id)
);

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
    FOREIGN KEY (actividad_id) REFERENCES actividades(id),
    FOREIGN KEY (evento_id) REFERENCES eventos(id),
    FOREIGN KEY (worker_id) REFERENCES workers(id)
);

CREATE TABLE IF NOT EXISTS evento_media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evento_id INTEGER,
    file_path TEXT,
    file_type TEXT,
    drive_link TEXT,
    FOREIGN KEY (evento_id) REFERENCES eventos(id)
);
