"""
Motor de descubrimiento.

Busca apps por palabras clave en Google Play y añade las nuevas al pool de
candidatas (gp_url_base) para que 'evaluate' las analice después.

Las palabras clave se leen de config/seed_keywords.txt (una por línea) o se
pasan directamente al construir el motor.
"""

import os

from models.gp_url_base_model import GpUrlBaseModel
from services.play_service import PlayService

_SEEDS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "config",
    "seed_keywords.txt",
)


class DiscoverEngine:

    def __init__(self, keywords: list = None, per_keyword: int = 30):
        self.keywords = keywords if keywords else self._load_seed_keywords()
        self.per_keyword = per_keyword

    @staticmethod
    def _load_seed_keywords():
        if not os.path.exists(_SEEDS_FILE):
            return []
        with open(_SEEDS_FILE, encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]

    def run(self):
        if not self.keywords:
            print(
                "No hay palabras clave. Añade algunas a config/seed_keywords.txt "
                "o pásalas como argumento."
            )
            return {"added": 0}

        added_total = 0
        print(f"Buscando por {len(self.keywords)} palabras clave...\n")

        for keyword in self.keywords:
            app_ids = PlayService.search_app_ids(keyword, limit=self.per_keyword)
            urls = [PlayService.app_id_to_url(a) for a in app_ids]
            new_rows = GpUrlBaseModel.insertAppLinks(urls)
            added_total += len(new_rows)
            print(f"  '{keyword}': {len(app_ids)} resultados, {len(new_rows)} nuevas")

        print(f"\nHecho. Nuevas candidatas añadidas al pool: {added_total}")
        return {"added": added_total}
