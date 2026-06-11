"""
gerar_graficos.py -- Reads result CSVs and generates an HTML report.

Usage:
    python load-tests/gerar_graficos.py
    python load-tests/gerar_graficos.py load-tests/results/temp
Output: <folder>/relatorio.html

Two-tab mode activates when _py/_ts CSVs are found:
  Tab 1 Detalhado  -- one series per implementation (up to 8)
  Tab 2 Agregado   -- one series per technology (avg Py + TS)
"""

import csv, os, sys, glob, datetime

if len(sys.argv) > 1:
    RESULTS_DIR = os.path.abspath(sys.argv[1])
else:
    RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")

OUTPUT = os.path.join(RESULTS_DIR, "relatorio.html")
PERFIS_BASE = ["leve", "medio", "pesado"]

KNOWN_IMPLS = [
    "rest_py", "rest_ts", "graphql_py", "graphql_ts",
    "grpc_py", "grpc_ts", "soap_py", "soap_ts",
    "rest", "graphql", "grpc", "soap",
]

IMPL_LABELS = {
    "rest_py": "REST Python", "rest_ts": "REST TypeScript",
    "graphql_py": "GraphQL Python", "graphql_ts": "GraphQL TypeScript",
    "grpc_py": "gRPC Python", "grpc_ts": "gRPC TypeScript",
    "soap_py": "SOAP Python", "soap_ts": "SOAP TypeScript",
    "rest": "REST", "graphql": "GraphQL", "grpc": "gRPC", "soap": "SOAP",
}

IMPL_COLORS = {
    "rest_py": "#1a65c0", "rest_ts": "#7eb5f5",
    "graphql_py": "#b84a00", "graphql_ts": "#f0a070",
    "grpc_py": "#1a8a3e", "grpc_ts": "#6ed498",
    "soap_py": "#8a1a8e", "soap_ts": "#d47dd8",
    "rest": "#4A90E2", "graphql": "#E2844A", "grpc": "#50C878", "soap": "#C850C8",
}

AGG_LABELS = {"rest": "REST", "graphql": "GraphQL", "grpc": "gRPC", "soap": "SOAP"}
AGG_COLORS = {"rest": "#4A90E2", "graphql": "#E2844A", "grpc": "#50C878", "soap": "#C850C8"}
TECH_IMPLS = {
    "rest": ["rest_py","rest_ts"], "graphql": ["graphql_py","graphql_ts"],
    "grpc": ["grpc_py","grpc_ts"], "soap": ["soap_py","soap_ts"],
}

# -- detect ------------------------------------------------------------------
def detect_impls_and_perfis():
    impls, perfis = set(), set()
    for f in glob.glob(os.path.join(RESULTS_DIR, "*_stats.csv")):
        base = os.path.basename(f).replace("_stats.csv", "")
        for impl in KNOWN_IMPLS:
            if base.startswith(impl + "_"):
                perfis.add(base[len(impl)+1:])
                impls.add(impl)
                break
    ordered = [i for i in KNOWN_IMPLS if i in impls]
    fixed   = [p for p in PERFIS_BASE if p in perfis]
    return ordered, fixed + sorted(perfis - set(PERFIS_BASE))

IMPLS, PERFIS_DISP = detect_impls_and_perfis()
HAS_SPLIT = any("_py" in i or "_ts" in i for i in IMPLS)

# -- csv helpers -------------------------------------------------------------
def csv_size_kb(impl, perfil):
    path = os.path.join(RESULTS_DIR, f"{impl}_{perfil}_stats.csv")
    if not os.path.exists(path): return 0.0
    return round(os.path.getsize(path) / 1024, 1)

