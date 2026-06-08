import { pool } from "./db";

async function musicas_da_playlist(playlistId: number) {
  const r = await pool.query(
    `SELECT m.* FROM musicas m
     JOIN playlist_musicas pm ON m.id = pm.musica_id
     WHERE pm.playlist_id = $1 ORDER BY m.id`,
    [playlistId]
  );
  return r.rows.map(row2musica);
}

function row2usuario(r: any) {
  return { id: r.id, nome: r.nome, email: r.email, criadoEm: new Date(r.criado_em).toISOString(), playlists: [] };
}
function row2musica(r: any) {
  return { id: r.id, titulo: r.titulo, artista: r.artista, anoLancamento: r.ano_lancamento, duracaoSegundos: r.duracao_segundos, criadoEm: new Date(r.criado_em).toISOString() };
}
async function row2playlist(r: any) {
  const musicas = await musicas_da_playlist(r.id);
  return { id: r.id, nome: r.nome, usuarioId: r.usuario_id, criadoEm: new Date(r.criado_em).toISOString(), musicas };
}

export const resolvers = {
  Query: {
    // Q1
    usuarios: async () => {
      const r = await pool.query("SELECT * FROM usuarios ORDER BY id");
      return r.rows.map(row2usuario);
    },
    usuario: async (_: any, { id }: { id: number }) => {
      const r = await pool.query("SELECT * FROM usuarios WHERE id=$1", [id]);
      return r.rows[0] ? row2usuario(r.rows[0]) : null;
    },
    // Q2
    musicas: async () => {
      const r = await pool.query("SELECT * FROM musicas ORDER BY id");
      return r.rows.map(row2musica);
    },
    musica: async (_: any, { id }: { id: number }) => {
      const r = await pool.query("SELECT * FROM musicas WHERE id=$1", [id]);
      return r.rows[0] ? row2musica(r.rows[0]) : null;
    },
    playlists: async () => {
      const r = await pool.query("SELECT * FROM playlists ORDER BY id");
      return Promise.all(r.rows.map(row2playlist));
    },
    playlist: async (_: any, { id }: { id: number }) => {
      const r = await pool.query("SELECT * FROM playlists WHERE id=$1", [id]);
      return r.rows[0] ? row2playlist(r.rows[0]) : null;
    },
    // Q3
    playlistsDoUsuario: async (_: any, { usuarioId }: { usuarioId: number }) => {
      const r = await pool.query("SELECT * FROM playlists WHERE usuario_id=$1 ORDER BY id", [usuarioId]);
      return Promise.all(r.rows.map(row2playlist));
    },
    // Q4
    musicasDaPlaylist: async (_: any, { playlistId }: { playlistId: number }) => {
      return musicas_da_playlist(playlistId);
    },
    // Q5
    playlistsComMusica: async (_: any, { musicaId }: { musicaId: number }) => {
      const r = await pool.query(
        `SELECT p.* FROM playlists p
         JOIN playlist_musicas pm ON p.id = pm.playlist_id
         WHERE pm.musica_id = $1 ORDER BY p.id`,
        [musicaId]
      );
      return Promise.all(r.rows.map(row2playlist));
    },
  },

  Mutation: {
    criarUsuario: async (_: any, { dados }: any) => {
      const r = await pool.query(
        "INSERT INTO usuarios (nome, email) VALUES ($1,$2) RETURNING *",
        [dados.nome, dados.email]
      );
      return row2usuario(r.rows[0]);
    },
    atualizarUsuario: async (_: any, { id, dados }: any) => {
      const cur = await pool.query("SELECT * FROM usuarios WHERE id=$1", [id]);
      if (!cur.rows[0]) return null;
      const a = cur.rows[0];
      const r = await pool.query(
        "UPDATE usuarios SET nome=$1, email=$2 WHERE id=$3 RETURNING *",
        [dados.nome ?? a.nome, dados.email ?? a.email, id]
      );
      return row2usuario(r.rows[0]);
    },
    removerUsuario: async (_: any, { id }: any) => {
      const r = await pool.query("DELETE FROM usuarios WHERE id=$1 RETURNING id", [id]);
      return r.rows.length > 0;
    },

    criarMusica: async (_: any, { dados }: any) => {
      const r = await pool.query(
        "INSERT INTO musicas (titulo, artista, ano_lancamento, duracao_segundos) VALUES ($1,$2,$3,$4) RETURNING *",
        [dados.titulo, dados.artista, dados.anoLancamento ?? null, dados.duracaoSegundos ?? null]
      );
      return row2musica(r.rows[0]);
    },
    atualizarMusica: async (_: any, { id, dados }: any) => {
      const cur = await pool.query("SELECT * FROM musicas WHERE id=$1", [id]);
      if (!cur.rows[0]) return null;
      const a = cur.rows[0];
      const r = await pool.query(
        "UPDATE musicas SET titulo=$1, artista=$2, ano_lancamento=$3, duracao_segundos=$4 WHERE id=$5 RETURNING *",
        [dados.titulo ?? a.titulo, dados.artista ?? a.artista, dados.anoLancamento ?? a.ano_lancamento, dados.duracaoSegundos ?? a.duracao_segundos, id]
      );
      return row2musica(r.rows[0]);
    },
    removerMusica: async (_: any, { id }: any) => {
      const r = await pool.query("DELETE FROM musicas WHERE id=$1 RETURNING id", [id]);
      return r.rows.length > 0;
    },

    criarPlaylist: async (_: any, { dados }: any) => {
      const u = await pool.query("SELECT id FROM usuarios WHERE id=$1", [dados.usuarioId]);
      if (!u.rows[0]) return null;
      const r = await pool.query(
        "INSERT INTO playlists (nome, usuario_id) VALUES ($1,$2) RETURNING *",
        [dados.nome, dados.usuarioId]
      );
      return row2playlist(r.rows[0]);
    },
    atualizarPlaylist: async (_: any, { id, nome }: any) => {
      const r = await pool.query("UPDATE playlists SET nome=$1 WHERE id=$2 RETURNING *", [nome, id]);
      return r.rows[0] ? row2playlist(r.rows[0]) : null;
    },
    removerPlaylist: async (_: any, { id }: any) => {
      const r = await pool.query("DELETE FROM playlists WHERE id=$1 RETURNING id", [id]);
      return r.rows.length > 0;
    },

    adicionarMusicaNaPlaylist: async (_: any, { playlistId, musicaId }: any) => {
      await pool.query(
        "INSERT INTO playlist_musicas (playlist_id, musica_id) VALUES ($1,$2) ON CONFLICT DO NOTHING",
        [playlistId, musicaId]
      );
      return true;
    },
    removerMusicaDaPlaylist: async (_: any, { playlistId, musicaId }: any) => {
      const r = await pool.query(
        "DELETE FROM playlist_musicas WHERE playlist_id=$1 AND musica_id=$2 RETURNING playlist_id",
        [playlistId, musicaId]
      );
      return r.rows.length > 0;
    },
  },
};
