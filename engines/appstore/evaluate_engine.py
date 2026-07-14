"""
Evaluación de candidatas iOS.

Toma ids del pool, los consulta por lotes en el Lookup de iTunes (varios ids
por llamada) y guarda como nicho las apps que superan el criterio de
AppStoreConfig.
"""

import time

from config.appstore_config import AppStoreConfig
from models.appstore_model import AppstoreCandidateModel, AppstoreNicheModel
from services.appstore_service import AppStoreService


class AppStoreEvaluateEngine:

    def __init__(self, limit=200, country=None, delay=None):
        self.limit = limit
        self.country = country or AppStoreConfig.COUNTRY
        self.delay = AppStoreConfig.REQUEST_DELAY if delay is None else delay

    def run(self):
        ids = AppstoreCandidateModel.get_batch_to_scan(self.limit)
        if not ids:
            print("No hay candidatas en el pool. Ejecuta primero 'ios-discover'.")
            return {"scanned": 0, "niches": 0}

        print(f"Evaluando {len(ids)} apps iOS (en lotes)...\n")

        scanned = niches = 0
        # fetch_apps ya trocea en lotes de 50; iteramos en bloques para pausar.
        for start in range(0, len(ids), 50):
            block = ids[start:start + 50]
            data_list = AppStoreService.fetch_apps(block, country=self.country)
            scanned += len(data_list)

            for data in data_list:
                if AppStoreConfig.is_niche(data):
                    AppstoreNicheModel.upsert(data)
                    niches += 1
                    print(
                        f"  ✓ NICHO  {(data['title'] or '')[:38]:38}  "
                        f"{data['rating_count']:>9,} valoraciones  "
                        f"{data['age_days']:>4}d  "
                        f"{data['ratings_per_day']:>8,.0f}/día  [{data['genre']}]"
                    )

            if self.delay:
                time.sleep(self.delay)

        print(f"\nHecho. Evaluadas: {scanned} | Nichos: {niches}")
        return {"scanned": scanned, "niches": niches}
