import strawberry
from typing import Optional, List
from datetime import datetime


@strawberry.type
class UsuarioType:
    id:        int
    nome:      str
    email:     str
    criado_em: datetime
    playlists: List["PlaylistType"] = strawberry.field(default_factory=list)


@strawberry.type
class MusicaType:
    id:               int
    titulo:           str
    artista:          str
    ano_lancamento:   Optional[int]
    duracao_segundos: Optional[int]
    criado_em:        datetime


@strawberry.type
class PlaylistType:
    id:         int
    nome:       str
    usuario_id: int
    criado_em:  datetime
    musicas:    List[MusicaType] = strawberry.field(default_factory=list)


# ---- Inputs ----

@strawberry.input
class UsuarioInput:
    nome:  str
    email: str

@strawberry.input
class UsuarioUpdateInput:
    nome:  Optional[str] = None
    email: Optional[str] = None

@strawberry.input
class MusicaInput:
    titulo:           str
    artista:          str
    ano_lancamento:   Optional[int] = None
    duracao_segundos: Optional[int] = None

@strawberry.input
class MusicaUpdateInput:
    titulo:           Optional[str] = None
    artista:          Optional[str] = None
    ano_lancamento:   Optional[int] = None
    duracao_segundos: Optional[int] = None

@strawberry.input
class PlaylistInput:
    nome:       str
    usuario_id: int

@strawberry.input
class PlaylistUpdateInput:
    nome: Optional[str] = None
