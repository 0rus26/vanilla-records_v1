from src.domain.entities.planta import Planta
from src.domain.entities.evento import Evento

def test_crear_evento():
    planta = Planta("001", "Sector A")
    evento = Evento(planta.id, "abonado", "Aplicación de compost")
    assert evento.planta_id == "001"
    assert evento.tipo == "abonado"
    assert isinstance(evento.to_dict(), dict)
