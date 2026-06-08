import * as grpc from "@grpc/grpc-js";
import * as protoLoader from "@grpc/proto-loader";
import * as path from "path";
import { pool } from "./db";

const PROTO_PATH = path.join(__dirname, "../../streaming.proto");

const pkgDef = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
});
const proto = (grpc.loadPackageDefinition(pkgDef) as any).streaming;

// ─── helpers ──────────────────────────────────────────────────────────────────
function rowU(r: any) { return { id: r.id, nome: r.nome, email: r.email, criado_em: new Date(r.criado_em).toISOString() }; }
function rowM(r: any) { return { id: r.id, titulo: r.titulo, artista: r.artista, ano_lancamento: r.ano_lancamento ?? 0, duracao_segundos: r.duracao_segundos ?? 0, criado_em: new Date(r.criado_em).toISOString() }; }
function rowP(r: any) { return { id: r.id, nome: r.nome, usuario_id: r.usuario_id, criado_em: new Date(r.criado_em).toISOString() }; }

function err(call: grpc.ServerUnaryCall<any, any>, cb: grpc.sendUnaryData<any>, e: unknown) {
  console.error(e);
  cb({ code: grpc.status.INTERNAL, message: String(e) } as grpc.ServiceError);
}

// ─── UsuarioService ───────────────────────────────────────────────────────────
const usuarioImpl = {
  CriarUsuario: async (call: grpc.ServerUnaryCall<any, any>, cb: grpc.sendUnaryData<any>) => {
    try {
      const { nome, email } = call.request;
      const r = await pool.query("INSERT INTO usuarios (nome, email) VALUES ($1,$2) RETURNING *", [nome, email]);
      cb(null, rowU(r.rows[0]));
    } catch (e) { err(call, cb, e); }
  },
  ObterUsuario: async (call: grpc.ServerUnaryCall<any, any>, cb: grpc.sendUnaryData<any>) => {
    try {
      const r = await pool.query("SELECT * FROM usuarios WHERE id=$1", [call.request.id]);
      if (!r.rows[0]) { cb({ code: grpc.status.NOT_FOUND } as grpc.ServiceError); return; }
      cb(null, rowU(r.rows[0]));
    } catch (e) { err(call, cb, e); }
  },
  ListarUsuarios: async (call: grpc.ServerUnaryCall<any, any>, cb: grpc.sendUnaryData<any>) => { // Q1
    try {
      const r = await pool.query("SELECT * FROM usuarios ORDER BY id");
      cb(null, { usuarios: r.rows.map(rowU) });
    } catch (e) { err(call, cb, e); }
  },
  AtualizarUsuario: async (call: grpc.ServerUnaryCall<any, any>, cb: grpc.sendUnaryData<any>) => {
    try {
      const { id, nome, email } = call.request;
      const cur = await pool.query("SELECT * FROM usuarios WHERE id=$1", [id]);
      if (!cur.rows[0]) { cb({ code: grpc.status.NOT_FOUND } as grpc.ServiceError); return; }
      const a = cur.rows[0];
      const r = await pool.query("UPDATE usuarios SET nome=$1, email=$2 WHERE id=$3 RETURNING *", [nome || a.nome, email || a.email, id]);
      cb(null, rowU(r.rows[0]));
    } catch (e) { err(call, cb, e); }
  },
  RemoverUsuario: async (call: grpc.ServerUnaryCall<any, any>, cb: grpc.sendUnaryData<any>) => {
    try {
      const r = await pool.query("DELETE FROM usuarios WHERE id=$1 RETURNING id", [call.request.id]);
      cb(null, { ok: r.rows.length > 0 });
    } catch (e) { err(call, cb, e); }
  },
};

