import Fastify from "fastify";
import sensible from "@fastify/sensible";
import { pool } from "./db";

const app = Fastify({ logger: true });
app.register(sensible);

// ==============================================================
// USUARIOS  (U1–U5, Q1, Q3)
// ==============================================================

app.post("/usuarios", async (req, reply) => {
  const { nome, email } = req.body as { nome: string; email: string };
  try {
    const r = await pool.query(
      "INSERT INTO usuarios (nome, email) VALUES ($1, $2) RETURNING *",
      [nome, email]
    );
    return reply.status(201).send(r.rows[0]);
  } catch (e: any) {
    if (e.code === "23505") return reply.conflict("Email ja cadastrado");
    throw e;
  }
});

app.get("/usuarios", async () => {
  const r = await pool.query("SELECT * FROM usuarios ORDER BY id");
  return r.rows;
});

app.get<{ Params: { id: string } }>("/usuarios/:id", async (req, reply) => {
  const r = await pool.query("SELECT * FROM usuarios WHERE id = $1", [req.params.id]);
  if (!r.rows[0]) return reply.notFound("Usuario nao encontrado");
  return r.rows[0];
});

app.put<{ Params: { id: string } }>("/usuarios/:id", async (req, reply) => {
  const { nome, email } = req.body as { nome?: string; email?: string };
  const r = await pool.query("SELECT * FROM usuarios WHERE id = $1", [req.params.id]);
  if (!r.rows[0]) return reply.notFound("Usuario nao encontrado");
  const atual = r.rows[0];
  const upd = await pool.query(
    "UPDATE usuarios SET nome=$1, email=$2 WHERE id=$3 RETURNING *",
    [nome ?? atual.nome, email ?? atual.email, req.params.id]
  );
  return upd.rows[0];
});

app.delete<{ Params: { id: string } }>("/usuarios/:id", async (req, reply) => {
  const r = await pool.query("DELETE FROM usuarios WHERE id=$1 RETURNING id", [req.params.id]);
  if (!r.rows[0]) return reply.notFound("Usuario nao encontrado");
  return reply.status(204).send();
});

// Q3 – Playlists de um usuario
app.get<{ Params: { id: string } }>("/usuarios/:id/playlists", async (req, reply) => {
  const u = await pool.query("SELECT id FROM usuarios WHERE id=$1", [req.params.id]);
  if (!u.rows[0]) return reply.notFound("Usuario nao encontrado");
  const r = await pool.query(
    "SELECT * FROM playlists WHERE usuario_id=$1 ORDER BY id",
    [req.params.id]
  );
  return r.rows;
});

// ==============================================================
// MUSICAS  (M1–M5, Q2, Q5)
// ==============================================================

app.post("/musicas", async (req, reply) => {
  const { titulo, artista, ano_lancamento, duracao_segundos } = req.body as any;
  const r = await pool.query(
    "INSERT INTO musicas (titulo, artista, ano_lancamento, duracao_segundos) VALUES ($1,$2,$3,$4) RETURNING *",
    [titulo, artista, ano_lancamento ?? null, duracao_segundos ?? null]
  );
  return reply.status(201).send(r.rows[0]);
});

app.get("/musicas", async () => {
  const r = await pool.query("SELECT * FROM musicas ORDER BY id");
  return r.rows;
});

app.get<{ Params: { id: string } }>("/musicas/:id", async (req, reply) => {
  const r = await pool.query("SELECT * FROM musicas WHERE id=$1", [req.params.id]);
  if (!r.rows[0]) return reply.notFound("Musica nao encontrada");
  return r.rows[0];
});

app.put<{ Params: { id: string } }>("/musicas/:id", async (req, reply) => {
  const r = await pool.query("SELECT * FROM musicas WHERE id=$1", [req.params.id]);
  if (!r.rows[0]) return reply.notFound("Musica nao encontrada");
  const a = r.rows[0];
  const b = req.body as any;
  const upd = await pool.query(
    "UPDATE musicas SET titulo=$1, artista=$2, ano_lancamento=$3, duracao_segundos=$4 WHERE id=$5 RETURNING *",
    [b.titulo ?? a.titulo, b.artista ?? a.artista, b.ano_lancamento ?? a.ano_lancamento, b.duracao_segundos ?? a.duracao_segundos, req.params.id]
  );
  return upd.rows[0];
});

app.delete<{ Params: { id: string } }>("/musicas/:id", async (req, reply) => {
  const r = await pool.query("DELETE FROM musicas WHERE id=$1 RETURNING id", [req.params.id]);
  if (!r.rows[0]) return reply.notFound("Musica nao encontrada");
  return reply.status(204).send();
});

