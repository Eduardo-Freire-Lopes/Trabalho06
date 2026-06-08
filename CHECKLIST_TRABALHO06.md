# Checklist de Implementacao - Trabalho 06

## Status Geral
- [x] Projeto iniciado
- [x] Requisito extra da sala incorporado (2 linguagens por tecnologia)
- [ ] Ambiente base configurado
- [ ] Entregaveis finalizados

## 1) Definicao Inicial
- [x] Escolher duas linguagens principais: L1 = Python, L2 = TypeScript (Node.js)
- [ ] Definir stack e ferramentas (framework web, ORM, banco, gerador de dados)
- [x] Criar repositorio/estrutura de pastas do projeto
- [ ] Definir padrao de dados comum para as implementacoes em L1 e L2
- [ ] Definir estrategia de autenticacao (se houver) e tratamento de erros
- [ ] Definir matriz de implementacao: SOAP, REST, GraphQL e gRPC em L1 e L2

## 2) Modelagem do Dominio (Streaming)
- [x] Modelar entidades: Usuario, Musica, Playlist
- [x] Definir relacionamentos (Playlist <-> Musica; Usuario -> Playlists)
- [x] Definir esquema de persistencia (PostgreSQL)
- [x] Criar schema inicial (db/schema.sql)
- [x] Preparar script de seed com 500 usuarios, 500 musicas, 300 playlists (db/seed.py)

## 3) Contratos de API (equivalentes entre tecnologias)
- [x] Especificar operacoes CRUD de Usuario (U1-U5)
- [x] Especificar operacoes CRUD de Musica (M1-M5)
- [x] Especificar operacoes CRUD de Playlist + associacoes (P1-P7)
- [x] Especificar consultas exigidas no enunciado (api-contracts.json)
- [x] Listar todos os usuarios (Q1)
- [x] Listar todas as musicas (Q2)
- [x] Listar playlists de um usuario (Q3)
- [x] Listar musicas de uma playlist (Q4)
- [x] Listar playlists que contem uma musica (Q5)

## 4) Implementacao SOAP
- [x] Implementar servidor SOAP em L1 (Python - http.server manual) — soap/python/server.py ✓ testado
- [x] Implementar cliente SOAP em L1 — soap/python/client.py ✓ testado
- [x] Implementar servidor SOAP em L2 (TypeScript - soap) — soap/typescript/src/server.ts ✓ testado
- [x] Implementar cliente SOAP em L2 — soap/typescript/src/client.ts ✓ testado

## 5) Implementacao REST
- [ ] Definir rotas e recursos REST
- [x] Implementar servidor REST em L1 (Python - FastAPI) — rest/python/main.py ✓ testado
- [x] Implementar cliente REST em L1 — rest/python/client.py ✓ testado
- [x] Implementar servidor REST em L2 (TypeScript - Fastify) — rest/typescript/src/server.ts ✓ testado
- [x] Implementar cliente REST em L2 — rest/typescript/src/client.ts ✓ testado
- [x] Definir codigos HTTP e formato de erros

## 6) Implementacao GraphQL
- [ ] Definir schema (types, queries, mutations)
- [x] Implementar servidor GraphQL em L1 (Python - Strawberry) — graphql/python/main.py ✓ testado
- [x] Implementar cliente GraphQL em L1 — graphql/python/client.py ✓ testado
- [x] Implementar servidor GraphQL em L2 (TypeScript - Apollo Server) — graphql/typescript/src/server.ts ✓ testado
- [x] Implementar cliente GraphQL em L2 — graphql/typescript/src/client.ts ✓ testado
- [ ] Validar performance de consultas aninhadas (evitar N+1)

## 7) Implementacao gRPC
- [x] Definir arquivo .proto (mensagens e servicos) — grpc/streaming.proto
- [x] Implementar servidor gRPC em L1 (Python - grpclib+betterproto) — grpc/python/server.py ✓ testado
- [x] Implementar cliente gRPC em L1 — grpc/python/client.py ✓ testado
- [x] Implementar servidor gRPC em L2 (TypeScript - @grpc/grpc-js) — grpc/typescript/src/server.ts ✓ testado
- [x] Implementar cliente gRPC em L2 — grpc/typescript/src/client.ts ✓ testado

## 8) Testes de Carga (comparativos) ✓ CONCLUIDO
- [x] Usar Locust como ferramenta de carga (professor recomendou explicitamente)
- [x] Criar script de seed: carregar centenas de usuarios e musicas antes dos testes
- [x] Garantir que as respostas sejam grandes (ex: GET /usuarios retorna 500+ registros)
- [x] Definir cenario equivalente para as 4 tecnologias em L1 e L2
- [x] Executar perfil de carga LEVE (10u/60s) e coletar metricas — CSVs em load-tests/results/
- [x] Executar perfil de carga MEDIA (50u/60s) e coletar metricas
- [x] Executar perfil de carga ALTA (150u/60s) e coletar metricas
- [x] Organizar resultados em tabela unica (tecnologia x linguagem x perfil) — ver abaixo
- [ ] Gerar graficos comparativos por tecnologia e por linguagem

