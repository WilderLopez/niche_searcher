"""Exporta los nichos guardados a un CSV ordenado por momentum."""

import csv

from models.niche_model import NicheModel

_COLUMNS = [
    "app_id",
    "title",
    "developer",
    "genre_id",
    "real_installs",
    "min_installs",
    "score",
    "ratings",
    "reviews",
    "age_days",
    "installs_per_day",
    "free",
    "contains_ads",
    "offers_iap",
    "released",
    "url",
]


class ExportService:

    @staticmethod
    def to_csv(path: str = "niches.csv"):
        rows = NicheModel.all()

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(_COLUMNS)
            for r in rows:
                writer.writerow([getattr(r, c) for c in _COLUMNS])

        print(f"Exportados {len(rows)} nichos a {path}")
        return len(rows)
