"""
Criterio de nicho para el App Store (iOS).

Apple no publica descargas, así que el proxy de tracción es el número de
valoraciones (rating_count) y su velocidad (valoraciones/día). El criterio
busca apps *jóvenes* que ya acumulan *muchas valoraciones*: señal de un nicho
con demanda real.
"""


class AppStoreConfig:
    # País/storefront a consultar (us, es, mx, gb...).
    COUNTRY = "us"

    # Valoraciones mínimas (proxy de volumen de descargas).
    MIN_RATINGS = 1_000

    # Antigüedad máxima desde su publicación, en días.
    MAX_AGE_DAYS = 365

    # Filtro opcional por género de Apple (nombres tal cual los devuelve la API,
    # p.ej. "Education", "Productivity"). Lista vacía = sin filtrar.
    GENRES = []

    # Pausa entre peticiones a Apple (segundos). El Lookup va por lotes, así que
    # se hacen pocas llamadas y el rate limit no suele ser problema.
    REQUEST_DELAY = 0.3

    @staticmethod
    def is_niche(data: dict) -> bool:
        if data["rating_count"] < AppStoreConfig.MIN_RATINGS:
            return False
        if data["age_days"] is None:
            return False
        if data["age_days"] > AppStoreConfig.MAX_AGE_DAYS:
            return False
        if AppStoreConfig.GENRES and data["genre"] not in AppStoreConfig.GENRES:
            return False
        return True
