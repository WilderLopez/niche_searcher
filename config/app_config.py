"""
Criterio de nicho. Ajusta estos valores para afinar qué apps te interesan.

La idea: detectar apps *jóvenes* (publicadas hace poco) que ya acumulan
*muchas descargas*. Esa combinación es señal de un nicho con tracción.
"""


class AppConfig:
    # Instalaciones mínimas para considerar la app un nicho interesante.
    MIN_INSTALLS = 100_000

    # Antigüedad máxima desde su publicación, en días (365 = último año).
    MAX_AGE_DAYS = 365

    # Filtro opcional por categorías de Google Play. Deja la lista vacía para
    # no filtrar por categoría. Ejemplos de ids: TOOLS, PRODUCTIVITY,
    # BOOKS_AND_REFERENCE, HEALTH_AND_FITNESS, FINANCE, EDUCATION...
    CATEGORIES = []  # p.ej. ["TOOLS", "PRODUCTIVITY", "BOOKS_AND_REFERENCE"]

    # Pausa entre peticiones a Google Play, en segundos (buena vecindad para
    # no saturar y reducir el riesgo de bloqueo temporal).
    REQUEST_DELAY = 0.4

    @staticmethod
    def is_niche(data: dict) -> bool:
        """Aplica el criterio de nicho al dict que devuelve PlayService."""
        if data["real_installs"] < AppConfig.MIN_INSTALLS:
            return False

        # Sin fecha de publicación no podemos verificar que sea reciente.
        if data["age_days"] is None:
            return False

        if data["age_days"] > AppConfig.MAX_AGE_DAYS:
            return False

        if AppConfig.CATEGORIES and data["genre_id"] not in AppConfig.CATEGORIES:
            return False

        return True
