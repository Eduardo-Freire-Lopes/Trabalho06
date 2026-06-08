"""
server.py — Servidor SOAP Python (implementação manual)
        Usa apenas stdlib (http.server + xml.etree) + psycopg2.
        Protocolo: SOAP 1.1 document/literal
        Porta: 8006
        WSDL: GET http://localhost:8006/?wsdl
"""

import os
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/streaming",
)

NS = "http://streaming.local/"
SOAP_ENV = "http://schemas.xmlsoap.org/soap/envelope/"


# ─── BD ──────────────────────────────────────────────────────────────────────
def _fetch(sql, params=None):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchall() if cur.description else []


# ─── Helpers XML ─────────────────────────────────────────────────────────────
def _str(v):
    return "" if v is None else str(v)


def _bool_str(v):
    return "true" if v else "false"


def _u_elem(r):
    e = ET.Element("return")
    ET.SubElement(e, "id").text        = _str(r["id"])
    ET.SubElement(e, "nome").text      = _str(r["nome"])
    ET.SubElement(e, "email").text     = _str(r["email"])
    ET.SubElement(e, "criado_em").text = _str(r["criado_em"])
    return e


def _m_elem(r):
    e = ET.Element("return")
    ET.SubElement(e, "id").text               = _str(r["id"])
    ET.SubElement(e, "titulo").text           = _str(r["titulo"])
    ET.SubElement(e, "artista").text          = _str(r["artista"])
    ET.SubElement(e, "ano_lancamento").text   = _str(r["ano_lancamento"] or 0)
    ET.SubElement(e, "duracao_segundos").text = _str(r["duracao_segundos"] or 0)
    ET.SubElement(e, "criado_em").text        = _str(r["criado_em"])
    return e


def _p_elem(r):
    e = ET.Element("return")
    ET.SubElement(e, "id").text         = _str(r["id"])
    ET.SubElement(e, "nome").text       = _str(r["nome"])
    ET.SubElement(e, "usuario_id").text = _str(r["usuario_id"])
    ET.SubElement(e, "criado_em").text  = _str(r["criado_em"])
    return e


def _list_u(rows):
    e = ET.Element("return")
    for r in rows:
        item = ET.SubElement(e, "item")
        ET.SubElement(item, "id").text        = _str(r["id"])
        ET.SubElement(item, "nome").text      = _str(r["nome"])
        ET.SubElement(item, "email").text     = _str(r["email"])
        ET.SubElement(item, "criado_em").text = _str(r["criado_em"])
    return e


def _list_m(rows):
    e = ET.Element("return")
    for r in rows:
        item = ET.SubElement(e, "item")
        ET.SubElement(item, "id").text               = _str(r["id"])
        ET.SubElement(item, "titulo").text           = _str(r["titulo"])
        ET.SubElement(item, "artista").text          = _str(r["artista"])
        ET.SubElement(item, "ano_lancamento").text   = _str(r["ano_lancamento"] or 0)
        ET.SubElement(item, "duracao_segundos").text = _str(r["duracao_segundos"] or 0)
        ET.SubElement(item, "criado_em").text        = _str(r["criado_em"])
    return e


def _list_p(rows):
    e = ET.Element("return")
    for r in rows:
        item = ET.SubElement(e, "item")
        ET.SubElement(item, "id").text         = _str(r["id"])
        ET.SubElement(item, "nome").text       = _str(r["nome"])
        ET.SubElement(item, "usuario_id").text = _str(r["usuario_id"])
        ET.SubElement(item, "criado_em").text  = _str(r["criado_em"])
    return e


def _soap_response(action: str, body_elem) -> bytes:
    env  = ET.Element("{%s}Envelope" % SOAP_ENV)
    body = ET.SubElement(env, "{%s}Body" % SOAP_ENV)
    resp = ET.SubElement(body, "{%s}%sResponse" % (NS, action))
    resp.append(body_elem)
    return b'<?xml version="1.0" encoding="utf-8"?>' + ET.tostring(env, encoding="unicode").encode()


def _get_text(body, tag):
    el = body.find(".//{%s}%s" % (NS, tag))
    if el is None:
        el = body.find(".//%s" % tag)
    return el.text if el is not None else None


def _get_int(body, tag):
    v = _get_text(body, tag)
    return int(v) if v else 0


