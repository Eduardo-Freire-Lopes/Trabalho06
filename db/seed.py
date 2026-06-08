"""
seed.py — Popula o banco PostgreSQL com dados ficticios para os testes de carga.

Requisitos:
    pip install faker psycopg2-binary

Uso:
    python db/seed.py

Variaveis de ambiente (ou edite DATABASE_URL abaixo):
    DATABASE_URL=postgresql://usuario:senha@localhost:5432/streaming
"""

import os
import random
import psycopg2
from faker import Faker

# ------------------------------------------------------------------
# Configuracao
# ------------------------------------------------------------------
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/streaming"
)

NUM_USUARIOS  = 500
NUM_MUSICAS   = 500
NUM_PLAYLISTS = 300   # distribuidas entre os usuarios
MAX_MUSICAS_POR_PLAYLIST = 20

fake = Faker("pt_BR")

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def criar_usuarios(cur, n):
    emails = set()
    rows = []
    while len(rows) < n:
        email = fake.unique.email()
        if email not in emails:
            emails.add(email)
            rows.append((fake.name(), email))
    cur.executemany(
        "INSERT INTO usuarios (nome, email) VALUES (%s, %s) ON CONFLICT DO NOTHING",
        rows
    )
    cur.execute("SELECT id FROM usuarios ORDER BY id")
    return [r[0] for r in cur.fetchall()]


def criar_musicas(cur, n):
    generos  = ["Rock", "Pop", "MPB", "Samba", "Forró", "Jazz", "Classical", "Hip-Hop", "Eletrônico"]
    artistas = [fake.name() for _ in range(80)]
    rows = [
        (
            fake.catch_phrase(),          # titulo criativo
            random.choice(artistas),
            random.randint(1960, 2025),
            random.randint(120, 360),
        )
        for _ in range(n)
    ]
    cur.executemany(
        "INSERT INTO musicas (titulo, artista, ano_lancamento, duracao_segundos) VALUES (%s, %s, %s, %s)",
        rows
    )
    cur.execute("SELECT id FROM musicas ORDER BY id")
    return [r[0] for r in cur.fetchall()]


def criar_playlists(cur, usuario_ids, musica_ids, n):
    playlist_rows = [
        (fake.bs().title(), random.choice(usuario_ids))
        for _ in range(n)
    ]
    cur.executemany(
        "INSERT INTO playlists (nome, usuario_id) VALUES (%s, %s)",
        playlist_rows
    )
    cur.execute("SELECT id FROM playlists ORDER BY id")
    playlist_ids = [r[0] for r in cur.fetchall()]

    assoc = set()
    for pid in playlist_ids:
        qtd = random.randint(3, MAX_MUSICAS_POR_PLAYLIST)
        for mid in random.sample(musica_ids, min(qtd, len(musica_ids))):
            assoc.add((pid, mid))

    cur.executemany(
        "INSERT INTO playlist_musicas (playlist_id, musica_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
        list(assoc)
    )


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main():
    print(f"Conectando em {DATABASE_URL} ...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    cur = conn.cursor()

    try:
        print(f"Inserindo {NUM_USUARIOS} usuarios ...")
        usuario_ids = criar_usuarios(cur, NUM_USUARIOS)

        print(f"Inserindo {NUM_MUSICAS} musicas ...")
        musica_ids = criar_musicas(cur, NUM_MUSICAS)

        print(f"Inserindo {NUM_PLAYLISTS} playlists com musicas ...")
        criar_playlists(cur, usuario_ids, musica_ids, NUM_PLAYLISTS)

        conn.commit()
        print("Seed concluido com sucesso!")
        print(f"  usuarios : {len(usuario_ids)}")
        print(f"  musicas  : {len(musica_ids)}")
        print(f"  playlists: {NUM_PLAYLISTS}")

    except Exception as exc:
        conn.rollback()
        print(f"Erro durante o seed: {exc}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
