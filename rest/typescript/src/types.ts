// Tipos compartilhados que espelham as entidades do banco
export interface Usuario {
  id: number;
  nome: string;
  email: string;
  criado_em: string;
}

export interface Musica {
  id: number;
  titulo: string;
  artista: string;
  ano_lancamento: number | null;
  duracao_segundos: number | null;
  criado_em: string;
}

export interface Playlist {
  id: number;
  nome: string;
  usuario_id: number;
  criado_em: string;
}
