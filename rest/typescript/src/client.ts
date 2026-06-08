/**
 * client.ts — Cliente de demonstração REST (TypeScript / fetch nativo Node 18+)
 * Cobre todas as operações: U1-U5, M1-M5, P1-P7, Q1-Q5
 *
 * Uso: npm run client  (servidor deve estar em http://localhost:8001)
 */

const BASE = "http://localhost:8001";

async function req(
  method: string,
  path: string,
  body?: object
): Promise<{ status: number; data: unknown }> {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  let data: unknown;
  try { data = JSON.parse(text); } catch { data = text; }
  return { status: res.status, data };
}

function titulo(t: string) {
  console.log(`\n${"=".repeat(55)}\n  ${t}\n${"=".repeat(55)}`);
}

function exibir(r: { status: number; data: unknown }) {
  if (Array.isArray(r.data)) {
    const arr = r.data as unknown[];
    console.log(`[${arr.length} itens] primeiro: ${JSON.stringify(arr[0])}`);
  } else {
    console.log(JSON.stringify(r.data, null, 2));
  }
  console.log(`→ HTTP ${r.status}`);
}

async function main() {
  // U1
  titulo("U1 - Criar usuario");
  let r = await req("POST", "/usuarios", { nome: "Bruno Melo", email: "bruno@demo.com" });
  exibir(r);
  if (r.status !== 201) { console.error("Servidor não está rodando?"); process.exit(1); }
  const usuarioId = (r.data as any).id as number;

  // U2/Q1
  titulo("U2/Q1 - Listar todos os usuarios");
  r = await req("GET", "/usuarios");
  console.log(`Total: ${(r.data as any[]).length} usuarios  → HTTP ${r.status}`);

  // U3
  titulo(`U3 - Buscar usuario id=${usuarioId}`);
  r = await req("GET", `/usuarios/${usuarioId}`);
  exibir(r);

  // M1
  titulo("M1 - Criar musica");
  r = await req("POST", "/musicas", { titulo: "Garota de Ipanema", artista: "Tom Jobim", ano_lancamento: 1962, duracao_segundos: 258 });
  exibir(r);
  const musicaId = (r.data as any).id as number;

  // M2/Q2
  titulo("M2/Q2 - Listar todas as musicas");
  r = await req("GET", "/musicas");
  console.log(`Total: ${(r.data as any[]).length} musicas  → HTTP ${r.status}`);

  // P1
  titulo(`P1 - Criar playlist para usuario id=${usuarioId}`);
  r = await req("POST", "/playlists", { nome: "Bossa Nova", usuario_id: usuarioId });
  exibir(r);
  const playlistId = (r.data as any).id as number;

  // P6
  titulo(`P6 - Adicionar musica id=${musicaId} na playlist id=${playlistId}`);
  r = await req("POST", `/playlists/${playlistId}/musicas`, { musica_id: musicaId });
  console.log(`→ HTTP ${r.status}`);

  // Q3
  titulo(`Q3 - Playlists do usuario id=${usuarioId}`);
  r = await req("GET", `/usuarios/${usuarioId}/playlists`);
  exibir(r);

  // Q4
  titulo(`Q4 - Musicas da playlist id=${playlistId}`);
  r = await req("GET", `/playlists/${playlistId}/musicas`);
  exibir(r);

  // Q5
  titulo(`Q5 - Playlists que contem musica id=${musicaId}`);
  r = await req("GET", `/musicas/${musicaId}/playlists`);
  exibir(r);

  // U4
  titulo(`U4 - Atualizar usuario id=${usuarioId}`);
  r = await req("PUT", `/usuarios/${usuarioId}`, { nome: "Bruno Lima" });
  exibir(r);

  // P4
  titulo(`P4 - Atualizar playlist id=${playlistId}`);
  r = await req("PUT", `/playlists/${playlistId}`, { nome: "Bossa Nova Classica" });
  exibir(r);

  // P7
  titulo(`P7 - Remover musica id=${musicaId} da playlist id=${playlistId}`);
  r = await req("DELETE", `/playlists/${playlistId}/musicas/${musicaId}`);
  console.log(`→ HTTP ${r.status}`);

  // P5
  titulo(`P5 - Remover playlist id=${playlistId}`);
  r = await req("DELETE", `/playlists/${playlistId}`);
  console.log(`→ HTTP ${r.status}`);

  // M5
  titulo(`M5 - Remover musica id=${musicaId}`);
  r = await req("DELETE", `/musicas/${musicaId}`);
  console.log(`→ HTTP ${r.status}`);

  // U5
  titulo(`U5 - Remover usuario id=${usuarioId}`);
  r = await req("DELETE", `/usuarios/${usuarioId}`);
  console.log(`→ HTTP ${r.status}`);

  console.log("\nDemo concluida com sucesso!");
}

main().catch((e) => { console.error(e); process.exit(1); });
