"""
locust_grpc.py — Teste de carga gRPC (grpclib Python porta 8004)

grpclib é asyncio; Locust é gevent.  Solução canônica:
  gevent.get_hub().threadpool.apply(asyncio.run, (coro,))
Cada chamada abre/fecha um canal HTTP/2 em um OS thread do threadpool do gevent.
O greenlet fica suspenso e o hub continua rodando enquanto o thread trabalha.
"""

import asyncio
import random
import sys
import os
import time

import gevent

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../grpc/python"))

from grpclib.client import Channel
from streaming import (
    UsuarioServiceStub,
    MusicaServiceStub,
    PlaylistServiceStub,
)

from locust import User, task, between

HOST = "localhost"
PORT = 8004


class GRPCUser(User):
    wait_time = between(0.05, 0.3)

    def _call(self, name: str, make_coro):
        """
        make_coro(u, m, p) → coroutine
        Executa num OS thread real via threadpool do gevent usando asyncio.run().
        """
        start = time.perf_counter()
        exc = None
        try:
            async def run():
                async with Channel(HOST, PORT) as ch:
                    u = UsuarioServiceStub(ch)
                    m = MusicaServiceStub(ch)
                    p = PlaylistServiceStub(ch)
                    return await make_coro(u, m, p)

            gevent.get_hub().threadpool.apply(asyncio.run, (run(),))
        except Exception as e:
            exc = e
        elapsed = int((time.perf_counter() - start) * 1000)
        self.environment.events.request.fire(
            request_type="gRPC",
            name=name,
            response_time=elapsed,
            response_length=0,
            exception=exc,
            context=self,
        )

    @task(3)
    def q1_listar_usuarios(self):
        self._call("Q1 ListarUsuarios",
                   lambda u, m, p: u.listar_usuarios())

    @task(3)
    def q2_listar_musicas(self):
        self._call("Q2 ListarMusicas",
                   lambda u, m, p: m.listar_musicas())

    @task(2)
    def q3_playlists_do_usuario(self):
        uid = random.randint(1, 500)
        self._call("Q3 PlaylistsDoUsuario",
                   lambda u, m, p: p.playlists_do_usuario(usuario_id=uid))

    @task(2)
    def q4_musicas_da_playlist(self):
        pid = random.randint(1, 300)
        self._call("Q4 MusicasDaPlaylist",
                   lambda u, m, p: p.musicas_da_playlist(playlist_id=pid))

    @task(1)
    def q5_playlists_com_musica(self):
        mid = random.randint(1, 500)
        self._call("Q5 PlaylistsComMusica",
                   lambda u, m, p: p.playlists_com_musica(musica_id=mid))