def read_aggregated(impl, perfil):
    path = os.path.join(RESULTS_DIR, f"{impl}_{perfil}_stats.csv")
    if not os.path.exists(path): return None
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("Name","").strip() == "Aggregated":
                def _i(v):
                    try: return int(float(v or 0))
                    except (ValueError, TypeError): return 0
                def _f(v):
                    try: return float(v or 0)
                    except (ValueError, TypeError): return 0.0
                rc = _i(row["Request Count"]); fc = _i(row["Failure Count"])
                return {
                    "reqs": rc, "fails": fc,
                    "fail_pct": round(fc/rc*100,2) if rc else 0.0,
                    "rps": round(_f(row["Requests/s"]),1),
                    "p50": _i(row["50%"]), "p95": _i(row["95%"]),
                    "avg_content_kb": round(_f(row.get("Average Content Size",0))/1024,1),
                    "csv_kb": csv_size_kb(impl, perfil),
                }
    return None

data = {i: {p: read_aggregated(i,p) for p in PERFIS_DISP} for i in IMPLS}

agg_data = {}
for _t, _sub in TECH_IMPLS.items():
    agg_data[_t] = {}
    for _p in PERFIS_DISP:
        vals = [v for v in (data.get(i,{}).get(_p) for i in _sub) if v]
        if not vals: agg_data[_t][_p] = None; continue
        def _avg(m, vl=vals): return round(sum(v[m] for v in vl)/len(vl), 2)
        agg_data[_t][_p] = {m: _avg(m) for m in vals[0]}

# -- js helpers --------------------------------------------------------------
def js_arr(values): return "[" + ", ".join(str(v) for v in values) + "]"

def mk_ds(label, color, values):
    return (f"{{label: '{label}', data: {js_arr(values)}, "
            f"backgroundColor: '{color}', borderColor: '{color}', "
            f"borderWidth: 2, fill: false }}")

def series(src, metric):
    return {k: [(src[k][p][metric] if src.get(k,{}).get(p) else 0) for p in PERFIS_DISP]
            for k in src}

perfil_labels = [p.upper() for p in PERFIS_DISP]
si = {m: series(data, m) for m in ("p50","p95","rps","fail_pct","reqs","avg_content_kb","csv_kb")}
sa = {m: series(agg_data,m) for m in ("p50","p95","rps","fail_pct","reqs","avg_content_kb")}

def impl_ds(s): return ", ".join(mk_ds(IMPL_LABELS.get(i,i), IMPL_COLORS.get(i,"#888"), s[i]) for i in IMPLS)
def agg_ds(s):  return ", ".join(mk_ds(AGG_LABELS[t], AGG_COLORS[t], s[t]) for t in TECH_IMPLS)

# -- chart block -------------------------------------------------------------
def chart_block(cid, title, ds_js, y_label):
    ljs = str(perfil_labels).replace("'", '"')
    return (
        f'<div class="chart-wrap"><h3>{title}</h3><canvas id="{cid}"></canvas></div>\n'
        f'<script>\nnew Chart(document.getElementById("{cid}"), {{\n'
        f'  type: "bar",\n'
        f'  data: {{ labels: {ljs}, datasets: [{ds_js}] }},\n'
        f'  options: {{\n'
        f'    responsive: true,\n'
        f'    plugins: {{ legend: {{ position: "top" }}, tooltip: {{ mode: "index", intersect: false }} }},\n'
        f'    scales: {{ y: {{ beginAtZero: true, title: {{ display: true, text: "{y_label}" }} }} }}\n'
        f'  }}\n}});\n</script>'
    )

# -- table rows --------------------------------------------------------------
def table_rows(impl_list, src):
    rows = []
    for p in PERFIS_DISP:
        for impl in impl_list:
            d = src.get(impl,{}).get(p)
            if not d: continue
            lbl = IMPL_LABELS.get(impl, impl)
            css = "fail-high" if d["fail_pct"] > 5 else "fail-low"
            note = ' <small style="color:#999">(bin)</small>' if impl in ("grpc_py","grpc_ts","grpc") else ""
            rows.append(
                f'<tr><td>{p.upper()}</td><td>{lbl}</td>'
                f'<td>{int(d["reqs"]):,}</td>'
                f'<td>{int(d["p50"])} ms</td><td>{int(d["p95"])} ms</td>'
                f'<td>{d["rps"]}</td>'
                f'<td class="{css}">{d["fail_pct"]:.1f}%</td>'
                f'<td>{d["avg_content_kb"]} KB{note}</td>'
                f'<td>{d["csv_kb"]} KB</td></tr>'
            )
    return "\n".join(rows)

