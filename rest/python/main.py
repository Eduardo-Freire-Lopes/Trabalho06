from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import engine, get_db, Base

# Cria tabelas se nao existirem (util para dev sem migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Streaming de Musicas - REST (Python / FastAPI)",
    version="1.0.0",
)


# ==============================================================
# USUARIOS  (U1-U5, Q1, Q3)
# ==============================================================

@app.post("/usuarios", response_model=schemas.UsuarioOut,
          status_code=status.HTTP_201_CREATED, tags=["usuarios"])
def criar_usuario(body: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(models.Usuario).filter(models.Usuario.email == body.email).first():
        raise HTTPException(status_code=409, detail="Email ja cadastrado")
    usuario = models.Usuario(**body.model_dump())
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@app.get("/usuarios", response_model=List[schemas.UsuarioOut], tags=["usuarios"])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(models.Usuario).all()


@app.get("/usuarios/{usuario_id}", response_model=schemas.UsuarioOut, tags=["usuarios"])
def buscar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.get(models.Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    return usuario


@app.put("/usuarios/{usuario_id}", response_model=schemas.UsuarioOut, tags=["usuarios"])
def atualizar_usuario(usuario_id: int, body: schemas.UsuarioUpdate,
                      db: Session = Depends(get_db)):
    usuario = db.get(models.Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    for campo, valor in body.model_dump(exclude_none=True).items():
        setattr(usuario, campo, valor)
    db.commit()
    db.refresh(usuario)
    return usuario


@app.delete("/usuarios/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["usuarios"])
def remover_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.get(models.Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    db.delete(usuario)
    db.commit()


@app.get("/usuarios/{usuario_id}/playlists", response_model=List[schemas.PlaylistOut],
         tags=["usuarios"])
def playlists_do_usuario(usuario_id: int, db: Session = Depends(get_db)):
    if not db.get(models.Usuario, usuario_id):
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    return (db.query(models.Playlist)
              .filter(models.Playlist.usuario_id == usuario_id)
              .all())


# ==============================================================
# MUSICAS  (M1-M5, Q2, Q5)
# ==============================================================

@app.post("/musicas", response_model=schemas.MusicaOut,
          status_code=status.HTTP_201_CREATED, tags=["musicas"])
def criar_musica(body: schemas.MusicaCreate, db: Session = Depends(get_db)):
    musica = models.Musica(**body.model_dump())
    db.add(musica)
    db.commit()
    db.refresh(musica)
    return musica


@app.get("/musicas", response_model=List[schemas.MusicaOut], tags=["musicas"])
def listar_musicas(db: Session = Depends(get_db)):
    return db.query(models.Musica).all()


@app.get("/musicas/{musica_id}", response_model=schemas.MusicaOut, tags=["musicas"])
def buscar_musica(musica_id: int, db: Session = Depends(get_db)):
    musica = db.get(models.Musica, musica_id)
    if not musica:
        raise HTTPException(status_code=404, detail="Musica nao encontrada")
    return musica


@app.put("/musicas/{musica_id}", response_model=schemas.MusicaOut, tags=["musicas"])
def atualizar_musica(musica_id: int, body: schemas.MusicaUpdate,
                     db: Session = Depends(get_db)):
    musica = db.get(models.Musica, musica_id)
    if not musica:
        raise HTTPException(status_code=404, detail="Musica nao encontrada")
    for campo, valor in body.model_dump(exclude_none=True).items():
        setattr(musica, campo, valor)
    db.commit()
    db.refresh(musica)
    return musica


@app.delete("/musicas/{musica_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["musicas"])
def remover_musica(musica_id: int, db: Session = Depends(get_db)):
    musica = db.get(models.Musica, musica_id)
    if not musica:
        raise HTTPException(status_code=404, detail="Musica nao encontrada")
    db.delete(musica)
    db.commit()


@app.get("/musicas/{musica_id}/playlists", response_model=List[schemas.PlaylistOut],
         tags=["musicas"])
def playlists_com_musica(musica_id: int, db: Session = Depends(get_db)):
    if not db.get(models.Musica, musica_id):
        raise HTTPException(status_code=404, detail="Musica nao encontrada")
    return (db.query(models.Playlist)
              .join(models.playlist_musicas_table,
                    models.Playlist.id == models.playlist_musicas_table.c.playlist_id)
              .filter(models.playlist_musicas_table.c.musica_id == musica_id)
              .all())


# ==============================================================
# PLAYLISTS  (P1-P7, Q4)
# ==============================================================

@app.post("/playlists", response_model=schemas.PlaylistOut,
          status_code=status.HTTP_201_CREATED, tags=["playlists"])
def criar_playlist(body: schemas.PlaylistCreate, db: Session = Depends(get_db)):
    if not db.get(models.Usuario, body.usuario_id):
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    playlist = models.Playlist(**body.model_dump())
    db.add(playlist)
    db.commit()
    db.refresh(playlist)
    return playlist


@app.get("/playlists", response_model=List[schemas.PlaylistOut], tags=["playlists"])
def listar_playlists(db: Session = Depends(get_db)):
    return db.query(models.Playlist).all()


@app.get("/playlists/{playlist_id}", response_model=schemas.PlaylistOut, tags=["playlists"])
def buscar_playlist(playlist_id: int, db: Session = Depends(get_db)):
    playlist = db.get(models.Playlist, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist nao encontrada")
    return playlist


@app.put("/playlists/{playlist_id}", response_model=schemas.PlaylistOut, tags=["playlists"])
def atualizar_playlist(playlist_id: int, body: schemas.PlaylistUpdate,
                       db: Session = Depends(get_db)):
    playlist = db.get(models.Playlist, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist nao encontrada")
    for campo, valor in body.model_dump(exclude_none=True).items():
        setattr(playlist, campo, valor)
    db.commit()
    db.refresh(playlist)
    return playlist


@app.delete("/playlists/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["playlists"])
def remover_playlist(playlist_id: int, db: Session = Depends(get_db)):
    playlist = db.get(models.Playlist, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist nao encontrada")
    db.delete(playlist)
    db.commit()


@app.post("/playlists/{playlist_id}/musicas",
          status_code=status.HTTP_204_NO_CONTENT, tags=["playlists"])
def adicionar_musica_na_playlist(playlist_id: int, body: schemas.AddMusica,
                                 db: Session = Depends(get_db)):
    playlist = db.get(models.Playlist, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist nao encontrada")
    musica = db.get(models.Musica, body.musica_id)
    if not musica:
        raise HTTPException(status_code=404, detail="Musica nao encontrada")
    if musica not in playlist.musicas:
        playlist.musicas.append(musica)
        db.commit()


@app.delete("/playlists/{playlist_id}/musicas/{musica_id}",
            status_code=status.HTTP_204_NO_CONTENT, tags=["playlists"])
def remover_musica_da_playlist(playlist_id: int, musica_id: int,
                                db: Session = Depends(get_db)):
    playlist = db.get(models.Playlist, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist nao encontrada")
    musica = db.get(models.Musica, musica_id)
    if not musica or musica not in playlist.musicas:
        raise HTTPException(status_code=404, detail="Musica nao encontrada na playlist")
    playlist.musicas.remove(musica)
    db.commit()


@app.get("/playlists/{playlist_id}/musicas", response_model=List[schemas.MusicaOut],
         tags=["playlists"])
def musicas_da_playlist(playlist_id: int, db: Session = Depends(get_db)):
    playlist = db.get(models.Playlist, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist nao encontrada")
    return playlist.musicas