# ─── Dispatcher ──────────────────────────────────────────────────────────────
ACTIONS: dict = {}


def action(name):
    def d(fn):
        ACTIONS[name] = fn
        return fn
    return d


@action("criar_usuario")
def _criar_usuario(body):
    rows = _fetch("INSERT INTO usuarios (nome, email) VALUES (%s,%s) RETURNING *",
                  (_get_text(body, "nome"), _get_text(body, "email")))
    return _u_elem(rows[0])


@action("obter_usuario")
def _obter_usuario(body):
    rows = _fetch("SELECT * FROM usuarios WHERE id=%s", (_get_int(body, "id"),))
    return _u_elem(rows[0]) if rows else ET.Element("return")


@action("listar_usuarios")
def _listar_usuarios(body):  # Q1
    return _list_u(_fetch("SELECT * FROM usuarios ORDER BY id"))


@action("atualizar_usuario")
def _atualizar_usuario(body):
    id_ = _get_int(body, "id")
    cur = _fetch("SELECT * FROM usuarios WHERE id=%s", (id_,))
    if not cur:
        return ET.Element("return")
    a = cur[0]
    rows = _fetch("UPDATE usuarios SET nome=%s, email=%s WHERE id=%s RETURNING *",
                  (_get_text(body, "nome") or a["nome"], _get_text(body, "email") or a["email"], id_))
    return _u_elem(rows[0])


@action("remover_usuario")
def _remover_usuario(body):
    rows = _fetch("DELETE FROM usuarios WHERE id=%s RETURNING id", (_get_int(body, "id"),))
    e = ET.Element("return"); e.text = _bool_str(len(rows) > 0); return e


@action("criar_musica")
def _criar_musica(body):
    rows = _fetch(
        "INSERT INTO musicas (titulo, artista, ano_lancamento, duracao_segundos) VALUES (%s,%s,%s,%s) RETURNING *",
        (_get_text(body, "titulo"), _get_text(body, "artista"),
         _get_int(body, "ano_lancamento") or None, _get_int(body, "duracao_segundos") or None),
    )
    return _m_elem(rows[0])


@action("obter_musica")
def _obter_musica(body):
    rows = _fetch("SELECT * FROM musicas WHERE id=%s", (_get_int(body, "id"),))
    return _m_elem(rows[0]) if rows else ET.Element("return")


@action("listar_musicas")
def _listar_musicas(body):  # Q2
    return _list_m(_fetch("SELECT * FROM musicas ORDER BY id"))


@action("atualizar_musica")
def _atualizar_musica(body):
    id_ = _get_int(body, "id")
    cur = _fetch("SELECT * FROM musicas WHERE id=%s", (id_,))
    if not cur:
        return ET.Element("return")
    a = cur[0]
    rows = _fetch(
        "UPDATE musicas SET titulo=%s, artista=%s, ano_lancamento=%s, duracao_segundos=%s WHERE id=%s RETURNING *",
        (_get_text(body, "titulo") or a["titulo"], _get_text(body, "artista") or a["artista"],
         _get_int(body, "ano_lancamento") or a["ano_lancamento"],
         _get_int(body, "duracao_segundos") or a["duracao_segundos"], id_),
    )
    return _m_elem(rows[0])


@action("remover_musica")
def _remover_musica(body):
    rows = _fetch("DELETE FROM musicas WHERE id=%s RETURNING id", (_get_int(body, "id"),))
    e = ET.Element("return"); e.text = _bool_str(len(rows) > 0); return e


@action("criar_playlist")
def _criar_playlist(body):
    rows = _fetch("INSERT INTO playlists (nome, usuario_id) VALUES (%s,%s) RETURNING *",
                  (_get_text(body, "nome"), _get_int(body, "usuario_id")))
    return _p_elem(rows[0])


@action("obter_playlist")
def _obter_playlist(body):
    rows = _fetch("SELECT * FROM playlists WHERE id=%s", (_get_int(body, "id"),))
    return _p_elem(rows[0]) if rows else ET.Element("return")


@action("listar_playlists")
def _listar_playlists(body):
    return _list_p(_fetch("SELECT * FROM playlists ORDER BY id"))


@action("atualizar_playlist")
def _atualizar_playlist(body):
    rows = _fetch("UPDATE playlists SET nome=%s WHERE id=%s RETURNING *",
                  (_get_text(body, "nome"), _get_int(body, "id")))
    return _p_elem(rows[0]) if rows else ET.Element("return")


