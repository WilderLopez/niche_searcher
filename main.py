"""
Niche Searcher — herramienta personal para detectar nichos de apps en Google Play.

Uso:
    python main.py                      menú interactivo
    python main.py discover [kw...]     busca apps y las añade al pool
    python main.py evaluate [--limit N] evalúa candidatas y guarda los nichos
    python main.py export [--out F]     exporta los nichos a CSV
    python main.py stats                muestra el estado de la BD
"""

import argparse

from config.app_config import AppConfig
from config.appstore_config import AppStoreConfig
from engines.discover_engine.discover_engine import DiscoverEngine
from engines.evaluate_engine.evaluate_engine import EvaluateEngine
from engines.appstore.discover_engine import AppStoreDiscoverEngine
from engines.appstore.evaluate_engine import AppStoreEvaluateEngine
from models import model
from models.gp_url_base_model import GpUrlBaseModel
from models.niche_model import NicheModel
from models.appstore_model import AppstoreCandidateModel, AppstoreNicheModel
from services.export_service import ExportService


def cmd_discover(keywords=None, per_keyword=30):
    DiscoverEngine(keywords=keywords, per_keyword=per_keyword).run()


def cmd_evaluate(limit=200, delay=None):
    EvaluateEngine(limit=limit, delay=delay).run()


def cmd_export(out="niches.csv"):
    ExportService.to_csv(out)


def cmd_stats():
    print("Estado de la base de datos")
    print("-" * 32)
    print(f"Candidatas en el pool : {GpUrlBaseModel.count():>8,}")
    print(f"Nichos detectados     : {NicheModel.count():>8,}")
    print()
    print("Criterio de nicho actual (config/app_config.py):")
    print(f"  Instalaciones mínimas : {AppConfig.MIN_INSTALLS:,}")
    print(f"  Antigüedad máxima     : {AppConfig.MAX_AGE_DAYS} días")
    print(f"  Categorías            : {AppConfig.CATEGORIES or 'todas'}")

    top = NicheModel.top(limit=10)
    if top:
        print("\nTop 10 nichos por momentum (instalaciones/día):")
        for n in top:
            print(
                f"  {n.installs_per_day:>10,.0f}/día  "
                f"{n.real_installs:>12,} inst.  "
                f"{(n.title or '')[:38]:38}  [{n.genre_id}]"
            )


# ---------------------------------------------------------------------------
# App Store (iOS)
# ---------------------------------------------------------------------------

def cmd_ios_discover(keywords=None, per_keyword=40, country=None):
    AppStoreDiscoverEngine(keywords=keywords, per_keyword=per_keyword, country=country).run_search()


def cmd_ios_charts(country=None, per_genre=100):
    AppStoreDiscoverEngine(country=country).run_charts(per_genre=per_genre)


def cmd_ios_evaluate(limit=200, country=None, delay=None):
    AppStoreEvaluateEngine(limit=limit, country=country, delay=delay).run()


def cmd_ios_report(out="report.html"):
    from services.appstore_report import AppStoreReport
    AppStoreReport.generate(out)


def cmd_ios_stats():
    print("Estado App Store (iOS)")
    print("-" * 32)
    print(f"Candidatas en el pool : {AppstoreCandidateModel.count():>8,}")
    print(f"Nichos detectados     : {AppstoreNicheModel.count():>8,}")
    print()
    print("Criterio de nicho (config/appstore_config.py):")
    print(f"  Valoraciones mínimas : {AppStoreConfig.MIN_RATINGS:,}")
    print(f"  Antigüedad máxima    : {AppStoreConfig.MAX_AGE_DAYS} días")
    print(f"  País                 : {AppStoreConfig.COUNTRY}")
    top = AppstoreNicheModel.top(limit=10)
    if top:
        print("\nTop 10 nichos iOS por momentum (valoraciones/día):")
        for n in top:
            print(
                f"  {n.ratings_per_day:>8,.0f}/día  {n.rating_count:>9,} val.  "
                f"{n.age_days:>4}d  {(n.title or '')[:34]:34} [{n.genre}]"
            )


