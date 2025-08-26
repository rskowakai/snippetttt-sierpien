from app.models.opcja import Opcja
from .base_repository import BaseRepository

class OpcjaRepository(BaseRepository[Opcja]):
    def __init__(self):
        super().__init__(Opcja)

opcja_repository = OpcjaRepository()
