"""
Motor de evaluación.

Toma candidatas del pool (gp_url_base), descarga sus datos actuales desde
Google Play y guarda como nicho las que superan el criterio de AppConfig.
"""

import time

from config.app_config import AppConfig
from models.gp_url_base_model import GpUrlBaseModel
from models.niche_model import NicheModel
from services.play_service import PlayService, AppRemovedError


class EvaluateEngine:

    def __init__(self, limit: int = 200, delay: float = None):
        self.limit = limit
        self.delay = AppConfig.REQUEST_DELAY if delay is None else delay

    def run(self):
        urls = GpUrlBaseModel.getBatchToScan(self.limit)

        if not urls:
            print("No hay candidatas en el pool. Ejecuta primero 'discover'.")
            return {"scanned": 0, "niches": 0, "removed": 0, "errors": 0}

        scanned = niches = removed = errors = 0

        print(f"Evaluando {len(urls)} apps...\n")

        for url in urls:
            app_id = PlayService.extract_app_id(url)
            if not app_id:
                continue

            try:
                data = PlayService.fetch_app(app_id)
            except AppRemovedError:
                removed += 1
                GpUrlBaseModel.delete(url)
                continue
            except Exception as e:
                errors += 1
                print(f"  ! error con {app_id}: {type(e).__name__}")
                continue
            finally:
                if self.delay:
                    time.sleep(self.delay)

            if data is None:
                continue

            scanned += 1

            if AppConfig.is_niche(data):
                NicheModel.upsert(data)
                niches += 1
                print(
                    f"  ✓ NICHO  {data['title'][:40]:40}  "
                    f"{data['real_installs']:>12,} inst.  "
                    f"{data['age_days']:>4}d  "
                    f"{data['installs_per_day']:>10,.0f}/día"
                )

        print(
            f"\nHecho. Evaluadas: {scanned} | Nichos: {niches} | "
            f"Retiradas: {removed} | Errores: {errors}"
        )
        return {
            "scanned": scanned,
            "niches": niches,
            "removed": removed,
            "errors": errors,
        }