// ─── MusicaService ────────────────────────────────────────────────────────────
const musicaImpl = {
  CriarMusica: async (call: grpc.ServerUnaryCall<any, any>, cb: grpc.sendUnaryData<any>) => {
    try {
      const { titulo, artista, ano_lancamento, duracao_segundos } = call.request;
      const r = await pool.query(
        "INSERT INTO musicas (titulo, artista, ano_lancamento, duracao_segundos) VALUES ($1,$2,$3,$4) RETURNING *",
        [titulo, artista, ano_lancamento || null, duracao_segundos || null],
      );
      cb(null, rowM(r.rows[0]));
    } catch (e) { err(call, cb, e); }
  },
  ObterMusica: async (call: grpc.ServerUnaryCall<any, any>, cb: grpc.sendUnaryData<any>) => {
    try {
      const r = await pool.query("SELECT * FROM musicas WHERE id=$1", [call.request.id]);
      if (!r.rows[0]) { cb({ code: grpc.status.NOT_FOUND } as grpc.ServiceError); return; }
      cb(null, rowM(r.rows[0]));
    } catch (e) { err(call, cb, e); }
  },
  ListarMusicas: async (call: grpc.ServerUnaryCall<any, any>, cb: grpc.sendUnaryData<any>) => { // Q2
    try {
      const r = await pool.query("SELECT * FROM musicas ORDER BY id");
      cb(null, { musicas: r.rows.map(rowM) });
    } catch (e) { err(call, cb, e); }
  },
  AtualizarMusica: async (call: grpc.ServerUnaryCall<any, any>, cb: grpc.sendUnaryData<any>) => {
    try {
      const { id, titulo, artista, ano_lancamento, duracao_segundos } = call.request;
      const cur = await pool.query("SELECT * FROM musicas WHERE id=$1", [id]);
      if (!cur.rows[0]) { cb({ code: grpc.status.NOT_FOUND } as grpc.ServiceError); return; }
      const a = cur.rows[0];
      const r = await pool.query(
        "UPDATE musicas SET titulo=$1, artista=$2, ano_lancamento=$3, duracao_segundos=$4 WHERE id=$5 RETURNING *",
        [titulo || a.titulo, artista || a.artista, ano_lancamento || a.ano_lancamento, duracao_segundos || a.duracao_segundos, id],
      );
      cb(null, rowM(r.rows[0]));
    } catch (e) { err(call, cb, e); }
  },
  RemoverMusica: async (call: grpc.ServerUnaryCall<any, any>, cb: grpc.sendUnaryData<any>) => {
    try {
      const r = await pool.query("DELETE FROM musicas WHERE id=$1 RETURNING id", [call.request.id]);
      cb(null, { ok: r.rows.length > 0 });
    } catch (e) { err(call, cb, e); }
  },
};