### Resultados consolidados (Python L1, porta padrao)

| Tecnologia | Perfil  | Usuarios | Reqs  | p50 (ms) | p95 (ms) | req/s  | Falhas |
|------------|---------|----------|-------|----------|----------|--------|--------|
| REST       | LEVE    | 10       | 2354  | 36       | 82       | 42.5   | 1.1%   |
| REST       | MEDIO   | 50       | 11056 | 57       | 190      | 186.4  | 0.85%  |
| REST       | PESADO  | 150      | 10412 | 320      | 790      | 175.3  | 0.93%  |
| GraphQL    | LEVE    | 10       | 2314  | 280      | 500      | 38.6   | 0%     |
| GraphQL    | MEDIO   | 50       | 6057  | 292      | 500      | 102.2  | 0%     |
| GraphQL    | PESADO  | 150      | 5779  | 1300     | 1900     | 97.7   | 0%     |
| gRPC*      | LEVE    | 10       | 2321  | 63       | 105      | 38.7   | 0%     |
| gRPC*      | MEDIO   | 50       | 3630  | 428      | 758      | 60.5   | 0%     |
| gRPC*      | PESADO  | 150      | 2866  | 1557     | 3374     | 47.8   | 0%     |
| SOAP       | LEVE    | 10       | 246   | 2100     | 2200     | 4.1    | 0%     |
| SOAP       | MEDIO   | 50       | 1214  | 2100     | 2200     | 20.5   | 0%     |
| SOAP       | PESADO  | 150      | 2218  | 3900     | 4300     | 37.3   | 37%    |

*gRPC medido com bench_grpc.py (asyncio puro) — grpclib incompativel com gevent do Locust.
 SOAP Python usa http.server single-thread (stdlib); latencia alta e'esperada e academicamente relevante.

## 9) Analise Critica ✓ CONCLUIDO
- [x] Consolidar vantagens/desvantagens observadas por tecnologia — ANALISE_CRITICA.md
- [x] Consolidar vantagens/desvantagens observadas por linguagem
- [x] Relacionar resultados de carga com caracteristicas tecnicas de tecnologia e linguagem
- [x] Escrever conclusoes (quando usar cada abordagem)

## 10) Demo ao Vivo (exigido pelo professor) ✓ ROTEIRO PRONTO
- [x] Mostrar servidor rodando para cada tecnologia (L1 e L2) — ver DEMO_ROTEIRO.md
- [x] Demo: listar todos os usuarios
- [x] Demo: listar todas as musicas
- [x] Demo: criar playlist para um usuario
- [x] Demo: listar musicas de uma playlist
- [x] Demo: listar playlists que contem uma musica

## 11) Slides (Entregavel)
- [ ] Identificacao dos membros
- [ ] Origem, caracteristicas, vantagens/desvantagens (com codigo em duas linguagens)
- [ ] Mostrar matriz final de implementacoes (4 tecnologias x 2 linguagens)
- [ ] Analise critica baseada na implementacao e testes
- [ ] Graficos de teste de carga
- [ ] Revisao final de clareza e tempo de apresentacao

## Proposta de Linguagens e Stack (Recomendada)
- [x] Aprovar proposta de linguagens (Python + TypeScript/Node.js)
- [x] Aprovar proposta de stack

### Linguagens (L1 e L2)
- L1: Python
- L2: TypeScript (Node.js)

### Justificativa resumida
- Cobrem dois ecossistemas bem diferentes (Python vs Node.js/TS), fortalecendo a comparacao.
- Ambas possuem suporte maduro e bibliotecas ativas para SOAP, REST, GraphQL e gRPC.
- Curva de implementacao rapida para trabalho academico; TypeScript adiciona tipagem sem overhead de compilacao lenta.

### Stack sugerida por tecnologia
- SOAP: Python (Spyne) e TypeScript (strong-soap / soap)
- REST: Python (FastAPI) e TypeScript (Fastify ou Express)
- GraphQL: Python (Strawberry GraphQL) e TypeScript (Apollo Server)
- gRPC: Python (grpcio) e TypeScript (@grpc/grpc-js)

### Persistencia e padrao comum
- Banco unico para todas as implementacoes: PostgreSQL
- ORM em Python: SQLAlchemy
- ORM em TypeScript: Prisma
- Estrategia para acelerar: schema de banco unico e dataset seed unico

### Ferramenta de testes de carga
- Locust (recomendado pelo professor em aula)

### Ordem de implementacao recomendada
1. REST em Python e Java (base do dominio e validacao dos fluxos CRUD)
2. GraphQL em Python e Java (reuso de modelo e regras)
3. gRPC em Python e Java (contrato .proto compartilhado)
4. SOAP em Python e Java (contrato WSDL/XSD e adaptacao final)

## Proximo Passo Imediato
- [ ] Confirmar L1, L2 e stack para iniciarmos a implementacao
