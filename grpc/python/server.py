"""
server.py — Servidor gRPC Python usando grpclib (puro Python / asyncio)
         e betterproto para serialização protobuf.
Porta: 8004
"""

import asyncio
import os
import sys

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from grpclib.const import Cardinality, Handler
from grpclib.server import Server

import streaming as s  # stubs gerados pelo betterproto

load_dotenv()
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/streaming",
)


# ─── DB helper ────────────────────────────────────────────────────────────────
def _db_exec(sql, params=None):
    """Executa SQL em thread separada; retorna lista de RealDictRow ou []."""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, params)
                return cur.fetchall() if cur.description else []
    finally:
        conn.close()


async def db(sql, params=None):
    return await asyncio.to_thread(_db_exec, sql, params)


# ─── UsuarioService ───────────────────────────────────────────────────────────
class UsuarioServicer:
    async def criar_usuario(self, stream):
        req: s.CriarUsuarioRequest = await stream.recv_message()
        rows = await db("INSERT INTO usuarios (nome, email) VALUES (%s,%s) RETURNING *",
                        (req.nome, req.email))
        r = rows[0]
        await stream.send_message(s.Usuario(id=r["id"], nome=r["nome"], email=r["email"], criado_em=str(r["criado_em"])))

    async def obter_usuario(self, stream):
        req: s.IdRequest = await stream.recv_message()
        rows = await db("SELECT * FROM usuarios WHERE id=%s", (req.id,))
        if not rows:
            await stream.send_message(s.Usuario())
            return
        r = rows[0]
        await stream.send_message(s.Usuario(id=r["id"], nome=r["nome"], email=r["email"], criado_em=str(r["criado_em"])))

    async def listar_usuarios(self, stream):  # Q1
        await stream.recv_message()
        rows = await db("SELECT * FROM usuarios ORDER BY id")
        await stream.send_message(s.ListaUsuarios(usuarios=[
            s.Usuario(id=r["id"], nome=r["nome"], email=r["email"], criado_em=str(r["criado_em"])) for r in rows
        ]))

    async def atualizar_usuario(self, stream):
        req: s.AtualizarUsuarioRequest = await stream.recv_message()
        cur = await db("SELECT * FROM usuarios WHERE id=%s", (req.id,))
        if not cur:
            await stream.send_message(s.Usuario())
            return
        a = cur[0]
        rows = await db("UPDATE usuarios SET nome=%s, email=%s WHERE id=%s RETURNING *",
                        (req.nome or a["nome"], req.email or a["email"], req.id))
        r = rows[0]
        await stream.send_message(s.Usuario(id=r["id"], nome=r["nome"], email=r["email"], criado_em=str(r["criado_em"])))

    async def remover_usuario(self, stream):
        req: s.IdRequest = await stream.recv_message()
        rows = await db("DELETE FROM usuarios WHERE id=%s RETURNING id", (req.id,))
        await stream.send_message(s.BoolResponse(ok=len(rows) > 0))

    def __mapping__(self):
        return {
            "/streaming.UsuarioService/CriarUsuario":     Handler(self.criar_usuario,     Cardinality.UNARY_UNARY, s.CriarUsuarioRequest,     s.Usuario),
            "/streaming.UsuarioService/ObterUsuario":      Handler(self.obter_usuario,      Cardinality.UNARY_UNARY, s.IdRequest,               s.Usuario),
            "/streaming.UsuarioService/ListarUsuarios":    Handler(self.listar_usuarios,    Cardinality.UNARY_UNARY, s.Empty,                   s.ListaUsuarios),
            "/streaming.UsuarioService/AtualizarUsuario":  Handler(self.atualizar_usuario,  Cardinality.UNARY_UNARY, s.AtualizarUsuarioRequest,  s.Usuario),
            "/streaming.UsuarioService/RemoverUsuario":    Handler(self.remover_usuario,    Cardinality.UNARY_UNARY, s.IdRequest,               s.BoolResponse),
        }


