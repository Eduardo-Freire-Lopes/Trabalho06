import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI
from typing import Optional, List
from sqlalchemy.orm import Session

import models
from database import SessionLocal, engine, Base
from gql_types import (
    UsuarioType, MusicaType, PlaylistType,
    UsuarioInput, UsuarioUpdateInput,
    MusicaInput, MusicaUpdateInput,
    PlaylistInput, PlaylistUpdateInput,
)

Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # fechado manualmente em cada resolver


def _usuario_to_type(u: models.Usuario) -> UsuarioType:
    return UsuarioType(
        id=u.id, nome=u.nome, email=u.email, criado_em=u.criado_em, playlists=[]
    )


def _musica_to_type(m: models.Musica) -> MusicaType:
    return MusicaType(
        id=m.id, titulo=m.titulo, artista=m.artista,
        ano_lancamento=m.ano_lancamento, duracao_segundos=m.duracao_segundos,
        criado_em=m.criado_em,
    )


def _playlist_to_type(p: models.Playlist) -> PlaylistType:
    return PlaylistType(
        id=p.id, nome=p.nome, usuario_id=p.usuario_id, criado_em=p.criado_em,
        musicas=[_musica_to_type(m) for m in p.musicas],
    )


# ==============================================================
# Queries
# ==============================================================

@strawberry.type
class Query:

    @strawberry.field
    def usuarios(self) -> List[UsuarioType]:
        db = get_db()
        try:
            return [_usuario_to_type(u) for u in db.query(models.Usuario).all()]
        finally:
            db.close()

    @strawberry.field
    def usuario(self, id: int) -> Optional[UsuarioType]:
        db = get_db()
        try:
            u = db.get(models.Usuario, id)
            return _usuario_to_type(u) if u else None
        finally:
            db.close()

    @strawberry.field
    def musicas(self) -> List[MusicaType]:
        db = get_db()
        try:
            return [_musica_to_type(m) for m in db.query(models.Musica).all()]
        finally:
            db.close()

    @strawberry.field
    def musica(self, id: int) -> Optional[MusicaType]:
        db = get_db()
        try:
            m = db.get(models.Musica, id)
            return _musica_to_type(m) if m else None
        finally:
            db.close()

    @strawberry.field
    def playlists(self) -> List[PlaylistType]:
        db = get_db()
        try:
            return [_playlist_to_type(p) for p in db.query(models.Playlist).all()]
        finally:
            db.close()

    @strawberry.field
    def playlist(self, id: int) -> Optional[PlaylistType]:
        db = get_db()
        try:
            p = db.get(models.Playlist, id)
            return _playlist_to_type(p) if p else None
        finally:
            db.close()

    # Q3
    @strawberry.field
    def playlists_do_usuario(self, usuario_id: int) -> List[PlaylistType]:
        db = get_db()
        try:
            return [
                _playlist_to_type(p)
                for p in db.query(models.Playlist)
                           .filter(models.Playlist.usuario_id == usuario_id)
                           .all()
            ]
        finally:
            db.close()

    # Q4
    @strawberry.field
    def musicas_da_playlist(self, playlist_id: int) -> List[MusicaType]:
        db = get_db()
        try:
            p = db.get(models.Playlist, playlist_id)
            return [_musica_to_type(m) for m in p.musicas] if p else []
        finally:
            db.close()

    # Q5
    @strawberry.field
    def playlists_com_musica(self, musica_id: int) -> List[PlaylistType]:
        db = get_db()
        try:
            rows = (
                db.query(models.Playlist)
                  .join(models.playlist_musicas_table,
                        models.Playlist.id == models.playlist_musicas_table.c.playlist_id)
                  .filter(models.playlist_musicas_table.c.musica_id == musica_id)
                  .all()
            )
            return [_playlist_to_type(p) for p in rows]
        finally:
            db.close()


# ==============================================================
# Mutations
# ==============================================================

