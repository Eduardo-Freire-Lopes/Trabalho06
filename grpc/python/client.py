"""
client.py — Cliente gRPC Python usando grpclib + betterproto stubs
Cobre: Q1-Q5 + CRUD completo de Usuario, Musica e Playlist.
Uso: python client.py  (servidor deve estar em localhost:8004)
"""

import asyncio
from grpclib.client import Channel
from streaming import (
    UsuarioServiceStub, MusicaServiceStub, PlaylistServiceStub,
)

ADDR = ("localhost", 8004)


def titulo(t: str):
    print(f"\n{'='*55}\n  {t}\n{'='*55}")


async def main():
    async with Channel(*ADDR) as ch:
        u = UsuarioServiceStub(ch)
        m = MusicaServiceStub(ch)
        p = PlaylistServiceStub(ch)

        # criar_usuario
        titulo("CriarUsuario")
        usuario = await u.criar_usuario(nome="Ana gRPC", email="ana@grpc.com")
        print(f"Criado: id={usuario.id} nome={usuario.nome}")

        # Q1
        titulo("Q1 - ListarUsuarios")
        lu = await u.listar_usuarios()
        print(f"Total: {len(lu.usuarios)} usuarios")

        # atualizar_usuario
        titulo("AtualizarUsuario")
        u2 = await u.atualizar_usuario(id=usuario.id, nome="Ana gRPC Atualizada")
        print(f"Atualizado: nome={u2.nome}")

        # criar_musica
        titulo("CriarMusica")
        musica = await m.criar_musica(titulo="Garota de Ipanema", artista="Tom Jobim",
                                      ano_lancamento=1962, duracao_segundos=270)
        print(f"Criada: id={musica.id} titulo={musica.titulo}")

        # Q2
        titulo("Q2 - ListarMusicas")
        lm = await m.listar_musicas()
        print(f"Total: {len(lm.musicas)} musicas")

        # criar_playlist
        titulo("CriarPlaylist")
        playlist = await p.criar_playlist(nome="Bossa Nova gRPC", usuario_id=usuario.id)
        print(f"Criada: id={playlist.id} nome={playlist.nome}")

        # adicionar_musica
        titulo("AdicionarMusica")
        r = await p.adicionar_musica(playlist_id=playlist.id, musica_id=musica.id)
        print(f"ok={r.ok}")

        # Q3
        titulo("Q3 - PlaylistsDoUsuario")
        q3 = await p.playlists_do_usuario(usuario_id=usuario.id)
        print(f"Playlists: {[pl.nome for pl in q3.playlists]}")

        # Q4
        titulo("Q4 - MusicasDaPlaylist")
        q4 = await p.musicas_da_playlist(playlist_id=playlist.id)
        print(f"Musicas: {[ms.titulo for ms in q4.musicas]}")

        # Q5
        titulo("Q5 - PlaylistsComMusica")
        q5 = await p.playlists_com_musica(musica_id=musica.id)
        print(f"Playlists: {[pl.nome for pl in q5.playlists]}")

        # remover_musica da playlist
        titulo("RemoverMusica (da playlist)")
        r = await p.remover_musica(playlist_id=playlist.id, musica_id=musica.id)
        print(f"ok={r.ok}")

        # remover_playlist
        titulo("RemoverPlaylist")
        r = await p.remover_playlist(id=playlist.id)
        print(f"ok={r.ok}")

        # remover_musica do catálogo
        titulo("RemoverMusica (catalogo)")
        r = await m.remover_musica(id=musica.id)
        print(f"ok={r.ok}")

        # remover_usuario
        titulo("RemoverUsuario")
        r = await u.remover_usuario(id=usuario.id)
        print(f"ok={r.ok}")

    print("\nDemo gRPC Python concluida com sucesso!")


if __name__ == "__main__":
    asyncio.run(main())

