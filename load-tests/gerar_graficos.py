"""
gerar_graficos.py — Lê os CSVs de load-tests/results/ e gera um
relatório HTML com gráficos interativos (Chart.js via CDN).

Uso: python load-tests/gerar_graficos.py
Saída: load-tests/results/relatorio.html
"""

import csv
import os

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
OUTPUT = os.path.join(RESULTS_DIR, "relatorio.html")

TECHS   = ["rest", "graphql", "grpc", "soap"]
PERFIS  = ["leve", "medio", "pesado"]
LABELS  = {"rest": "REST (FastAPI/Py)", "graphql": "GraphQL (Strawberry/Py)",
           "grpc": "gRPC (grpclib/Py)", "soap": "SOAP (http.server/Py)"}
COLORS  = {"rest": "#4A90E2", "graphql": "#E2844A", "grpc": "#50C878", "soap": "#C850C8"}

# ── leitura dos CSVs ────────────────────────────────────────────────────────

def read_aggregated(tech: str, perfil: str) -> dict | None:
    path = os.path.join(RESULTS_DIR, f"{tech}_{perfil}_stats.csv")
    if not os.path.exists(path):
        return None
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name = row.get("Name", "").strip()
            if name == "Aggregated":
                rc   = int(row["Request Count"])
                fc   = int(row["Failure Count"])
                rps  = float(row["Requests/s"])
                p50  = int(row["50%"]  or 0)
                p95  = int(row["95%"]  or 0)
                p99  = int(row["99%"]  or 0)
                fail_pct = round(fc / rc * 100, 2) if rc else 0
                return {"reqs": rc, "fails": fc, "fail_pct": fail_pct,
                        "rps": round(rps, 1), "p50": p50, "p95": p95, "p99": p99}
    return None


data = {}
for t in TECHS:
    data[t] = {}
    for p in PERFIS:
        data[t][p] = read_aggregated(t, p)


# ── helpers JS ──────────────────────────────────────────────────────────────

def js_array(values):
    return "[" + ", ".join(str(v) for v in values) + "]"


def dataset(tech, values, extra=""):
    return (f"{{label: '{LABELS[tech]}', data: {js_array(values)}, "
            f"backgroundColor: '{COLORS[tech]}', borderColor: '{COLORS[tech]}', "
            f"borderWidth: 2, fill: false {extra}}}")


# ── dados por gráfico ────────────────────────────────────────────────────────

perfil_labels = ["LEVE (10u)", "MÉDIO (50u)", "PESADO (150u)"]

def series(metric):
    return {t: [data[t][p][metric] if data[t][p] else 0 for p in PERFIS]
            for t in TECHS}

p50_series   = series("p50")
p95_series   = series("p95")
rps_series   = series("rps")
fail_series  = series("fail_pct")
reqs_series  = series("reqs")

# ── tabela resumo ────────────────────────────────────────────────────────────

def table_rows():
    rows = []
    for p in PERFIS:
        label = {"leve": "LEVE (10u/60s)", "medio": "MÉDIO (50u/60s)",
                 "pesado": "PESADO (150u/60s)"}[p]
        for t in TECHS:
            d = data[t][p]
            if not d:
                continue
            rows.append(
                f"<tr><td>{label}</td><td>{LABELS[t]}</td>"
                f"<td>{d['reqs']:,}</td><td>{d['p50']}ms</td>"
                f"<td>{d['p95']}ms</td><td>{d['rps']}</td>"
                f"<td class='{'fail-high' if d['fail_pct']>5 else 'fail-low'}'>"
                f"{d['fail_pct']:.1f}%</td></tr>"
            )
    return "\n".join(rows)


# ── HTML ─────────────────────────────────────────────────────────────────────

def chart_block(canvas_id: str, title: str, datasets_js: str,
                y_label: str, chart_type: str = "bar") -> str:
    labels_js = str(perfil_labels).replace("'", '"')
    return f"""
<div class="chart-wrap">
  <h3>{title}</h3>
  <canvas id="{canvas_id}"></canvas>
</div>
<script>
new Chart(document.getElementById('{canvas_id}'), {{
  type: '{chart_type}',
  data: {{
    labels: {labels_js},
    datasets: [{datasets_js}]
  }},
  options: {{
    responsive: true,
    plugins: {{
      legend: {{ position: 'top' }},
      tooltip: {{ mode: 'index', intersect: false }}
    }},
    scales: {{
      y: {{
        beginAtZero: true,
        title: {{ display: true, text: '{y_label}' }}
      }}
    }}
  }}
}});
</script>
"""