# ─── MusicaService ────────────────────────────────────────────────────────────
class MusicaServicer:
    async def criar_musica(self, stream):
        req: s.CriarMusicaRequest = await stream.recv_message()
        rows = await db(
            "INSERT INTO musicas (titulo, artista, ano_lancamento, duracao_segundos) VALUES (%s,%s,%s,%s) RETURNING *",
            (req.titulo, req.artista, req.ano_lancamento or None, req.duracao_segundos or None),
        )
        r = rows[0]
        await stream.send_message(s.Musica(id=r["id"], titulo=r["titulo"], artista=r["artista"],
                                            ano_lancamento=r["ano_lancamento"] or 0,
                                            duracao_segundos=r["duracao_segundos"] or 0,
                                            criado_em=str(r["criado_em"])))

    async def obter_musica(self, stream):
        req: s.IdRequest = await stream.recv_message()
        rows = await db("SELECT * FROM musicas WHERE id=%s", (req.id,))
        if not rows:
            await stream.send_message(s.Musica())
            return
        r = rows[0]
        await stream.send_message(s.Musica(id=r["id"], titulo=r["titulo"], artista=r["artista"],
                                            ano_lancamento=r["ano_lancamento"] or 0,
                                            duracao_segundos=r["duracao_segundos"] or 0,
                                            criado_em=str(r["criado_em"])))

    async def listar_musicas(self, stream):  # Q2
        await stream.recv_message()
        rows = await db("SELECT * FROM musicas ORDER BY id")
        await stream.send_message(s.ListaMusicas(musicas=[
            s.Musica(id=r["id"], titulo=r["titulo"], artista=r["artista"],
                     ano_lancamento=r["ano_lancamento"] or 0,
                     duracao_segundos=r["duracao_segundos"] or 0,
                     criado_em=str(r["criado_em"])) for r in rows
        ]))

    async def atualizar_musica(self, stream):
        req: s.AtualizarMusicaRequest = await stream.recv_message()
        cur = await db("SELECT * FROM musicas WHERE id=%s", (req.id,))
        if not cur:
            await stream.send_message(s.Musica())
            return
        a = cur[0]
        rows = await db(
            "UPDATE musicas SET titulo=%s, artista=%s, ano_lancamento=%s, duracao_segundos=%s WHERE id=%s RETURNING *",
            (req.titulo or a["titulo"], req.artista or a["artista"],
             req.ano_lancamento or a["ano_lancamento"], req.duracao_segundos or a["duracao_segundos"], req.id),
        )
        r = rows[0]
        await stream.send_message(s.Musica(id=r["id"], titulo=r["titulo"], artista=r["artista"],
                                            ano_lancamento=r["ano_lancamento"] or 0,
                                            duracao_segundos=r["duracao_segundos"] or 0,
                                            criado_em=str(r["criado_em"])))

    async def remover_musica(self, stream):
        req: s.IdRequest = await stream.recv_message()
        rows = await db("DELETE FROM musicas WHERE id=%s RETURNING id", (req.id,))
        await stream.send_message(s.BoolResponse(ok=len(rows) > 0))

    def __mapping__(self):
        return {
            "/streaming.MusicaService/CriarMusica":     Handler(self.criar_musica,    Cardinality.UNARY_UNARY, s.CriarMusicaRequest,     s.Musica),
            "/streaming.MusicaService/ObterMusica":      Handler(self.obter_musica,    Cardinality.UNARY_UNARY, s.IdRequest,              s.Musica),
            "/streaming.MusicaService/ListarMusicas":    Handler(self.listar_musicas,  Cardinality.UNARY_UNARY, s.Empty,                  s.ListaMusicas),
            "/streaming.MusicaService/AtualizarMusica":  Handler(self.atualizar_musica,Cardinality.UNARY_UNARY, s.AtualizarMusicaRequest,  s.Musica),
            "/streaming.MusicaService/RemoverMusica":    Handler(self.remover_musica,  Cardinality.UNARY_UNARY, s.IdRequest,              s.BoolResponse),
        }


