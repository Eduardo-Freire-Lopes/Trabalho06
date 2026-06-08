/**
 * client.ts — Cliente SOAP TypeScript usando a biblioteca soap
 * Cobre: Q1-Q5 + CRUD completo de Usuario, Musica e Playlist.
 * Uso: npm run client  (servidor deve estar em http://localhost:8007)
 */

import * as soap from "soap";

const WSDL_URL = "http://localhost:8007/?wsdl";

function titulo(t: string) {
  console.log(`\n${"=".repeat(55)}\n  ${t}\n${"=".repeat(55)}`);
}

function p(label: string, val: any) {
  console.log(`${label}:`, JSON.stringify(val, null, 2));
}

async function main() {
  const client = await soap.createClientAsync(WSDL_URL);

  // criar_usuario
  titulo("criar_usuario");
  let [res] = await client.criar_usuarioAsync({ nome: "Fernanda SOAP", email: "fernanda@soap.com" });
  const u = res.return;
  p("Criado", u);

  // Q1
  titulo("Q1 - listar_usuarios");
  [res] = await client.listar_usuariosAsync({});
  const lu = res.return?.item ?? [];
  console.log(`Total: ${lu.length} usuarios`);

  // atualizar_usuario
  titulo("atualizar_usuario");
  [res] = await client.atualizar_usuarioAsync({ id: u.id, nome: "Fernanda SOAP Atualizada", email: u.email });
  p("Atualizado", res.return);

  // criar_musica
  titulo("criar_musica");
  [res] = await client.criar_musicaAsync({ titulo: "Aguas de Marco", artista: "Tom Jobim", ano_lancamento: 1972, duracao_segundos: 210 });
  const m = res.return;
  p("Criada", m);

  // Q2
  titulo("Q2 - listar_musicas");
  [res] = await client.listar_musicasAsync({});
  const lm = res.return?.item ?? [];
  console.log(`Total: ${lm.length} musicas`);

  // criar_playlist
  titulo("criar_playlist");
  [res] = await client.criar_playlistAsync({ nome: "Bossa SOAP TS", usuario_id: u.id });
  const pl = res.return;
  p("Criada", pl);

  // adicionar_musica_na_playlist
  titulo("adicionar_musica_na_playlist");
  [res] = await client.adicionar_musica_na_playlistAsync({ playlist_id: pl.id, musica_id: m.id });
  console.log("ok:", res.return);

  // Q3
  titulo("Q3 - playlists_do_usuario");
  [res] = await client.playlists_do_usuarioAsync({ usuario_id: u.id });
  const q3 = res.return?.item ?? [];
  console.log("Playlists:", q3.map((x: any) => x.nome));

  // Q4
  titulo("Q4 - musicas_da_playlist");
  [res] = await client.musicas_da_playlistAsync({ playlist_id: pl.id });
  const q4 = res.return?.item ?? [];
  console.log("Musicas:", q4.map((x: any) => x.titulo));

  // Q5
  titulo("Q5 - playlists_com_musica");
  [res] = await client.playlists_com_musicaAsync({ musica_id: m.id });
  const q5 = res.return?.item ?? [];
  console.log("Playlists:", q5.map((x: any) => x.nome));

  // remover_musica_da_playlist
  titulo("remover_musica_da_playlist");
  [res] = await client.remover_musica_da_playlistAsync({ playlist_id: pl.id, musica_id: m.id });
  console.log("ok:", res.return);

  // remover_playlist
  titulo("remover_playlist");
  [res] = await client.remover_playlistAsync({ id: pl.id });
  console.log("ok:", res.return);

  // remover_musica
  titulo("remover_musica");
  [res] = await client.remover_musicaAsync({ id: m.id });
  console.log("ok:", res.return);

  // remover_usuario
  titulo("remover_usuario");
  [res] = await client.remover_usuarioAsync({ id: u.id });
  console.log("ok:", res.return);

  console.log("\nDemo SOAP TypeScript concluida com sucesso!");
  process.exit(0);
}

main().catch((e) => { console.error(e); process.exit(1); });
