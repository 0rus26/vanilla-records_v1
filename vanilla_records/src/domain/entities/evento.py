from datetime import datetime

class Evento:
    def __init__(self, planta_id: str, tipo: str, descripcion: str, media_path=None, fecha=None):
        self.planta_id = planta_id
        self.tipo = tipo
        self.descripcion = descripcion
        self.media_path = media_path or []
        self.fecha = fecha or datetime.now()

    def to_dict(self):
        return {
            "planta_id": self.planta_id,
            "tipo": self.tipo,
            "descripcion": self.descripcion,
            "fecha": self.fecha.isoformat(),
            "media_path": self.media_path,
        }
