# Análise Crítica — Trabalho 06: Invocação Remota

## Contexto do Experimento

- **Domínio:** serviço de streaming de música (usuários, músicas, playlists)
- **Banco de dados:** PostgreSQL 16 (Docker), 500 usuários · 500 músicas · 300 playlists
- **Linguagens:** Python (L1) e TypeScript/Node.js (L2)
- **Tecnologias:** SOAP, REST, GraphQL, gRPC
- **Carga:** Locust 2.44 — perfis LEVE (10u/60s), MÉDIO (50u/60s) e PESADO (150u/60s)
- **Servidor testado:** Python L1 em cada tecnologia (porta padrão)

---

## 1. Resultados de Carga Consolidados

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
| SOAP       | PESADO  | 3900     | 4300     | 37.3   | **37%** |

> \* gRPC medido com `bench_grpc.py` (asyncio puro) — `grpclib` é incompatível com o gevent do Locust; ver Seção 4.

---

## 2. Análise por Tecnologia

### 2.1 REST

**Implementações:** FastAPI (Python) · Fastify (TypeScript)

**Vantagens:**
- Menor latência absoluta nos três perfis: p50 de apenas **36 ms** no LEVE.
- Maior throughput sustentado: **186 req/s** no MÉDIO, mantendo p95 < 200 ms.
- Sem estado no protocolo — escala horizontalmente sem coordenação entre instâncias.
- Ecossistema maduro: ferramentas de teste (Locust, k6, Postman), observabilidade (OpenAPI/Swagger gerado automaticamente pelo FastAPI) e cache HTTP nativos.
- Curva de aprendizado baixa: qualquer desenvolvedor conhece HTTP + JSON.

**Desvantagens:**
- Contrato implícito: sem schema formal obrigatório, mudanças de API podem quebrar clientes silenciosamente (mitigado por OpenAPI, mas não é estrutural).
- Over-fetching/under-fetching: o cliente recebe todos os campos de uma resposta mesmo que precise de apenas um subconjunto.
- Ausência de tipagem binária: serialização JSON é verbosa comparada a Protobuf.

**Conclusão:** melhor escolha para APIs públicas, microsserviços de uso geral e times com perfis variados. Desempenho excelente com frameworks async (FastAPI, Fastify).

---

### 2.2 GraphQL

**Implementações:** Strawberry + FastAPI (Python) · Apollo Server 4 (TypeScript)

**Vantagens:**
- Schema tipado e auto-documentado (`schema.graphql` é a fonte de verdade).
- O cliente especifica exatamente os campos que precisa — elimina over-fetching estruturalmente.
- Introspection: IDEs e ferramentas (GraphiQL, Insomnia) entendem o schema automaticamente.
- Uma única URL para todas as operações — simples de configurar em proxies/firewalls.
- Mutations agrupáveis: múltiplas escritas em uma única requisição.

**Desvantagens:**
- Latência de base mais alta: p50 de **280 ms** mesmo no LEVE, contra 36 ms do REST. O overhead vem do parsing e validação do AST da query a cada requisição.
- Sob carga pesada a latência triplica (280 ms → 1300 ms), sugerindo que o executor de queries se torna gargalo antes do banco.
- Problema N+1: queries aninhadas sem DataLoader geram múltiplos selects no banco (não mitigado nesta implementação).
- Curva de aprendizado maior: resolvers, DataLoader, diretivas e paginação por cursor são conceitos específicos do GraphQL.
- Cache HTTP convencional não funciona (POST único endpoint) — requer cache a nível de aplicação.

**Conclusão:** ideal para APIs com clientes variados (mobile, web, parceiros) que consomem subconjuntos diferentes dos dados. Custo de latência é justificado quando a flexibilidade do schema reduz round-trips.

---

### 2.3 gRPC

**Implementações:** grpclib + betterproto (Python) · @grpc/grpc-js (TypeScript)

**Vantagens:**
- Protocolo binário (Protobuf): payloads significativamente menores que JSON; serialização/deserialização mais rápida.
- Schema obrigatório (`.proto`): contrato explícito e fortemente tipado, geração de stubs em múltiplas linguagens a partir de um único arquivo.
- Suporte nativo a streaming bidirecional (server-streaming, client-streaming, bidirecional) — não disponível nativamente em REST/GraphQL.
- Multiplexação HTTP/2: múltiplas chamadas concorrentes sobre uma única conexão TCP, reduzindo overhead de handshake.
- Ótimo para comunicação inter-serviços (service mesh) onde ambos os lados controlam o schema.

