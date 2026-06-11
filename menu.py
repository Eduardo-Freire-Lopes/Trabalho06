#!/usr/bin/env python3
"""
menu.py — Gerenciador interativo para Trabalho 06
Uso: python menu.py   (na raiz do projeto)
"""

import os
import subprocess
import time

# ── Cores ANSI ────────────────────────────────────────────────────────────────
os.system("")  # habilita VT100 no Windows
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
DIM    = "\033[2m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(text):   return f"{GREEN}{text}{RESET}"
def warn(text): return f"{YELLOW}{text}{RESET}"
def err(text):  return f"{RED}{text}{RESET}"
def dim(text):  return f"{DIM}{text}{RESET}"
def bold(text): return f"{BOLD}{text}{RESET}"

ROOT   = os.path.dirname(os.path.abspath(__file__))
PYTHON = os.path.join(ROOT, ".venv", "Scripts", "python.exe")
LOCUST = os.path.join(ROOT, ".venv", "Scripts", "locust")

# ── Servidores ────────────────────────────────────────────────────────────────
SERVERS = [
    ("REST Python      (porta 8000)", [PYTHON, "-m", "uvicorn", "main:app", "--port", "8000"], os.path.join(ROOT, "rest",     "python")),
    ("REST TypeScript  (porta 8001)", ["npx", "ts-node", "src/server.ts"],                     os.path.join(ROOT, "rest",     "typescript")),
    ("GraphQL Python   (porta 8002)", [PYTHON, "-m", "uvicorn", "main:app", "--port", "8002"], os.path.join(ROOT, "graphql",  "python")),
    ("GraphQL TypeScript (porta 4000)", ["npx", "ts-node", "src/server.ts"],                   os.path.join(ROOT, "graphql",  "typescript")),
    ("gRPC Python      (porta 8004)", [PYTHON, "server.py"],                                   os.path.join(ROOT, "grpc",     "python")),
    ("gRPC TypeScript  (porta 8005)", ["npx", "ts-node", "src/server.ts"],                     os.path.join(ROOT, "grpc",     "typescript")),
    ("SOAP Python      (porta 8006)", [PYTHON, "server.py"],                                   os.path.join(ROOT, "soap",     "python")),
    ("SOAP TypeScript  (porta 8007)", ["npx", "ts-node", "src/server.ts"],                     os.path.join(ROOT, "soap",     "typescript")),
]

# Porta de cada servidor (mesma ordem de SERVERS)
SERVER_PORTS = [8000, 8001, 8002, 4000, 8004, 8005, 8006, 8007]

# ── Testes de carga ──────────────────────────────────────────────────────────
# (tech, script, host_py, port_py, host_ts, port_ts)
LOCUST_TESTS = [
    ("REST",    "locust_rest.py",    "http://localhost:8000", 8000, "http://localhost:8001", 8001),
    ("GraphQL", "locust_graphql.py", "http://localhost:8002", 8002, "http://localhost:4000", 4000),
    ("SOAP",    "locust_soap.py",    "http://localhost:8006", 8006, "http://localhost:8007", 8007),
]

PROFILES = [
    ("LEVE",   "leve",   10,  2,  60),
    ("MEDIO",  "medio",  50,  10, 60),
    ("PESADO", "pesado", 100, 20, 60),
]

# Todas as 8 implementacoes para benchmark completo
# (impl_name, locust_script_or_None, host_or_None, port)
ALL_IMPLS = [
    ("rest_py",    "locust_rest.py",    "http://localhost:8000", 8000),
    ("rest_ts",    "locust_rest.py",    "http://localhost:8001", 8001),
    ("graphql_py", "locust_graphql.py", "http://localhost:8002", 8002),
    ("graphql_ts", "locust_graphql.py", "http://localhost:4000", 4000),
    ("soap_py",    "locust_soap.py",    "http://localhost:8006", 8006),
    ("soap_ts",    "locust_soap.py",    "http://localhost:8007", 8007),
    ("grpc_py",    None,                None,                    8004),
    ("grpc_ts",    None,                None,                    8005),
]

# ── Utilitários ───────────────────────────────────────────────────────────────
def clear():
    os.system("cls" if os.name == "nt" else "clear")

def header():
    print(bold("=" * 55))
    print(bold("    TRABALHO 06 — Gerenciador de Servicos"))
    print(bold("=" * 55))

