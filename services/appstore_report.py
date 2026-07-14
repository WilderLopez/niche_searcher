"""
Genera un dashboard HTML autónomo con los nichos iOS detectados.

El archivo resultante es un HTML completo y self-contained (CSS y JS en línea,
sin recursos externos): se puede abrir con doble clic en el Mac, sin servidor.
"""

import html
from datetime import datetime

from config.appstore_config import AppStoreConfig
from models.appstore_model import AppstoreNicheModel


def _fmt(n):
    try:
        return f"{int(n):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "-"


def _age_class(age):
    if age is None:
        return "age-unknown", "?"
    if age < 90:
        return "age-fresh", f"{age}d"
    if age < 180:
        return "age-recent", f"{age}d"
    return "age-mature", f"{age}d"


_CSS = """
:root{
  --bg:#EAEEF2; --panel:#FFFFFF; --panel-2:#F5F7F9;
  --ink:#151B22; --muted:#5B6772; --faint:#8A96A1;
  --border:#DCE2E8; --accent:#0C7C84; --accent-soft:#0c7c8419;
  --heat-lo:#F6C177; --heat-mid:#EC7B3C; --heat-hi:#D62839;
  --fresh:#0E9F6E; --fresh-bg:#0e9f6e18;
  --recent:#0C7C84; --recent-bg:#0c7c8418;
  --mature-bg:#8a96a115;
}
@media (prefers-color-scheme:dark){
  :root{
    --bg:#0D1216; --panel:#151C22; --panel-2:#111820;
    --ink:#E7EDF2; --muted:#8B98A4; --faint:#5E6C77;
    --border:#232D36; --accent:#3CC7C0; --accent-soft:#3cc7c01f;
    --heat-lo:#E0A85B; --heat-mid:#EC7B3C; --heat-hi:#F0475E;
    --fresh:#31C48D; --fresh-bg:#31c48d1f;
    --recent:#3CC7C0; --recent-bg:#3cc7c01f;
    --mature-bg:#8a96a112;
  }
}
:root[data-theme="light"]{
  --bg:#EAEEF2; --panel:#FFFFFF; --panel-2:#F5F7F9;
  --ink:#151B22; --muted:#5B6772; --faint:#8A96A1;
  --border:#DCE2E8; --accent:#0C7C84; --accent-soft:#0c7c8419;
  --heat-lo:#F6C177; --heat-mid:#EC7B3C; --heat-hi:#D62839;
  --fresh:#0E9F6E; --fresh-bg:#0e9f6e18;
  --recent:#0C7C84; --recent-bg:#0c7c8418; --mature-bg:#8a96a115;
}
:root[data-theme="dark"]{
  --bg:#0D1216; --panel:#151C22; --panel-2:#111820;
  --ink:#E7EDF2; --muted:#8B98A4; --faint:#5E6C77;
  --border:#232D36; --accent:#3CC7C0; --accent-soft:#3cc7c01f;
  --heat-lo:#E0A85B; --heat-mid:#EC7B3C; --heat-hi:#F0475E;
  --fresh:#31C48D; --fresh-bg:#31c48d1f;
  --recent:#3CC7C0; --recent-bg:#3cc7c01f; --mature-bg:#8a96a112;
}

*{box-sizing:border-box}
body{
  margin:0; background:var(--bg); color:var(--ink);
  font-family:"SF Pro Text",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  font-size:15px; line-height:1.5; -webkit-font-smoothing:antialiased;
}
.wrap{max-width:1180px; margin:0 auto; padding:32px 24px 64px}
.num{font-family:"SF Mono",ui-monospace,Menlo,monospace; font-variant-numeric:tabular-nums}

header.top{display:flex; justify-content:space-between; align-items:flex-end;
  gap:20px; flex-wrap:wrap; margin-bottom:8px}
h1{font-family:"SF Pro Display",-apple-system,BlinkMacSystemFont,sans-serif;
  font-size:30px; font-weight:700; letter-spacing:-.02em; margin:0; text-wrap:balance}
.eyebrow{text-transform:uppercase; letter-spacing:.14em; font-size:11px;
  font-weight:600; color:var(--accent); margin:0 0 6px}
.meta{color:var(--muted); font-size:13px; text-align:right}
.meta b{color:var(--ink)}

.kpis{display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin:24px 0}
.kpi{background:var(--panel); border:1px solid var(--border); border-radius:14px; padding:16px 18px}
.kpi .label{font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:.06em}
.kpi .val{font-size:26px; font-weight:700; letter-spacing:-.02em; margin-top:6px}
.kpi .sub{font-size:12px; color:var(--faint); margin-top:2px}

.panel{background:var(--panel); border:1px solid var(--border); border-radius:16px;
  padding:20px 22px; margin-bottom:22px}
.panel h2{font-size:13px; text-transform:uppercase; letter-spacing:.08em;
  color:var(--muted); margin:0 0 16px; font-weight:600}

.clusters{display:grid; gap:9px}
.crow{display:grid; grid-template-columns:150px 1fr 40px; align-items:center; gap:12px}
.crow .cname{font-size:13px; color:var(--ink); text-align:right; white-space:nowrap;
  overflow:hidden; text-overflow:ellipsis}
.crow .ctrack{background:var(--panel-2); border-radius:5px; height:10px; overflow:hidden}
.crow .cbar{height:100%; background:var(--accent); border-radius:5px}
.crow .ccount{font-size:12px; color:var(--muted); text-align:left}

.tablewrap{overflow-x:auto; background:var(--panel); border:1px solid var(--border); border-radius:16px}
table{border-collapse:collapse; width:100%; min-width:760px}
th,td{text-align:left; padding:12px 14px; border-bottom:1px solid var(--border); white-space:nowrap}
thead th{position:sticky; top:0; background:var(--panel); font-size:11px; text-transform:uppercase;
  letter-spacing:.06em; color:var(--muted); font-weight:600; cursor:pointer; user-select:none}
thead th.right{text-align:right}
thead th[aria-sort="ascending"]::after{content:" ▲"; color:var(--accent)}
thead th[aria-sort="descending"]::after{content:" ▼"; color:var(--accent)}
tbody tr:hover{background:var(--accent-soft)}
tbody tr:last-child td{border-bottom:none}
td.right{text-align:right}
.rank{color:var(--faint); font-size:13px}
.app{font-weight:600}
.app a{color:var(--ink); text-decoration:none}
.app a:hover{color:var(--accent); text-decoration:underline}
.dev{color:var(--muted); font-size:12px; font-weight:400}
.chip{display:inline-block; font-size:11px; padding:2px 8px; border-radius:20px;
  background:var(--panel-2); color:var(--muted); border:1px solid var(--border)}
.pill{display:inline-block; font-size:12px; padding:2px 9px; border-radius:20px; font-weight:600}
.age-fresh{color:var(--fresh); background:var(--fresh-bg)}
.age-recent{color:var(--recent); background:var(--recent-bg)}
.age-mature{color:var(--muted); background:var(--mature-bg)}
.age-unknown{color:var(--faint); background:var(--mature-bg)}
.mom{position:relative; min-width:120px}
.mom .track{position:absolute; inset:8px 14px; border-radius:5px; background:var(--panel-2)}
.mom .bar{position:absolute; left:14px; top:8px; bottom:8px; border-radius:5px}
.mom .v{position:relative; z-index:1; float:right; font-weight:600}
.free{color:var(--fresh); font-weight:600}
footer{color:var(--faint); font-size:12px; margin-top:26px; line-height:1.7}
@media (max-width:720px){ .kpis{grid-template-columns:repeat(2,1fr)} .crow{grid-template-columns:110px 1fr 34px} }
"""