# -- html assembly -----------------------------------------------------------
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

CSS = """
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f9; color: #333; padding: 24px; }
  h1 { font-size: 1.7rem; margin-bottom: 4px; }
  h2 { font-size: 1.2rem; margin: 32px 0 12px; border-left: 4px solid #4A90E2; padding-left: 10px; }
  h3 { font-size: 1rem; margin-bottom: 8px; color: #555; }
  .subtitle { color: #666; margin-bottom: 16px; font-size: 0.9rem; }
  .tabs { display: flex; gap: 8px; margin-bottom: 24px; flex-wrap: wrap; }
  .tab-btn { padding: 9px 22px; border: 2px solid #4A90E2; border-radius: 6px;
             background: #fff; color: #4A90E2; font-size: .9rem; cursor: pointer; transition: .15s; }
  .tab-btn.active { background: #4A90E2; color: #fff; }
  .tab-content { display: none; }
  .tab-content.active { display: block; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
  .chart-wrap { background: #fff; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px #0001; }
  canvas { max-height: 300px; }
  table { width: 100%; border-collapse: collapse; background: #fff;
          border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px #0001; margin-top: 8px; }
  th { background: #4A90E2; color: #fff; padding: 10px 14px; text-align: left; font-size: .85rem; }
  td { padding: 9px 14px; border-bottom: 1px solid #eee; font-size: .85rem; }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: #f0f7ff; }
  .fail-high { color: #c0392b; font-weight: bold; }
  .fail-low  { color: #27ae60; }
  .note { font-size: .8rem; color: #888; margin-top: 10px; }
  @media(max-width:700px) { .grid { grid-template-columns: 1fr; } }
"""

JS = """
function showTab(id) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
  document.getElementById('tab-' + id).classList.add('active');
  document.getElementById('btn-' + id).classList.add('active');
  setTimeout(() => {
    document.querySelectorAll('#tab-' + id + ' canvas').forEach(canvas => {
      const chart = Chart.getChart(canvas);
      if (chart) chart.resize();
    });
  }, 60);
}
"""

tabs_html = (
    '<div class="tabs">'
    '<button class="tab-btn active" id="btn-ind" onclick="showTab(\'ind\')">'
    'Detalhado (8 implementa&ccedil;&otilde;es)</button> '
    '<button class="tab-btn" id="btn-agg" onclick="showTab(\'agg\')">'
    'Agregado por tecnologia</button></div>'
) if HAS_SPLIT else ""

notes_block = """
<div class="chart-wrap">
  <h3>Notas t&eacute;cnicas</h3>
  <ul style="margin-top:10px;line-height:1.9;font-size:.88rem;padding-left:18px">
    <li><b>REST</b>: FastAPI (Python) / Fastify (TypeScript)</li>
    <li><b>GraphQL</b>: Strawberry+FastAPI (Py) / Apollo Server 4 (TS)</li>
    <li><b>gRPC</b>: grpclib (Py) / @grpc/grpc-js (TS) &mdash; medido com bench_grpc.py.
        Resposta 0 KB = protocolo bin&aacute;rio sem Content-Length HTTP.</li>
    <li><b>SOAP</b>: http.server stdlib (Py) / soap library (TS)</li>
    <li>Falhas REST/gRPC = 404s de IDs aleat&oacute;rios (esperado).</li>
    <li>GraphQL/SOAP usam POST para todas as opera&ccedil;&otilde;es.</li>
  </ul>
</div>
"""

