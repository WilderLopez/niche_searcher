"""
Perfil de "clonabilidad".

Define qué hace que una app sea buena candidata a clonar para un desarrollador
iOS en solitario: que tenga demanda, que se monetice sin depender de anuncios,
que sea SENCILLA de construir y que se pueda COMPETIR (no dominada por gigantes
ni dependiente de efecto red o de una librería de contenido).

Todo aquí es ajustable a mano. El scoring vive en services/clone_score.py.
"""


class CloneProfile:

    # --- Facilidad de construcción por categoría (0 = imposible, 1 = trivial) ---
    CATEGORY_BUILDABILITY = {
        "Utilities": 0.95,
        "Productivity": 0.90,
        "Reference": 0.90,
        "Photo & Video": 0.85,
        "Graphics & Design": 0.85,
        "Weather": 0.85,
        "Education": 0.80,
        "Health & Fitness": 0.80,
        "Lifestyle": 0.75,
        "Books": 0.70,
        "Food & Drink": 0.70,
        "Business": 0.60,
        "Travel": 0.55,
        "Sports": 0.55,
        "Finance": 0.50,
        "Medical": 0.50,
        "Entertainment": 0.45,
        "News": 0.40,
        "Music": 0.40,
        "Shopping": 0.35,
        "Games": 0.35,
        "Navigation": 0.30,
        "Social Networking": 0.10,
    }
    DEFAULT_BUILDABILITY = 0.60

    # --- Simplicidad de DISEÑO por categoría (1 = UI estándar, 0 = todo arte) ---
    # Pensado para alguien que NO es diseñador: premia UI de listas/formularios/
    # cámara->resultado y castiga apps cuyo valor es el arte propio.
    CATEGORY_DESIGN_SIMPLICITY = {
        "Utilities": 0.95,
        "Productivity": 0.95,
        "Reference": 0.90,
        "Finance": 0.90,
        "Medical": 0.90,
        "Books": 0.90,
        "Health & Fitness": 0.85,
        "Education": 0.85,
        "Business": 0.85,
        "News": 0.85,
        "Weather": 0.80,
        "Food & Drink": 0.80,
        "Travel": 0.75,
        "Sports": 0.75,
        "Lifestyle": 0.70,
        "Music": 0.60,
        "Navigation": 0.60,
        "Entertainment": 0.55,
        "Photo & Video": 0.55,
        "Shopping": 0.50,
        "Graphics & Design": 0.40,
        "Social Networking": 0.40,
        "Games": 0.25,
    }
    DEFAULT_DESIGN_SIMPLICITY = 0.70

    # Apps cuyo producto ES el diseño/arte -> mucho trabajo de diseñador.
    DESIGN_HEAVY_KEYWORDS = [
        "wallpaper", "wallpapers", "live wallpaper", "theme", "themes",
        "aesthetic", "sticker", "stickers", "collage", "icon pack",
        "template", "templates", "animated background", "beautifully designed",
        "stunning design", "gorgeous", "customize your home screen",
    ]

    # --- Aprecio: valoración media (¿le gusta a la gente?) ---
    WELL_LIKED_RATING = 4.5
    POORLY_RATED = 3.8

    # Categorías que dependen de efecto red / dos lados de mercado -> casi
    # imposibles de arrancar en solitario.
    NETWORK_EFFECT_GENRES = {"Social Networking", "Dating", "Shopping", "Business"}

    # Apps que necesitan una librería de contenido propia (dramas, streaming...).
    # Si aparecen estas palabras en la descripción, se penaliza la construcción.
    CONTENT_HEAVY_KEYWORDS = [
        "episode", "episodes", "series", "drama", "dramas", "stream", "streaming",
        "channel", "live tv", "watch free", "thousands of videos", "catalog",
        "library of", "movies", "originals", "web series",
    ]

    # Señales (en la descripción) de que la app se monetiza con pago/suscripción.
    MONETIZATION_KEYWORDS = [
        "subscription", "subscribe", "premium", "pro version", "free trial",
        "unlock", "upgrade", "membership", "per week", "per month", "per year",
        "/week", "/month", "/year", "billed", "auto-renew", "paywall",
    ]

    # Gigantes: si el desarrollador contiene alguno de estos, es inviable competir.
    GIANT_SELLERS = [
        "google", "meta", "facebook", "instagram", "whatsapp", "bytedance",
        "tiktok", "adobe", "microsoft", "amazon", "apple", "netflix", "spotify",
        "fox", "disney", "snap", "pinterest", "x corp", "twitter", "openai",
        "samsung", "huawei", "tencent", "alibaba", "epic games", "king",
        "supercell", "zynga", "electronic arts", "ubisoft", "roblox", "uber",
        "airbnb", "paypal", "coinbase", "duolingo", "canva", "shopify",
        "the walt disney", "warner", "paramount", "nbcuniversal", "comcast",
    ]

    # --- Umbrales de complejidad ---
    HEAVY_SCREENSHOTS = 8      # más capturas => más pantallas/funciones
    HEAVY_SIZE_MB = 250        # apps grandes => más complejas
    BIG_SIZE_MB = 150
    LONG_DESCRIPTION = 2500    # descripción muy larga => muchas features

    # --- Saturación por nº de valoraciones (incumbente entrenado) ---
    SATURATED_RATINGS = 500_000
    CROWDED_RATINGS = 150_000

    # Momentum (val./día) que se considera "tope" al normalizar la demanda.
    DEMAND_CAP = 200

    # Puntuación mínima para marcar una app como objetivo recomendado.
    GOOD_SCORE = 45
