"""
Genera un dashboard HTML autónomo con los nichos iOS, rankeados por "clone score".

El archivo resultante es un HTML completo y self-contained (CSS y JS en línea,
sin recursos externos): se abre con doble clic en el Mac, sin servidor.
"""

import html
from datetime import datetime

from config.appstore_config import AppStoreConfig
from config.clone_profile import CloneProfile
from models.appstore_model import AppstoreNicheModel


def _fmt(n):
    try:
        return f"{int(n):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "-"


def _age_class(age):
    if age is None:
        return "age-mature", "?"
    if age < 90:
        return "age-fresh", f"{age}d"
    if age < 180:
        return "age-recent", f"{age}d"
    return "age-mature", f"{age}d"


def _score_class(s):
    s = s or 0
    if s >= 60:
        return "sc-top"
    if s >= CloneProfile.GOOD_SCORE:
        return "sc-good"
    if s >= 30:
        return "sc-mid"
    return "sc-low"


_CSS = """
:root{
  --bg:#EAEEF2; --panel:#FFFFFF; --panel-2:#F5F7F9;
  --ink:#151B22; --muted:#5B6772; --faint:#8A96A1;
  --border:#DCE2E8; --accent:#0C7C84; --accent-soft:#0c7c8419;
  --good:#0E9F6E; --good-bg:#0e9f6e18; --warn:#C97A17; --warn-bg:#e0a03518;
  --bad:#C6413B; --bad-bg:#c6413b14;
}
@media (prefers-color-scheme:dark){:root{
  --bg:#0D1216; --panel:#151C22; --panel-2:#111820;
  --ink:#E7EDF2; --muted:#8B98A4; --faint:#5E6C77;
  --border:#232D36; --accent:#3CC7C0; --accent-soft:#3cc7c01f;
  --good:#31C48D; --good-bg:#31c48d1f; --warn:#E0A85B; --warn-bg:#e0a85b1c;
  --bad:#F0685E; --bad-bg:#f0685e18;
}}
:root[data-theme="light"]{
  --bg:#EAEEF2; --panel:#FFFFFF; --panel-2:#F5F7F9;
  --ink:#151B22; --muted:#5B6772; --faint:#8A96A1;
  --border:#DCE2E8; --accent:#0C7C84; --accent-soft:#0c7c8419;
  --good:#0E9F6E; --good-bg:#0e9f6e18; --warn:#C97A17; --warn-bg:#e0a03518;
  --bad:#C6413B; --bad-bg:#c6413b14;
}
:root[data-theme="dark"]{
  --bg:#0D1216; --panel:#151C22; --panel-2:#111820;
  --ink:#E7EDF2; --muted:#8B98A4; --faint:#5E6C77;
  --border:#232D36; --accent:#3CC7C0; --accent-soft:#3cc7c01f;
  --good:#31C48D; --good-bg:#31c48d1f; --warn:#E0A85B; --warn-bg:#e0a85b1c;
  --bad:#F0685E; --bad-bg:#f0685e18;
}

*{box-sizing:border-box}
body{margin:0; background:var(--bg); color:var(--ink);
  font-family:"SF Pro Text",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  font-size:15px; line-height:1.5; -webkit-font-smoothing:antialiased}
.wrap{max-width:1240px; margin:0 auto; padding:32px 24px 64px}
.num{font-family:"SF Mono",ui-monospace,Menlo,monospace; font-variant-numeric:tabular-nums}

header.top{display:flex; justify-content:space-between; align-items:flex-end; gap:20px; flex-wrap:wrap}
h1{font-family:"SF Pro Display",-apple-system,BlinkMacSystemFont,sans-serif;
  font-size:30px; font-weight:700; letter-spacing:-.02em; margin:0; text-wrap:balance}
.eyebrow{text-transform:uppercase; letter-spacing:.14em; font-size:11px; font-weight:600;
  color:var(--accent); margin:0 0 6px}
.lede{color:var(--muted); font-size:14px; margin:8px 0 0; max-width:60ch}
.meta{color:var(--muted); font-size:13px; text-align:right}
.meta b{color:var(--ink)}

.kpis{display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin:24px 0}
.kpi{background:var(--panel); border:1px solid var(--border); border-radius:14px; padding:16px 18px}
.kpi .label{font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:.06em}
.kpi .val{font-size:26px; font-weight:700; letter-spacing:-.02em; margin-top:6px}
.kpi .sub{font-size:12px; color:var(--faint); margin-top:2px}

.panel{background:var(--panel); border:1px solid var(--border); border-radius:16px; padding:20px 22px; margin-bottom:22px}
.panel h2{font-size:13px; text-transform:uppercase; letter-spacing:.08em; color:var(--muted); margin:0 0 16px; font-weight:600}
.clusters{display:grid; gap:9px}
.crow{display:grid; grid-template-columns:150px 1fr 40px; align-items:center; gap:12px}
.crow .cname{font-size:13px; text-align:right; white-space:nowrap; overflow:hidden; text-overflow:ellipsis}
.crow .ctrack{background:var(--panel-2); border-radius:5px; height:10px; overflow:hidden}
.crow .cbar{height:100%; background:var(--accent); border-radius:5px}
.crow .ccount{font-size:12px; color:var(--muted)}

.tablewrap{overflow-x:auto; background:var(--panel); border:1px solid var(--border); border-radius:16px}
table{border-collapse:collapse; width:100%; min-width:900px}
th,td{text-align:left; padding:12px 14px; border-bottom:1px solid var(--border); vertical-align:middle}
thead th{position:sticky; top:0; background:var(--panel); font-size:11px; text-transform:uppercase;
  letter-spacing:.06em; color:var(--muted); font-weight:600; cursor:pointer; user-select:none; white-space:nowrap}
thead th.right{text-align:right}
thead th[aria-sort="ascending"]::after{content:" ▲"; color:var(--accent)}
thead th[aria-sort="descending"]::after{content:" ▼"; color:var(--accent)}
tbody tr:hover{background:var(--accent-soft)}
tbody tr:last-child td{border-bottom:none}
td.right{text-align:right}
.rank{color:var(--faint); font-size:13px}
.app{font-weight:600; min-width:180px}
.app a{color:var(--ink); text-decoration:none}
.app a:hover{color:var(--accent); text-decoration:underline}
.dev{color:var(--muted); font-size:12px; font-weight:400}
.chip{display:inline-block; font-size:11px; padding:2px 8px; border-radius:20px; background:var(--panel-2); color:var(--muted); border:1px solid var(--border); white-space:nowrap}

.scorecell{min-width:150px}
.scorehead{display:flex; align-items:baseline; gap:8px}
.scoreval{font-size:22px; font-weight:700; letter-spacing:-.02em}
.sc-top .scoreval{color:var(--good)} .sc-good .scoreval{color:var(--accent)}
.sc-mid .scoreval{color:var(--warn)} .sc-low .scoreval{color:var(--bad)}
.scoremax{font-size:12px; color:var(--faint)}
.subbars{display:grid; grid-template-columns:repeat(3,1fr); gap:6px 8px; margin-top:8px; max-width:210px}
.sb{display:flex; flex-direction:column; gap:3px}
.sb .sbl{font-size:9px; color:var(--faint); letter-spacing:.02em}
.sb .sbt{height:6px; border-radius:3px; background:var(--border); overflow:hidden}
.sb .sbf{height:100%; background:var(--accent); border-radius:3px; min-width:2px}

.flags{display:flex; flex-wrap:wrap; gap:5px; max-width:260px}
.flag{font-size:11px; padding:2px 8px; border-radius:6px; white-space:nowrap}
.flag.pos{background:var(--good-bg); color:var(--good)}
.flag.neu{background:var(--panel-2); color:var(--muted); border:1px solid var(--border)}
.flag.neg{background:var(--warn-bg); color:var(--warn)}

.pill{display:inline-block; font-size:12px; padding:2px 9px; border-radius:20px; font-weight:600}
.age-fresh{color:var(--good); background:var(--good-bg)}
.age-recent{color:var(--accent); background:var(--accent-soft)}
.age-mature{color:var(--muted); background:var(--panel-2)}
footer{color:var(--faint); font-size:12px; margin-top:26px; line-height:1.7}
footer b{color:var(--muted)}
@media (max-width:720px){.kpis{grid-template-columns:repeat(2,1fr)} .crow{grid-template-columns:110px 1fr 34px}}
"""

