"""
Minería temática de reseñas.

Descarga las reseñas de una app y clasifica las negativas (1-3★) en temas de
queja, con citas de ejemplo. Sirve para encontrar el hueco de un incumbente:
donde sus usuarios de pago se quejan está nuestra oportunidad de diferenciarnos.
"""

from services.review_service import ReviewService

# Temas de queja habituales en apps de identificación/colección. Ajustables.
THEMES = {
    "Cobros / suscripción / reembolso": [
        "charge", "charged", "refund", "subscription", "cancel", "billed",
        "money back", "auto-renew", "renew", "expensive", "overpriced",
    ],
    "Paywall engañoso / trial trampa": [
        "scam", "paywall", "free trial", "trial", "bait", "trick", "forced",
        "hidden fee", "deceptive", "misleading", "trap", "not as advertised",
    ],
    "Precisión / identificación errónea": [
        "wrong", "inaccurate", "incorrect", "not accurate", "doesn't work",
        "didn't work", "useless", "made up", "hallucinat", "not right",
        "garbage", "random", "generic",
    ],
    "Valor / precio poco fiable": [
        "value", "worth", "estimate", "appraisal", "valuation", "price guide",
        "undervalue", "overvalue",
    ],
    "Bugs / rendimiento": [
        "crash", "bug", "freeze", "glitch", "won't open", "error", "broken",
        "stuck", "loading", "slow", "performance",
    ],
    "Colección / organización": [
        "collection", "organize", "sort", "export", "folder", "catalog",
        "wishlist", "binder", "import", "inventory", "add notes", "portfolio",
    ],
    "Soporte al cliente": [
        "support", "respond", "customer service", "no response", "contact",
    ],
}


class ReviewMiner:

    @staticmethod
    def mine(app_id, country="us", pages=10):
        reviews = ReviewService.fetch_reviews(app_id, country=country, pages=pages)
        neg = [r for r in reviews if r["rating"] <= 3]

        dist = {i: 0 for i in range(1, 6)}
        for r in reviews:
            dist[r["rating"]] = dist.get(r["rating"], 0) + 1

        themes = []
        for name, kws in THEMES.items():
            hits = [r for r in neg
                    if any(k in (r["title"] + " " + r["content"]).lower() for k in kws)]
            if hits:
                themes.append({
                    "theme": name,
                    "count": len(hits),
                    "pct": round(100 * len(hits) / len(neg)) if neg else 0,
                    "samples": [r["content"][:200].strip() for r in hits[:3]],
                })
        themes.sort(key=lambda t: t["count"], reverse=True)

        return {"total": len(reviews), "distribution": dist,
                "negatives": len(neg), "themes": themes}

    @staticmethod
    def print_report(app_id, country="us", pages=10):
        data = ReviewMiner.mine(app_id, country=country, pages=pages)
        print(f"Reseñas: {data['total']} | distribución {data['distribution']} | "
              f"negativas: {data['negatives']}")
        for t in data["themes"]:
            print(f"\n• {t['theme']}: {t['count']} ({t['pct']}% de las negativas)")
            for s in t["samples"][:2]:
                print(f"    \"{s[:160]}\"")
        return data