# ─── PlaylistService ──────────────────────────────────────────────────────────
class PlaylistServicer:
    async def criar_playlist(self, stream):
        req: s.CriarPlaylistRequest = await stream.recv_message()
        rows = await db("INSERT INTO playlists (nome, usuario_id) VALUES (%s,%s) RETURNING *",
                        (req.nome, req.usuario_id))
        r = rows[0]
        await stream.send_message(s.Playlist(id=r["id"], nome=r["nome"], usuario_id=r["usuario_id"], criado_em=str(r["criado_em"])))

    async def obter_playlist(self, stream):
        req: s.IdRequest = await stream.recv_message()
        rows = await db("SELECT * FROM playlists WHERE id=%s", (req.id,))
        if not rows:
            await stream.send_message(s.Playlist())
            return
        r = rows[0]
        await stream.send_message(s.Playlist(id=r["id"], nome=r["nome"], usuario_id=r["usuario_id"], criado_em=str(r["criado_em"])))

    async def listar_playlists(self, stream):
        await stream.recv_message()
        rows = await db("SELECT * FROM playlists ORDER BY id")
        await stream.send_message(s.ListaPlaylists(playlists=[
            s.Playlist(id=r["id"], nome=r["nome"], usuario_id=r["usuario_id"], criado_em=str(r["criado_em"])) for r in rows
        ]))

    async def atualizar_playlist(self, stream):
        req: s.AtualizarPlaylistRequest = await stream.recv_message()
        rows = await db("UPDATE playlists SET nome=%s WHERE id=%s RETURNING *", (req.nome, req.id))
        if not rows:
            await stream.send_message(s.Playlist())
            return
        r = rows[0]
        await stream.send_message(s.Playlist(id=r["id"], nome=r["nome"], usuario_id=r["usuario_id"], criado_em=str(r["criado_em"])))

    async def remover_playlist(self, stream):
        req: s.IdRequest = await stream.recv_message()
        rows = await db("DELETE FROM playlists WHERE id=%s RETURNING id", (req.id,))
        await stream.send_message(s.BoolResponse(ok=len(rows) > 0))

    async def adicionar_musica(self, stream):
        req: s.PlaylistMusicaRequest = await stream.recv_message()
        await db("INSERT INTO playlist_musicas (playlist_id, musica_id) VALUES (%s,%s) ON CONFLICT DO NOTHING",
                 (req.playlist_id, req.musica_id))
        await stream.send_message(s.BoolResponse(ok=True))

    async def remover_musica(self, stream):
        req: s.PlaylistMusicaRequest = await stream.recv_message()
        rows = await db("DELETE FROM playlist_musicas WHERE playlist_id=%s AND musica_id=%s RETURNING playlist_id",
                        (req.playlist_id, req.musica_id))
        await stream.send_message(s.BoolResponse(ok=len(rows) > 0))

    async def playlists_do_usuario(self, stream):  # Q3
        req: s.UsuarioIdRequest = await stream.recv_message()
        rows = await db("SELECT * FROM playlists WHERE usuario_id=%s ORDER BY id", (req.usuario_id,))
        await stream.send_message(s.ListaPlaylists(playlists=[
            s.Playlist(id=r["id"], nome=r["nome"], usuario_id=r["usuario_id"], criado_em=str(r["criado_em"])) for r in rows
        ]))

    async def musicas_da_playlist(self, stream):  # Q4
        req: s.PlaylistIdRequest = await stream.recv_message()
        rows = await db(
            "SELECT m.* FROM musicas m JOIN playlist_musicas pm ON m.id=pm.musica_id WHERE pm.playlist_id=%s ORDER BY m.id",
            (req.playlist_id,),
        )
        await stream.send_message(s.ListaMusicas(musicas=[
            s.Musica(id=r["id"], titulo=r["titulo"], artista=r["artista"],
                     ano_lancamento=r["ano_lancamento"] or 0,
                     duracao_segundos=r["duracao_segundos"] or 0,
                     criado_em=str(r["criado_em"])) for r in rows
        ]))

    async def playlists_com_musica(self, stream):  # Q5
        req: s.MusicaIdRequest = await stream.recv_message()
        rows = await db(
            "SELECT p.* FROM playlists p JOIN playlist_musicas pm ON p.id=pm.playlist_id WHERE pm.musica_id=%s ORDER BY p.id",
            (req.musica_id,),
        )
        await stream.send_message(s.ListaPlaylists(playlists=[
            s.Playlist(id=r["id"], nome=r["nome"], usuario_id=r["usuario_id"], criado_em=str(r["criado_em"])) for r in rows
        ]))

    def __mapping__(self):
        return {
            "/streaming.PlaylistService/CriarPlaylist":      Handler(self.criar_playlist,      Cardinality.UNARY_UNARY, s.CriarPlaylistRequest,     s.Playlist),
            "/streaming.PlaylistService/ObterPlaylist":       Handler(self.obter_playlist,       Cardinality.UNARY_UNARY, s.IdRequest,               s.Playlist),
            "/streaming.PlaylistService/ListarPlaylists":     Handler(self.listar_playlists,     Cardinality.UNARY_UNARY, s.Empty,                   s.ListaPlaylists),
            "/streaming.PlaylistService/AtualizarPlaylist":   Handler(self.atualizar_playlist,   Cardinality.UNARY_UNARY, s.AtualizarPlaylistRequest, s.Playlist),
            "/streaming.PlaylistService/RemoverPlaylist":     Handler(self.remover_playlist,     Cardinality.UNARY_UNARY, s.IdRequest,               s.BoolResponse),
            "/streaming.PlaylistService/AdicionarMusica":     Handler(self.adicionar_musica,     Cardinality.UNARY_UNARY, s.PlaylistMusicaRequest,   s.BoolResponse),
            "/streaming.PlaylistService/RemoverMusica":       Handler(self.remover_musica,       Cardinality.UNARY_UNARY, s.PlaylistMusicaRequest,   s.BoolResponse),
            "/streaming.PlaylistService/PlaylistsDoUsuario":  Handler(self.playlists_do_usuario, Cardinality.UNARY_UNARY, s.UsuarioIdRequest,        s.ListaPlaylists),
            "/streaming.PlaylistService/MusicasDaPlaylist":   Handler(self.musicas_da_playlist,  Cardinality.UNARY_UNARY, s.PlaylistIdRequest,       s.ListaMusicas),
            "/streaming.PlaylistService/PlaylistsComMusica":  Handler(self.playlists_com_musica, Cardinality.UNARY_UNARY, s.MusicaIdRequest,         s.ListaPlaylists),
        }


