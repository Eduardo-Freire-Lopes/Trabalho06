import * as soap from "soap";
import * as http from "http";
import { pool } from "./db";
import { WSDL } from "./wsdl";

// ── helpers ─────────────────────────────────────────────────────────────────
function rowU(r: any) { return { id: r.id, nome: r.nome, email: r.email, criado_em: new Date(r.criado_em).toISOString() }; }
function rowM(r: any) { return { id: r.id, titulo: r.titulo, artista: r.artista, ano_lancamento: r.ano_lancamento ?? 0, duracao_segundos: r.duracao_segundos ?? 0, criado_em: new Date(r.criado_em).toISOString() }; }
function rowP(r: any) { return { id: r.id, nome: r.nome, usuario_id: r.usuario_id, criado_em: new Date(r.criado_em).toISOString() }; }

// O soap.js espera que o service retorne { return: valor }
const serviceImpl = {
  StreamingService: {
    StreamingPort: {

      async criar_usuario({ nome, email }: any) {
        const r = await pool.query("INSERT INTO usuarios (nome, email) VALUES ($1,$2) RETURNING *", [nome, email]);
        return { return: rowU(r.rows[0]) };
      },
      async obter_usuario({ id }: any) {
        const r = await pool.query("SELECT * FROM usuarios WHERE id=$1", [id]);
        return { return: r.rows[0] ? rowU(r.rows[0]) : null };
      },
      async listar_usuarios() {  // Q1
        const r = await pool.query("SELECT * FROM usuarios ORDER BY id");
        return { return: { item: r.rows.map(rowU) } };
      },
      async atualizar_usuario({ id, nome, email }: any) {
        const cur = await pool.query("SELECT * FROM usuarios WHERE id=$1", [id]);
        if (!cur.rows[0]) return { return: null };
        const a = cur.rows[0];
        const r = await pool.query("UPDATE usuarios SET nome=$1, email=$2 WHERE id=$3 RETURNING *", [nome || a.nome, email || a.email, id]);
        return { return: rowU(r.rows[0]) };
      },
      async remover_usuario({ id }: any) {
        const r = await pool.query("DELETE FROM usuarios WHERE id=$1 RETURNING id", [id]);
        return { return: r.rows.length > 0 };
      },

      async criar_musica({ titulo, artista, ano_lancamento, duracao_segundos }: any) {
        const r = await pool.query("INSERT INTO musicas (titulo, artista, ano_lancamento, duracao_segundos) VALUES ($1,$2,$3,$4) RETURNING *",
          [titulo, artista, ano_lancamento || null, duracao_segundos || null]);
        return { return: rowM(r.rows[0]) };
      },
      async obter_musica({ id }: any) {
        const r = await pool.query("SELECT * FROM musicas WHERE id=$1", [id]);
        return { return: r.rows[0] ? rowM(r.rows[0]) : null };
      },
      async listar_musicas() {  // Q2
        const r = await pool.query("SELECT * FROM musicas ORDER BY id");
        return { return: { item: r.rows.map(rowM) } };
      },
      async atualizar_musica({ id, titulo, artista, ano_lancamento, duracao_segundos }: any) {
        const cur = await pool.query("SELECT * FROM musicas WHERE id=$1", [id]);
        if (!cur.rows[0]) return { return: null };
        const a = cur.rows[0];
        const r = await pool.query("UPDATE musicas SET titulo=$1, artista=$2, ano_lancamento=$3, duracao_segundos=$4 WHERE id=$5 RETURNING *",
          [titulo || a.titulo, artista || a.artista, ano_lancamento || a.ano_lancamento, duracao_segundos || a.duracao_segundos, id]);
        return { return: rowM(r.rows[0]) };
      },
      async remover_musica({ id }: any) {
        const r = await pool.query("DELETE FROM musicas WHERE id=$1 RETURNING id", [id]);
        return { return: r.rows.length > 0 };
      },

      async criar_playlist({ nome, usuario_id }: any) {
        const r = await pool.query("INSERT INTO playlists (nome, usuario_id) VALUES ($1,$2) RETURNING *", [nome, usuario_id]);
        return { return: rowP(r.rows[0]) };
      },
      async obter_playlist({ id }: any) {
        const r = await pool.query("SELECT * FROM playlists WHERE id=$1", [id]);
        return { return: r.rows[0] ? rowP(r.rows[0]) : null };
      },
      async listar_playlists() {
        const r = await pool.query("SELECT * FROM playlists ORDER BY id");
        return { return: { item: r.rows.map(rowP) } };
      },
      async atualizar_playlist({ id, nome }: any) {
        const r = await pool.query("UPDATE playlists SET nome=$1 WHERE id=$2 RETURNING *", [nome, id]);
        return { return: r.rows[0] ? rowP(r.rows[0]) : null };
      },
      async remover_playlist({ id }: any) {
        const r = await pool.query("DELETE FROM playlists WHERE id=$1 RETURNING id", [id]);
        return { return: r.rows.length > 0 };
      },
      async adicionar_musica_na_playlist({ playlist_id, musica_id }: any) {
        await pool.query("INSERT INTO playlist_musicas (playlist_id, musica_id) VALUES ($1,$2) ON CONFLICT DO NOTHING", [playlist_id, musica_id]);
        return { return: true };
      },
      async remover_musica_da_playlist({ playlist_id, musica_id }: any) {
        const r = await pool.query("DELETE FROM playlist_musicas WHERE playlist_id=$1 AND musica_id=$2 RETURNING playlist_id", [playlist_id, musica_id]);
        return { return: r.rows.length > 0 };
      },
      async playlists_do_usuario({ usuario_id }: any) {  // Q3
        const r = await pool.query("SELECT * FROM playlists WHERE usuario_id=$1 ORDER BY id", [usuario_id]);
        return { return: { item: r.rows.map(rowP) } };
      },
      async musicas_da_playlist({ playlist_id }: any) {  // Q4
        const r = await pool.query("SELECT m.* FROM musicas m JOIN playlist_musicas pm ON m.id=pm.musica_id WHERE pm.playlist_id=$1 ORDER BY m.id", [playlist_id]);
        return { return: { item: r.rows.map(rowM) } };
      },
      async playlists_com_musica({ musica_id }: any) {  // Q5
        const r = await pool.query("SELECT p.* FROM playlists p JOIN playlist_musicas pm ON p.id=pm.playlist_id WHERE pm.musica_id=$1 ORDER BY p.id", [musica_id]);
        return { return: { item: r.rows.map(rowP) } };
      },
    },
  },
};

const server = http.createServer((req, res) => {
  res.end("SOAP server running");
});

soap.listen(server, "/", serviceImpl, WSDL, () => {
  console.log("SOAP TypeScript rodando na porta 8007");
});

server.listen(8007);