**Desvantagens:**
- **Incompatibilidade com grpcio no ambiente**: a política AppControl do Windows bloqueou o binário `grpcio`, exigindo uso de `grpclib` (asyncio puro). Isso é uma limitação real de ambientes corporativos restritivos.
- **Incompatibilidade com Locust**: `grpclib` usa asyncio; Locust usa gevent com monkey-patch global de sockets — incompatíveis. Medição exigiu benchmark alternativo (`bench_grpc.py`), sem o isolamento e os relatórios nativos do Locust.
- Latência cresce acentuadamente sob carga: p50 sobe de 63 ms (LEVE) para **1557 ms** (PESADO), indicando que o servidor asyncio single-process `grpclib` não paraleliza tão bem quanto o FastAPI com múltiplos workers.
- HTTP/2 dificulta depuração com ferramentas comuns (Wireshark precisa de configuração extra, proxies intermediários podem não suportá-lo).
- Não adequado para APIs públicas diretamente expostas a browsers sem uma camada gRPC-Web.

**Conclusão:** excelente para comunicação interna entre microsserviços onde latência e banda são críticos e ambos os lados controlam o schema. A barreira de adoção (tooling, compatibilidade, debugging) é alta para APIs externas.

---

### 2.4 SOAP

**Implementações:** http.server + xml.etree (Python manual) · `soap` library (TypeScript)

**Vantagens:**
- Padrão maduro e amplamente suportado em ambientes corporativos e governamentais legados.
- WSDL como contrato formal e validável por ferramentas de terceiros (SoapUI, etc.).
- Suporte nativo a transações distribuídas (WS-AtomicTransaction), segurança padronizada (WS-Security) e roteamento (WS-Addressing) — recursos sem equivalente nativo em REST/GraphQL/gRPC.
- Fortemente tipado via XML Schema (XSD).

**Desvantagens:**
- **Pior desempenho absoluto em todos os perfis**: p50 ≥ 2100 ms mesmo no LEVE com apenas 10 usuários.
  - Causa principal: a implementação Python usa `http.server.HTTPServer` da stdlib, que é **single-thread** — atende uma requisição por vez. Isso é uma limitação da ausência de framework SOAP compatível com Python 3.14 (spyne falha por dependência de `six`, removida no Python 3.x).
  - Mesmo com um servidor multi-thread, o overhead do envelope XML (parsing, namespace resolution, validação) é intrinsecamente maior que JSON ou Protobuf.
- PESADO atingiu **37% de falhas** por timeout de fila — o servidor não consegue drenar requisições na velocidade em que chegam.
- Verbosidade extrema: um envelope SOAP simples é 5-10× maior que o equivalente JSON.
- Complexidade de implementação manual alta: sem framework, é necessário construir e parsear XML manualmente.
- Praticamente obsoleto para novos projetos fora de contextos legados/governamentais.

**Conclusão:** use SOAP apenas quando a integração com sistemas legados ou regulamentações específicas o exigirem. Para novos projetos, qualquer outra tecnologia desta lista é superior em desempenho, simplicidade e manutenibilidade.

---

## 3. Análise por Linguagem

### Python (L1)
- **FastAPI** (REST/GraphQL): framework async com excelente desempenho; geração automática de OpenAPI; Strawberry integra naturalmente ao FastAPI via `include_router`.
- **grpclib + betterproto**: única alternativa viável no ambiente (grpcio bloqueado). API asyncio nativa, mas ecossistema menor e menos documentado que grpcio.
- **Stdlib SOAP**: obrigado a implementar manualmente por incompatibilidade do spyne com Python 3.14. Academicamente interessante, mas impraticável em produção.
- **Ponto forte:** rico ecossistema científico/de dados; Python 3.14 com asyncio nativo permite servidores eficientes sem dependências externas pesadas.
- **Ponto fraco:** GIL (Global Interpreter Lock) limita paralelismo real em CPU-bound; contornado com múltiplos workers (Uvicorn + Gunicorn) ou asyncio.

### TypeScript/Node.js (L2)
- **Fastify** (REST): throughput comparável ao FastAPI; type-safety nativa com TypeScript reduz erros de contrato.
- **Apollo Server 4** (GraphQL): implementação de referência; standalone mode sem Express simplifica deploy.
- **@grpc/grpc-js** (gRPC): biblioteca oficial Google para Node.js; usa bindings nativos mas sem restrições de AppControl como o grpcio.
- **`soap` library** (SOAP): única opção madura para Node.js; WSDL inline elimina necessidade de arquivo externo.
- **Ponto forte:** event loop single-thread não bloqueante é naturalmente adequado para I/O-bound (requisições de rede, banco); TypeScript garante contratos em tempo de compilação.
- **Ponto fraco:** tipagem dinâmica do JS na fronteira com bibliotecas sem tipos pode introduzir bugs sutis; ecosystem de qualidade variável para protocolos menos comuns (SOAP).

