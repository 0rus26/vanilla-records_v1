class Planta:
    def __init__(self, id: str, ubicacion: str = None, especie: str = "Vanilla planifolia"):
        self.id = id
        self.ubicacion = ubicacion
        self.especie = especie

    def __repr__(self):
        return f"<Planta {self.id} - {self.especie}>"
