export const WSDL = `<?xml version="1.0" encoding="UTF-8"?>
<definitions name="StreamingService"
  targetNamespace="http://streaming.local/"
  xmlns="http://schemas.xmlsoap.org/wsdl/"
  xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
  xmlns:tns="http://streaming.local/"
  xmlns:xsd="http://www.w3.org/2001/XMLSchema">

  <!-- ── Tipos ─────────────────────────────────────────────── -->
  <types>
    <xsd:schema targetNamespace="http://streaming.local/">

      <xsd:complexType name="Usuario">
        <xsd:sequence>
          <xsd:element name="id"        type="xsd:int"/>
          <xsd:element name="nome"      type="xsd:string"/>
          <xsd:element name="email"     type="xsd:string"/>
          <xsd:element name="criado_em" type="xsd:string"/>
        </xsd:sequence>
      </xsd:complexType>

      <xsd:complexType name="Musica">
        <xsd:sequence>
          <xsd:element name="id"                type="xsd:int"/>
          <xsd:element name="titulo"            type="xsd:string"/>
          <xsd:element name="artista"           type="xsd:string"/>
          <xsd:element name="ano_lancamento"    type="xsd:int"/>
          <xsd:element name="duracao_segundos"  type="xsd:int"/>
          <xsd:element name="criado_em"         type="xsd:string"/>
        </xsd:sequence>
      </xsd:complexType>

      <xsd:complexType name="Playlist">
        <xsd:sequence>
          <xsd:element name="id"         type="xsd:int"/>
          <xsd:element name="nome"       type="xsd:string"/>
          <xsd:element name="usuario_id" type="xsd:int"/>
          <xsd:element name="criado_em"  type="xsd:string"/>
        </xsd:sequence>
      </xsd:complexType>

      <xsd:complexType name="ListaUsuarios">
        <xsd:sequence>
          <xsd:element name="item" type="tns:Usuario" minOccurs="0" maxOccurs="unbounded"/>
        </xsd:sequence>
      </xsd:complexType>

      <xsd:complexType name="ListaMusicas">
        <xsd:sequence>
          <xsd:element name="item" type="tns:Musica" minOccurs="0" maxOccurs="unbounded"/>
        </xsd:sequence>
      </xsd:complexType>

      <xsd:complexType name="ListaPlaylists">
        <xsd:sequence>
          <xsd:element name="item" type="tns:Playlist" minOccurs="0" maxOccurs="unbounded"/>
        </xsd:sequence>
      </xsd:complexType>

      <!-- Requests/Responses -->
      <xsd:element name="criar_usuario">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="nome"  type="xsd:string"/>
          <xsd:element name="email" type="xsd:string"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>
      <xsd:element name="criar_usuarioResponse">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="return" type="tns:Usuario"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>

      <xsd:element name="obter_usuario">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="id" type="xsd:int"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>
      <xsd:element name="obter_usuarioResponse">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="return" type="tns:Usuario"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>

      <xsd:element name="listar_usuarios">
        <xsd:complexType><xsd:sequence/></xsd:complexType>
      </xsd:element>
      <xsd:element name="listar_usuariosResponse">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="return" type="tns:ListaUsuarios"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>

      <xsd:element name="atualizar_usuario">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="id"    type="xsd:int"/>
          <xsd:element name="nome"  type="xsd:string"/>
          <xsd:element name="email" type="xsd:string"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>
      <xsd:element name="atualizar_usuarioResponse">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="return" type="tns:Usuario"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>

      <xsd:element name="remover_usuario">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="id" type="xsd:int"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>
      <xsd:element name="remover_usuarioResponse">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="return" type="xsd:boolean"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>

      <xsd:element name="criar_musica">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="titulo"           type="xsd:string"/>
          <xsd:element name="artista"          type="xsd:string"/>
          <xsd:element name="ano_lancamento"   type="xsd:int"/>
          <xsd:element name="duracao_segundos" type="xsd:int"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>
      <xsd:element name="criar_musicaResponse">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="return" type="tns:Musica"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>

      <xsd:element name="obter_musica">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="id" type="xsd:int"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>
      <xsd:element name="obter_musicaResponse">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="return" type="tns:Musica"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>

      <xsd:element name="listar_musicas">
        <xsd:complexType><xsd:sequence/></xsd:complexType>
      </xsd:element>
      <xsd:element name="listar_musicasResponse">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="return" type="tns:ListaMusicas"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>

      <xsd:element name="atualizar_musica">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="id"               type="xsd:int"/>
          <xsd:element name="titulo"           type="xsd:string"/>
          <xsd:element name="artista"          type="xsd:string"/>
          <xsd:element name="ano_lancamento"   type="xsd:int"/>
          <xsd:element name="duracao_segundos" type="xsd:int"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>
      <xsd:element name="atualizar_musicaResponse">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="return" type="tns:Musica"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>

      <xsd:element name="remover_musica">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="id" type="xsd:int"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>
      <xsd:element name="remover_musicaResponse">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="return" type="xsd:boolean"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>

      <xsd:element name="criar_playlist">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="nome"       type="xsd:string"/>
          <xsd:element name="usuario_id" type="xsd:int"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>
      <xsd:element name="criar_playlistResponse">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="return" type="tns:Playlist"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>

      <xsd:element name="obter_playlist">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="id" type="xsd:int"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>
      <xsd:element name="obter_playlistResponse">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="return" type="tns:Playlist"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>

      <xsd:element name="listar_playlists">
        <xsd:complexType><xsd:sequence/></xsd:complexType>
      </xsd:element>
      <xsd:element name="listar_playlistsResponse">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="return" type="tns:ListaPlaylists"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>

      <xsd:element name="atualizar_playlist">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="id"   type="xsd:int"/>
          <xsd:element name="nome" type="xsd:string"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>
      <xsd:element name="atualizar_playlistResponse">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="return" type="tns:Playlist"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>

      <xsd:element name="remover_playlist">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="id" type="xsd:int"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>
      <xsd:element name="remover_playlistResponse">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="return" type="xsd:boolean"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>

      <xsd:element name="adicionar_musica_na_playlist">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="playlist_id" type="xsd:int"/>
          <xsd:element name="musica_id"   type="xsd:int"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>
      <xsd:element name="adicionar_musica_na_playlistResponse">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="return" type="xsd:boolean"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>

      <xsd:element name="remover_musica_da_playlist">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="playlist_id" type="xsd:int"/>
          <xsd:element name="musica_id"   type="xsd:int"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>
      <xsd:element name="remover_musica_da_playlistResponse">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="return" type="xsd:boolean"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>

      <xsd:element name="playlists_do_usuario">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="usuario_id" type="xsd:int"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>
      <xsd:element name="playlists_do_usuarioResponse">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="return" type="tns:ListaPlaylists"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>

      <xsd:element name="musicas_da_playlist">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="playlist_id" type="xsd:int"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>
      <xsd:element name="musicas_da_playlistResponse">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="return" type="tns:ListaMusicas"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>

      <xsd:element name="playlists_com_musica">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="musica_id" type="xsd:int"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>
      <xsd:element name="playlists_com_musicaResponse">
        <xsd:complexType><xsd:sequence>
          <xsd:element name="return" type="tns:ListaPlaylists"/>
        </xsd:sequence></xsd:complexType>
      </xsd:element>

    </xsd:schema>
  </types>

  <!-- ── Mensagens ─────────────────────────────────────────── -->
  <message name="criar_usuarioRequest">   <part name="parameters" element="tns:criar_usuario"/></message>
  <message name="criar_usuarioResponse">  <part name="parameters" element="tns:criar_usuarioResponse"/></message>
  <message name="obter_usuarioRequest">   <part name="parameters" element="tns:obter_usuario"/></message>
  <message name="obter_usuarioResponse">  <part name="parameters" element="tns:obter_usuarioResponse"/></message>
  <message name="listar_usuariosRequest"> <part name="parameters" element="tns:listar_usuarios"/></message>
  <message name="listar_usuariosResponse"><part name="parameters" element="tns:listar_usuariosResponse"/></message>
  <message name="atualizar_usuarioRequest">  <part name="parameters" element="tns:atualizar_usuario"/></message>
  <message name="atualizar_usuarioResponse"> <part name="parameters" element="tns:atualizar_usuarioResponse"/></message>
  <message name="remover_usuarioRequest">  <part name="parameters" element="tns:remover_usuario"/></message>
  <message name="remover_usuarioResponse"> <part name="parameters" element="tns:remover_usuarioResponse"/></message>

  <message name="criar_musicaRequest">   <part name="parameters" element="tns:criar_musica"/></message>
  <message name="criar_musicaResponse">  <part name="parameters" element="tns:criar_musicaResponse"/></message>
  <message name="obter_musicaRequest">   <part name="parameters" element="tns:obter_musica"/></message>
  <message name="obter_musicaResponse">  <part name="parameters" element="tns:obter_musicaResponse"/></message>
  <message name="listar_musicasRequest"> <part name="parameters" element="tns:listar_musicas"/></message>
  <message name="listar_musicasResponse"><part name="parameters" element="tns:listar_musicasResponse"/></message>
  <message name="atualizar_musicaRequest">  <part name="parameters" element="tns:atualizar_musica"/></message>
  <message name="atualizar_musicaResponse"> <part name="parameters" element="tns:atualizar_musicaResponse"/></message>
  <message name="remover_musicaRequest">  <part name="parameters" element="tns:remover_musica"/></message>
  <message name="remover_musicaResponse"> <part name="parameters" element="tns:remover_musicaResponse"/></message>

  <message name="criar_playlistRequest">   <part name="parameters" element="tns:criar_playlist"/></message>
  <message name="criar_playlistResponse">  <part name="parameters" element="tns:criar_playlistResponse"/></message>
  <message name="obter_playlistRequest">   <part name="parameters" element="tns:obter_playlist"/></message>
  <message name="obter_playlistResponse">  <part name="parameters" element="tns:obter_playlistResponse"/></message>
  <message name="listar_playlistsRequest"> <part name="parameters" element="tns:listar_playlists"/></message>
  <message name="listar_playlistsResponse"><part name="parameters" element="tns:listar_playlistsResponse"/></message>
  <message name="atualizar_playlistRequest">  <part name="parameters" element="tns:atualizar_playlist"/></message>
  <message name="atualizar_playlistResponse"> <part name="parameters" element="tns:atualizar_playlistResponse"/></message>
  <message name="remover_playlistRequest">  <part name="parameters" element="tns:remover_playlist"/></message>
  <message name="remover_playlistResponse"> <part name="parameters" element="tns:remover_playlistResponse"/></message>
  <message name="adicionar_musica_na_playlistRequest">  <part name="parameters" element="tns:adicionar_musica_na_playlist"/></message>
  <message name="adicionar_musica_na_playlistResponse"> <part name="parameters" element="tns:adicionar_musica_na_playlistResponse"/></message>
  <message name="remover_musica_da_playlistRequest">  <part name="parameters" element="tns:remover_musica_da_playlist"/></message>
  <message name="remover_musica_da_playlistResponse"> <part name="parameters" element="tns:remover_musica_da_playlistResponse"/></message>
  <message name="playlists_do_usuarioRequest">  <part name="parameters" element="tns:playlists_do_usuario"/></message>
  <message name="playlists_do_usuarioResponse"> <part name="parameters" element="tns:playlists_do_usuarioResponse"/></message>
  <message name="musicas_da_playlistRequest">  <part name="parameters" element="tns:musicas_da_playlist"/></message>
  <message name="musicas_da_playlistResponse"> <part name="parameters" element="tns:musicas_da_playlistResponse"/></message>
  <message name="playlists_com_musicaRequest">  <part name="parameters" element="tns:playlists_com_musica"/></message>
  <message name="playlists_com_musicaResponse"> <part name="parameters" element="tns:playlists_com_musicaResponse"/></message>

  <!-- ── PortType ──────────────────────────────────────────── -->
  <portType name="StreamingPortType">
    <operation name="criar_usuario">   <input message="tns:criar_usuarioRequest"/>   <output message="tns:criar_usuarioResponse"/></operation>
    <operation name="obter_usuario">   <input message="tns:obter_usuarioRequest"/>   <output message="tns:obter_usuarioResponse"/></operation>
    <operation name="listar_usuarios"> <input message="tns:listar_usuariosRequest"/> <output message="tns:listar_usuariosResponse"/></operation>
    <operation name="atualizar_usuario"><input message="tns:atualizar_usuarioRequest"/><output message="tns:atualizar_usuarioResponse"/></operation>
    <operation name="remover_usuario"> <input message="tns:remover_usuarioRequest"/> <output message="tns:remover_usuarioResponse"/></operation>
    <operation name="criar_musica">    <input message="tns:criar_musicaRequest"/>    <output message="tns:criar_musicaResponse"/></operation>
    <operation name="obter_musica">    <input message="tns:obter_musicaRequest"/>    <output message="tns:obter_musicaResponse"/></operation>
    <operation name="listar_musicas">  <input message="tns:listar_musicasRequest"/>  <output message="tns:listar_musicasResponse"/></operation>
    <operation name="atualizar_musica"><input message="tns:atualizar_musicaRequest"/><output message="tns:atualizar_musicaResponse"/></operation>
    <operation name="remover_musica">  <input message="tns:remover_musicaRequest"/>  <output message="tns:remover_musicaResponse"/></operation>
    <operation name="criar_playlist">  <input message="tns:criar_playlistRequest"/>  <output message="tns:criar_playlistResponse"/></operation>
    <operation name="obter_playlist">  <input message="tns:obter_playlistRequest"/>  <output message="tns:obter_playlistResponse"/></operation>
    <operation name="listar_playlists"><input message="tns:listar_playlistsRequest"/><output message="tns:listar_playlistsResponse"/></operation>
    <operation name="atualizar_playlist"><input message="tns:atualizar_playlistRequest"/><output message="tns:atualizar_playlistResponse"/></operation>
    <operation name="remover_playlist"><input message="tns:remover_playlistRequest"/><output message="tns:remover_playlistResponse"/></operation>
    <operation name="adicionar_musica_na_playlist"><input message="tns:adicionar_musica_na_playlistRequest"/><output message="tns:adicionar_musica_na_playlistResponse"/></operation>
    <operation name="remover_musica_da_playlist"><input message="tns:remover_musica_da_playlistRequest"/><output message="tns:remover_musica_da_playlistResponse"/></operation>
    <operation name="playlists_do_usuario"><input message="tns:playlists_do_usuarioRequest"/><output message="tns:playlists_do_usuarioResponse"/></operation>
    <operation name="musicas_da_playlist"><input message="tns:musicas_da_playlistRequest"/><output message="tns:musicas_da_playlistResponse"/></operation>
    <operation name="playlists_com_musica"><input message="tns:playlists_com_musicaRequest"/><output message="tns:playlists_com_musicaResponse"/></operation>
  </portType>

  <!-- ── Binding ───────────────────────────────────────────── -->
  <binding name="StreamingBinding" type="tns:StreamingPortType">
    <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
    <operation name="criar_usuario">   <soap:operation soapAction="criar_usuario"/>   <input><soap:body use="literal"/></input>   <output><soap:body use="literal"/></output></operation>
    <operation name="obter_usuario">   <soap:operation soapAction="obter_usuario"/>   <input><soap:body use="literal"/></input>   <output><soap:body use="literal"/></output></operation>
    <operation name="listar_usuarios"> <soap:operation soapAction="listar_usuarios"/> <input><soap:body use="literal"/></input>   <output><soap:body use="literal"/></output></operation>
    <operation name="atualizar_usuario"><soap:operation soapAction="atualizar_usuario"/><input><soap:body use="literal"/></input><output><soap:body use="literal"/></output></operation>
    <operation name="remover_usuario"> <soap:operation soapAction="remover_usuario"/> <input><soap:body use="literal"/></input>   <output><soap:body use="literal"/></output></operation>
    <operation name="criar_musica">    <soap:operation soapAction="criar_musica"/>    <input><soap:body use="literal"/></input>   <output><soap:body use="literal"/></output></operation>
    <operation name="obter_musica">    <soap:operation soapAction="obter_musica"/>    <input><soap:body use="literal"/></input>   <output><soap:body use="literal"/></output></operation>
    <operation name="listar_musicas">  <soap:operation soapAction="listar_musicas"/>  <input><soap:body use="literal"/></input>   <output><soap:body use="literal"/></output></operation>
    <operation name="atualizar_musica"><soap:operation soapAction="atualizar_musica"/><input><soap:body use="literal"/></input>   <output><soap:body use="literal"/></output></operation>
    <operation name="remover_musica">  <soap:operation soapAction="remover_musica"/>  <input><soap:body use="literal"/></input>   <output><soap:body use="literal"/></output></operation>
    <operation name="criar_playlist">  <soap:operation soapAction="criar_playlist"/>  <input><soap:body use="literal"/></input>   <output><soap:body use="literal"/></output></operation>
    <operation name="obter_playlist">  <soap:operation soapAction="obter_playlist"/>  <input><soap:body use="literal"/></input>   <output><soap:body use="literal"/></output></operation>
    <operation name="listar_playlists"><soap:operation soapAction="listar_playlists"/><input><soap:body use="literal"/></input>   <output><soap:body use="literal"/></output></operation>
    <operation name="atualizar_playlist"><soap:operation soapAction="atualizar_playlist"/><input><soap:body use="literal"/></input><output><soap:body use="literal"/></output></operation>
    <operation name="remover_playlist"><soap:operation soapAction="remover_playlist"/><input><soap:body use="literal"/></input>   <output><soap:body use="literal"/></output></operation>
    <operation name="adicionar_musica_na_playlist"><soap:operation soapAction="adicionar_musica_na_playlist"/><input><soap:body use="literal"/></input><output><soap:body use="literal"/></output></operation>
    <operation name="remover_musica_da_playlist"><soap:operation soapAction="remover_musica_da_playlist"/><input><soap:body use="literal"/></input><output><soap:body use="literal"/></output></operation>
    <operation name="playlists_do_usuario"><soap:operation soapAction="playlists_do_usuario"/><input><soap:body use="literal"/></input><output><soap:body use="literal"/></output></operation>
    <operation name="musicas_da_playlist"><soap:operation soapAction="musicas_da_playlist"/><input><soap:body use="literal"/></input><output><soap:body use="literal"/></output></operation>
    <operation name="playlists_com_musica"><soap:operation soapAction="playlists_com_musica"/><input><soap:body use="literal"/></input><output><soap:body use="literal"/></output></operation>
  </binding>

  <!-- ── Service ───────────────────────────────────────────── -->
  <service name="StreamingService">
    <port name="StreamingPort" binding="tns:StreamingBinding">
      <soap:address location="http://localhost:8007/"/>
    </port>
  </service>

</definitions>`;
