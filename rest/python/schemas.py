from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# ---- Usuario ----

class UsuarioCreate(BaseModel):
    nome:  str
    email: str

class UsuarioUpdate(BaseModel):
    nome:  Optional[str] = None
    email: Optional[str] = None

class UsuarioOut(BaseModel):
    id:        int
    nome:      str
    email:     str
    criado_em: datetime
    model_config = {"from_attributes": True}


# ---- Musica ----

class MusicaCreate(BaseModel):
    titulo:           str
    artista:          str
    ano_lancamento:   Optional[int] = None
    duracao_segundos: Optional[int] = None

class MusicaUpdate(BaseModel):
    titulo:           Optional[str] = None
    artista:          Optional[str] = None
    ano_lancamento:   Optional[int] = None
    duracao_segundos: Optional[int] = None

class MusicaOut(BaseModel):
    id:               int
    titulo:           str
    artista:          str
    ano_lancamento:   Optional[int]
    duracao_segundos: Optional[int]
    criado_em:        datetime
    model_config = {"from_attributes": True}


# ---- Playlist ----

class PlaylistCreate(BaseModel):
    nome:       str
    usuario_id: int

class PlaylistUpdate(BaseModel):
    nome: Optional[str] = None

class PlaylistOut(BaseModel):
    id:         int
    nome:       str
    usuario_id: int
    criado_em:  datetime
    model_config = {"from_attributes": True}


# ---- Associacao ----

class AddMusica(BaseModel):
    musica_id: int