# ─── Main ─────────────────────────────────────────────────────────────────────
async def main():
    server = Server([UsuarioServicer(), MusicaServicer(), PlaylistServicer()])
    await server.start("0.0.0.0", 8004)
    print("gRPC Python (grpclib) rodando na porta 8004")
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())



def row_to_musica(r):
    return streaming_pb2.Musica(
        id=r["id"], titulo=r["titulo"], artista=r["artista"],
        ano_lancamento=r["ano_lancamento"] or 0,
        duracao_segundos=r["duracao_segundos"] or 0,
        criado_em=str(r["criado_em"]),
    )


def row_to_playlist(r):
    return streaming_pb2.Playlist(
        id=r["id"], nome=r["nome"], usuario_id=r["usuario_id"],
        criado_em=str(r["criado_em"]),
    )


# ─── UsuarioService ───────────────────────────────────────────────────────────
class UsuarioServicer(streaming_pb2_grpc.UsuarioServiceServicer):

    def CriarUsuario(self, request, context):
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO usuarios (nome, email) VALUES (%s,%s) RETURNING *",
                    (request.nome, request.email),
                )
                return row_to_usuario(cur.fetchone())

    def ObterUsuario(self, request, context):
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM usuarios WHERE id=%s", (request.id,))
                row = cur.fetchone()
        if not row:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return streaming_pb2.Usuario()
        return row_to_usuario(row)

    def ListarUsuarios(self, request, context):  # Q1
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM usuarios ORDER BY id")
                rows = cur.fetchall()
        return streaming_pb2.ListaUsuarios(usuarios=[row_to_usuario(r) for r in rows])

    def AtualizarUsuario(self, request, context):
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM usuarios WHERE id=%s", (request.id,))
                cur_row = cur.fetchone()
                if not cur_row:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    return streaming_pb2.Usuario()
                nome = request.nome or cur_row["nome"]
                email = request.email or cur_row["email"]
                cur.execute(
                    "UPDATE usuarios SET nome=%s, email=%s WHERE id=%s RETURNING *",
                    (nome, email, request.id),
                )
                return row_to_usuario(cur.fetchone())

    def RemoverUsuario(self, request, context):
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM usuarios WHERE id=%s RETURNING id", (request.id,))
                deleted = cur.fetchone()
        return streaming_pb2.BoolResponse(ok=deleted is not None)


# ─── MusicaService ────────────────────────────────────────────────────────────
class MusicaServicer(streaming_pb2_grpc.MusicaServiceServicer):

    def CriarMusica(self, request, context):
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO musicas (titulo, artista, ano_lancamento, duracao_segundos) VALUES (%s,%s,%s,%s) RETURNING *",
                    (request.titulo, request.artista,
                     request.ano_lancamento or None, request.duracao_segundos or None),
                )
                return row_to_musica(cur.fetchone())

    def ObterMusica(self, request, context):
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM musicas WHERE id=%s", (request.id,))
                row = cur.fetchone()
        if not row:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return streaming_pb2.Musica()
        return row_to_musica(row)

    def ListarMusicas(self, request, context):  # Q2
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM musicas ORDER BY id")
                rows = cur.fetchall()
        return streaming_pb2.ListaMusicas(musicas=[row_to_musica(r) for r in rows])

    def AtualizarMusica(self, request, context):
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM musicas WHERE id=%s", (request.id,))
                cur_row = cur.fetchone()
                if not cur_row:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    return streaming_pb2.Musica()
                titulo = request.titulo or cur_row["titulo"]
                artista = request.artista or cur_row["artista"]
                ano = request.ano_lancamento or cur_row["ano_lancamento"]
                dur = request.duracao_segundos or cur_row["duracao_segundos"]
                cur.execute(
                    "UPDATE musicas SET titulo=%s, artista=%s, ano_lancamento=%s, duracao_segundos=%s WHERE id=%s RETURNING *",
                    (titulo, artista, ano, dur, request.id),
                )
                return row_to_musica(cur.fetchone())

    def RemoverMusica(self, request, context):
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM musicas WHERE id=%s RETURNING id", (request.id,))
                deleted = cur.fetchone()
        return streaming_pb2.BoolResponse(ok=deleted is not None)