_JS = """
(function(){
  var table=document.getElementById('nichetable');
  if(!table) return;
  var ths=table.querySelectorAll('thead th');
  ths.forEach(function(th,idx){
    th.addEventListener('click',function(){
      var asc=th.getAttribute('aria-sort')!=='ascending';
      ths.forEach(function(o){o.removeAttribute('aria-sort')});
      th.setAttribute('aria-sort',asc?'ascending':'descending');
      var rows=Array.prototype.slice.call(table.querySelectorAll('tbody tr'));
      rows.sort(function(a,b){
        var x=a.children[idx].dataset.v, y=b.children[idx].dataset.v;
        var nx=parseFloat(x), ny=parseFloat(y);
        if(!isNaN(nx)&&!isNaN(ny)){return asc?nx-ny:ny-nx;}
        return asc?(''+x).localeCompare(y):(''+y).localeCompare(x);
      });
      var tb=table.querySelector('tbody');
      rows.forEach(function(r){tb.appendChild(r)});
    });
  });
})();
"""


class AppStoreReport:

    @staticmethod
    def generate(out="report.html"):
        niches = AppstoreNicheModel.all()
        if not niches:
            print("No hay nichos que mostrar. Ejecuta primero 'ios-evaluate'.")
            return 0

        max_mom = max((n.ratings_per_day or 0) for n in niches) or 1
        newest = min((n.age_days for n in niches if n.age_days is not None), default=None)
        top = niches[0]

        # --- clusters por categoría ---
        cats = {}
        for n in niches:
            cats[n.genre or "?"] = cats.get(n.genre or "?", 0) + 1
        cats = sorted(cats.items(), key=lambda kv: kv[1], reverse=True)
        cmax = cats[0][1] if cats else 1
        cluster_rows = "".join(
            f'<div class="crow"><div class="cname">{html.escape(name)}</div>'
            f'<div class="ctrack"><div class="cbar" style="width:{max(6, round(cnt / cmax * 100))}%"></div></div>'
            f'<div class="ccount num">{cnt}</div></div>'
            for name, cnt in cats
        )

        # --- filas de la tabla ---
        rows = []
        for i, n in enumerate(niches, 1):
            age_cls, age_txt = _age_class(n.age_days)
            mom = n.ratings_per_day or 0
            pct = max(3, round(mom / max_mom * 100))
            ratio = mom / max_mom
            heat = "var(--heat-hi)" if ratio > .66 else "var(--heat-mid)" if ratio > .33 else "var(--heat-lo)"
            price = '<span class="free">Gratis</span>' if n.free else f'{n.price} {n.currency or ""}'
            url = html.escape(n.url or "#")
            title = html.escape(n.title or "")
            dev = html.escape(n.developer or "")
            genre = html.escape(n.genre or "")
            rows.append(
                f'<tr>'
                f'<td class="rank num" data-v="{i}">{i}</td>'
                f'<td class="app" data-v="{title.lower()}"><a href="{url}" target="_blank" rel="noopener">{title}</a>'
                f'<div class="dev">{dev}</div></td>'
                f'<td data-v="{genre}"><span class="chip">{genre}</span></td>'
                f'<td class="right num" data-v="{n.rating_count or 0}">{_fmt(n.rating_count)}</td>'
                f'<td class="right" data-v="{n.age_days if n.age_days is not None else 99999}">'
                f'<span class="pill {age_cls}">{age_txt}</span></td>'
                f'<td class="right mom num" data-v="{mom:.2f}">'
                f'<span class="track"></span>'
                f'<span class="bar" style="width:calc((100% - 28px) * {pct} / 100); background:{heat}"></span>'
                f'<span class="v">{_fmt(round(mom))}</span></td>'
                f'<td class="right num" data-v="{0 if n.free else (n.price or 0)}">{price}</td>'
                f'</tr>'
            )
        table_rows = "".join(rows)

        genres_txt = ", ".join(g for g, _ in cats[:3])
        now = datetime.now().strftime("%d/%m/%Y %H:%M")

        kpis = (
            f'<div class="kpi"><div class="label">Nichos detectados</div>'
            f'<div class="val num">{len(niches)}</div><div class="sub">apps que cumplen el criterio</div></div>'
            f'<div class="kpi"><div class="label">Categorías con nicho</div>'
            f'<div class="val num">{len(cats)}</div><div class="sub">concentradas en {html.escape(genres_txt)}</div></div>'
            f'<div class="kpi"><div class="label">Mayor momentum</div>'
            f'<div class="val num">{_fmt(round(top.ratings_per_day or 0))}</div>'
            f'<div class="sub">val./día · {html.escape((top.title or "")[:22])}</div></div>'
            f'<div class="kpi"><div class="label">Más nueva</div>'
            f'<div class="val num">{newest if newest is not None else "-"}<span style="font-size:15px"> días</span></div>'
            f'<div class="sub">desde su lanzamiento</div></div>'
        )

        doc = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>App Store Niche Radar</title>
