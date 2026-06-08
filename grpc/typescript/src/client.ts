/**
 * client.ts — Cliente gRPC TypeScript
 * Cobre: Q1-Q5 + CRUD completo de Usuario, Musica e Playlist.
 * Uso: npm run client  (servidor deve estar em localhost:8005)
 */

import * as grpc from "@grpc/grpc-js";
import * as protoLoader from "@grpc/proto-loader";
import * as path from "path";

const PROTO_PATH = path.join(__dirname, "../../streaming.proto");
const pkgDef = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
});
const proto = (grpc.loadPackageDefinition(pkgDef) as any).streaming;

const ADDR = "localhost:8005";
const creds = grpc.credentials.createInsecure();

function call<T>(stub: any, method: string, req: any): Promise<T> {
  return new Promise((resolve, reject) => {
    stub[method](req, (e: grpc.ServiceError | null, res: T) => {
      if (e) reject(e);
      else resolve(res);
    });
  });
}

function titulo(t: string) {
  console.log(`\n${"=".repeat(55)}\n  ${t}\n${"=".repeat(55)}`);
}

async function main() {
  const uStub = new proto.UsuarioService(ADDR, creds);
  const mStub = new proto.MusicaService(ADDR, creds);
  const pStub = new proto.PlaylistService(ADDR, creds);

  // criarUsuario
  titulo("CriarUsuario");
  const u: any = await call(uStub, "CriarUsuario", { nome: "Lucas gRPC", email: "lucas@grpc.com" });
  console.log(`Criado: id=${u.id} nome=${u.nome}`);

  // Q1
  titulo("Q1 - ListarUsuarios");
  const lu: any = await call(uStub, "ListarUsuarios", {});
  console.log(`Total: ${lu.usuarios.length} usuarios`);

  // atualizarUsuario
  titulo("AtualizarUsuario");
  const u2: any = await call(uStub, "AtualizarUsuario", { id: u.id, nome: "Lucas gRPC Atualizado" });
  console.log(`Atualizado: nome=${u2.nome}`);

  // criarMusica
  titulo("CriarMusica");
  const m: any = await call(mStub, "CriarMusica", { titulo: "Wave", artista: "Tom Jobim", ano_lancamento: 1967, duracao_segundos: 230 });
  console.log(`Criada: id=${m.id} titulo=${m.titulo}`);

  // Q2
  titulo("Q2 - ListarMusicas");
  const lm: any = await call(mStub, "ListarMusicas", {});
  console.log(`Total: ${lm.musicas.length} musicas`);

  // criarPlaylist
  titulo("CriarPlaylist");
  const pl: any = await call(pStub, "CriarPlaylist", { nome: "Bossa Nova TS", usuario_id: u.id });
  console.log(`Criada: id=${pl.id} nome=${pl.nome}`);

  // adicionarMusica
  titulo("AdicionarMusica");
  const r1: any = await call(pStub, "AdicionarMusica", { playlist_id: pl.id, musica_id: m.id });
  console.log(`ok=${r1.ok}`);

  // Q3
  titulo("Q3 - PlaylistsDoUsuario");
  const q3: any = await call(pStub, "PlaylistsDoUsuario", { usuario_id: u.id });
  console.log(`Playlists: ${q3.playlists.map((p: any) => p.nome)}`);

  // Q4
  titulo("Q4 - MusicasDaPlaylist");
  const q4: any = await call(pStub, "MusicasDaPlaylist", { playlist_id: pl.id });
  console.log(`Musicas: ${q4.musicas.map((ms: any) => ms.titulo)}`);

  // Q5
  titulo("Q5 - PlaylistsComMusica");
  const q5: any = await call(pStub, "PlaylistsComMusica", { musica_id: m.id });
  console.log(`Playlists: ${q5.playlists.map((p: any) => p.nome)}`);

  // removerMusica da playlist
  titulo("RemoverMusica (da playlist)");
  const r2: any = await call(pStub, "RemoverMusica", { playlist_id: pl.id, musica_id: m.id });
  console.log(`ok=${r2.ok}`);

  // removerPlaylist
  titulo("RemoverPlaylist");
  const r3: any = await call(pStub, "RemoverPlaylist", { id: pl.id });
  console.log(`ok=${r3.ok}`);

  // removerMusica do catalogo
  titulo("RemoverMusica (catalogo)");
  const r4: any = await call(mStub, "RemoverMusica", { id: m.id });
  console.log(`ok=${r4.ok}`);

  // removerUsuario
  titulo("RemoverUsuario");
  const r5: any = await call(uStub, "RemoverUsuario", { id: u.id });
  console.log(`ok=${r5.ok}`);

  console.log("\nDemo gRPC TypeScript concluida com sucesso!");
  process.exit(0);
}

main().catch((e) => { console.error(e); process.exit(1); });
