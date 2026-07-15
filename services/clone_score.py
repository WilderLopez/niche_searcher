"""
Motor de "clone score".

Puntuación 0-100 para un dev iOS en solitario (con Claude Code de copiloto) que
quiere clonar apps rentables, sencillas de construir, SIN diseño complejo y sin
depender de anuncios:

  clone_score = 100 * oportunidad * viabilidad

    oportunidad = 0.45·demanda + 0.35·monetización + 0.20·aprecio
    viabilidad  = construibilidad · competibilidad · simplicidad_diseño

Los factores de viabilidad son multiplicativos: si no puedes construirla, no
puedes competir, o exige mucho diseño, la nota se hunde por bueno que sea el
mercado. Devuelve sub-notas (0-100) y flags legibles.
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


def _appeal(data):
    """Valoración media -> 0..1. 3★ o menos = 0, 5★ = 1."""
    r = data.get("avg_rating") or 0
    appeal = max(0.0, min(1.0, (r - 3.0) / 2.0))
    flag = None
    if r >= P.WELL_LIKED_RATING:
        flag = f"★ Muy valorada ({r:.1f})"
    elif 0 < r < P.POORLY_RATED:
        flag = f"⚠ Baja valoración ({r:.1f})"
    return appeal, flag


def _buildability(data, desc):
    """Esfuerzo TÉCNico de construcción (independiente del diseño)."""
    flags = []
    genre = data.get("genre") or ""
    base = P.CATEGORY_BUILDABILITY.get(genre, P.DEFAULT_BUILDABILITY)

    if base >= 0.8:
        flags.append("Categoría simple")
    elif base < 0.4:
        flags.append("⚠ Categoría compleja")

    score = base
    if any(k in desc for k in P.CONTENT_HEAVY_KEYWORDS):
        score *= 0.5
        flags.append("⚠ Necesita contenido")
    size = data.get("file_size_mb", 0) or 0
    if size > P.HEAVY_SIZE_MB:
        score *= 0.8
        flags.append("⚠ App pesada")
    elif size > P.BIG_SIZE_MB:
        score *= 0.9
    if len(desc) > P.LONG_DESCRIPTION:
        score *= 0.9

    return min(score, 1.0), flags


def _design_simplicity(data, desc):
    """Cuánto diseño/arte propio exige (alto = UI estándar, poco diseño)."""
    flags = []
    genre = data.get("genre") or ""
    score = P.CATEGORY_DESIGN_SIMPLICITY.get(genre, P.DEFAULT_DESIGN_SIMPLICITY)

    if any(k in desc for k in P.DESIGN_HEAVY_KEYWORDS):
        score *= 0.4
        flags.append("⚠ Diseño intensivo")

    # Muchas capturas => muchas pantallas que diseñar.
    if data.get("screenshot_count", 0) > P.HEAVY_SCREENSHOTS:
        score *= 0.85

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
    """Recibe el dict normalizado y devuelve puntuación total, sub-notas y flags."""
    desc = (data.get("description") or "").lower()

    demand = _demand(data.get("ratings_per_day", 0))
    monetization, mon_flag = _monetization(data, desc)
    appeal, appeal_flag = _appeal(data)
    buildability, build_flags = _buildability(data, desc)
    design, design_flags = _design_simplicity(data, desc)
    competibility, comp_flags = _competibility(data)

    opportunity = 0.45 * demand + 0.35 * monetization + 0.20 * appeal
    feasibility = buildability * competibility * design
    total = round(100 * opportunity * feasibility)

    flags = [mon_flag]
    if appeal_flag:
        flags.append(appeal_flag)
    flags += build_flags + design_flags + comp_flags

    # Apps de UI estándar, fáciles de construir y competir: nuestro terreno.
    if buildability >= 0.8 and design >= 0.8 and competibility >= 0.7 and total >= P.GOOD_SCORE:
        flags.insert(0, "🛠 Ideal SwiftUI")

    return {
        "clone_score": total,
        "s_demand": round(demand * 100),
        "s_monetization": round(monetization * 100),
        "s_appeal": round(appeal * 100),
        "s_buildability": round(buildability * 100),
        "s_design": round(design * 100),
        "s_competibility": round(competibility * 100),
        "flags": flags,
    }