_JS = """
(function(){
  var table=document.getElementById('nichetable'); if(!table) return;
  var ths=table.querySelectorAll('thead th');
  ths.forEach(function(th,idx){
    if(th.dataset.nosort!==undefined) return;
    th.addEventListener('click',function(){
      var asc=th.getAttribute('aria-sort')!=='ascending';
      ths.forEach(function(o){o.removeAttribute('aria-sort')});
      th.setAttribute('aria-sort',asc?'ascending':'descending');
      var rows=Array.prototype.slice.call(table.querySelectorAll('tbody tr'));
      rows.sort(function(a,b){
        var x=a.children[idx].dataset.v, y=b.children[idx].dataset.v;
        var nx=parseFloat(x), ny=parseFloat(y);
        if(!isNaN(nx)&&!isNaN(ny)) return asc?nx-ny:ny-nx;
        return asc?(''+x).localeCompare(y):(''+y).localeCompare(x);
      });
      var tb=table.querySelector('tbody'); rows.forEach(function(r){tb.appendChild(r)});
    });
  });
})();
"""


def _flag_class(flag):
    if flag.startswith("⚠"):
        return "neg"
    if flag in ("Indie", "De pago", "Gratis + suscripción", "Categoría simple"):
        return "pos"
    return "neu"


def _subbar(label, value):
    v = max(0, min(100, value or 0))
    return (f'<div class="sb"><span class="sbl">{label}</span>'
            f'<span class="sbt"><span class="sbf" style="width:{v}%"></span></span></div>')