ind_content = (
    '<h2>Lat&ecirc;ncia p50 por perfil (ms)</h2><div class="grid">'
    + chart_block("c_p50","Mediana (p50) &mdash; ms",impl_ds(si["p50"]),"ms")
    + chart_block("c_p95","Percentil 95 (p95) &mdash; ms",impl_ds(si["p95"]),"ms")
    + '</div><h2>Throughput e falhas</h2><div class="grid">'
    + chart_block("c_rps","Requisi&ccedil;&otilde;es/s",impl_ds(si["rps"]),"req/s")
    + chart_block("c_fail","Taxa de falhas (%)",impl_ds(si["fail_pct"]),"%")
    + '</div><h2>Tamanho dos dados</h2><div class="grid">'
    + chart_block("c_cont","Tamanho m&eacute;dio da resposta (KB/req)",impl_ds(si["avg_content_kb"]),"KB")
    + chart_block("c_csv","Tamanho do CSV de resultados (KB)",impl_ds(si["csv_kb"]),"KB")
    + '</div><h2>Total de requisi&ccedil;&otilde;es</h2><div class="grid">'
    + chart_block("c_reqs","Total de requisi&ccedil;&otilde;es",impl_ds(si["reqs"]),"reqs")
    + notes_block
    + '</div><h2>Tabela completa</h2>'
    + '<table><thead><tr><th>Perfil</th><th>Implementa&ccedil;&atilde;o</th>'
    + '<th>Total reqs</th><th>p50</th><th>p95</th><th>req/s</th>'
    + '<th>Falhas</th><th>Resp. m&eacute;dia</th><th>CSV</th></tr></thead><tbody>'
    + table_rows(IMPLS, data) + '</tbody></table>'
)

agg_content = ""
if HAS_SPLIT:
    agg_content = (
        '<h2>Lat&ecirc;ncia p50 &mdash; m&eacute;dia Python+TypeScript (ms)</h2><div class="grid">'
        + chart_block("a_p50","Mediana (p50) &mdash; ms",agg_ds(sa["p50"]),"ms")
        + chart_block("a_p95","Percentil 95 (p95) &mdash; ms",agg_ds(sa["p95"]),"ms")
        + '</div><h2>Throughput e falhas &mdash; m&eacute;dia Python+TypeScript</h2><div class="grid">'
        + chart_block("a_rps","Requisi&ccedil;&otilde;es/s",agg_ds(sa["rps"]),"req/s")
        + chart_block("a_fail","Taxa de falhas (%)",agg_ds(sa["fail_pct"]),"%")
        + '</div><h2>Total de requisi&ccedil;&otilde;es &mdash; m&eacute;dia Python+TypeScript</h2><div class="grid">'
        + chart_block("a_reqs","Total de requisi&ccedil;&otilde;es",agg_ds(sa["reqs"]),"reqs")
        + chart_block("a_cont","Resp. m&eacute;dia (KB/req)",agg_ds(sa["avg_content_kb"]),"KB")
        + '</div><h2>Tabela agregada (m&eacute;dia Python + TypeScript)</h2>'
        + '<table><thead><tr><th>Perfil</th><th>Tecnologia</th>'
        + '<th>Total reqs</th><th>p50</th><th>p95</th><th>req/s</th>'
        + '<th>Falhas</th><th>Resp. m&eacute;dia</th><th>CSV</th></tr></thead><tbody>'
        + table_rows(list(TECH_IMPLS.keys()), agg_data) + '</tbody></table>'
    )

tab2_div = f'<div id="tab-agg" class="tab-content">{agg_content}</div>' if HAS_SPLIT else ""

html = (
    '<!DOCTYPE html>\n<html lang="pt-BR">\n<head>\n'
    '<meta charset="UTF-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    '<title>Relatorio de Testes de Carga &mdash; Trabalho 06</title>\n'
    '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>\n'
    f'<style>{CSS}</style>\n</head>\n<body>\n'
    '<h1>Testes de Carga &mdash; Trabalho 06</h1>\n'
    f'<p class="subtitle">Pasta: {RESULTS_DIR} | Gerado em: {now}</p>\n'
    f'{tabs_html}\n'
    f'<div id="tab-ind" class="tab-content active">{ind_content}</div>\n'
    f'{tab2_div}\n'
    '<p class="note">Gerado por gerar_graficos.py</p>\n'
    f'<script>{JS}</script>\n'
    '</body>\n</html>\n'
)

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Relatorio gerado: {OUTPUT}")
