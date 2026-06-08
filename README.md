# Trabalho 06 — Comparação de Tecnologias de Invocação de Serviços Remotos

---

## 👥 Alunos

| Nome | Matrícula |
|------|-----------|
| Eduardo Célio Freire Lopes | 2120351 |
| Sara Pessoa Silva | 2120371 |
| Luiz Roberto Chaves | 2418598 |

---

Implementação de um serviço de **streaming de música** usando 4 tecnologias de invocação remota, cada uma em 2 linguagens de programação, com testes de carga comparativos.

## Tecnologias e Linguagens

| Tecnologia | Python (L1) | TypeScript/Node.js (L2) |
|------------|-------------|--------------------------|
| **REST**    | FastAPI + Uvicorn — porta `8000` | Fastify — porta `8001` |
| **GraphQL** | Strawberry + FastAPI — porta `8002` | Apollo Server 4 — porta `4000` |
| **gRPC**    | grpclib + betterproto — porta `8004` | @grpc/grpc-js — porta `8005` |
| **SOAP**    | http.server (stdlib manual) — porta `8006` | soap library — porta `8007` |

## Domínio

Serviço de streaming com as entidades:
- **Usuário** — CRUD completo
- **Música** — CRUD completo
- **Playlist** — CRUD + associação com músicas

### Consultas obrigatórias
| # | Descrição |
|---|-----------|
| Q1 | Listar todos os usuários |
| Q2 | Listar todas as músicas |
| Q3 | Listar playlists de um usuário |
| Q4 | Listar músicas de uma playlist |
| Q5 | Listar playlists que contêm uma música |

## Banco de Dados

PostgreSQL 16 via Docker.

```bash
docker run -d --name streaming-pg \
  -e POSTGRES_DB=streaming \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:16-alpine
```

Aplicar o schema:
```bash
docker exec -i streaming-pg psql -U postgres -d streaming < db/schema.sql
```

Popular com dados de teste (500 usuários, 500 músicas, 300 playlists):
```bash
python db/seed.py
```

## Estrutura do Projeto

```
Trabalho06/
├── db/
│   ├── schema.sql          # Schema PostgreSQL
│   └── seed.py             # Gerador de dados de teste
├── rest/
│   ├── python/             # FastAPI (porta 8000)
│   └── typescript/         # Fastify (porta 8001)
├── graphql/
│   ├── python/             # Strawberry + FastAPI (porta 8002)
│   └── typescript/         # Apollo Server 4 (porta 4000)
├── grpc/
│   ├── streaming.proto     # Contrato compartilhado
│   ├── python/             # grpclib + betterproto (porta 8004)
│   └── typescript/         # @grpc/grpc-js (porta 8005)
├── soap/
│   ├── python/             # http.server manual (porta 8006)
│   └── typescript/         # soap library (porta 8007)
├── load-tests/
│   ├── locust_rest.py      # Teste de carga REST
│   ├── locust_graphql.py   # Teste de carga GraphQL
│   ├── locust_soap.py      # Teste de carga SOAP
│   ├── bench_grpc.py       # Benchmark gRPC (asyncio puro)
│   ├── gerar_graficos.py   # Gera relatorio.html com Chart.js
│   └── results/            # CSVs e relatorio.html
├── ANALISE_CRITICA.md      # Análise comparativa completa
└── DEMO_ROTEIRO.md         # Roteiro para a apresentação
```

## Pré-requisitos

- Python 3.12+
- Node.js 18+
- Docker
- Git

## Instalação

### Python
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# ou: source .venv/bin/activate  # Linux/macOS

pip install fastapi uvicorn strawberry-graphql grpclib betterproto \
            requests psycopg2-binary faker locust
```

### TypeScript (por subprojeto)
```bash
cd rest/typescript      && npm install
cd graphql/typescript   && npm install
cd grpc/typescript      && npm install
cd soap/typescript      && npm install
```

## Como Executar

### REST
```bash
# Python
python -m uvicorn rest.python.main:app --port 8000