# ─── PlaylistService ──────────────────────────────────────────────────────────
class PlaylistServicer(streaming_pb2_grpc.PlaylistServiceServicer):

    def CriarPlaylist(self, request, context):
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO playlists (nome, usuario_id) VALUES (%s,%s) RETURNING *",
                    (request.nome, request.usuario_id),
                )
                return row_to_playlist(cur.fetchone())

    def ObterPlaylist(self, request, context):
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM playlists WHERE id=%s", (request.id,))
                row = cur.fetchone()
        if not row:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return streaming_pb2.Playlist()
        return row_to_playlist(row)

    def ListarPlaylists(self, request, context):
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM playlists ORDER BY id")
                rows = cur.fetchall()
        return streaming_pb2.ListaPlaylists(playlists=[row_to_playlist(r) for r in rows])

    def AtualizarPlaylist(self, request, context):
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "UPDATE playlists SET nome=%s WHERE id=%s RETURNING *",
                    (request.nome, request.id),
                )
                row = cur.fetchone()
        if not row:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return streaming_pb2.Playlist()
        return row_to_playlist(row)

    def RemoverPlaylist(self, request, context):
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM playlists WHERE id=%s RETURNING id", (request.id,))
                deleted = cur.fetchone()
        return streaming_pb2.BoolResponse(ok=deleted is not None)

    def AdicionarMusica(self, request, context):
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO playlist_musicas (playlist_id, musica_id) VALUES (%s,%s) ON CONFLICT DO NOTHING",
                    (request.playlist_id, request.musica_id),
                )
        return streaming_pb2.BoolResponse(ok=True)

    def RemoverMusica(self, request, context):
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM playlist_musicas WHERE playlist_id=%s AND musica_id=%s RETURNING playlist_id",
                    (request.playlist_id, request.musica_id),
                )
                deleted = cur.fetchone()
        return streaming_pb2.BoolResponse(ok=deleted is not None)

    def PlaylistsDoUsuario(self, request, context):  # Q3
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM playlists WHERE usuario_id=%s ORDER BY id",
                    (request.usuario_id,),
                )
                rows = cur.fetchall()
        return streaming_pb2.ListaPlaylists(playlists=[row_to_playlist(r) for r in rows])

    def MusicasDaPlaylist(self, request, context):  # Q4
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT m.* FROM musicas m "
                    "JOIN playlist_musicas pm ON m.id=pm.musica_id "
                    "WHERE pm.playlist_id=%s ORDER BY m.id",
                    (request.playlist_id,),
                )
                rows = cur.fetchall()
        return streaming_pb2.ListaMusicas(musicas=[row_to_musica(r) for r in rows])

    def PlaylistsComMusica(self, request, context):  # Q5
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT p.* FROM playlists p "
                    "JOIN playlist_musicas pm ON p.id=pm.playlist_id "
                    "WHERE pm.musica_id=%s ORDER BY p.id",
                    (request.musica_id,),
                )
                rows = cur.fetchall()
        return streaming_pb2.ListaPlaylists(playlists=[row_to_playlist(r) for r in rows])


# ─── Main ─────────────────────────────────────────────────────────────────────
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    streaming_pb2_grpc.add_UsuarioServiceServicer_to_server(UsuarioServicer(), server)
    streaming_pb2_grpc.add_MusicaServiceServicer_to_server(MusicaServicer(), server)
    streaming_pb2_grpc.add_PlaylistServiceServicer_to_server(PlaylistServicer(), server)
    server.add_insecure_port("[::]:8004")
    server.start()
    print("gRPC Python rodando na porta 8004")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