// Q5 – Playlists que contém uma musica
app.get<{ Params: { id: string } }>("/musicas/:id/playlists", async (req, reply) => {
  const m = await pool.query("SELECT id FROM musicas WHERE id=$1", [req.params.id]);
  if (!m.rows[0]) return reply.notFound("Musica nao encontrada");
  const r = await pool.query(
    `SELECT p.* FROM playlists p
     JOIN playlist_musicas pm ON p.id = pm.playlist_id
     WHERE pm.musica_id = $1 ORDER BY p.id`,
    [req.params.id]
  );
  return r.rows;
});

// ==============================================================
// PLAYLISTS  (P1–P7, Q4)
// ==============================================================

app.post("/playlists", async (req, reply) => {
  const { nome, usuario_id } = req.body as { nome: string; usuario_id: number };
  const u = await pool.query("SELECT id FROM usuarios WHERE id=$1", [usuario_id]);
  if (!u.rows[0]) return reply.notFound("Usuario nao encontrado");
  const r = await pool.query(
    "INSERT INTO playlists (nome, usuario_id) VALUES ($1,$2) RETURNING *",
    [nome, usuario_id]
  );
  return reply.status(201).send(r.rows[0]);
});

app.get("/playlists", async () => {
  const r = await pool.query("SELECT * FROM playlists ORDER BY id");
  return r.rows;
});

app.get<{ Params: { id: string } }>("/playlists/:id", async (req, reply) => {
  const r = await pool.query("SELECT * FROM playlists WHERE id=$1", [req.params.id]);
  if (!r.rows[0]) return reply.notFound("Playlist nao encontrada");
  return r.rows[0];
});

app.put<{ Params: { id: string } }>("/playlists/:id", async (req, reply) => {
  const r = await pool.query("SELECT * FROM playlists WHERE id=$1", [req.params.id]);
  if (!r.rows[0]) return reply.notFound("Playlist nao encontrada");
  const { nome } = req.body as { nome?: string };
  const upd = await pool.query(
    "UPDATE playlists SET nome=$1 WHERE id=$2 RETURNING *",
    [nome ?? r.rows[0].nome, req.params.id]
  );
  return upd.rows[0];
});

app.delete<{ Params: { id: string } }>("/playlists/:id", async (req, reply) => {
  const r = await pool.query("DELETE FROM playlists WHERE id=$1 RETURNING id", [req.params.id]);
  if (!r.rows[0]) return reply.notFound("Playlist nao encontrada");
  return reply.status(204).send();
});

// P6 – Adicionar musica na playlist
app.post<{ Params: { id: string } }>("/playlists/:id/musicas", async (req, reply) => {
  const { musica_id } = req.body as { musica_id: number };
  const p = await pool.query("SELECT id FROM playlists WHERE id=$1", [req.params.id]);
  if (!p.rows[0]) return reply.notFound("Playlist nao encontrada");
  const m = await pool.query("SELECT id FROM musicas WHERE id=$1", [musica_id]);
  if (!m.rows[0]) return reply.notFound("Musica nao encontrada");
  await pool.query(
    "INSERT INTO playlist_musicas (playlist_id, musica_id) VALUES ($1,$2) ON CONFLICT DO NOTHING",
    [req.params.id, musica_id]
  );
  return reply.status(204).send();
});

// P7 – Remover musica da playlist
app.delete<{ Params: { id: string; musica_id: string } }>(
  "/playlists/:id/musicas/:musica_id",
  async (req, reply) => {
    const r = await pool.query(
      "DELETE FROM playlist_musicas WHERE playlist_id=$1 AND musica_id=$2 RETURNING playlist_id",
      [req.params.id, req.params.musica_id]
    );
    if (!r.rows[0]) return reply.notFound("Musica nao encontrada na playlist");
    return reply.status(204).send();
  }
);

// Q4 – Musicas de uma playlist
app.get<{ Params: { id: string } }>("/playlists/:id/musicas", async (req, reply) => {
  const p = await pool.query("SELECT id FROM playlists WHERE id=$1", [req.params.id]);
  if (!p.rows[0]) return reply.notFound("Playlist nao encontrada");
  const r = await pool.query(
    `SELECT m.* FROM musicas m
     JOIN playlist_musicas pm ON m.id = pm.musica_id
     WHERE pm.playlist_id = $1 ORDER BY m.id`,
    [req.params.id]
  );
  return r.rows;
});

// ==============================================================
// Start
// ==============================================================
app.listen({ port: 8001, host: "0.0.0.0" }, (err) => {
  if (err) { app.log.error(err); process.exit(1); }
});
