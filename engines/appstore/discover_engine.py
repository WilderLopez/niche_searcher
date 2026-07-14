"""
Descubrimiento de apps iOS.

Dos fuentes:
  - búsqueda por palabras clave (iTunes Search API)
  - top charts por categoría (RSS de Apple)

Los ids encontrados se añaden al pool de candidatas para que 'ios-evaluate'
los analice después.
"""

import os
import time

from config.appstore_config import AppStoreConfig
from models.appstore_model import AppstoreCandidateModel
from services.appstore_service import AppStoreService, APPLE_GENRES

_SEEDS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "config",
    "seed_keywords.txt",
)


class AppStoreDiscoverEngine:

    def __init__(self, keywords=None, per_keyword=40, country=None):
        self.keywords = keywords if keywords else self._load_seed_keywords()
        self.per_keyword = per_keyword
        self.country = country or AppStoreConfig.COUNTRY

    @staticmethod
    def _load_seed_keywords():
        if not os.path.exists(_SEEDS_FILE):
            return []
        with open(_SEEDS_FILE, encoding="utf-8") as f:
            return [l.strip() for l in f if l.strip() and not l.startswith("#")]

    def run_search(self):
        if not self.keywords:
            print("No hay palabras clave. Añade algunas a config/seed_keywords.txt.")
            return {"added": 0}

        added = 0
        print(f"Buscando por {len(self.keywords)} palabras clave en el App Store ({self.country})...\n")
        for kw in self.keywords:
            ids = AppStoreService.search_app_ids(kw, country=self.country, limit=self.per_keyword)
            new = AppstoreCandidateModel.insert_ids(ids)
            added += len(new)
            print(f"  '{kw}': {len(ids)} resultados, {len(new)} nuevas")
            time.sleep(AppStoreConfig.REQUEST_DELAY)
        print(f"\nHecho. Nuevas candidatas: {added}")
        return {"added": added}

    def run_charts(self, per_genre=100):
        added = 0
        print(f"Recogiendo top charts por categoría ({self.country})...\n")
        for name, genre_id in APPLE_GENRES.items():
            ids = AppStoreService.top_chart_ids(genre_id, country=self.country, limit=per_genre)
            new = AppstoreCandidateModel.insert_ids(ids)
            added += len(new)
            print(f"  {name:22} ({genre_id}): {len(ids)} apps, {len(new)} nuevas")
            time.sleep(AppStoreConfig.REQUEST_DELAY)
        print(f"\nHecho. Nuevas candidatas desde charts: {added}")
        return {"added": added}
