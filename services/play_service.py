"""
Capa de datos de Google Play.

Sustituye al antiguo scraping con Selenium + XPaths absolutos por la librería
`google-play-scraper`, que consulta los endpoints JSON internos de Google Play.
Es multiplataforma (Mac/Linux/Windows), no necesita navegador ni driver, y
devuelve los datos ya parseados (installs, ratings, score...).
"""

import re
from datetime import datetime

from google_play_scraper import app as gp_app
from google_play_scraper import search as gp_search
from google_play_scraper.exceptions import NotFoundError

# Consultamos siempre en inglés/US para tener un formato de fecha estable
# ("May 27, 2014") y evitar sorpresas de localización al parsear.
_LANG = "en"
_COUNTRY = "us"


class AppRemovedError(Exception):
    """La ficha ya no existe en Google Play (fue retirada)."""


class PlayService:

    @staticmethod
    def extract_app_id(url_or_id: str):
        """
        Acepta tanto una URL de Play como un package name y devuelve el
        identificador de la app (p.ej. 'com.spotify.music'), o None si no
        se puede extraer.
        """
        if not url_or_id:
            return None

        url_or_id = url_or_id.strip()

        # Si ya es un package name (sin barras ni parámetros)
        if "/" not in url_or_id and "?" not in url_or_id:
            return url_or_id or None

        match = re.search(r"[?&]id=([a-zA-Z0-9._]+)", url_or_id)
        return match.group(1) if match else None

    @staticmethod
    def app_id_to_url(app_id: str):
        return "https://play.google.com/store/apps/details?id=" + app_id

    @staticmethod
    def _parse_released(released_str):
        """'May 27, 2014' -> (millis, age_days) o (None, None) si no se puede."""
        if not released_str:
            return None, None
        try:
            dt = datetime.strptime(released_str.strip(), "%b %d, %Y")
        except ValueError:
            return None, None
        millis = round(dt.timestamp() * 1000)
        age_days = max((datetime.now() - dt).days, 0)
        return millis, age_days

    @staticmethod
    def fetch_app(app_id: str):
        """
        Descarga los datos de una app y los normaliza a un diccionario plano.

        Devuelve None si el id es inválido.
        Lanza AppRemovedError si la app ya no existe en Play.
        Propaga cualquier otra excepción (red, etc.) para que el motor decida.
        """
        if not app_id:
            return None

        try:
            d = gp_app(app_id, lang=_LANG, country=_COUNTRY)
        except NotFoundError:
            raise AppRemovedError(app_id)

        released_millis, age_days = PlayService._parse_released(d.get("released"))

        real_installs = d.get("realInstalls") or d.get("minInstalls") or 0
        installs_per_day = (real_installs / age_days) if age_days else 0.0

        return {
            "app_id": d.get("appId", app_id),
            "url": PlayService.app_id_to_url(d.get("appId", app_id)),
            "title": d.get("title"),
            "developer": d.get("developer"),
            "genre_id": d.get("genreId"),
            "min_installs": d.get("minInstalls") or 0,
            "real_installs": real_installs,
            "score": d.get("score") or 0.0,
            "ratings": d.get("ratings") or 0,
            "reviews": d.get("reviews") or 0,
            "free": bool(d.get("free")),
            "contains_ads": bool(d.get("containsAds")),
            "offers_iap": bool(d.get("offersIAP")),
            "released": d.get("released"),
            "released_millis": released_millis,
            "age_days": age_days,
            "installs_per_day": round(installs_per_day, 2),
        }

    @staticmethod
    def search_app_ids(query: str, limit: int = 30):
        """Busca apps por palabra clave y devuelve una lista de package names."""
        try:
            hits = gp_search(query, lang=_LANG, country=_COUNTRY, n_hits=limit)
        except Exception:
            return []
        return [h["appId"] for h in hits if h.get("appId")]
