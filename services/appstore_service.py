"""
Capa de datos del App Store (iOS), basada en las APIs públicas de Apple:

- iTunes Search API   -> descubrir apps por término
- iTunes Lookup API   -> datos de apps por id (admite lotes: varios ids/llamada)
- RSS Top Charts      -> apps más descargadas por categoría/país

A diferencia de Google Play, Apple NO expone el número de descargas en público.
Usamos el nº de valoraciones (userRatingCount) y su velocidad como proxy de
tracción, que es justo lo que hacen las herramientas ASO en su capa gratuita.
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime

_BASE = "https://itunes.apple.com"
_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"

# Categorías de Google Play -> ids de género de Apple (para los top charts).
APPLE_GENRES = {
    "BUSINESS": 6000,
    "UTILITIES": 6002,
    "PRODUCTIVITY": 6007,
    "PHOTO_AND_VIDEO": 6008,
    "LIFESTYLE": 6012,
    "HEALTH_AND_FITNESS": 6013,
    "FINANCE": 6015,
    "ENTERTAINMENT": 6016,
    "EDUCATION": 6017,
    "REFERENCE": 6006,
    "FOOD_AND_DRINK": 6023,
    "GRAPHICS_AND_DESIGN": 6027,
}


class AppStoreService:

    @staticmethod
    def _get(url):
        req = urllib.request.Request(url, headers={"User-Agent": _UA})
        with urllib.request.urlopen(req, timeout=25) as r:
            return json.loads(r.read().decode("utf-8", "replace"))

    @staticmethod
    def _parse_release(released_str):
        """'2024-09-25T07:00:00Z' -> (millis, age_days) o (None, None)."""
        if not released_str:
            return None, None
        try:
            dt = datetime.strptime(released_str[:10], "%Y-%m-%d")
        except ValueError:
            return None, None
        millis = round(dt.timestamp() * 1000)
        age_days = max((datetime.now() - dt).days, 0)
        return millis, age_days

    @staticmethod
    def _normalize(a):
        released = a.get("releaseDate")
        released_millis, age_days = AppStoreService._parse_release(released)
        rating_count = a.get("userRatingCount") or 0
        ratings_per_day = (rating_count / age_days) if age_days else 0.0
        price = a.get("price") or 0

        try:
            file_size_mb = round(int(a.get("fileSizeBytes", 0)) / 1_000_000)
        except (TypeError, ValueError):
            file_size_mb = 0

        return {
            "app_id": str(a.get("trackId")),
            "bundle_id": a.get("bundleId"),
            "url": a.get("trackViewUrl"),
            "title": a.get("trackName"),
            "developer": a.get("sellerName") or a.get("artistName"),
            "genre": a.get("primaryGenreName"),
            "genre_id": str(a.get("primaryGenreId")),
            "avg_rating": a.get("averageUserRating") or 0.0,
            "rating_count": rating_count,
            "price": price,
            "currency": a.get("currency"),
            "free": price == 0,
            "released": released,
            "released_millis": released_millis,
            "age_days": age_days,
            "updated": a.get("currentVersionReleaseDate"),
            "content_rating": a.get("contentAdvisoryRating"),
            "ratings_per_day": round(ratings_per_day, 2),
            # señales de complejidad para el "clone score"
            "description": a.get("description") or "",
            "file_size_mb": file_size_mb,
            "screenshot_count": len(a.get("screenshotUrls") or []),
            "language_count": len(a.get("languageCodesISO2A") or []),
        }

    @staticmethod
    def search_app_ids(term, country="us", limit=50):
        """Busca apps por término y devuelve una lista de ids (trackId)."""
        url = (
            f"{_BASE}/search?term={urllib.parse.quote(term)}"
            f"&country={country}&entity=software&limit={limit}"
        )
        try:
            d = AppStoreService._get(url)
        except Exception:
            return []
        return [str(a["trackId"]) for a in d.get("results", []) if a.get("trackId")]

    @staticmethod
    def top_chart_ids(genre_id, country="us", feed="topfreeapplications", limit=100):
        """Devuelve los ids de las apps del top chart de una categoría."""
        url = f"{_BASE}/{country}/rss/{feed}/limit={limit}/genre={genre_id}/json"
        try:
            d = AppStoreService._get(url)
            entries = d["feed"].get("entry", [])
        except Exception:
            return []
        # Cuando solo hay 1 resultado Apple devuelve un dict en vez de lista.
        if isinstance(entries, dict):
            entries = [entries]
        return [e["id"]["attributes"]["im:id"] for e in entries if e.get("id")]

    @staticmethod
    def fetch_apps(app_ids, country="us"):
        """
        Datos de varias apps por id, en lotes (el Lookup admite varios ids por
        llamada). Devuelve una lista de dicts normalizados.
        """
        results = []
        for chunk_start in range(0, len(app_ids), 50):
            chunk = app_ids[chunk_start:chunk_start + 50]
            ids = ",".join(str(i) for i in chunk)
            url = f"{_BASE}/lookup?id={ids}&country={country}&entity=software"
            try:
                d = AppStoreService._get(url)
            except Exception:
                continue
            for a in d.get("results", []):
                if a.get("wrapperType") == "software" or a.get("kind") == "software":
                    results.append(AppStoreService._normalize(a))
        return results
