"""
locust_graphql.py — Teste de carga GraphQL (Strawberry+FastAPI Python porta 8002)
"""

import random
from locust import HttpUser, task, between


class GraphQLUser(HttpUser):
    host = "http://localhost:8002"
    wait_time = between(0.05, 0.3)

    def _gql(self, query: str, variables: dict = None, name: str = "gql"):
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        with self.client.post("/graphql", json=payload, name=name, catch_response=True) as r:
            body = r.json()
            if "errors" in body:
                r.failure(str(body["errors"]))

    @task(3)
    def q1_usuarios(self):
        self._gql("{usuarios{id nome email}}", name="Q1 {usuarios}")

    @task(3)
    def q2_musicas(self):
        self._gql("{musicas{id titulo artista}}", name="Q2 {musicas}")

    @task(2)
    def q3_playlists_do_usuario(self):
        uid = random.randint(1, 500)
        self._gql(
            "query($uid:Int!){playlistsDoUsuario(usuarioId:$uid){id nome}}",
            {"uid": uid},
            name="Q3 playlistsDoUsuario",
        )

    @task(2)
    def q4_musicas_da_playlist(self):
        pid = random.randint(1, 300)
        self._gql(
            "query($pid:Int!){musicasDaPlaylist(playlistId:$pid){id titulo}}",
            {"pid": pid},
            name="Q4 musicasDaPlaylist",
        )

    @task(1)
    def q5_playlists_com_musica(self):
        mid = random.randint(1, 500)
        self._gql(
            "query($mid:Int!){playlistsComMusica(musicaId:$mid){id nome}}",
            {"mid": mid},
            name="Q5 playlistsComMusica",
        )
