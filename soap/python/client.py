"""
client.py — Cliente SOAP Python usando requests + xml.etree
Envia envelopes SOAP 1.1 manualmente para http://localhost:8006/
"""

import xml.etree.ElementTree as ET
import requests

URL = "http://localhost:8006/"
NS = "http://streaming.local/"
SOAP_ENV = "http://schemas.xmlsoap.org/soap/envelope/"


def _call(action: str, **kwargs) -> ET.Element:
    """Monta um envelope SOAP, envia, retorna o elemento <return>."""
    body_inner = "<{a} xmlns=\"{ns}\">{fields}</{a}>".format(
        a=action, ns=NS,
        fields="".join(f"<{k}>{v}</{k}>" for k, v in kwargs.items()),
    )
    envelope = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"'
        '  xmlns:tns="http://streaming.local/">'
        '<soapenv:Body>' + body_inner + '</soapenv:Body>'
        '</soapenv:Envelope>'
    )
    resp = requests.post(URL, data=envelope.encode(), headers={"Content-Type": "text/xml; charset=utf-8"})
    root = ET.fromstring(resp.text)
    ret = root.find(".//{%s}%sResponse/{%s}return" % (NS, action, NS))
    if ret is None:
        ret = root.find(".//return")
    return ret


def _items(el, sub_tag):
    if el is None:
        return []
    return el.findall(sub_tag)


def titulo(t: str):
    print(f"\n{'='*55}\n  {t}\n{'='*55}")


def main():
    # criar_usuario
    titulo("criar_usuario")
    u = _call("criar_usuario", nome="Carlos SOAP", email="carlos@soap.com")
    uid = int(u.findtext("id"))
    print(f"Criado: id={uid} nome={u.findtext('nome')}")

    # Q1
    titulo("Q1 - listar_usuarios")
    lu = _call("listar_usuarios")
    print(f"Total: {len(_items(lu, 'item'))} usuarios")

    # atualizar_usuario
    titulo("atualizar_usuario")
    u2 = _call("atualizar_usuario", id=uid, nome="Carlos SOAP Atualizado", email="carlos@soap.com")
    print(f"Atualizado: nome={u2.findtext('nome')}")

    # criar_musica
    titulo("criar_musica")
    m = _call("criar_musica", titulo="So Danco Samba", artista="Tom Jobim",
              ano_lancamento=1963, duracao_segundos=185)
    mid = int(m.findtext("id"))
    print(f"Criada: id={mid} titulo={m.findtext('titulo')}")

    # Q2
    titulo("Q2 - listar_musicas")
    lm = _call("listar_musicas")
    print(f"Total: {len(_items(lm, 'item'))} musicas")

    # criar_playlist
    titulo("criar_playlist")
    pl = _call("criar_playlist", nome="Bossa SOAP PY", usuario_id=uid)
    pid = int(pl.findtext("id"))
    print(f"Criada: id={pid} nome={pl.findtext('nome')}")

    # adicionar_musica_na_playlist
    titulo("adicionar_musica_na_playlist")
    r = _call("adicionar_musica_na_playlist", playlist_id=pid, musica_id=mid)
    print(f"ok={r.text}")

    # Q3
    titulo("Q3 - playlists_do_usuario")
    q3 = _call("playlists_do_usuario", usuario_id=uid)
    print(f"Playlists: {[i.findtext('nome') for i in _items(q3, 'item')]}")

    # Q4
    titulo("Q4 - musicas_da_playlist")
    q4 = _call("musicas_da_playlist", playlist_id=pid)
    print(f"Musicas: {[i.findtext('titulo') for i in _items(q4, 'item')]}")

    # Q5
    titulo("Q5 - playlists_com_musica")
    q5 = _call("playlists_com_musica", musica_id=mid)
    print(f"Playlists: {[i.findtext('nome') for i in _items(q5, 'item')]}")

    # remover_musica_da_playlist
    titulo("remover_musica_da_playlist")
    r = _call("remover_musica_da_playlist", playlist_id=pid, musica_id=mid)
    print(f"ok={r.text}")

    # remover_playlist
    titulo("remover_playlist")
    r = _call("remover_playlist", id=pid)
    print(f"ok={r.text}")

    # remover_musica
    titulo("remover_musica")
    r = _call("remover_musica", id=mid)
    print(f"ok={r.text}")

    # remover_usuario
    titulo("remover_usuario")
    r = _call("remover_usuario", id=uid)
    print(f"ok={r.text}")

    print("\nDemo SOAP Python concluida com sucesso!")


if __name__ == "__main__":
    main()
