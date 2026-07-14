# Niche Searcher

Herramienta personal para **detectar nichos de apps en Google Play**: aplicaciones
publicadas hace poco que ya acumulan muchas descargas (señal de un mercado con tracción).

No usa navegador ni Selenium: consulta los datos de Google Play a través de la
librería [`google-play-scraper`](https://pypi.org/project/google-play-scraper/),
así que funciona directamente en **Mac** (y Linux/Windows) sin drivers ni `.exe`.

## Cómo funciona

1. **discover** — busca apps por palabras clave y las añade a un *pool* de
   candidatas (tabla `gp_url_base` en SQLite). El repo ya trae ~150.000 candidatas.
2. **evaluate** — descarga los datos actuales de cada candidata (instalaciones,
   fecha de publicación, valoraciones...) y guarda como **nicho** las que cumplen
   el criterio de `config/app_config.py`.
3. **export** — vuelca los nichos a un CSV ordenado por *momentum* (instalaciones/día).

## Instalación (Mac)

Requiere Python 3.9+ (macOS ya trae Python 3; si no, `brew install python`).

```bash
cd niche_searcher
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Uso

```bash
# Ver el estado de la base de datos y el top de nichos
python3 main.py stats

# Añadir candidatas buscando por palabras clave
python3 main.py discover                     # usa config/seed_keywords.txt
python3 main.py discover "habit tracker" "budget app"

# Evaluar candidatas (200 por pasada por defecto). Repite para avanzar el pool.
python3 main.py evaluate --limit 200

# Exportar los nichos encontrados a CSV
python3 main.py export --out niches.csv
```

Sin argumentos, `python3 main.py` abre un **menú interactivo** con las mismas opciones.

## Ajustar el criterio de nicho

Edita `config/app_config.py`:

| Ajuste | Por defecto | Qué hace |
|---|---|---|
| `MIN_INSTALLS` | `100_000` | Instalaciones mínimas |
| `MAX_AGE_DAYS` | `365` | Antigüedad máxima desde su publicación |
| `CATEGORIES` | `[]` (todas) | Filtrar por categorías (p.ej. `["TOOLS", "PRODUCTIVITY"]`) |
| `REQUEST_DELAY` | `0.4` | Pausa entre peticiones (segundos) |

## Notas

- **Sé prudente con el ritmo.** Google puede limitar temporalmente si haces
  muchísimas peticiones seguidas; para eso está `REQUEST_DELAY` y el `--limit`.
- `evaluate` procesa las candidatas que hace más tiempo que no se revisan, así
  que puedes ejecutarlo repetidamente para ir recorriendo todo el pool.
- Las apps que ya no existen en Play se eliminan automáticamente del pool.
- Los resultados se guardan en la tabla `niche` de `databases/g_scraper.db`.

## Estructura

```
main.py                      CLI (discover / evaluate / export / stats)
config/app_config.py         Criterio de nicho
config/seed_keywords.txt     Palabras clave para 'discover'
services/play_service.py     Capa de datos (google-play-scraper)
services/export_service.py   Export a CSV
engines/discover_engine/     Descubrimiento por búsqueda
engines/evaluate_engine/     Evaluación y detección de nichos
models/                      Modelos SQLAlchemy y acceso a datos
databases/g_scraper.db       SQLite (pool de candidatas + nichos)
```