@action("remover_playlist")
def _remover_playlist(body):
    rows = _fetch("DELETE FROM playlists WHERE id=%s RETURNING id", (_get_int(body, "id"),))
    e = ET.Element("return"); e.text = _bool_str(len(rows) > 0); return e


@action("adicionar_musica_na_playlist")
def _adicionar(body):
    _fetch("INSERT INTO playlist_musicas (playlist_id, musica_id) VALUES (%s,%s) ON CONFLICT DO NOTHING",
           (_get_int(body, "playlist_id"), _get_int(body, "musica_id")))
    e = ET.Element("return"); e.text = "true"; return e


@action("remover_musica_da_playlist")
def _remover_assoc(body):
    rows = _fetch("DELETE FROM playlist_musicas WHERE playlist_id=%s AND musica_id=%s RETURNING playlist_id",
                  (_get_int(body, "playlist_id"), _get_int(body, "musica_id")))
    e = ET.Element("return"); e.text = _bool_str(len(rows) > 0); return e


@action("playlists_do_usuario")
def _pdu(body):  # Q3
    return _list_p(_fetch("SELECT * FROM playlists WHERE usuario_id=%s ORDER BY id",
                           (_get_int(body, "usuario_id"),)))


@action("musicas_da_playlist")
def _mdp(body):  # Q4
    return _list_m(_fetch(
        "SELECT m.* FROM musicas m JOIN playlist_musicas pm ON m.id=pm.musica_id WHERE pm.playlist_id=%s ORDER BY m.id",
        (_get_int(body, "playlist_id"),),
    ))


@action("playlists_com_musica")
def _pcm(body):  # Q5
    return _list_p(_fetch(
        "SELECT p.* FROM playlists p JOIN playlist_musicas pm ON p.id=pm.playlist_id WHERE pm.musica_id=%s ORDER BY p.id",
        (_get_int(body, "musica_id"),),
    ))


# ─── WSDL mínimo ─────────────────────────────────────────────────────────────
WSDL_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<definitions name="StreamingService"
  targetNamespace="http://streaming.local/"
  xmlns="http://schemas.xmlsoap.org/wsdl/"
  xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
  xmlns:tns="http://streaming.local/">
  <service name="StreamingService">
    <port name="StreamingPort" binding="tns:StreamingBinding">
      <soap:address location="http://localhost:8006/"/>
    </port>
  </service>
</definitions>"""


# ─── Handler HTTP ─────────────────────────────────────────────────────────────
class SOAPHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        if "wsdl" in self.path.lower():
            self.send_response(200)
            self.send_header("Content-Type", "text/xml; charset=utf-8")
            self.send_header("Content-Length", str(len(WSDL_XML)))
            self.end_headers()
            self.wfile.write(WSDL_XML)
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"SOAP Python server running")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw    = self.rfile.read(length)
        try:
            root    = ET.fromstring(raw)
            body_el = root.find("{%s}Body" % SOAP_ENV)
            op_el   = list(body_el)[0]
            local   = op_el.tag.split("}")[-1] if "}" in op_el.tag else op_el.tag
            handler = ACTIONS.get(local)
            if not handler:
                raise ValueError(f"Ação desconhecida: {local}")
            result         = handler(body_el)
            response_bytes = _soap_response(local, result)
            self.send_response(200)
            self.send_header("Content-Type", "text/xml; charset=utf-8")
            self.send_header("Content-Length", str(len(response_bytes)))
            self.end_headers()
            self.wfile.write(response_bytes)
        except Exception as exc:
            fault = (
                b'<?xml version="1.0" encoding="utf-8"?>'
                b'<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">'
                b'<soapenv:Body><soapenv:Fault><faultcode>Server</faultcode>'
                b'<faultstring>' + str(exc).encode() + b'</faultstring>'
                b'</soapenv:Fault></soapenv:Body></soapenv:Envelope>'
            )
            self.send_response(500)
            self.send_header("Content-Type", "text/xml; charset=utf-8")
            self.send_header("Content-Length", str(len(fault)))
            self.end_headers()
            self.wfile.write(fault)


if __name__ == "__main__":
    srv = HTTPServer(("0.0.0.0", 8006), SOAPHandler)
    print("SOAP Python rodando na porta 8006")
    srv.serve_forever()
