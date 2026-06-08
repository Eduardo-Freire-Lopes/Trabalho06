"""
locust_soap.py — Teste de carga SOAP (servidor Python manual porta 8006)
"""

import random
from locust import HttpUser, task, between

NS = "http://streaming.local/"
SOAP_ENV = "http://schemas.xmlsoap.org/soap/envelope/"


def _envelope(action: str, **kwargs) -> bytes:
    fields = "".join(f"<{k}>{v}</{k}>" for k, v in kwargs.items())
    xml = (
        f'<?xml version="1.0" encoding="utf-8"?>'
        f'<soapenv:Envelope xmlns:soapenv="{SOAP_ENV}" xmlns:tns="{NS}">'
        f"<soapenv:Body><tns:{action}>{fields}</tns:{action}></soapenv:Body>"
        f"</soapenv:Envelope>"
    )
    return xml.encode()


HEADERS = {"Content-Type": "text/xml; charset=utf-8"}


class SOAPUser(HttpUser):
    host = "http://localhost:8006"
    wait_time = between(0.05, 0.3)

    def _soap(self, action: str, name: str = None, **kwargs):
        self.client.post(
            "/",
            data=_envelope(action, **kwargs),
            headers=HEADERS,
            name=name or action,
        )

    @task(3)
    def q1_listar_usuarios(self):
        self._soap("listar_usuarios", name="Q1 listar_usuarios")

    @task(3)
    def q2_listar_musicas(self):
        self._soap("listar_musicas", name="Q2 listar_musicas")

    @task(2)
    def q3_playlists_do_usuario(self):
        self._soap("playlists_do_usuario",
                   name="Q3 playlists_do_usuario",
                   usuario_id=random.randint(1, 500))

    @task(2)
    def q4_musicas_da_playlist(self):
        self._soap("musicas_da_playlist",
                   name="Q4 musicas_da_playlist",
                   playlist_id=random.randint(1, 300))

    @task(1)
    def q5_playlists_com_musica(self):
        self._soap("playlists_com_musica",
                   name="Q5 playlists_com_musica",
                   musica_id=random.randint(1, 500))
