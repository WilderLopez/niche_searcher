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
from engines.discover_engine.discover_engine import DiscoverEngine
from engines.evaluate_engine.evaluate_engine import EvaluateEngine
from models import model
from models.gp_url_base_model import GpUrlBaseModel
from models.niche_model import NicheModel
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


def interactive_menu():
    actions = {
        "1": lambda: cmd_discover(),
        "2": lambda: cmd_evaluate(),
        "3": lambda: cmd_export(),
        "4": lambda: cmd_stats(),
    }
    while True:
        print("\n=== Niche Searcher ===")
        print("1) Descubrir apps (discover)")
        print("2) Evaluar candidatas (evaluate)")
        print("3) Exportar nichos a CSV")
        print("4) Ver estado")
        print("0) Salir")

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

    sub.add_parser("stats", help="Muestra el estado de la base de datos")

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
    else:
        interactive_menu()


if __name__ == "__main__":
    main()