class AppStoreReport:

    @staticmethod
    def generate(out="report.html"):
        niches = AppstoreNicheModel.all()
        if not niches:
            print("No hay nichos que mostrar. Ejecuta primero 'ios-evaluate'.")
            return 0

        good = [n for n in niches if (n.clone_score or 0) >= CloneProfile.GOOD_SCORE]
        top = niches[0]

        # clusters: nº de OBJETIVOS recomendados por categoría
        cats = {}
        for n in good:
            cats[n.genre or "?"] = cats.get(n.genre or "?", 0) + 1
        cats = sorted(cats.items(), key=lambda kv: kv[1], reverse=True)
        cmax = cats[0][1] if cats else 1
        cluster_rows = "".join(
            f'<div class="crow"><div class="cname">{html.escape(name)}</div>'
            f'<div class="ctrack"><div class="cbar" style="width:{max(6, round(c / cmax * 100))}%"></div></div>'
            f'<div class="ccount num">{c}</div></div>'
            for name, c in cats
        ) or '<div class="ccount">Sin objetivos por encima del umbral.</div>'

        rows = []
        for i, n in enumerate(niches, 1):
            age_cls, age_txt = _age_class(n.age_days)
            sc = n.clone_score or 0
            flags_html = "".join(
                f'<span class="flag {_flag_class(f)}">{html.escape(f)}</span>'
                for f in (n.flags or "").split(" · ") if f
            )
            subbars = (
                '<div class="subbars">'
                + _subbar("DEM", n.s_demand) + _subbar("MON", n.s_monetization)
                + _subbar("APEL", n.s_appeal) + _subbar("BUILD", n.s_buildability)
                + _subbar("DISE", n.s_design) + _subbar("COMP", n.s_competibility)
                + '</div>'
            )
            rows.append(
                f'<tr>'
                f'<td class="rank num" data-v="{i}">{i}</td>'
                f'<td class="app" data-v="{html.escape((n.title or "").lower())}">'
                f'<a href="{html.escape(n.url or "#")}" target="_blank" rel="noopener">{html.escape(n.title or "")}</a>'
                f'<div class="dev">{html.escape(n.developer or "")}</div></td>'
                f'<td data-v="{html.escape(n.genre or "")}"><span class="chip">{html.escape(n.genre or "")}</span></td>'
                f'<td class="scorecell {_score_class(sc)}" data-v="{sc}">'
                f'<div class="scorehead"><span class="scoreval num">{sc}</span><span class="scoremax">/100</span></div>'
                f'{subbars}</td>'
                f'<td data-nosort><div class="flags">{flags_html}</div></td>'
                f'<td class="right num" data-v="{n.rating_count or 0}">{_fmt(n.rating_count)}</td>'
                f'<td class="right" data-v="{n.age_days if n.age_days is not None else 99999}">'
                f'<span class="pill {age_cls}">{age_txt}</span></td>'
                f'</tr>'
            )
        table_rows = "".join(rows)

        now = datetime.now().strftime("%d/%m/%Y %H:%M")
        best_cats = ", ".join(g for g, _ in cats[:3]) or "—"
        kpis = (
            f'<div class="kpi"><div class="label">Objetivos recomendados</div>'
            f'<div class="val num" style="color:var(--good)">{len(good)}</div>'
            f'<div class="sub">clone score &ge; {CloneProfile.GOOD_SCORE} de {len(niches)} nichos</div></div>'
            f'<div class="kpi"><div class="label">Mejor objetivo</div>'
            f'<div class="val num">{top.clone_score or 0}<span style="font-size:14px;color:var(--faint)">/100</span></div>'
            f'<div class="sub">{html.escape((top.title or "")[:24])}</div></div>'
            f'<div class="kpi"><div class="label">Dónde están</div>'
            f'<div class="val" style="font-size:17px; line-height:1.3">{html.escape(best_cats)}</div>'
            f'<div class="sub">categorías con más objetivos</div></div>'
            f'<div class="kpi"><div class="label">Nichos analizados</div>'
            f'<div class="val num">{len(niches)}</div><div class="sub">recientes y con tracción</div></div>'
        )

        doc = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>App Store Clone Radar</title>
