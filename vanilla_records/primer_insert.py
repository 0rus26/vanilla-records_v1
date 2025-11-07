from src.infrastructure.db_sqlite_repository import SQLiteRepository
from src.domain.entities.evento import Evento

repo = SQLiteRepository()
evento = Evento("P001", "abonado", "Aplicación de compost orgánico")
repo.guardar_evento(evento.to_dict())
print(repo.listar_eventos())
