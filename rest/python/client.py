"""
client.py — Cliente de demonstracao REST (Python / httpx)

Demonstra todas as operacoes do contrato (U1-U5, M1-M5, P1-P7, Q1-Q5).

Uso:
    python rest/python/client.py
    (o servidor deve estar rodando em http://localhost:8000)
"""

import httpx
import json
import sys

BASE = "http://localhost:8000"


def titulo(texto):
    print(f"\n{'=' * 55}")
    print(f"  {texto}")
    print("=" * 55)


def exibir(resp):
    try:
        data = resp.json()
        if isinstance(data, list):
            print(f"[{len(data)} itens] primeiro: {json.dumps(data[0], ensure_ascii=False) if data else 'vazio'}")
        else:
            print(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception:
        print(resp.text[:300])
    print(f"→ HTTP {resp.status_code}")


client = httpx.Client(base_url=BASE, timeout=15.0)

# ------------------------------------------------------------------
# U1 - Criar usuario
# ------------------------------------------------------------------
titulo("U1 - Criar usuario")
r = client.post("/usuarios", json={"nome": "Ana Silva", "email": "ana@demo.com"})
exibir(r)
usuario_id = r.json()["id"] if r.is_success else None
if not usuario_id:
    print("Erro ao criar usuario. O servidor esta rodando?")
    sys.exit(1)

# ------------------------------------------------------------------
# U2 / Q1 - Listar todos os usuarios
# ------------------------------------------------------------------
titulo("U2/Q1 - Listar todos os usuarios")
r = client.get("/usuarios")
data = r.json()
print(f"Total: {len(data)} usuarios  → HTTP {r.status_code}")

# ------------------------------------------------------------------
# U3 - Buscar usuario por ID
# ------------------------------------------------------------------
titulo(f"U3 - Buscar usuario id={usuario_id}")
r = client.get(f"/usuarios/{usuario_id}")
exibir(r)

# ------------------------------------------------------------------
# M1 - Criar musica
# ------------------------------------------------------------------
titulo("M1 - Criar musica")
r = client.post("/musicas", json={
    "titulo": "Aquarela",
    "artista": "Toquinho",
    "ano_lancamento": 1983,
    "duracao_segundos": 212,
})
exibir(r)
musica_id = r.json()["id"] if r.is_success else None

# ------------------------------------------------------------------
# M2 / Q2 - Listar todas as musicas
# ------------------------------------------------------------------
titulo("M2/Q2 - Listar todas as musicas")
r = client.get("/musicas")
print(f"Total: {len(r.json())} musicas  → HTTP {r.status_code}")

# ------------------------------------------------------------------
# P1 - Criar playlist
# ------------------------------------------------------------------
titulo(f"P1 - Criar playlist para usuario id={usuario_id}")
r = client.post("/playlists", json={"nome": "Minha Playlist", "usuario_id": usuario_id})
exibir(r)
playlist_id = r.json()["id"] if r.is_success else None

# ------------------------------------------------------------------
# P6 - Adicionar musica na playlist
# ------------------------------------------------------------------
titulo(f"P6 - Adicionar musica id={musica_id} na playlist id={playlist_id}")
r = client.post(f"/playlists/{playlist_id}/musicas", json={"musica_id": musica_id})
print(f"→ HTTP {r.status_code}")

# ------------------------------------------------------------------
# Q3 - Playlists de um usuario
# ------------------------------------------------------------------
titulo(f"Q3 - Playlists do usuario id={usuario_id}")
r = client.get(f"/usuarios/{usuario_id}/playlists")
exibir(r)

# ------------------------------------------------------------------
# Q4 - Musicas de uma playlist
# ------------------------------------------------------------------
titulo(f"Q4 - Musicas da playlist id={playlist_id}")
r = client.get(f"/playlists/{playlist_id}/musicas")
exibir(r)

# ------------------------------------------------------------------
# Q5 - Playlists que contem uma musica
# ------------------------------------------------------------------
titulo(f"Q5 - Playlists que contem musica id={musica_id}")
r = client.get(f"/musicas/{musica_id}/playlists")
exibir(r)

# ------------------------------------------------------------------
# U4 - Atualizar usuario
# ------------------------------------------------------------------
titulo(f"U4 - Atualizar usuario id={usuario_id}")
r = client.put(f"/usuarios/{usuario_id}", json={"nome": "Ana Costa"})
exibir(r)

# ------------------------------------------------------------------
# P4 - Atualizar playlist
# ------------------------------------------------------------------
titulo(f"P4 - Atualizar playlist id={playlist_id}")
r = client.put(f"/playlists/{playlist_id}", json={"nome": "Playlist Atualizada"})
exibir(r)

# ------------------------------------------------------------------
# P7 - Remover musica da playlist
# ------------------------------------------------------------------
titulo(f"P7 - Remover musica id={musica_id} da playlist id={playlist_id}")
r = client.delete(f"/playlists/{playlist_id}/musicas/{musica_id}")
print(f"→ HTTP {r.status_code}")

# ------------------------------------------------------------------
# P5 - Remover playlist
# ------------------------------------------------------------------
titulo(f"P5 - Remover playlist id={playlist_id}")
r = client.delete(f"/playlists/{playlist_id}")
print(f"→ HTTP {r.status_code}")

# ------------------------------------------------------------------
# M5 - Remover musica
# ------------------------------------------------------------------
titulo(f"M5 - Remover musica id={musica_id}")
r = client.delete(f"/musicas/{musica_id}")
print(f"→ HTTP {r.status_code}")

# ------------------------------------------------------------------
# U5 - Remover usuario
# ------------------------------------------------------------------
titulo(f"U5 - Remover usuario id={usuario_id}")
r = client.delete(f"/usuarios/{usuario_id}")
print(f"→ HTTP {r.status_code}")

print("\nDemo concluida com sucesso!")
client.close()