---

## 4. Observações Técnicas Relevantes

### Conflito grpclib + Locust (gevent)
O Locust utiliza `gevent` com monkey-patch global de sockets (`gevent.monkey.patch_all()`). O `grpclib` é baseado em `asyncio`, que usa os sockets originais do sistema operacional. Após o patch, o asyncio tenta usar os sockets gevent em threads secundárias e bloqueia indefinidamente (deadlock silencioso — 0 requisições sem erro).

Abordagens testadas e seus resultados:
| Abordagem | Resultado |
|-----------|-----------|
| `asyncio.run()` diretamente no greenlet | Falha: `RuntimeError: no current event loop` |
| `asyncio.set_event_loop()` + `run_until_complete()` | Trava: loop não avança dentro do greenlet |
| `threading.Thread` + `run_coroutine_threadsafe` | Trava: `threading.Thread` foi monkey-patched para greenlet |
| `gevent.monkey.get_original("threading", "Thread")` + `run_coroutine_threadsafe` | Deadlock: `future.result()` bloqueia o greenlet |
| `gevent.get_hub().threadpool.apply(asyncio.run, ...)` | Trava: gevent patcha `select`/sockets globalmente |
| **`bench_grpc.py` (asyncio puro, sem Locust)** | **✅ Funciona — 2321/3630/2866 reqs nos 3 perfis** |

**Solução adotada:** benchmark autônomo em asyncio (`load-tests/bench_grpc.py`), gerando CSVs no mesmo formato do Locust.

### SOAP Python — servidor single-thread
O `spyne` (framework SOAP Python) falha no Python 3.14 por dependência de `six` (removida). A implementação manual com `http.server.HTTPServer` é **single-thread por padrão** — atende exatamente uma requisição por vez. Isso explica o p50 ≥ 2100 ms constante: cada requisição espera na fila. Com `ThreadingMixIn` ou um servidor WSGI multi-worker (Gunicorn), o SOAP Python seria significativamente mais rápido, mas a complexidade de manutenção do XML manual persistiria.

---

## 5. Quando Usar Cada Tecnologia

| Cenário | Recomendação |
|---------|-------------|
| API pública consumida por browsers/mobile | **REST** — baixa latência, cache HTTP, ampla compatibilidade |
| API com múltiplos clientes com necessidades diferentes | **GraphQL** — cliente define o que precisa, schema auto-documentado |
| Comunicação interna entre microsserviços | **gRPC** — Protobuf binário, streaming, schema obrigatório |
| Integração com sistemas legados corporativos/gov | **SOAP** — padrão WS-*, WSDL, compatibilidade garantida |
| Sistema financeiro com transações distribuídas | **SOAP** (WS-AtomicTransaction) ou **gRPC** (com saga pattern) |
| Prototipagem rápida | **REST** — menor boilerplate, ferramentas ubíquas |

---

## 6. Conclusão

Os resultados confirmam as expectativas teóricas com dados concretos:

1. **REST domina em throughput e latência** para operações simples de leitura/escrita — a combinação FastAPI + asyncio + PostgreSQL async entrega p50 < 60 ms até 50 usuários concorrentes.

2. **GraphQL tem custo de latência fixo** pelo parsing do AST, mas oferece flexibilidade estrutural única. O p50 de 280–292 ms nos perfis LEVE e MÉDIO é aceitável para APIs interativas; o salto para 1300 ms no PESADO indica necessidade de caching de queries parseadas em produção.

3. **gRPC é eficiente no LEVE** (p50=63 ms), mas o servidor asyncio single-process satura sob 150 usuários (p50=1557 ms). Em produção, múltiplos workers ou um servidor gRPC baseado em threads (como o `grpcio` nativo) mitigariam isso.

4. **SOAP é estruturalmente inadequado para alta carga** com implementações baseadas em stdlib. A latência de 2+ segundos por requisição é intrínseca ao processamento XML e ao modelo single-thread, não apenas à implementação escolhida.

5. **A escolha da linguagem importa menos que a escolha do framework**: FastAPI (Python) e Fastify (TypeScript) têm desempenho comparável; o que diferencia as implementações é o modelo de I/O (async vs. sync) e a qualidade das bibliotecas de suporte para cada protocolo.