@strawberry.type
class Mutation:

    # --- Usuarios ---
    @strawberry.mutation
    def criar_usuario(self, dados: UsuarioInput) -> UsuarioType:
        db = get_db()
        try:
            u = models.Usuario(nome=dados.nome, email=dados.email)
            db.add(u); db.commit(); db.refresh(u)
            return _usuario_to_type(u)
        finally:
            db.close()

    @strawberry.mutation
    def atualizar_usuario(self, id: int, dados: UsuarioUpdateInput) -> Optional[UsuarioType]:
        db = get_db()
        try:
            u = db.get(models.Usuario, id)
            if not u:
                return None
            if dados.nome is not None:  u.nome  = dados.nome
            if dados.email is not None: u.email = dados.email
            db.commit(); db.refresh(u)
            return _usuario_to_type(u)
        finally:
            db.close()

    @strawberry.mutation
    def remover_usuario(self, id: int) -> bool:
        db = get_db()
        try:
            u = db.get(models.Usuario, id)
            if not u: return False
            db.delete(u); db.commit()
            return True
        finally:
            db.close()

    # --- Musicas ---
    @strawberry.mutation
    def criar_musica(self, dados: MusicaInput) -> MusicaType:
        db = get_db()
        try:
            m = models.Musica(
                titulo=dados.titulo, artista=dados.artista,
                ano_lancamento=dados.ano_lancamento,
                duracao_segundos=dados.duracao_segundos,
            )
            db.add(m); db.commit(); db.refresh(m)
            return _musica_to_type(m)
        finally:
            db.close()

    @strawberry.mutation
    def atualizar_musica(self, id: int, dados: MusicaUpdateInput) -> Optional[MusicaType]:
        db = get_db()
        try:
            m = db.get(models.Musica, id)
            if not m: return None
            for campo in ("titulo", "artista", "ano_lancamento", "duracao_segundos"):
                val = getattr(dados, campo)
                if val is not None:
                    setattr(m, campo, val)
            db.commit(); db.refresh(m)
            return _musica_to_type(m)
        finally:
            db.close()

    @strawberry.mutation
    def remover_musica(self, id: int) -> bool:
        db = get_db()
        try:
            m = db.get(models.Musica, id)
            if not m: return False
            db.delete(m); db.commit()
            return True
        finally:
            db.close()

    # --- Playlists ---
    @strawberry.mutation
    def criar_playlist(self, dados: PlaylistInput) -> Optional[PlaylistType]:
        db = get_db()
        try:
            if not db.get(models.Usuario, dados.usuario_id):
                return None
            p = models.Playlist(nome=dados.nome, usuario_id=dados.usuario_id)
            db.add(p); db.commit(); db.refresh(p)
            return _playlist_to_type(p)
        finally:
            db.close()

    @strawberry.mutation
    def atualizar_playlist(self, id: int, dados: PlaylistUpdateInput) -> Optional[PlaylistType]:
        db = get_db()
        try:
            p = db.get(models.Playlist, id)
            if not p: return None
            if dados.nome is not None: p.nome = dados.nome
            db.commit(); db.refresh(p)
            return _playlist_to_type(p)
        finally:
            db.close()

    @strawberry.mutation
    def remover_playlist(self, id: int) -> bool:
        db = get_db()
        try:
            p = db.get(models.Playlist, id)
            if not p: return False
            db.delete(p); db.commit()
            return True
        finally:
            db.close()

    @strawberry.mutation
    def adicionar_musica_na_playlist(self, playlist_id: int, musica_id: int) -> bool:
        db = get_db()
        try:
            p = db.get(models.Playlist, playlist_id)
            m = db.get(models.Musica, musica_id)
            if not p or not m: return False
            if m not in p.musicas:
                p.musicas.append(m)
                db.commit()
            return True
        finally:
            db.close()

    @strawberry.mutation
    def remover_musica_da_playlist(self, playlist_id: int, musica_id: int) -> bool:
        db = get_db()
        try:
            p = db.get(models.Playlist, playlist_id)
            m = db.get(models.Musica, musica_id)
            if not p or not m or m not in p.musicas: return False
            p.musicas.remove(m)
            db.commit()
            return True
        finally:
            db.close()


# ==============================================================
# App FastAPI
# ==============================================================

schema = strawberry.Schema(query=Query, mutation=Mutation)

app = FastAPI(title="Streaming de Musicas - GraphQL (Python / Strawberry)")
app.include_router(GraphQLRouter(schema), prefix="/graphql")
