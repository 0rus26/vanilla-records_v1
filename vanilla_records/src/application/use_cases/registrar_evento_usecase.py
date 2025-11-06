from src.domain.entities.evento import Evento

class RegistrarEventoUseCase:
    def __init__(self, storage, drive):
        self.storage = storage
        self.drive = drive

    def execute(self, planta_id, tipo, descripcion, media_files=None):
        evento = Evento(planta_id, tipo, descripcion, media_files)
        self.storage.guardar_evento(evento.to_dict())

        uploaded_links = []
        if media_files:
            for f in media_files:
                file_id = self.drive.upload_file(f)
                uploaded_links.append(f"https://drive.google.com/file/d/{file_id}/view")

        return {"evento": evento.to_dict(), "drive_links": uploaded_links}
