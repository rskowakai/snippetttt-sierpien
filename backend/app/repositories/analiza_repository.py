from app.models.analiza import Analiza
from .base_repository import BaseRepository

class AnalizaRepository(BaseRepository[Analiza]):
    def __init__(self):
        super().__init__(Analiza)

analiza_repository = AnalizaRepository()
