"""
client.py — Cliente de demonstração GraphQL (Python / httpx)
Cobre: Q1-Q5, criar/atualizar/remover Usuario, Musica e Playlist.

Uso:
    python graphql/python/client.py
    (servidor deve estar em http://localhost:8002/graphql)
"""

import httpx, json, sys

URL = "http://localhost:8002/graphql"


def gql(query: str, variables: dict = {}):
    r = httpx.post(URL, json={"query": query, "variables": variables}, timeout=15)
    data = r.json()
    if "errors" in data:
        print("ERRO GraphQL:", data["errors"])
        sys.exit(1)
    return data["data"]


def titulo(t: str):
    print(f"\n{'='*55}\n  {t}\n{'='*55}")


# ---- Criar usuario ----
titulo("criar_usuario")
d = gql("""
mutation CriarUsuario($nome: String!, $email: String!) {
  criarUsuario(dados: { nome: $nome, email: $email }) {
    id nome email criadoEm
  }
}
""", {"nome": "Carla Souza", "email": "carla@demo.com"})
print(json.dumps(d, ensure_ascii=False, indent=2))
uid = d["criarUsuario"]["id"]

# ---- Q1 Listar usuarios ----
titulo("Q1 - usuarios")
d = gql("{ usuarios { id nome email } }")
print(f"Total: {len(d['usuarios'])} usuarios")

# ---- Criar musica ----
titulo("criar_musica")
d = gql("""
mutation CriarMusica($titulo: String!, $artista: String!) {
  criarMusica(dados: { titulo: $titulo, artista: $artista, anoLancamento: 1999, duracaoSegundos: 200 }) {
    id titulo artista anoLancamento
  }
}
""", {"titulo": "Como Nossos Pais", "artista": "Elis Regina"})
print(json.dumps(d, ensure_ascii=False, indent=2))
mid = d["criarMusica"]["id"]

# ---- Q2 Listar musicas ----
titulo("Q2 - musicas")
d = gql("{ musicas { id titulo artista } }")
print(f"Total: {len(d['musicas'])} musicas")

# ---- Criar playlist ----
titulo("criar_playlist")
d = gql("""
mutation CriarPlaylist($nome: String!, $usuarioId: Int!) {
  criarPlaylist(dados: { nome: $nome, usuarioId: $usuarioId }) {
    id nome usuarioId
  }
}
""", {"nome": "Clássicos BR", "usuarioId": uid})
print(json.dumps(d, ensure_ascii=False, indent=2))
pid = d["criarPlaylist"]["id"]

# ---- Adicionar musica na playlist ----
titulo("adicionar_musica_na_playlist")
d = gql("""
mutation($pid: Int!, $mid: Int!) {
  adicionarMusicaNaPlaylist(playlistId: $pid, musicaId: $mid)
}
""", {"pid": pid, "mid": mid})
print("ok:", d["adicionarMusicaNaPlaylist"])

# ---- Q3 Playlists do usuario ----
titulo("Q3 - playlists_do_usuario")
d = gql("query($uid: Int!) { playlistsDoUsuario(usuarioId: $uid) { id nome } }",
        {"uid": uid})
print(json.dumps(d, ensure_ascii=False, indent=2))

# ---- Q4 Musicas da playlist ----
titulo("Q4 - musicas_da_playlist")
d = gql("query($pid: Int!) { musicasDaPlaylist(playlistId: $pid) { id titulo } }",
        {"pid": pid})
print(json.dumps(d, ensure_ascii=False, indent=2))

# ---- Q5 Playlists com musica ----
titulo("Q5 - playlists_com_musica")
d = gql("query($mid: Int!) { playlistsComMusica(musicaId: $mid) { id nome } }",
        {"mid": mid})
print(json.dumps(d, ensure_ascii=False, indent=2))

# ---- Atualizar usuario ----
titulo("atualizar_usuario")
d = gql("""
mutation($id: Int!) {
  atualizarUsuario(id: $id, dados: { nome: "Carla Lima" }) { id nome }
}
""", {"id": uid})
print(json.dumps(d, ensure_ascii=False, indent=2))

# ---- Remover musica da playlist ----
titulo("remover_musica_da_playlist")
d = gql("mutation($pid: Int!, $mid: Int!) { removerMusicaDaPlaylist(playlistId: $pid, musicaId: $mid) }",
        {"pid": pid, "mid": mid})
print("ok:", d["removerMusicaDaPlaylist"])

# ---- Remover playlist ----
titulo("remover_playlist")
d = gql("mutation($id: Int!) { removerPlaylist(id: $id) }", {"id": pid})
print("ok:", d["removerPlaylist"])

# ---- Remover musica ----
titulo("remover_musica")
d = gql("mutation($id: Int!) { removerMusica(id: $id) }", {"id": mid})
print("ok:", d["removerMusica"])

# ---- Remover usuario ----
titulo("remover_usuario")
d = gql("mutation($id: Int!) { removerUsuario(id: $id) }", {"id": uid})
print("ok:", d["removerUsuario"])

print("\nDemo GraphQL Python concluida com sucesso!")
