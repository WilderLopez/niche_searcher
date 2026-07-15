"""
Lector de reseñas del App Store.

Usa el feed RSS oficial de "customer reviews" de Apple (gratis, sin cuenta ni
token). Devuelve hasta ~500 reseñas por app (50 por página, hasta 10 páginas).
"""

import json
import urllib.request

_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"


class ReviewService:

    @staticmethod
    def _get(url):
        req = urllib.request.Request(url, headers={"User-Agent": _UA})
        with urllib.request.urlopen(req, timeout=25) as r:
            return json.loads(r.read().decode("utf-8", "replace"))

    @staticmethod
    def fetch_reviews(app_id, country="us", pages=10, sort="mostRecent"):
        """Devuelve una lista de dicts: {rating, title, content, version, author}."""
        reviews = []
        for page in range(1, pages + 1):
            url = (f"https://itunes.apple.com/{country}/rss/customerreviews/"
                   f"id={app_id}/sortBy={sort}/page={page}/json")
            try:
                d = ReviewService._get(url)
            except Exception:
                break

            entries = d.get("feed", {}).get("entry", [])
            # La primera "entry" del feed es la metadata de la app; se ignora si
            # no trae valoración.
            if isinstance(entries, dict):
                entries = [entries]

            page_had = 0
            for e in entries:
                if "im:rating" not in e:
                    continue
                reviews.append({
                    "rating": int(e["im:rating"]["label"]),
                    "title": e.get("title", {}).get("label", ""),
                    "content": e.get("content", {}).get("label", ""),
                    "version": e.get("im:version", {}).get("label", ""),
                    "author": e.get("author", {}).get("name", {}).get("label", ""),
                })
                page_had += 1

            if page_had == 0:
                break

        return reviews
