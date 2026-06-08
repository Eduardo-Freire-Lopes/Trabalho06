export const typeDefs = `#graphql
  type Usuario {
    id: Int!
    nome: String!
    email: String!
    criadoEm: String!
    playlists: [Playlist!]!
  }

  type Musica {
    id: Int!
    titulo: String!
    artista: String!
    anoLancamento: Int
    duracaoSegundos: Int
    criadoEm: String!
  }

  type Playlist {
    id: Int!
    nome: String!
    usuarioId: Int!
    criadoEm: String!
    musicas: [Musica!]!
  }

  input UsuarioInput {
    nome: String!
    email: String!
  }

  input UsuarioUpdateInput {
    nome: String
    email: String
  }

  input MusicaInput {
    titulo: String!
    artista: String!
    anoLancamento: Int
    duracaoSegundos: Int
  }

  input MusicaUpdateInput {
    titulo: String
    artista: String
    anoLancamento: Int
    duracaoSegundos: Int
  }

  input PlaylistInput {
    nome: String!
    usuarioId: Int!
  }

  type Query {
    # Q1
    usuarios: [Usuario!]!
    usuario(id: Int!): Usuario
    # Q2
    musicas: [Musica!]!
    musica(id: Int!): Musica
    playlists: [Playlist!]!
    playlist(id: Int!): Playlist
    # Q3
    playlistsDoUsuario(usuarioId: Int!): [Playlist!]!
    # Q4
    musicasDaPlaylist(playlistId: Int!): [Musica!]!
    # Q5
    playlistsComMusica(musicaId: Int!): [Playlist!]!
  }

  type Mutation {
    criarUsuario(dados: UsuarioInput!): Usuario!
    atualizarUsuario(id: Int!, dados: UsuarioUpdateInput!): Usuario
    removerUsuario(id: Int!): Boolean!

    criarMusica(dados: MusicaInput!): Musica!
    atualizarMusica(id: Int!, dados: MusicaUpdateInput!): Musica
    removerMusica(id: Int!): Boolean!

    criarPlaylist(dados: PlaylistInput!): Playlist
    atualizarPlaylist(id: Int!, nome: String!): Playlist
    removerPlaylist(id: Int!): Boolean!

    adicionarMusicaNaPlaylist(playlistId: Int!, musicaId: Int!): Boolean!
    removerMusicaDaPlaylist(playlistId: Int!, musicaId: Int!): Boolean!
  }
`;