def interactive_menu():
    actions = {
        "1": lambda: cmd_ios_discover(),
        "2": lambda: cmd_ios_charts(),
        "3": lambda: cmd_ios_evaluate(),
        "4": lambda: cmd_ios_report(),
        "5": lambda: cmd_ios_stats(),
        "6": lambda: cmd_discover(),
        "7": lambda: cmd_evaluate(),
        "8": lambda: cmd_export(),
        "9": lambda: cmd_stats(),
    }
    while True:
        print("\n=== Niche Searcher ===")
        print("  App Store (iOS)")
        print("  1) Descubrir por keywords   2) Descubrir por charts")
        print("  3) Evaluar candidatas       4) Generar dashboard HTML")
        print("  5) Ver estado")
        print("  Google Play (Android)")
        print("  6) Descubrir   7) Evaluar   8) Exportar CSV   9) Ver estado")
        print("  0) Salir")

        choice = input("Elige una opción: ").strip()
        if choice == "0":
            break
        action = actions.get(choice)
        if action:
            action()
        else:
            print("Opción no válida.")


def build_parser():
    parser = argparse.ArgumentParser(description="Detector de nichos de apps en Google Play")
    sub = parser.add_subparsers(dest="command")

    p_disc = sub.add_parser("discover", help="Busca apps y las añade al pool")
    p_disc.add_argument("keywords", nargs="*", help="Palabras clave (por defecto: config/seed_keywords.txt)")
    p_disc.add_argument("--per-keyword", type=int, default=30, help="Resultados por palabra clave")

    p_eval = sub.add_parser("evaluate", help="Evalúa candidatas y guarda los nichos")
    p_eval.add_argument("--limit", type=int, default=200, help="Cuántas apps evaluar en esta pasada")
    p_eval.add_argument("--delay", type=float, default=None, help="Pausa entre peticiones (s)")

    p_exp = sub.add_parser("export", help="Exporta los nichos a CSV")
    p_exp.add_argument("--out", default="niches.csv", help="Ruta del CSV de salida")

    sub.add_parser("stats", help="Muestra el estado de la base de datos (Google Play)")

    # --- App Store (iOS) ---
    p_id = sub.add_parser("ios-discover", help="Busca apps iOS por keyword y las añade al pool")
    p_id.add_argument("keywords", nargs="*", help="Palabras clave (por defecto: config/seed_keywords.txt)")
    p_id.add_argument("--per-keyword", type=int, default=40)
    p_id.add_argument("--country", default=None, help="Storefront (us, es, mx...)")

    p_ic = sub.add_parser("ios-charts", help="Recoge top charts iOS por categoría")
    p_ic.add_argument("--country", default=None)
    p_ic.add_argument("--per-genre", type=int, default=100)

    p_ie = sub.add_parser("ios-evaluate", help="Evalúa candidatas iOS y guarda los nichos")
    p_ie.add_argument("--limit", type=int, default=200)
    p_ie.add_argument("--country", default=None)
    p_ie.add_argument("--delay", type=float, default=None)

    p_ir = sub.add_parser("ios-report", help="Genera un dashboard HTML de los nichos iOS")
    p_ir.add_argument("--out", default="report.html")

    sub.add_parser("ios-stats", help="Muestra el estado del buscador iOS")

    return parser


def main():
    # Garantiza que las tablas existen (incluida la nueva tabla 'niche').
    model.init()

    parser = build_parser()
    args = parser.parse_args()

    if args.command == "discover":
        cmd_discover(keywords=args.keywords or None, per_keyword=args.per_keyword)
    elif args.command == "evaluate":
        cmd_evaluate(limit=args.limit, delay=args.delay)
    elif args.command == "export":
        cmd_export(out=args.out)
    elif args.command == "stats":
        cmd_stats()
    elif args.command == "ios-discover":
        cmd_ios_discover(keywords=args.keywords or None, per_keyword=args.per_keyword, country=args.country)
    elif args.command == "ios-charts":
        cmd_ios_charts(country=args.country, per_genre=args.per_genre)
    elif args.command == "ios-evaluate":
        cmd_ios_evaluate(limit=args.limit, country=args.country, delay=args.delay)
    elif args.command == "ios-report":
        cmd_ios_report(out=args.out)
    elif args.command == "ios-stats":
        cmd_ios_stats()
    else:
        interactive_menu()


if __name__ == "__main__":
    main()
