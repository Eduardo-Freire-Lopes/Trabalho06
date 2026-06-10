# Comandos da Demo — Trabalho 06

> Todos os comandos assumem que o terminal está em:
> `C:\Users\Profectum\NaborClasse\Trabalho06`

---

## 0. Preparação do ambiente

```powershell
# Ativar o ambiente virtual Python
.venv\Scripts\Activate.ps1
```

---

## 1. Banco de Dados (PostgreSQL + Docker)

```powershell
# Subir o container
docker run -d --name streaming-pg `
  -e POSTGRES_DB=streaming `
  -e POSTGRES_USER=postgres `
  -e POSTGRES_PASSWORD=postgres `
  -p 5432:5432 `
  postgres:16-alpine

# Verificar se subiu
docker ps --filter name=streaming-pg

# Aplicar o schema (criar tabelas)
Get-Content db/schema.sql | docker exec -i streaming-pg psql -U postgres -d streaming

# Popular com dados (500 usuários, 500 músicas, 300 playlists)
.venv\Scripts\python.exe db/seed.py

# Verificar contagem dos dados
docker exec streaming-pg psql -U postgres -d streaming -c `
  "SELECT 'usuarios' AS tabela, COUNT(*) FROM usuarios
   UNION ALL SELECT 'musicas', COUNT(*) FROM musicas
   UNION ALL SELECT 'playlists', COUNT(*) FROM playlists;"
```

---

## 2. REST

### Servidor Python (porta 8000)
```powershell
cd rest/python
..\..\venv\Scripts\python.exe -m uvicorn main:app --port 8000 --reload
```

### Servidor TypeScript (porta 8001)
```powershell
cd rest/typescript
npx ts-node src/server.ts
```

### Client Python (demonstra todas as operações)
```powershell
.venv\Scripts\python.exe rest/python/client.py
```

### Client TypeScript
```powershell
cd rest/typescript
npx ts-node src/client.ts
```

### Requisições HTTP diretas (curl / PowerShell)
```powershell
# Q1 - Listar todos os usuários
Invoke-RestMethod http://localhost:8000/usuarios

# Q2 - Listar todas as músicas
Invoke-RestMethod http://localhost:8000/musicas

# Q3 - Playlists de um usuário
Invoke-RestMethod http://localhost:8000/usuarios/1/playlists

# Q4 - Músicas de uma playlist
Invoke-RestMethod http://localhost:8000/playlists/1/musicas

# Q5 - Playlists que contêm uma música
Invoke-RestMethod http://localhost:8000/musicas/1/playlists

# Criar usuário
Invoke-RestMethod http://localhost:8000/usuarios -Method POST `
  -ContentType "application/json" `
  -Body '{"nome":"Teste Demo","email":"demo@teste.com"}'

# Criar música
Invoke-RestMethod http://localhost:8000/musicas -Method POST `
  -ContentType "application/json" `
  -Body '{"titulo":"Demo Song","artista":"Demo Artist","ano_lancamento":2024,"duracao_segundos":200}'

# Criar playlist
Invoke-RestMethod http://localhost:8000/playlists -Method POST `
  -ContentType "application/json" `
  -Body '{"nome":"Playlist Demo","usuario_id":1}'
```

---

## 3. GraphQL

### Servidor Python (porta 8002)
```powershell
cd graphql/python
..\..\venv\Scripts\python.exe -m uvicorn main:app --port 8002 --reload
```

### Servidor TypeScript (porta 4000)
```powershell
cd graphql/typescript
npx ts-node src/server.ts
```

### Client Python
```powershell
.venv\Scripts\python.exe graphql/python/client.py
```

### Client TypeScript
```powershell
cd graphql/typescript
npx ts-node src/client.ts
```

### Playground interativo (abrir no navegador)
```powershell
Start-Process "http://localhost:8002/graphql"
```

### Queries GraphQL diretas (PowerShell)
```powershell
# Q1 - Listar usuários
Invoke-RestMethod http://localhost:8002/graphql -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"{ usuarios { id nome email } }"}'

# Q2 - Listar músicas
Invoke-RestMethod http://localhost:8002/graphql -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"{ musicas { id titulo artista } }"}'

# Q3 - Playlists de um usuário
Invoke-RestMethod http://localhost:8002/graphql -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"{ playlistsDoUsuario(usuarioId: 1) { id nome } }"}'

# Q4 - Músicas de uma playlist
Invoke-RestMethod http://localhost:8002/graphql -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"{ musicasDaPlaylist(playlistId: 1) { id titulo } }"}'

# Q5 - Playlists que contêm uma música
Invoke-RestMethod http://localhost:8002/graphql -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"{ playlistsComMusica(musicaId: 1) { id nome } }"}'
```

---

## 4. gRPC

### Servidor Python (porta 8004)
```powershell
.venv\Scripts\python.exe grpc/python/server.py
```

### Servidor TypeScript (porta 8005)
```powershell
cd grpc/typescript
npx ts-node src/server.ts
```

### Client Python
```powershell
.venv\Scripts\python.exe grpc/python/client.py
```

### Client TypeScript
```powershell
cd grpc/typescript
npx ts-node src/client.ts
```

> **Nota:** gRPC usa protocolo binário (Protobuf) sobre HTTP/2.
> O contrato está em `grpc/streaming.proto`.

---

## 5. SOAP

### Servidor Python (porta 8006)
```powershell
.venv\Scripts\python.exe soap/python/server.py
```

### Servidor TypeScript (porta 8007)
```powershell
cd soap/typescript
npx ts-node src/server.ts
```

### Client Python
```powershell
.venv\Scripts\python.exe soap/python/client.py
```

### Client TypeScript
```powershell
cd soap/typescript
npx ts-node src/client.ts
```

---

## 6. Verificações rápidas

```powershell
# Ver quais servidores estão rodando
netstat -an | findstr "LISTENING" | findstr ":800"

# Testar REST rapidamente
Invoke-RestMethod http://localhost:8000/usuarios | Select-Object -First 3

# Testar GraphQL rapidamente
(Invoke-RestMethod http://localhost:8002/graphql -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"{ musicas { id titulo } }"}').data.musicas | Select-Object -First 3
```

---

## 7. Testes de Carga

```powershell
# Abrir relatório visual com gráficos
Start-Process "load-tests\results\relatorio.html"

# Rodar Locust manualmente (exemplo REST LEVE)
.venv\Scripts\locust -f load-tests/locust_rest.py --headless `
  -u 10 -r 2 --run-time 60s `
  --csv=load-tests/results/rest_leve `
  --host=http://localhost:8000

# Benchmark gRPC (asyncio puro)
.venv\Scripts\python.exe load-tests/bench_grpc.py `
  --users 10 --run-time 60 --csv load-tests/results/grpc_leve
```

---

## 8. Encerrar tudo

```powershell
# Parar o container do banco
docker stop streaming-pg

# Remover o container (apaga os dados)
docker rm streaming-pg
```