<style>{_CSS}</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <div>
      <p class="eyebrow">App Store · Clone Radar</p>
      <h1>Apps para clonar y monetizar</h1>
      <p class="lede">Rankeadas por <b>clone score</b>: apps con demanda, que se pagan
      (sin anuncios), gustan a la gente, sencillas de construir <b>sin diseño complejo</b>
      y con hueco para competir en solitario.</p>
    </div>
    <div class="meta">
      Storefront <b>{AppStoreConfig.COUNTRY.upper()}</b> · <b>{now}</b><br>
      Criterio base: &ge; <b>{_fmt(AppStoreConfig.MIN_RATINGS)}</b> valoraciones ·
      &le; <b>{AppStoreConfig.MAX_AGE_DAYS}</b> días
    </div>
  </header>

  <div class="kpis">{kpis}</div>

  <div class="panel">
    <h2>Dónde están los objetivos recomendados</h2>
    <div class="clusters">{cluster_rows}</div>
  </div>

  <div class="tablewrap">
    <table id="nichetable">
      <thead><tr>
        <th class="right">#</th>
        <th>App</th>
        <th>Categoría</th>
        <th>Clone score</th>
        <th data-nosort>Señales</th>
        <th class="right">Valoraciones</th>
        <th class="right">Edad</th>
      </tr></thead>
      <tbody>{table_rows}</tbody>
    </table>
  </div>

  <footer>
    <b>Clone score = oportunidad × viabilidad.</b>
    Oportunidad = 0,45·<b>DEM</b> (demanda: val./día) + 0,35·<b>MON</b> (monetización: pago/suscripción)
    + 0,20·<b>APEL</b> (aprecio: valoración media).
    Viabilidad = <b>BUILD</b> (construible: categoría simple, app ligera, sin contenido propio)
    × <b>DISE</b> (diseño simple: UI estándar, sin arte/temas/wallpapers)
    × <b>COMP</b> (competible: indie, no gigante, no saturado).<br>
    Ajusta pesos y listas en <b>config/clone_profile.py</b>. Clic en las cabeceras para reordenar.
    Datos vía APIs públicas de Apple (iTunes + RSS). Herramienta personal — niche_searcher.
  </footer>
</div>
<script>{_JS}</script>
</body>
</html>"""

        with open(out, "w", encoding="utf-8") as f:
            f.write(doc)
        print(f"Dashboard generado: {out}  ({len(niches)} nichos, {len(good)} objetivos recomendados)")
        return len(niches)