def db_running() -> bool:
    """Retorna True se o container streaming-pg estiver Up."""
    r = subprocess.run(
        "docker ps --filter name=streaming-pg --filter status=running --format {{.Names}}",
        shell=True, capture_output=True, text=True
    )
    return "streaming-pg" in r.stdout

def pause():
    input("\n  [Enter] para continuar...")

def port_running(port: int) -> bool:
    """Retorna True se há algum processo em LISTEN na porta."""
    r = subprocess.run(
        f'netstat -ano | findstr ":{port} "',
        shell=True, capture_output=True, text=True
    )
    return "LISTENING" in r.stdout

def kill_port(port: int) -> bool:
    """Mata o(s) processo(s) que estão ouvindo na porta. Retorna True se matou ao menos um."""
    r = subprocess.run(
        f'netstat -ano | findstr ":{port} "',
        shell=True, capture_output=True, text=True
    )
    pids = set()
    for line in r.stdout.splitlines():
        if "LISTENING" in line:
            parts = line.strip().split()
            if parts:
                pids.add(parts[-1])
    if not pids:
        return False
    for pid in pids:
        subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
    return True

def launch_server(name, cmd, cwd):
    print(f"  >> Subindo {name}...")
    print(f"     cd \"{cwd}\"")
    print(f"     {' '.join(cmd)}")
    # Roda via cmd /c "comando & pause" para a janela ficar aberta mesmo em erro
    cmd_str = " ".join(f'"{c}"' if " " in c else c for c in cmd)
    wrapped = ["cmd", "/c", f'{cmd_str} & pause']
    subprocess.Popen(wrapped, cwd=cwd, creationflags=subprocess.CREATE_NEW_CONSOLE)
    time.sleep(0.4)