# TypeScript
cd rest/typescript && npx ts-node src/server.ts
```

### GraphQL
```bash
# Python
python -m uvicorn graphql.python.main:app --port 8002

# TypeScript
cd graphql/typescript && npx ts-node src/server.ts
```

### gRPC
```bash
# Python
python grpc/python/server.py

# TypeScript
cd grpc/typescript && npx ts-node src/server.ts
```

### SOAP
```bash
# Python
python soap/python/server.py

# TypeScript
cd soap/typescript && npx ts-node src/server.ts
```

### Clientes (demonstração)
```bash
python rest/python/client.py
python graphql/python/client.py
python grpc/python/client.py
python soap/python/client.py

cd rest/typescript      && npx ts-node src/client.ts
cd graphql/typescript   && npx ts-node src/client.ts
cd grpc/typescript      && npx ts-node src/client.ts
cd soap/typescript      && npx ts-node src/client.ts
```

## Testes de Carga

Os testes cobrem 3 perfis: **LEVE** (10 usuários), **MÉDIO** (50 usuários) e **PESADO** (150 usuários), todos com 60 segundos de duração.

```bash
# REST, GraphQL e SOAP — via Locust
.venv\Scripts\locust -f load-tests/locust_rest.py --headless \
  -u 10 -r 2 --run-time 60s --csv=load-tests/results/rest_leve \
  --host=http://localhost:8000

# gRPC — benchmark asyncio (grpclib incompatível com gevent do Locust)
python load-tests/bench_grpc.py --users 10 --run-time 60 \
  --csv load-tests/results/grpc_leve
```

### Gerar relatório visual
```bash
python load-tests/gerar_graficos.py
# Abre: load-tests/results/relatorio.html
```

### Resultados (servidores Python L1)

| Tecnologia | Perfil  | p50 (ms) | p95 (ms) | req/s  | Falhas |
|------------|---------|----------|----------|--------|--------|
| REST       | LEVE    | 36       | 82       | 42.5   | 1.1%   |
| REST       | MÉDIO   | 57       | 190      | 186.4  | 0.85%  |
| REST       | PESADO  | 320      | 790      | 175.3  | 0.93%  |
| GraphQL    | LEVE    | 280      | 500      | 38.6   | 0%     |
| GraphQL    | MÉDIO   | 292      | 500      | 102.2  | 0%     |
| GraphQL    | PESADO  | 1300     | 1900     | 97.7   | 0%     |
| gRPC *     | LEVE    | 63       | 105      | 38.7   | 0%     |
| gRPC *     | MÉDIO   | 428      | 758      | 60.5   | 0%     |
| gRPC *     | PESADO  | 1557     | 3374     | 47.8   | 0%     |
| SOAP       | LEVE    | 2100     | 2200     | 4.1    | 0%     |
| SOAP       | MÉDIO   | 2100     | 2200     | 20.5   | 0%     |
| SOAP       | PESADO  | 3900     | 4300     | 37.3   | **37%**|

> \* gRPC medido com `bench_grpc.py` — `grpclib` é incompatível com o gevent do Locust.  
> SOAP usa `http.server` single-thread (stdlib); latência alta é esperada e academicamente relevante.

## Observações Técnicas

- **grpcio bloqueado**: a política AppControl do Windows bloqueou o binário `grpcio`. Alternativa: `grpclib` (asyncio puro) + `betterproto`.
- **spyne incompatível**: falha no Python 3.14 por dependência de `six`. SOAP implementado manualmente com `http.server` + `xml.etree.ElementTree`.
- **gRPC + Locust**: `grpclib` usa asyncio; Locust usa gevent com monkey-patch global — incompatíveis. Solução: `bench_grpc.py` autônomo.

Para a análise crítica completa, consulte [ANALISE_CRITICA.md](ANALISE_CRITICA.md).
