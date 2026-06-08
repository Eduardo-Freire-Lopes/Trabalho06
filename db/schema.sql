-- =============================================================
-- Schema compartilhado - Servico de Streaming de Musicas
-- Trabalho 06 - Computacao Distribuida
-- Usado por todas as implementacoes (SOAP, REST, GraphQL, gRPC)
-- em Python e TypeScript.
-- =============================================================

-- Extensao para UUID (opcional, mas util)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- -------------------------------------------------------------
-- Tabela: usuarios
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    id        SERIAL PRIMARY KEY,
    nome      VARCHAR(150) NOT NULL,
    email     VARCHAR(255) NOT NULL UNIQUE,
    criado_em TIMESTAMP NOT NULL DEFAULT NOW()
);

-- -------------------------------------------------------------
-- Tabela: musicas
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS musicas (
    id               SERIAL PRIMARY KEY,
    titulo           VARCHAR(255) NOT NULL,
    artista          VARCHAR(150) NOT NULL,
    ano_lancamento   SMALLINT,
    duracao_segundos INTEGER,
    criado_em        TIMESTAMP NOT NULL DEFAULT NOW()
);

-- -------------------------------------------------------------
-- Tabela: playlists
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS playlists (
    id         SERIAL PRIMARY KEY,
    nome       VARCHAR(255) NOT NULL,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    criado_em  TIMESTAMP NOT NULL DEFAULT NOW()
);

-- -------------------------------------------------------------
-- Tabela de associacao: playlist_musicas (N:N)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS playlist_musicas (
    playlist_id INTEGER NOT NULL REFERENCES playlists(id) ON DELETE CASCADE,
    musica_id   INTEGER NOT NULL REFERENCES musicas(id) ON DELETE CASCADE,
    PRIMARY KEY (playlist_id, musica_id)
);

-- -------------------------------------------------------------
-- Indices para consultas frequentes
-- -------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_playlists_usuario ON playlists(usuario_id);
CREATE INDEX IF NOT EXISTS idx_playlist_musicas_musica ON playlist_musicas(musica_id);