def run_locust(tech, script, host, users, ramp, dur, csv_prefix):
    os.makedirs(os.path.dirname(csv_prefix), exist_ok=True)
    cmd = [
        LOCUST, "-f", os.path.join(ROOT, "load-tests", script),
        "--headless",
        "-u", str(users), "-r", str(ramp),
        f"--run-time={dur}s",
        f"--csv={csv_prefix}",
        f"--host={host}",
    ]
    print(f"\n  Rodando {tech} | {users} usuarios | {dur}s")
    print(f"  >> {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=ROOT)

def run_grpc(users, dur, csv_prefix, port=8004):
    os.makedirs(os.path.dirname(csv_prefix), exist_ok=True)
    cmd = [
        PYTHON, os.path.join(ROOT, "load-tests", "bench_grpc.py"),
        "--users", str(users),
        "--run-time", str(dur),
        "--csv", csv_prefix,
        "--port", str(port),
    ]
    print(f"\n  Rodando gRPC | {users} usuarios | {dur}s | porta {port}")
    print(f"  >> {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=ROOT)

def _gerar_graficos_pasta(pasta: str):
    cmd = [PYTHON, os.path.join(ROOT, "load-tests", "gerar_graficos.py"), pasta]
    print(f"\n  Gerando graficos de: {warn(pasta)}")
    print(f"  >> {' '.join(cmd)}\n")
    subprocess.run(cmd, cwd=ROOT)
    relatorio = os.path.join(pasta, "relatorio.html")
    if os.path.exists(relatorio):
        os.startfile(relatorio)
        print(f"  {ok('Relatorio aberto no navegador.')}")

def gerar_graficos():
    _gerar_graficos_pasta(os.path.join(ROOT, "load-tests", "results"))

# ── Submenus ──────────────────────────────────────────────────────────────────
def escolher_perfil():
    print("\n  Perfil de carga:\n")
    for i, (nome, _, users, _, dur) in enumerate(PROFILES, 1):
        print(f"  [{i}] {nome:8s} — {users:3d} usuarios, {dur}s")
    print("\n  [0] Cancelar")
    op = input("\n  > ").strip()
    if op == "0":
        return None
    try:
        return PROFILES[int(op) - 1]
    except (ValueError, IndexError):
        return None

def menu_subir_todos():
    clear(); header()
    print("\n  Subindo todos os servicos em janelas separadas...\n")
    for name, cmd, cwd in SERVERS:
        launch_server(name, cmd, cwd)
    print("\n  Todos os servicos foram iniciados.")
    pause()

def menu_subir_especifico():
    while True:
        clear(); header()
        print("\n  Selecione o servico:\n")
        for i, (name, _, _) in enumerate(SERVERS, 1):
            print(f"  [{i:2d}] {name}")
        print("\n  [ 0] Voltar")
        op = input("\n  > ").strip()
        if op == "0":
            break
        try:
            name, cmd, cwd = SERVERS[int(op) - 1]
            launch_server(name, cmd, cwd)
            print(f"\n  {name} iniciado.")
            pause()
        except (ValueError, IndexError):
            pass

def menu_testes():
    while True:
        clear(); header()
        ativos = [name for (name, _, _), port in zip(SERVERS, SERVER_PORTS) if port_running(port)]
        if ativos:
            print(f"\n  Servicos ativos: {ok(', '.join(a.split('(')[0].strip() for a in ativos))}")
        else:
            print(f"  {warn('Aviso: nenhum servico detectado nas portas esperadas.')}")
            print(f"  {dim('Os testes vao falhar se os servidores nao estiverem rodando.')}")
        print("\n  Testes de Carga:\n")
        print("  [1] Rodar TODOS os testes (escolher perfil)")
        print("  [2] Rodar teste de uma tecnologia especifica")
        print("  [3] Teste personalizado (usuarios e tempo livres)")
        print(f"  [4] {ok('Benchmark completo: LEVE+MEDIO+PESADO x todos os servicos online')}")
        print("\n  [0] Voltar")
        op = input("\n  > ").strip()
        if op == "0":
            break

        elif op == "1":
            perfil = escolher_perfil()
            if not perfil:
                continue
            nome, slug, users, ramp, dur = perfil
            temp = os.path.join(ROOT, "load-tests", "results", "temp")
            os.makedirs(temp, exist_ok=True)
            ran = 0
            pulados = []
            for tech, script, host_py, port_py, host_ts, port_ts in LOCUST_TESTS:
                if port_running(port_py):
                    host, info = host_py, f"Py porta {port_py}"
                elif port_running(port_ts):
                    host, info = host_ts, f"TS porta {port_ts}"
                else:
                    pulados.append(f"{tech} (ambos offline)")
                    continue
                print(f"  {ok(f'{tech}: usando {info}')}")  
                run_locust(tech, script, host, users, ramp, dur, os.path.join(temp, f"{tech.lower()}_{slug}"))
                ran += 1
            grpc_port = 8004 if port_running(8004) else (8005 if port_running(8005) else None)
            if grpc_port:
                impl = "Py" if grpc_port == 8004 else "TS"
                print(f"  {ok(f'gRPC: usando {impl} porta {grpc_port}')}")
                run_grpc(users, dur, os.path.join(temp, f"grpc_{slug}"), grpc_port)
                ran += 1
            else:
                pulados.append("gRPC (ambos offline)")
            print("\n" + "─" * 50)
            if ran > 0:
                print(f"  {ok(f'{ran} teste(s) concluido(s)')}  →  CSVs em: {warn('load-tests/results/temp/')}")
            if pulados:
                print(f"  {err('Pulados (servidor offline):')} {', '.join(pulados)}")
                print(f"  {dim('Suba os servicos no menu principal [2] ou [3] e rode novamente.')}")
            if ran == 0:
                print(err("  Nenhum servico disponivel."))
            pause()

        elif op == "2":
            clear(); header()
            print("\n  Tecnologia:\n")
            techs = [(t, s, hp, pp, ht, pt) for t, s, hp, pp, ht, pt in LOCUST_TESTS] + [("gRPC", None, None, 8004, None, 8005)]
            for i, (name, *_) in enumerate(techs, 1):
                print(f"  [{i}] {name}")
            print("\n  [0] Cancelar")
            t_op = input("\n  > ").strip()
            if t_op == "0":
                continue
            try:
                tech, script, host_py, port_py, host_ts, port_ts = techs[int(t_op) - 1]
                perfil = escolher_perfil()
                if not perfil:
                    continue
                nome, slug, users, ramp, dur = perfil
                temp = os.path.join(ROOT, "load-tests", "results", "temp")
                os.makedirs(temp, exist_ok=True)
                if tech == "gRPC":
                    grpc_port = 8004 if port_running(8004) else (8005 if port_running(8005) else None)
                    if not grpc_port:
                        print(err("\n  gRPC offline em ambas as portas (8004 e 8005)."))
                        pause(); continue
                    run_grpc(users, dur, os.path.join(temp, f"grpc_{slug}"), grpc_port)
                else:
                    if port_running(port_py):
                        host, info = host_py, f"Py porta {port_py}"
                    elif port_running(port_ts):
                        host, info = host_ts, f"TS porta {port_ts}"
                    else:
                        print(err(f"\n  {tech} offline em ambas as portas ({port_py} e {port_ts})."))
                        pause(); continue
                    print(f"  {ok(f'Usando {info}')}")
                    run_locust(tech, script, host, users, ramp, dur, os.path.join(temp, f"{tech.lower()}_{slug}"))
                print(f"\n  Teste {tech} concluido. CSVs em: {warn('load-tests/results/temp/')}")
                pause()
            except (ValueError, IndexError):
                pass

        elif op == "3":
            clear(); header()
            print("\n  Teste Personalizado\n")
            print("  Tecnologia:")
            techs = [(t, s, hp, pp, ht, pt) for t, s, hp, pp, ht, pt in LOCUST_TESTS] + [("gRPC", None, None, 8004, None, 8005)]
            for i, (name, *_) in enumerate(techs, 1):
                print(f"  [{i}] {name}")
            print("  [0] Cancelar")
            t_op = input("\n  > ").strip()
            if t_op == "0":
                continue
            try:
                tech, script, host_py, port_py, host_ts, port_ts = techs[int(t_op) - 1]
            except (ValueError, IndexError):
                continue

            try:
                users = int(input("\n  Numero de usuarios simultaneos: ").strip())
                dur   = int(input("  Duracao em segundos:            ").strip())
            except ValueError:
                print(err("  Valor invalido."))
                pause()
                continue

            ramp = max(1, users // 5)
            slug = f"custom_{users}u_{dur}s"
            temp = os.path.join(ROOT, "load-tests", "results", "temp")
            os.makedirs(temp, exist_ok=True)
            csv_prefix = os.path.join(temp, f"{tech.lower()}_{slug}")

            if tech == "gRPC":
                grpc_port = 8004 if port_running(8004) else (8005 if port_running(8005) else None)
                if not grpc_port:
                    print(err("  gRPC offline em ambas as portas (8004 e 8005)."))
                    pause(); continue
                run_grpc(users, dur, csv_prefix, grpc_port)
            else:
                if port_running(port_py):
                    host, info = host_py, f"Py porta {port_py}"
                elif port_running(port_ts):
                    host, info = host_ts, f"TS porta {port_ts}"
                else:
                    print(err(f"  {tech} offline em ambas as portas ({port_py} e {port_ts})."))
                    pause(); continue
                print(f"  {ok(f'Usando {info}')}")
                run_locust(tech, script, host, users, ramp, dur, csv_prefix)

            print(f"\n  {ok('Teste concluido!')} CSVs salvos em: {warn('load-tests/results/temp/')}")
            gerar = input("\n  Gerar graficos agora? [s/N] ").strip().lower()
            if gerar == "s":
                _gerar_graficos_pasta(temp)
            pause()

        elif op == "4":
            clear(); header()
            online = [(impl, script, host, port)
                      for impl, script, host, port in ALL_IMPLS
                      if port_running(port)]
            if not online:
                print(err("\n  Nenhum servico online. Suba os servidores antes de rodar."))
                pause(); continue
            print(f"\n  Servicos online ({len(online)}):")
            for impl, _, _, port in online:
                print(f"    {ok(impl):30s} porta {port}")
            print(f"\n  Perfis: {bold('LEVE + MEDIO + PESADO')}")
            print(f"  Total de testes: {bold(str(len(online) * len(PROFILES)))}\n")
            confirm = input(warn("  Iniciar benchmark completo? [s/N] ")).strip().lower()
            if confirm != "s":
                continue
            temp = os.path.join(ROOT, "load-tests", "results", "temp")
            os.makedirs(temp, exist_ok=True)
            for nome, slug, users, ramp, dur in PROFILES:
                print(f"\n{'─'*50}\n  Perfil {bold(nome)} | {users} usuarios | {dur}s\n{'─'*50}")
                for impl, script, host, port in online:
                    csv_prefix = os.path.join(temp, f"{impl}_{slug}")
                    if script is None:  # gRPC
                        run_grpc(users, dur, csv_prefix, port)
                    else:
                        run_locust(impl, script, host, users, ramp, dur, csv_prefix)
            print(f"\n{'─'*50}")
            print(ok(f"  Benchmark completo! {len(online) * len(PROFILES)} testes concluidos."))
            print(f"  CSVs em: {warn('load-tests/results/temp/')}")
            gerar = input("\n  Gerar graficos agora? [s/N] ").strip().lower()
            if gerar == "s":
                _gerar_graficos_pasta(temp)
            pause()

def menu_banco():
    while True:
        clear(); header()
        db = db_running()
        status = ok("ONLINE") if db else err("OFFLINE")
        print(f"\n  Banco de Dados (PostgreSQL + Docker) — {status}\n")
        print(f"  [1] {ok('Subir container') if not db else warn('Subir container  (ja esta online)')}")
        print(f"  [2] Verificar status")
        if db:
            print(f"  [3] {ok('Popular com dados (seed.py)')}")
            print(f"  [4] {warn('Parar container')}")
        else:
            print(f"  [3] {dim('Popular com dados            (requer banco online)')}")
            print(f"  [4] {dim('Parar container              (banco ja esta offline)')}")
        print("\n  [0] Voltar")
        op = input("\n  > ").strip()
        if op == "0":
            break

        elif op == "3" and not db:
            print(err("\n  Banco offline! Suba o container primeiro (opcao 1)."))
            pause()
            continue

        elif op == "1":
            clear(); header()
            # tenta docker start; se falhar, faz docker run
            cmd_start = "docker start streaming-pg"
            print(f"\n  >> {cmd_start}")
            r = subprocess.run(cmd_start, shell=True, capture_output=True, text=True)
            if r.returncode == 0:
                print("  Container streaming-pg iniciado.")
            else:
                print("  Container nao existe. Criando...")
                cmd_run = (
                    "docker run -d --name streaming-pg "
                    "-e POSTGRES_DB=streaming "
                    "-e POSTGRES_USER=postgres "
                    "-e POSTGRES_PASSWORD=postgres "
                    "-p 5432:5432 "
                    "postgres:16-alpine"
                )
                print(f"  >> {cmd_run}")
                subprocess.run(cmd_run, shell=True)
                print("\n  Aguardando PostgreSQL inicializar (5s)...")
                time.sleep(5)
                cmd_schema = f'Get-Content "{os.path.join(ROOT, "db", "schema.sql")}" | docker exec -i streaming-pg psql -U postgres -d streaming'
                print(f"\n  Aplicando schema...")
                print(f"  >> {cmd_schema}")
                subprocess.run(["powershell", "-Command", cmd_schema])
            pause()

        elif op == "2":
            clear(); header()
            cmd = "docker ps --filter name=streaming-pg --format \"table {{.Names}}\t{{.Status}}\t{{.Ports}}\""
            print(f"\n  >> {cmd}\n")
            subprocess.run(cmd, shell=True)
            pause()

        elif op == "3":
            clear(); header()
            cmd = [PYTHON, os.path.join(ROOT, "db", "seed.py")]
            print(f"\n  >> {' '.join(cmd)}\n")
            subprocess.run(cmd, cwd=ROOT)
            pause()

        elif op == "4":
            clear(); header()
            cmd = "docker stop streaming-pg"
            print(f"\n  >> {cmd}")
            subprocess.run(cmd, shell=True)
            print("  Container parado.")
            pause()


def menu_derrubar():
    while True:
        clear(); header()
        print("\n  Derrubar Servicos:\n")
        statuses = [port_running(p) for p in SERVER_PORTS]
        any_running = any(statuses)
        for i, ((name, _, _), running) in enumerate(zip(SERVERS, statuses), 1):
            s = ok("ONLINE") if running else dim("offline")
            print(f"  [{i:2d}] {name}  [{s}]")
        print()
        if any_running:
            print(f"  [ A] {warn('Derrubar TODOS os servicos')}")
        else:
            print(f"  [ A] {dim('Derrubar TODOS             (nenhum ativo)')}")
        print("\n  [ 0] Voltar")
        op = input("\n  > ").strip().lower()
        if op == "0":
            break
        elif op == "a":
            if not any_running:
                print(err("\n  Nenhum servico ativo."))
                pause()
                continue
            clear(); header()
            print()
            for (name, _, _), port, running in zip(SERVERS, SERVER_PORTS, statuses):
                if running:
                    killed = kill_port(port)
                    print(f"  {name}: {ok('parado') if killed else err('falha ao parar')}")
                else:
                    print(f"  {name}: {dim('ja offline')}")
            pause()
        else:
            try:
                idx = int(op) - 1
                name, _, _ = SERVERS[idx]
                port = SERVER_PORTS[idx]
                if not statuses[idx]:
                    print(err(f"\n  {name.strip()} ja esta offline."))
                    pause()
                    continue
                killed = kill_port(port)
                if killed:
                    print(ok(f"\n  {name.strip()} parado."))
                else:
                    print(err(f"\n  Nao foi possivel parar {name.strip()}."))
                pause()
            except (ValueError, IndexError):
                pass

def menu_graficos():
    while True:
        clear(); header()
        temp = os.path.join(ROOT, "load-tests", "results", "temp")
        temp_exists = any(f.endswith("_stats.csv") for f in os.listdir(temp)) if os.path.exists(temp) else False
        print("\n  Graficos:\n")
        print("  [1] Gerar graficos dos resultados principais")
        print("  [2] Abrir relatorio.html existente (principal)")
        if temp_exists:
            print(f"  [3] {ok('Gerar graficos dos resultados temporarios (temp/)')}")
            print(f"  [4] {warn('Limpar arquivos temporarios (temp/)')}")
        else:
            print(f"  [3] {dim('Gerar graficos de resultados temporarios   (sem CSVs em temp/)')}")
            print(f"  [4] {dim('Limpar arquivos temporarios               (temp/ ja esta vazia)')}")
        print("\n  [0] Voltar")
        op = input("\n  > ").strip()
        if op == "0":
            break
        elif op == "1":
            clear(); header()
            gerar_graficos()
            pause()
        elif op == "2":
            path = os.path.join(ROOT, "load-tests", "results", "relatorio.html")
            if os.path.exists(path):
                os.startfile(path)
                print("\n  Abrindo relatorio.html...")
            else:
                print(err("\n  Arquivo nao encontrado. Gere os graficos primeiro (opcao 1)."))
            pause()
        elif op == "3":
            if not temp_exists:
                print(err("\n  Nenhum CSV encontrado em temp/. Execute um teste personalizado primeiro."))
                pause()
            else:
                clear(); header()
                _gerar_graficos_pasta(temp)
                pause()
        elif op == "4":
            if not temp_exists:
                print(err("\n  Pasta temp/ ja esta vazia."))
                pause()
            else:
                confirm = input(warn("\n  Apagar todos os arquivos de temp/? [s/N] ")).strip().lower()
                if confirm == "s":
                    import glob as _glob
                    for f in _glob.glob(os.path.join(temp, "*")):
                        os.remove(f)
                    print(ok("\n  Arquivos temporarios removidos."))
                else:
                    print("  Cancelado.")
                pause()

# ── Menu principal ────────────────────────────────────────────────────────────
def main():
    while True:
        clear(); header()
        db = db_running()
        status = ok("ONLINE") if db else err("OFFLINE")
        print(f"\n  Banco de dados: {status}\n")

        print(f"  [1] {bold('Banco de Dados (Docker)')}")

        if db:
            print(f"  [2] {ok('Subir TODOS os servicos')}")
            print(f"  [3] {ok('Subir servico especifico')}")
        else:
            print(f"  [2] {dim('Subir TODOS os servicos      (requer banco online)')}")
            print(f"  [3] {dim('Subir servico especifico     (requer banco online)')}")
        print(f"  [4] {ok('Executar testes de carga')}")

        print(f"  [5] {ok('Gerar graficos')}")
        print(f"  [6] {warn('Derrubar servicos')}")
        print(f"\n  [0] Sair")
        op = input("\n  > ").strip()
        if op == "0":
            clear()
            print("\n  Ate mais!\n")
            break
        elif op == "1": menu_banco()
        elif op == "2":
            if not db: print(err("\n  Banco offline! Suba o banco primeiro (opcao 1).")); pause()
            else: menu_subir_todos()
        elif op == "3":
            if not db: print(err("\n  Banco offline! Suba o banco primeiro (opcao 1).")); pause()
            else: menu_subir_especifico()
        elif op == "4": menu_testes()
        elif op == "5": menu_graficos()
        elif op == "6": menu_derrubar()

if __name__ == "__main__":
    main()
