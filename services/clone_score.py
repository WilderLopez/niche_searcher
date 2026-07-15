"""
Motor de "clone score".

Combina cuatro señales en una puntuación 0-100 orientada a un dev iOS solo que
quiere clonar apps rentables y sencillas, sin depender de anuncios:

  clone_score = 100 * oportunidad * viabilidad

    oportunidad = 0.55·demanda + 0.45·monetización   (¿hay mercado que paga?)
    viabilidad  = construibilidad · competibilidad    (¿puedo hacerla y competir?)

Construibilidad y competibilidad son multiplicativas: si no puedes construirla
o no puedes competir, la nota se hunde por bueno que sea el mercado.

Devuelve también sub-notas y flags legibles para explicar el porqué.
"""

import math

from config.clone_profile import CloneProfile as P


def _demand(momentum):
    """val./día -> 0..1 en escala logarítmica (rendimientos decrecientes)."""
    momentum = max(momentum or 0, 0)
    return min(1.0, math.log10(1 + momentum) / math.log10(1 + P.DEMAND_CAP))


def _monetization(data, desc):
    if data["price"] and data["price"] > 0:
        return 1.0, "De pago"
    if any(k in desc for k in P.MONETIZATION_KEYWORDS):
        return 0.8, "Gratis + suscripción"
    return 0.25, "⚠ Sin monetización clara"


def _buildability(data, desc):
    flags = []
    genre = data.get("genre") or ""
    base = P.CATEGORY_BUILDABILITY.get(genre, P.DEFAULT_BUILDABILITY)

    # La etiqueta de categoría se basa en la categoría en sí, no en las
    # penalizaciones concretas de esta app.
    if base >= 0.8:
        flags.append("Categoría simple")
    elif base < 0.4:
        flags.append("⚠ Categoría compleja")

    score = base
    if any(k in desc for k in P.CONTENT_HEAVY_KEYWORDS):
        score *= 0.5
        flags.append("⚠ Necesita contenido")
    if data.get("screenshot_count", 0) > P.HEAVY_SCREENSHOTS:
        score *= 0.85
    size = data.get("file_size_mb", 0) or 0
    if size > P.HEAVY_SIZE_MB:
        score *= 0.8
        flags.append("⚠ App pesada")
    elif size > P.BIG_SIZE_MB:
        score *= 0.9
    if len(desc) > P.LONG_DESCRIPTION:
        score *= 0.9

    return min(score, 1.0), flags


def _competibility(data):
    flags = []
    score = 1.0
    genre = data.get("genre") or ""
    dev = (data.get("developer") or "").lower()

    if genre in P.NETWORK_EFFECT_GENRES:
        score *= 0.15
        flags.append("⚠ Efecto red")

    if any(g in dev for g in P.GIANT_SELLERS):
        score *= 0.30
        flags.append("⚠ Incumbente gigante")
    else:
        flags.append("Indie")

    rc = data.get("rating_count", 0) or 0
    if rc > P.SATURATED_RATINGS:
        score *= 0.5
        flags.append("⚠ Mercado saturado")
    elif rc > P.CROWDED_RATINGS:
        score *= 0.75

    return min(score, 1.0), flags


def score_app(data):
    """
    Recibe el dict normalizado de PlayService/AppStoreService y devuelve un dict
    con la puntuación total, las sub-notas (0-100) y los flags.
    """
    desc = (data.get("description") or "").lower()

    demand = _demand(data.get("ratings_per_day", 0))
    monetization, mon_flag = _monetization(data, desc)
    buildability, build_flags = _buildability(data, desc)
    competibility, comp_flags = _competibility(data)

    opportunity = 0.55 * demand + 0.45 * monetization
    feasibility = buildability * competibility
    total = round(100 * opportunity * feasibility)

    flags = [mon_flag] + build_flags + comp_flags

    return {
        "clone_score": total,
        "s_demand": round(demand * 100),
        "s_monetization": round(monetization * 100),
        "s_buildability": round(buildability * 100),
        "s_competibility": round(competibility * 100),
        "flags": flags,
    }
