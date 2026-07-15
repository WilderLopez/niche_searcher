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
from services.clone_score import score_app


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
                    score = score_app(data)
                    data.update(score)
                    data["flags"] = " · ".join(score["flags"])
                    AppstoreNicheModel.upsert(data)
                    niches += 1
                    print(
                        f"  [{data['clone_score']:>3}]  {(data['title'] or '')[:32]:32}  "
                        f"{data['rating_count']:>8,} val  {data['age_days']:>4}d  "
                        f"[{(data['genre'] or '')[:15]:15}]  {data['flags']}"
                    )

            if self.delay:
                time.sleep(self.delay)

        print(f"\nHecho. Evaluadas: {scanned} | Nichos: {niches}")
        print("Visualiza el ranking con: python3 main.py ios-report")
        return {"scanned": scanned, "niches": niches}
