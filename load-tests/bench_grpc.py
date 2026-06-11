"""
bench_grpc.py — Benchmark autônomo para gRPC (asyncio puro, sem Locust/gevent).

grpclib é baseado em asyncio; o Locust usa gevent, que patcha sockets
globalmente e impede asyncio de funcionar em threads secundários.
Este script contorna o problema rodando o benchmark diretamente no asyncio,
sem qualquer monkey-patch, gerando CSVs no formato exato do Locust.

Uso:
  python bench_grpc.py --users 10  --run-time 60 --csv results/grpc_leve
  python bench_grpc.py --users 50  --run-time 60 --csv results/grpc_medio
  python bench_grpc.py --users 150 --run-time 60 --csv results/grpc_pesado
"""

import asyncio
import random
import time
import csv
import os
import sys
import argparse
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../grpc/python"))

from grpclib.client import Channel
from streaming import (
    UsuarioServiceStub,
    MusicaServiceStub,
    PlaylistServiceStub,
)

HOST = "localhost"
PORT = 8004  # default; pode ser sobrescrito via --port

TASKS = [
    ("Q1 ListarUsuarios",     3),
    ("Q2 ListarMusicas",      3),
    ("Q3 PlaylistsDoUsuario", 2),
    ("Q4 MusicasDaPlaylist",  2),
    ("Q5 PlaylistsComMusica", 1),
]
TASK_NAMES   = [t[0] for t in TASKS]
TASK_WEIGHTS = [t[1] for t in TASKS]


async def user_session(user_id: int, stats: dict, run_until: float):
    """Simula um usuário virtual com conexão HTTP/2 persistente."""
    async with Channel(HOST, PORT) as ch:
        u = UsuarioServiceStub(ch)
        m = MusicaServiceStub(ch)
        p = PlaylistServiceStub(ch)

        while time.monotonic() < run_until:
            name = random.choices(TASK_NAMES, weights=TASK_WEIGHTS, k=1)[0]
            start = time.perf_counter()
            exc = None
            try:
                if name == "Q1 ListarUsuarios":
                    await u.listar_usuarios()
                elif name == "Q2 ListarMusicas":
                    await m.listar_musicas()
                elif name == "Q3 PlaylistsDoUsuario":
                    await p.playlists_do_usuario(
                        usuario_id=random.randint(1, 500))
                elif name == "Q4 MusicasDaPlaylist":
                    await p.musicas_da_playlist(
                        playlist_id=random.randint(1, 300))
                elif name == "Q5 PlaylistsComMusica":
                    await p.playlists_com_musica(
                        musica_id=random.randint(1, 500))
            except Exception as e:
                exc = e

            elapsed = (time.perf_counter() - start) * 1000
            stats[name].append((elapsed, exc))

            await asyncio.sleep(random.uniform(0.05, 0.3))


def pct(sorted_vals: list, p: float) -> int:
    if not sorted_vals:
        return 0
    idx = max(0, int(len(sorted_vals) * p / 100) - 1)
    return int(sorted_vals[min(idx, len(sorted_vals) - 1)])


def write_csv(stats: dict, csv_prefix: str, run_time: float):
    os.makedirs(os.path.dirname(csv_prefix) if os.path.dirname(csv_prefix) else ".", exist_ok=True)

    header = [
        "Type", "Name", "Request Count", "Failure Count",
        "Median Response Time", "Average Response Time",
        "Min Response Time", "Max Response Time",
        "Average Content Size", "Requests/s", "Failures/s",
        "50%", "66%", "75%", "80%", "90%", "95%", "98%", "99%",
        "99.9%", "99.99%", "100%",
    ]

    rows = []
    agg_times: list = []
    agg_fails = 0
    agg_total = 0

    for name in sorted(stats.keys()):
        entries = stats[name]
        times   = sorted(e[0] for e in entries)
        fails   = sum(1 for e in entries if e[1] is not None)
        n       = len(times)
        agg_times.extend(times)
        agg_fails += fails
        agg_total += n

        if not times:
            continue

        avg = sum(times) / n
        rows.append([
            "gRPC", name, n, fails,
            pct(times, 50), round(avg, 3),
            round(times[0], 3), round(times[-1], 3), 0,
            round(n / run_time, 4), round(fails / run_time, 4),
            pct(times, 50), pct(times, 66), pct(times, 75),
            pct(times, 80), pct(times, 90), pct(times, 95),
            pct(times, 98), pct(times, 99), pct(times, 99.9),
            pct(times, 99.99), int(times[-1]),
        ])
        rows.append([])   # linha em branco entre entradas (padrão Locust)

    agg_sorted = sorted(agg_times)
    agg_avg = sum(agg_sorted) / len(agg_sorted) if agg_sorted else 0
    rows.append([
        "", "Aggregated", agg_total, agg_fails,
        pct(agg_sorted, 50), round(agg_avg, 3),
        round(agg_sorted[0], 3) if agg_sorted else 0,
        round(agg_sorted[-1], 3) if agg_sorted else 0, 0,
        round(agg_total / run_time, 4), round(agg_fails / run_time, 4),
        pct(agg_sorted, 50), pct(agg_sorted, 66), pct(agg_sorted, 75),
        pct(agg_sorted, 80), pct(agg_sorted, 90), pct(agg_sorted, 95),
        pct(agg_sorted, 98), pct(agg_sorted, 99), pct(agg_sorted, 99.9),
        pct(agg_sorted, 99.99), int(agg_sorted[-1]) if agg_sorted else 0,
    ])

    stats_path = csv_prefix + "_stats.csv"
    with open(stats_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)

    # CSVs auxiliares vazios (para manter paridade com Locust)
    for suffix, hdr in (
        ("_failures.csv",   ["Method", "Name", "Error", "Occurrences",
                             "First Seen", "Last Seen"]),
        ("_exceptions.csv", ["Count", "Message", "Traceback", "Nodes"]),
    ):
        with open(csv_prefix + suffix, "w", newline="") as f:
            csv.writer(f).writerow(hdr)

    print(f"[bench_grpc] {stats_path}")
    print(
        f"[bench_grpc] Total={agg_total} reqs  Falhas={agg_fails}  "
        f"avg={int(agg_avg)}ms  p50={pct(agg_sorted, 50)}ms  "
        f"p95={pct(agg_sorted, 95)}ms  req/s={round(agg_total/run_time, 2)}"
    )


async def main(num_users: int, run_time: int, csv_prefix: str, port: int = 8004):
    global PORT
    PORT = port
    print(f"[bench_grpc] {num_users} usuários × {run_time}s → {csv_prefix} (porta {PORT})")
    stats: dict = defaultdict(list)
    run_until = time.monotonic() + run_time

    tasks = [
        asyncio.create_task(user_session(i, stats, run_until))
        for i in range(num_users)
    ]
    await asyncio.gather(*tasks, return_exceptions=True)
    write_csv(stats, csv_prefix, float(run_time))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark gRPC (asyncio)")
    parser.add_argument("--users",    type=int, default=10,
                        help="Número de usuários simultâneos")
    parser.add_argument("--run-time", type=int, default=60,
                        help="Duração em segundos")
    parser.add_argument("--csv",      type=str, default="results/grpc_bench",
                        help="Prefixo do arquivo CSV de saída")
    parser.add_argument("--port",     type=int, default=8004,
                        help="Porta do servidor gRPC")
    args = parser.parse_args()

    asyncio.run(main(args.users, args.run_time, args.csv, args.port))