<style>{_CSS}</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <div>
      <p class="eyebrow">App Store · Niche Radar</p>
      <h1>Nichos iOS con tracción</h1>
    </div>
    <div class="meta">
      Storefront <b>{AppStoreConfig.COUNTRY.upper()}</b> · generado el <b>{now}</b><br>
      Criterio: &ge; <b>{_fmt(AppStoreConfig.MIN_RATINGS)}</b> valoraciones ·
      publicada hace &le; <b>{AppStoreConfig.MAX_AGE_DAYS}</b> días
    </div>
  </header>

  <div class="kpis">{kpis}</div>

  <div class="panel">
    <h2>Dónde se concentran los nichos</h2>
    <div class="clusters">{cluster_rows}</div>
  </div>

  <div class="tablewrap">
    <table id="nichetable">
      <thead><tr>
        <th class="right">#</th>
        <th>App</th>
        <th>Categoría</th>
        <th class="right">Valoraciones</th>
        <th class="right">Edad</th>
        <th class="right">Momentum ▸ val./día</th>
        <th class="right">Precio</th>
      </tr></thead>
      <tbody>{table_rows}</tbody>
    </table>
  </div>

  <footer>
    Momentum = valoraciones ÷ días desde el lanzamiento (proxy de velocidad de descargas,
    ya que Apple no publica instalaciones). Haz clic en cualquier cabecera para reordenar.<br>
    Datos vía iTunes Search/Lookup API y RSS de Apple. Herramienta personal — niche_searcher.
  </footer>
</div>
<script>{_JS}</script>
</body>
</html>"""

        with open(out, "w", encoding="utf-8") as f:
            f.write(doc)
        print(f"Dashboard generado: {out}  ({len(niches)} nichos)")
        return len(niches)
