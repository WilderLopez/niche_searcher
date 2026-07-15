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

## App Store (iOS)

Además del buscador de Google Play, la herramienta incluye un buscador de nichos
para el **App Store**, pensado para desarrolladores iOS.

Apple **no publica el número de descargas** en público, así que se usa el **número
de valoraciones** (`userRatingCount`) y su **velocidad** (valoraciones/día) como
proxy de tracción — que es justo lo que hace la capa gratuita de las herramientas
ASO profesionales. Los datos salen de fuentes oficiales de Apple: **iTunes Search
API**, **iTunes Lookup API** (por lotes) y los **RSS Top Charts** por categoría.

```bash
# Descubrir candidatas iOS (por palabras clave y/o por top charts)
python3 main.py ios-discover "ai video" "language learning"
python3 main.py ios-charts

# Evaluar y detectar nichos
python3 main.py ios-evaluate --limit 500

# Ver estado / top de nichos
python3 main.py ios-stats

# Generar un dashboard visual (HTML autónomo, se abre con doble clic en el Mac)
python3 main.py ios-report --out report.html
```

El criterio base se ajusta en `config/appstore_config.py` (`MIN_RATINGS`,
`MAX_AGE_DAYS`, `COUNTRY`, `GENRES`). El **dashboard** (`report.html`) es un único
archivo sin dependencias: KPIs, un panel de en qué categorías se concentran los
objetivos y una tabla reordenable.

### Clone score — apps para clonar en solitario

Cada nicho recibe un **clone score (0-100)** pensado para un dev iOS que quiere
clonar apps rentables y sencillas **sin depender de anuncios**:

```
clone_score = oportunidad × viabilidad
  oportunidad = 0,45·demanda + 0,35·monetización + 0,20·aprecio
  viabilidad  = construibilidad × diseño_simple × competibilidad
```

- **Demanda**: valoraciones/día (proxy de tracción).
- **Monetización**: de pago o con suscripción (penaliza lo que solo vive de ads).
- **Aprecio**: valoración media (¿le gusta a la gente?).
- **Construibilidad**: categoría simple, app ligera, sin librería de contenido propia.
- **Diseño simple**: UI estándar (listas/formularios/cámara→resultado); penaliza apps
  cuyo producto es el arte (wallpapers, temas, editores con lienzo) — pensado para
  quien no es diseñador.
- **Competibilidad**: indie (no gigante), sin efecto red, mercado no saturado.

Las apps de UI estándar, fáciles y bien valoradas se marcan con **🛠 Ideal SwiftUI**.

Todas las perillas —pesos de categoría, listas de gigantes, palabras clave de
contenido/monetización, umbrales— están en **`config/clone_profile.py`** para que
lo afines a lo que tú sabes/quieres construir.

### Qué usan las herramientas pro (y qué no puedes replicar gratis)

- **Metadata, ratings, categorías, charts** → APIs oficiales gratuitas (lo que usa esta herramienta).
- **Volumen real de keywords** → *Search Popularity* de **Apple Search Ads** (requiere cuenta de ASA). Es la única fuente legítima de demanda de búsqueda en iOS.
- **Rankings por keyword** → scraping de la AMP API interna (`amp-api.apps.apple.com`, con token rotatorio).
- **Estimaciones de descargas/ingresos** → modelos propietarios + datos de panel/SDK. No hay dato público de descargas en iOS.

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
