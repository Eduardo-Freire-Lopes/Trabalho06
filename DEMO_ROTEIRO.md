# Roteiro de Demo ao Vivo — Trabalho 06

> **Antes de começar:** abra 5 terminais PowerShell no diretório do projeto.
> Docker deve estar rodando com o container `streaming-pg`.

```powershell
cd C:\Users\Profectum\NaborClasse\Trabalho06
```

---

## 0. Verificações iniciais (30 s)

```powershell
# Banco de dados rodando?
docker ps --filter name=streaming-pg --format "{{.Names}} {{.Status}}"

# Contagem de registros
docker exec streaming-pg psql -U postgres -d streaming -c "
  SELECT 'usuarios' AS tabela, COUNT(*) FROM usuarios
  UNION ALL SELECT 'musicas', COUNT(*) FROM musicas
  UNION ALL SELECT 'playlists', COUNT(*) FROM playlists;"
```

Resultado esperado: 500 / 500 / 300.

---

## 1. REST

### Iniciar servidor Python (Terminal 1)
```powershell
.venv\Scripts\python.exe -m uvicorn rest.python.main:app --port 8000
```

### Iniciar servidor TypeScript (Terminal 2)
```powershell
cd rest/typescript ; npx ts-node src/server.ts
```

### Demonstração com o client Python (Terminal 3)
```powershell
.venv\Scripts\python.exe rest/python/client.py
```

O client executa automaticamente:
- Q1 — listar todos os usuários (500 registros)
- Q2 — listar todas as músicas (500 registros)
- Q3 — listar playlists de um usuário
- Q4 — listar músicas de uma playlist
- Q5 — listar playlists que contêm uma música
- Criação de playlist + adição de música + remoção

### Demonstração com o client TypeScript (Terminal 3)
```powershell
cd rest/typescript ; npx ts-node src/client.ts
```

---

## 2. GraphQL

### Iniciar servidor Python (Terminal 1)
```powershell
.venv\Scripts\python.exe -m uvicorn graphql.python.main:app --port 8002
```

### Iniciar servidor TypeScript (Terminal 2)
```powershell
cd graphql/typescript ; npx ts-node src/server.ts
```

### Demonstração com o client Python (Terminal 3)
```powershell
.venv\Scripts\python.exe graphql/python/client.py
```

### Demonstração com o client TypeScript (Terminal 3)
```powershell
cd graphql/typescript ; npx ts-node src/client.ts
```

> **Ponto de destaque para o professor:** abrir `http://localhost:8002/graphql` no
> navegador para mostrar o playground GraphiQL com introspecção do schema ao vivo.

---

## 3. gRPC

### Iniciar servidor Python (Terminal 1)
```powershell
.venv\Scripts\python.exe grpc/python/server.py
```

### Iniciar servidor TypeScript (Terminal 2)
```powershell
cd grpc/typescript ; npx ts-node src/server.ts
```

### Demonstração com o client Python (Terminal 3)
```powershell
.venv\Scripts\python.exe grpc/python/client.py
```

### Demonstração com o client TypeScript (Terminal 3)
```powershell
cd grpc/typescript ; npx ts-node src/client.ts
```

> **Ponto de destaque:** mostrar o arquivo `grpc/streaming.proto` — um único contrato
> gera stubs para Python e TypeScript.

---

## 4. SOAP

### Iniciar servidor Python (Terminal 1)
```powershell
.venv\Scripts\python.exe soap/python/server.py
```

### Iniciar servidor TypeScript (Terminal 2)
```powershell
cd soap/typescript ; npx ts-node src/server.ts
```

### Demonstração com o client Python (Terminal 3)
```powershell
.venv\Scripts\python.exe soap/python/client.py
```

### Demonstração com o client TypeScript (Terminal 3)
```powershell
cd soap/typescript ; npx ts-node src/client.ts
```

> **Ponto de destaque:** mostrar o envelope XML bruto no terminal para contrastar
> com a verbosidade em relação ao JSON/Protobuf.

---

## 5. Testes de Carga (resumo visual)

```powershell
# Abrir relatório HTML com gráficos comparativos
Start-Process "load-tests\results\relatorio.html"
```

Comentar os pontos principais ao mostrar o relatório:
1. **REST** — p50=36 ms LEVE, mantém < 200 ms até 50 usuários
2. **gRPC** — eficiente no LEVE (63 ms), satura no PESADO (1557 ms) por server single-process
3. **GraphQL** — overhead fixo de parsing (~280 ms) cresce sob carga pesada
4. **SOAP** — p50 ≥ 2100 ms em todos os perfis; 37% falhas no PESADO (fila single-thread)

---

## 6. Matriz de Implementações

| Tecnologia | Python (L1) | TypeScript (L2) |
|------------|-------------|-----------------|
| REST       | FastAPI (porta 8000) | Fastify (porta 8001) |
| GraphQL    | Strawberry + FastAPI (porta 8002) | Apollo Server 4 (porta 4000) |
| gRPC       | grpclib + betterproto (porta 8004) | @grpc/grpc-js (porta 8005) |
| SOAP       | http.server manual (porta 8006) | soap library (porta 8007) |

---

## Ordem sugerida de apresentação (≈ 20 min)

| Tempo | Etapa |
|-------|-------|
| 0–2 min | Apresentação do domínio: streaming de música, banco, seed |
| 2–6 min | REST: servidor + client Python + client TS + destaque OpenAPI |
| 6–10 min | GraphQL: servidor + playground GraphiQL + client |
| 10–14 min | gRPC: servidor + client + mostrar o .proto |
| 14–17 min | SOAP: servidor + client + envelope XML ao vivo |
| 17–20 min | Testes de carga: abrir relatorio.html + análise comparativa |
