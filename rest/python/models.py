from datetime import datetime
from sqlalchemy import Column, Integer, String, SmallInteger, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

# Tabela de associacao N:N  playlist <-> musica
playlist_musicas_table = Table(
    "playlist_musicas",
    Base.metadata,
    Column("playlist_id", Integer, ForeignKey("playlists.id", ondelete="CASCADE"), primary_key=True),
    Column("musica_id",   Integer, ForeignKey("musicas.id",   ondelete="CASCADE"), primary_key=True),
)


class Usuario(Base):
    __tablename__ = "usuarios"

    id        = Column(Integer, primary_key=True, index=True)
    nome      = Column(String(150), nullable=False)
    email     = Column(String(255), nullable=False, unique=True)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)

    playlists = relationship("Playlist", back_populates="usuario", cascade="all, delete-orphan")


class Musica(Base):
    __tablename__ = "musicas"

    id               = Column(Integer, primary_key=True, index=True)
    titulo           = Column(String(255), nullable=False)
    artista          = Column(String(150), nullable=False)
    ano_lancamento   = Column(SmallInteger)
    duracao_segundos = Column(Integer)
    criado_em        = Column(DateTime, default=datetime.utcnow, nullable=False)


class Playlist(Base):
    __tablename__ = "playlists"

    id         = Column(Integer, primary_key=True, index=True)
    nome       = Column(String(255), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    criado_em  = Column(DateTime, default=datetime.utcnow, nullable=False)

    usuario = relationship("Usuario", back_populates="playlists")
    musicas = relationship("Musica", secondary=playlist_musicas_table, lazy="select")
