/**
 * client.ts — Cliente GraphQL TypeScript (fetch nativo)
 * Cobre: Q1-Q5, criar/atualizar/remover Usuario, Musica e Playlist.
 * Uso: npm run client  (servidor deve estar em http://localhost:4000)
 */

const GQL_URL = "http://localhost:4000/";

async function gql(query: string, variables: Record<string, unknown> = {}) {
  const res = await fetch(GQL_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, variables }),
  });
  const json = (await res.json()) as { data?: any; errors?: any[] };
  if (json.errors) { console.error("Erro GraphQL:", json.errors); process.exit(1); }
  return json.data;
}

function titulo(t: string) { console.log(`\n${"=".repeat(55)}\n  ${t}\n${"=".repeat(55)}`); }

async function main() {
  // criar_usuario
  titulo("criarUsuario");
  let d = await gql(`mutation($nome:String!,$email:String!){criarUsuario(dados:{nome:$nome,email:$email}){id nome email criadoEm}}`,
    { nome: "Diego Nunes", email: "diego@demo.com" });
  console.log(JSON.stringify(d, null, 2));
  const uid: number = d.criarUsuario.id;

  // Q1
  titulo("Q1 - usuarios");
  d = await gql(`{usuarios{id nome}}`);
  console.log(`Total: ${d.usuarios.length} usuarios`);

  // criarMusica
  titulo("criarMusica");
  d = await gql(`mutation($t:String!,$a:String!){criarMusica(dados:{titulo:$t,artista:$a,anoLancamento:2001,duracaoSegundos:195}){id titulo artista}}`,
    { t: "Samba de Uma Nota Só", a: "João Gilberto" });
  console.log(JSON.stringify(d, null, 2));
  const mid: number = d.criarMusica.id;

  // Q2
  titulo("Q2 - musicas");
  d = await gql(`{musicas{id titulo}}`);
  console.log(`Total: ${d.musicas.length} musicas`);

  // criarPlaylist
  titulo("criarPlaylist");
  d = await gql(`mutation($nome:String!,$uid:Int!){criarPlaylist(dados:{nome:$nome,usuarioId:$uid}){id nome usuarioId}}`,
    { nome: "Playlist TS", uid });
  console.log(JSON.stringify(d, null, 2));
  const pid: number = d.criarPlaylist.id;

  // adicionarMusicaNaPlaylist
  titulo("adicionarMusicaNaPlaylist");
  d = await gql(`mutation($pid:Int!,$mid:Int!){adicionarMusicaNaPlaylist(playlistId:$pid,musicaId:$mid)}`, { pid, mid });
  console.log("ok:", d.adicionarMusicaNaPlaylist);

  // Q3
  titulo("Q3 - playlistsDoUsuario");
  d = await gql(`query($uid:Int!){playlistsDoUsuario(usuarioId:$uid){id nome}}`, { uid });
  console.log(JSON.stringify(d, null, 2));

  // Q4
  titulo("Q4 - musicasDaPlaylist");
  d = await gql(`query($pid:Int!){musicasDaPlaylist(playlistId:$pid){id titulo}}`, { pid });
  console.log(JSON.stringify(d, null, 2));

  // Q5
  titulo("Q5 - playlistsComMusica");
  d = await gql(`query($mid:Int!){playlistsComMusica(musicaId:$mid){id nome}}`, { mid });
  console.log(JSON.stringify(d, null, 2));

  // atualizarUsuario
  titulo("atualizarUsuario");
  d = await gql(`mutation($id:Int!){atualizarUsuario(id:$id,dados:{nome:"Diego Costa"}){id nome}}`, { id: uid });
  console.log(JSON.stringify(d, null, 2));

  // removerMusicaDaPlaylist
  titulo("removerMusicaDaPlaylist");
  d = await gql(`mutation($pid:Int!,$mid:Int!){removerMusicaDaPlaylist(playlistId:$pid,musicaId:$mid)}`, { pid, mid });
  console.log("ok:", d.removerMusicaDaPlaylist);

  // removerPlaylist
  titulo("removerPlaylist");
  d = await gql(`mutation($id:Int!){removerPlaylist(id:$id)}`, { id: pid });
  console.log("ok:", d.removerPlaylist);

  // removerMusica
  titulo("removerMusica");
  d = await gql(`mutation($id:Int!){removerMusica(id:$id)}`, { id: mid });
  console.log("ok:", d.removerMusica);

  // removerUsuario
  titulo("removerUsuario");
  d = await gql(`mutation($id:Int!){removerUsuario(id:$id)}`, { id: uid });
  console.log("ok:", d.removerUsuario);

  console.log("\nDemo GraphQL TypeScript concluida com sucesso!");
}

main().catch((e) => { console.error(e); process.exit(1); });
