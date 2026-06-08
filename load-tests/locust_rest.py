"""
locust_rest.py — Teste de carga REST (FastAPI Python porta 8000)
Operacoes testadas: Q1-Q5 (listar_usuarios, listar_musicas,
playlists_do_usuario, musicas_da_playlist, playlists_com_musica)
"""

import random
from locust import HttpUser, task, between


class RESTUser(HttpUser):
    host = "http://localhost:8000"
    wait_time = between(0.05, 0.3)

    @task(3)
    def q1_listar_usuarios(self):
        self.client.get("/usuarios", name="Q1 GET /usuarios")

    @task(3)
    def q2_listar_musicas(self):
        self.client.get("/musicas", name="Q2 GET /musicas")

    @task(2)
    def q3_playlists_do_usuario(self):
        uid = random.randint(1, 500)
        self.client.get(f"/usuarios/{uid}/playlists", name="Q3 GET /usuarios/[id]/playlists")

    @task(2)
    def q4_musicas_da_playlist(self):
        pid = random.randint(1, 300)
        self.client.get(f"/playlists/{pid}/musicas", name="Q4 GET /playlists/[id]/musicas")

    @task(1)
    def q5_playlists_com_musica(self):
        mid = random.randint(1, 500)
        self.client.get(f"/musicas/{mid}/playlists", name="Q5 GET /musicas/[id]/playlists")