// ─── PlaylistService ──────────────────────────────────────────────────────────
const playlistImpl = {
  CriarPlaylist: async (call: grpc.ServerUnaryCall<any, any>, cb: grpc.sendUnaryData<any>) => {
    try {
      const { nome, usuario_id } = call.request;
      const r = await pool.query("INSERT INTO playlists (nome, usuario_id) VALUES ($1,$2) RETURNING *", [nome, usuario_id]);
      cb(null, rowP(r.rows[0]));
    } catch (e) { err(call, cb, e); }
  },
  ObterPlaylist: async (call: grpc.ServerUnaryCall<any, any>, cb: grpc.sendUnaryData<any>) => {
    try {
      const r = await pool.query("SELECT * FROM playlists WHERE id=$1", [call.request.id]);
      if (!r.rows[0]) { cb({ code: grpc.status.NOT_FOUND } as grpc.ServiceError); return; }
      cb(null, rowP(r.rows[0]));
    } catch (e) { err(call, cb, e); }
  },
  ListarPlaylists: async (call: grpc.ServerUnaryCall<any, any>, cb: grpc.sendUnaryData<any>) => {
    try {
      const r = await pool.query("SELECT * FROM playlists ORDER BY id");
      cb(null, { playlists: r.rows.map(rowP) });
    } catch (e) { err(call, cb, e); }
  },
  AtualizarPlaylist: async (call: grpc.ServerUnaryCall<any, any>, cb: grpc.sendUnaryData<any>) => {
    try {
      const r = await pool.query("UPDATE playlists SET nome=$1 WHERE id=$2 RETURNING *", [call.request.nome, call.request.id]);
      if (!r.rows[0]) { cb({ code: grpc.status.NOT_FOUND } as grpc.ServiceError); return; }
      cb(null, rowP(r.rows[0]));
    } catch (e) { err(call, cb, e); }
  },
  RemoverPlaylist: async (call: grpc.ServerUnaryCall<any, any>, cb: grpc.sendUnaryData<any>) => {
    try {
      const r = await pool.query("DELETE FROM playlists WHERE id=$1 RETURNING id", [call.request.id]);
      cb(null, { ok: r.rows.length > 0 });
    } catch (e) { err(call, cb, e); }
  },
  AdicionarMusica: async (call: grpc.ServerUnaryCall<any, any>, cb: grpc.sendUnaryData<any>) => {
    try {
      await pool.query(
        "INSERT INTO playlist_musicas (playlist_id, musica_id) VALUES ($1,$2) ON CONFLICT DO NOTHING",
        [call.request.playlist_id, call.request.musica_id],
      );
      cb(null, { ok: true });
    } catch (e) { err(call, cb, e); }
  },
  RemoverMusica: async (call: grpc.ServerUnaryCall<any, any>, cb: grpc.sendUnaryData<any>) => {
    try {
      const r = await pool.query(
        "DELETE FROM playlist_musicas WHERE playlist_id=$1 AND musica_id=$2 RETURNING playlist_id",
        [call.request.playlist_id, call.request.musica_id],
      );
      cb(null, { ok: r.rows.length > 0 });
    } catch (e) { err(call, cb, e); }
  },
  PlaylistsDoUsuario: async (call: grpc.ServerUnaryCall<any, any>, cb: grpc.sendUnaryData<any>) => { // Q3
    try {
      const r = await pool.query("SELECT * FROM playlists WHERE usuario_id=$1 ORDER BY id", [call.request.usuario_id]);
      cb(null, { playlists: r.rows.map(rowP) });
    } catch (e) { err(call, cb, e); }
  },
  MusicasDaPlaylist: async (call: grpc.ServerUnaryCall<any, any>, cb: grpc.sendUnaryData<any>) => { // Q4
    try {
      const r = await pool.query(
        "SELECT m.* FROM musicas m JOIN playlist_musicas pm ON m.id=pm.musica_id WHERE pm.playlist_id=$1 ORDER BY m.id",
        [call.request.playlist_id],
      );
      cb(null, { musicas: r.rows.map(rowM) });
    } catch (e) { err(call, cb, e); }
  },
  PlaylistsComMusica: async (call: grpc.ServerUnaryCall<any, any>, cb: grpc.sendUnaryData<any>) => { // Q5
    try {
      const r = await pool.query(
        "SELECT p.* FROM playlists p JOIN playlist_musicas pm ON p.id=pm.playlist_id WHERE pm.musica_id=$1 ORDER BY p.id",
        [call.request.musica_id],
      );
      cb(null, { playlists: r.rows.map(rowP) });
    } catch (e) { err(call, cb, e); }
  },
};

// ─── Bootstrap ────────────────────────────────────────────────────────────────
const server = new grpc.Server();
server.addService(proto.UsuarioService.service, usuarioImpl);
server.addService(proto.MusicaService.service, musicaImpl);
server.addService(proto.PlaylistService.service, playlistImpl);

server.bindAsync("0.0.0.0:8005", grpc.ServerCredentials.createInsecure(), (err, port) => {
  if (err) { console.error(err); process.exit(1); }
  console.log(`gRPC TypeScript rodando na porta ${port}`);
});