html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Relatório de Testes de Carga — Trabalho 06</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f9; color: #333; padding: 24px; }}
  h1 {{ font-size: 1.7rem; margin-bottom: 4px; }}
  h2 {{ font-size: 1.2rem; margin: 32px 0 12px; border-left: 4px solid #4A90E2; padding-left: 10px; }}
  h3 {{ font-size: 1rem; margin-bottom: 8px; color: #555; }}
  .subtitle {{ color: #666; margin-bottom: 28px; font-size: 0.9rem; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }}
  .chart-wrap {{ background: #fff; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px #0001; }}
  canvas {{ max-height: 300px; }}
  table {{ width: 100%; border-collapse: collapse; background: #fff;
           border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px #0001; margin-top: 8px; }}
  th {{ background: #4A90E2; color: #fff; padding: 10px 14px; text-align: left; font-size: .85rem; }}
  td {{ padding: 9px 14px; border-bottom: 1px solid #eee; font-size: .85rem; }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover td {{ background: #f0f7ff; }}
  .fail-high {{ color: #c0392b; font-weight: bold; }}
  .fail-low  {{ color: #27ae60; }}
  .note {{ font-size: .8rem; color: #888; margin-top: 10px; }}
  @media(max-width:700px) {{ .grid {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<h1>Testes de Carga — Trabalho 06</h1>
<p class="subtitle">Servidor: Python L1 | 500 usuários · 500 músicas · 300 playlists no DB | 60 s por perfil</p>

<h2>Latência p50 por perfil (ms)</h2>
<div class="grid">
{chart_block("c_p50", "Mediana (p50) — ms", ", ".join(dataset(t, p50_series[t]) for t in TECHS), "ms")}
{chart_block("c_p95", "Percentil 95 (p95) — ms", ", ".join(dataset(t, p95_series[t]) for t in TECHS), "ms")}
</div>

<h2>Throughput e falhas por perfil</h2>
<div class="grid">
{chart_block("c_rps", "Requisições por segundo (req/s)", ", ".join(dataset(t, rps_series[t]) for t in TECHS), "req/s")}
{chart_block("c_fail", "Taxa de falhas (%)", ", ".join(dataset(t, fail_series[t]) for t in TECHS), "%")}
</div>

<h2>Total de requisições por perfil</h2>
<div class="grid">
{chart_block("c_reqs", "Total de requisições", ", ".join(dataset(t, reqs_series[t]) for t in TECHS), "reqs")}
<div class="chart-wrap">
  <h3>Notas técnicas</h3>
  <ul style="margin-top:10px;line-height:1.8;font-size:.88rem;padding-left:18px">
    <li><b>REST (FastAPI)</b>: melhor throughput e menor latência em todos os perfis.</li>
    <li><b>gRPC (grpclib)</b>: latência cresce com carga; medido com benchmark asyncio
        puro (<code>bench_grpc.py</code>) — grpclib incompatível com gevent do Locust.</li>
    <li><b>GraphQL (Strawberry)</b>: overhead de parsing da query aumenta latência base.</li>
    <li><b>SOAP (http.server stdlib)</b>: servidor single-thread; p50 ≥ 2 s em todos os
        perfis. PESADO gerou 37% de falhas por timeout de fila.</li>
    <li>Falhas em REST/gRPC são 404s esperados de IDs aleatórios fora do range.</li>
  </ul>
</div>
</div>

<h2>Tabela completa</h2>
<table>
<thead><tr>
  <th>Perfil</th><th>Tecnologia</th><th>Total reqs</th>
  <th>p50</th><th>p95</th><th>req/s</th><th>Falhas</th>
</tr></thead>
<tbody>
{table_rows()}
</tbody>
</table>
<p class="note">Gerado por gerar_graficos.py em {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
</body>
</html>
"""

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Relatório gerado: {OUTPUT}")
