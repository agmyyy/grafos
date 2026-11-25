"""
Gera uma página HTML para visualizar o digrafo, os ciclos, as SCCs e a condensação.

A página só MOSTRA resultados: quem calcula são os algoritmos ciclos.py, scc.py e condensacao.py.
"""

import json
from src.grafo import Digrafo


# Função responsável por reunir e organizar os resultados dos algoritmos.
# Ela não calcula ciclos nem componentes fortemente conexas.
# Apenas prepara os dados para que a página HTML consiga utilizá-los.
def montar_dados(
    g: Digrafo,  # Grafo original do projeto.
    titulo: str = "Dependências",  # Título que aparecerá na página.
    sccs: list[list[str]] | None = None,  # Componentes fortemente conexas encontradas.
    ciclo: list[str] | None = None,  # Um ciclo encontrado no grafo.
    g_cond: Digrafo | None = None,  # Grafo condensado.
    mapa_scc: dict[str, int] | None = None,  # Relaciona cada vértice à sua SCC.
    ordem_topologica: list[str] | None = None,  # Ordem topológica do grafo condensado.
    ciclos: list[list[str]] | None = None,  # Lista de ciclos encontrados.
    ciclos_truncado: bool = False,  # Indica se existem mais ciclos que os exibidos.
) -> dict:
    """Converte os resultados da equipe no JSON que a página consome."""

    # Cria um dicionário chamado dados.
    # Ele reúne todas as informações que serão enviadas para a página HTML.
    dados: dict = {
        # Armazena o título da página.
        "titulo": titulo,
        # Obtém todos os vértices do grafo original.
        # Cada vértice representa um módulo do projeto.
        "nos": g.vertices(),
        # Obtém todos os arcos (ligações) do grafo.
        # list(a) converte cada arco em uma lista.
        "arcos": [list(a) for a in g.arcos()],
        # Se as SCCs foram fornecidas, organiza os vértices de cada componente
        # em ordem alfabética utilizando sorted().
        # Caso contrário, armazena None.
        "sccs": [sorted(c) for c in sccs] if sccs is not None else None,
        # Armazena um ciclo encontrado pelo algoritmo.
        "ciclo": ciclo,
        # Armazena a lista de ciclos.
        # Se ciclos não for None, utiliza a lista recebida.
        # Caso contrário, verifica se existe um ciclo individual.
        # Se existir, cria uma lista contendo esse ciclo.
        # Se não existir, utiliza None.
        "ciclos": ciclos if ciclos is not None else ([ciclo] if ciclo else None),
        # Informa se a quantidade de ciclos encontrados ultrapassou
        # o limite de ciclos que serão exibidos.
        "ciclos_truncado": ciclos_truncado,
        # Inicialmente, a condensação não possui dados.
        # Será preenchida somente se o grafo condensado e o mapa das SCCs
        # tiverem sido fornecidos.
        "condensacao": None,
    }

    # Verifica se os dois dados necessários para montar a condensação
    # foram fornecidos: o grafo condensado e o mapa das SCCs.
    if g_cond is not None and mapa_scc is not None:
        # Cria um dicionário vazio.
        # Ele armazenará os vértices originais agrupados por componente.
        membros: dict[int, list[str]] = {}

        # Percorre o dicionário mapa_scc.
        # v representa o vértice original.
        # i representa o identificador da SCC à qual esse vértice pertence.
        for v, i in mapa_scc.items():
            # setdefault() verifica se já existe uma lista associada ao ID i.
            # Se não existir, cria uma lista vazia.
            # Em seguida, append(v) adiciona o vértice à lista correspondente.
            membros.setdefault(i, []).append(v)

        # Adiciona ao dicionário principal as informações da condensação.
        dados["condensacao"] = {
            # Obtém os vértices do grafo condensado.
            # Cada vértice representa uma componente fortemente conexa.
            "nos": [
                # Para cada componente do grafo condensado, cria um dicionário
                # contendo seu identificador e seus vértices originais.
                {
                    "id": c,
                    # c[1:] remove o primeiro caractere do identificador.
                    # int() converte o restante para inteiro.
                    # membros.get() procura os vértices pertencentes à SCC.
                    # Se não encontrar, retorna uma lista vazia.
                    # sorted() organiza os vértices em ordem alfabética.
                    "membros": sorted(membros.get(int(c[1:]), [])),
                }
                # Percorre todos os vértices do grafo condensado.
                for c in g_cond.vertices()
            ],
            # Obtém os arcos do grafo condensado.
            "arcos": [list(a) for a in g_cond.arcos()],
            # Armazena a ordenação topológica recebida.
            "ordem": ordem_topologica,
        }

    # Retorna o dicionário com todos os dados organizados.
    return dados


# Função responsável por gerar o código HTML completo da página.
# Recebe o dicionário produzido pela função montar_dados().
def gerar_html(dados: dict) -> str:
    """Devolve o HTML completo. `dados` vem de montar_dados()."""

    # Converte o dicionário Python para uma string no formato JSON.
    #
    # ensure_ascii=False mantém caracteres especiais, como acentos,
    # sem transformá-los em sequências Unicode.
    #
    # replace("</", "<\\/") evita que uma sequência </ presente nos dados
    # seja interpretada acidentalmente como o fechamento de uma tag HTML
    # dentro do elemento que contém o JavaScript.
    carga = json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")

    # Substitui os espaços reservados existentes no modelo HTML.
    #
    # __DADOS__ recebe os dados convertidos para JSON.
    # __TITULO__ recebe o título da página.
    #
    # replace("<", "&lt;") transforma o caractere < em uma entidade HTML,
    # evitando que ele seja interpretado como o início de uma tag.
    return _MODELO.replace("__DADOS__", carga).replace(
        "__TITULO__", dados["titulo"].replace("<", "&lt;")
    )


# Armazena o modelo HTML que será utilizado como estrutura da página.
# O prefixo r antes das aspas indica uma raw string.
# Isso evita que o Python interprete determinadas barras invertidas
# como caracteres especiais.
#
# Dentro desse modelo existem espaços reservados, como __DADOS__ e
# __TITULO__, que serão substituídos pela função gerar_html().
_MODELO = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>__TITULO__ · dependências</title>
<style>
  :root { --bg:#fafafa; --painel:#fff; --borda:#d9d9d9; --texto:#222; --suave:#777;
          --azul:#1565c0; --verde:#2e7d32; --vermelho:#d32f2f; --laranja:#ef6c00; }
  * { box-sizing: border-box; }
  body { margin:0; font:13px system-ui, sans-serif; color:var(--texto); background:var(--bg);
         display:flex; height:100vh; }
  #lateral { width:330px; background:var(--painel); border-right:1px solid var(--borda);
             padding:12px; overflow-y:auto; }
  #lateral h1 { font-size:16px; margin:0 0 4px; }
  #lateral h2 { font-size:12px; text-transform:uppercase; letter-spacing:.05em; color:var(--suave);
                margin:16px 0 6px; }
  #resumo { color:var(--suave); margin-bottom:8px; }
  input[type=search] { width:100%; padding:6px 8px; border:1px solid var(--borda); border-radius:4px; }
  .linha { display:flex; gap:6px; flex-wrap:wrap; margin:8px 0; }
  button { padding:5px 9px; border:1px solid var(--borda); background:#fff; border-radius:4px; cursor:pointer; }
  button.ativo { background:var(--azul); color:#fff; border-color:var(--azul); }
  button:disabled { opacity:.45; cursor:not-allowed; }
  ul { margin:4px 0; padding-left:18px; }
  li { margin:2px 0; word-break:break-all; }
  li.clicavel { cursor:pointer; } li.clicavel:hover { text-decoration:underline; }
  .leg { display:grid; grid-template-columns:24px 1fr; gap:7px 8px; align-items:center; }
  .sw.no { width:12px; height:12px; border-radius:50%; justify-self:center; }
  .sw.arco { width:22px; height:4px; border-radius:2px; }
  .sw.multi { background:conic-gradient(#e53935 0 33%, #8e24aa 0 66%, #3949ab 0); }
  .nota { margin-top:10px; color:var(--suave); }
  .nome { font-weight:600; word-break:break-all; }
  .sec { margin-top:10px; font-weight:600; }
  .sec.azul { color:var(--azul); } .sec.verde { color:var(--verde); }
  #info button { margin:4px 0; }
  .chip { display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:6px; }
  .aviso { background:#fff8e1; border:1px solid #ffe082; padding:6px 8px; border-radius:4px; margin:6px 0; }
  .ok { color:var(--verde); } .ruim { color:var(--vermelho); }
  #palco { flex:1; position:relative; }
  svg { width:100%; height:100%; display:block; cursor:grab; }
  .no circle { stroke:#fff; stroke-width:1.5; cursor:pointer; }
  .no text { font-size:11px; pointer-events:none; fill:#222; paint-order:stroke; stroke:#fff; stroke-width:3px; }
  .esmaece { opacity:.12; }
  .selecionado circle { stroke:#000; stroke-width:3; }
  .casa circle { stroke:var(--laranja); stroke-width:4; }
  #dica { position:absolute; left:10px; bottom:8px; color:var(--suave); background:rgba(255,255,255,.85);
          padding:3px 6px; border-radius:4px; }
</style>
</head>
<body>
<div id="lateral">
  <h1>__TITULO__</h1>
  <div id="resumo"></div>
  <input id="busca" type="search" placeholder="Buscar módulo...">
  <div class="linha">
    <button id="bGrafo" class="ativo">Grafo</button>
    <button id="bCond">Condensação</button>
    <button id="bCiclo">Destacar todos os ciclos</button>
    <button id="bRotulos" class="ativo">Rótulos</button>
    <button id="bAjustar">Ajustar tela</button>
  </div>
  <div id="avisos"></div>
  <h2>Selecionado</h2>
  <div id="info">Clique em um módulo para ver suas dependências.</div>
  <h2>Ciclos encontrados</h2>
  <div id="listaCiclos"></div>
  <h2>Componentes fortemente conexas</h2>
  <div id="listaScc"></div>
  <h2 id="tOrdem" style="display:none">Ordenação topológica</h2>
  <div id="ordem"></div>
  <h2>Legenda</h2>
  <div id="legenda" class="leg">
    <span class="sw no" style="background:#90a4ae"></span><span>Módulo fora de componente cíclica</span>
    <span class="sw no multi"></span><span>Módulo em componente cíclica (uma cor por componente)</span>
    <span class="sw arco" style="background:#d32f2f"></span><span>Arco dentro de componente cíclica</span>
    <span class="sw arco" style="background:#78909c"></span><span>Arco comum</span>
    <span class="sw arco" style="background:#ef6c00"></span><span>Ciclo destacado (clique num ciclo da lista)</span>
    <span class="sw arco" style="background:#1565c0"></span><span>Dependências diretas do módulo selecionado</span>
    <span class="sw arco" style="background:#2e7d32"></span><span>Dependentes diretos do módulo selecionado</span>
    <span class="sw arco" style="background:#6a1b9a"></span><span>Alcançáveis a partir do módulo selecionado</span>
  </div>
  <div class="nota">Arco A → B: A importa B (A depende de B).</div>
</div>
<div id="palco">
  <svg id="svg">
    <defs id="defs"></defs>
    <g id="cena"></g>
  </svg>
  <div id="dica">arraste o fundo para mover · roda do mouse para zoom · arraste um módulo para reposicioná-lo</div>
</div>

<script>
const DADOS = __DADOS__;
const NS = "http://www.w3.org/2000/svg";
const PALETA = ["#e53935","#8e24aa","#3949ab","#00897b","#f9a825","#6d4c41","#d81b60","#039be5","#7cb342","#fb8c00"];
const COR_COMUM = "#90a4ae", COR_ARCO = "#78909c", COR_CICLICO = "#d32f2f";

const el = id => document.getElementById(id);
const svg = el("svg"), cena = el("cena"), defs = el("defs");

// ---------- estado ----------
let modo = "grafo";            // "grafo" | "cond"
let selecionado = null;
let mostrarCiclo = false, mostrarRotulos = true;
let cicloAtivo = null;         // índice do ciclo escolhido na lista
let mostrarAlcance = false;    // destaca tudo que o módulo selecionado alcança
let termoBusca = "";
let destaque = null;          // conjunto de módulos destacado (clique numa SCC)
let vista = {x: 0, y: 0, k: 1};
const visoes = {};             // visão (nós/arcos/posições) de cada modo

// ---------- utilidades de grafo (só leitura, para exibição) ----------
function indexar(nos, arcos) {
  const saida = new Map(nos.map(n => [n.id, new Set()]));
  const entrada = new Map(nos.map(n => [n.id, new Set()]));
  arcos.forEach(([u, v]) => { saida.get(u).add(v); entrada.get(v).add(u); });
  return {saida, entrada};
}
function alcancaveis(saida, origem) {
  const visto = new Set(), pilha = [origem];
  while (pilha.length) {
    const u = pilha.pop();
    for (const v of saida.get(u)) if (!visto.has(v)) { visto.add(v); pilha.push(v); }
  }
  return visto;
}

// ---------- visões ----------
function criarVisao(nomeModo) {
  if (nomeModo === "grafo") {
    const nos = DADOS.nos.map(id => ({id, rotulo: id}));
    const arcos = DADOS.arcos.map(([u, v]) => ({u, v}));
    return {nos, arcos};
  }
  const c = DADOS.condensacao;
  const nos = c.nos.map(n => ({id: n.id, membros: n.membros,
    rotulo: n.membros.length === 1 ? n.id + ": " + n.membros[0]
                                   : n.id + " (" + n.membros.length + " módulos)"}));
  return {nos, arcos: c.arcos.map(([u, v]) => ({u, v}))};
}

// SCC de cada módulo, e se a componente é cíclica (tamanho > 1 ou laço)
function infoScc() {
  if (!DADOS.sccs) return null;
  const comp = new Map(), ciclica = [];
  const lacos = new Set(DADOS.arcos.filter(([u, v]) => u === v).map(a => a[0]));
  DADOS.sccs.forEach((c, i) => {
    c.forEach(v => comp.set(v, i));
    ciclica.push(c.length > 1 || (c.length === 1 && lacos.has(c[0])));
  });
  const cor = new Map(); let k = 0;
  ciclica.forEach((cic, i) => { if (cic) cor.set(i, PALETA[k++ % PALETA.length]); });
  return {comp, ciclica, cor};
}
const SCC = infoScc();

// ciclos: null = não calculados; [] = grafo acíclico
const CICLOS = DADOS.ciclos || (DADOS.ciclo ? [DADOS.ciclo] : null);
const ARCOS_CICLO = CICLOS ? CICLOS.map(c => new Set(c.slice(0, -1).map((u, i) => u + "\u0000" + c[i + 1]))) : null;

// ---------- layout ----------
function layoutForca(nos, arcos, L, A) {
  const n = nos.length, idx = new Map(nos.map((d, i) => [d.id, i]));
  nos.forEach((d, i) => {
    const a = 2 * Math.PI * i / n + 0.01 * (i % 7);
    const r = Math.min(L, A) / 3 * (0.6 + 0.4 * ((i * 37) % 10) / 10);
    d.x = L / 2 + Math.cos(a) * r; d.y = A / 2 + Math.sin(a) * r;
  });
  const k = Math.sqrt(L * A / Math.max(n, 1)) * 0.38;
  let t = L / 8;
  for (let it = 0; it < 350; it++) {
    const dx = new Array(n).fill(0), dy = new Array(n).fill(0);
    for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) {
      let ex = nos[i].x - nos[j].x, ey = nos[i].y - nos[j].y;
      let d = Math.hypot(ex, ey) || 0.01;
      const f = k * k / d;
      dx[i] += ex / d * f; dy[i] += ey / d * f; dx[j] -= ex / d * f; dy[j] -= ey / d * f;
    }
    arcos.forEach(({u, v}) => {
      const i = idx.get(u), j = idx.get(v); if (i === j) return;
      let ex = nos[i].x - nos[j].x, ey = nos[i].y - nos[j].y;
      let d = Math.hypot(ex, ey) || 0.01;
      const f = d * d / k;
      dx[i] -= ex / d * f; dy[i] -= ey / d * f; dx[j] += ex / d * f; dy[j] += ey / d * f;
    });
    for (let i = 0; i < n; i++) {
      const d = Math.hypot(dx[i], dy[i]) || 0.01, m = Math.min(d, t);
      nos[i].x += dx[i] / d * m; nos[i].y += dy[i] / d * m;
      nos[i].x += (L / 2 - nos[i].x) * 0.03; nos[i].y += (A / 2 - nos[i].y) * 0.03;
    }
    t *= 0.985;
  }
  // afastamento mínimo: nenhum nó fica em cima de outro
  const minimo = 95;
  for (let rodada = 0; rodada < 60; rodada++) {
    let moveu = false;
    for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) {
      let ex = nos[j].x - nos[i].x, ey = nos[j].y - nos[i].y;
      let d = Math.hypot(ex, ey);
      if (d < minimo) {
        if (d < 0.01) { ex = 1; ey = (i % 3) - 1; d = Math.hypot(ex, ey); }
        const empurrao = (minimo - d) / 2;
        nos[i].x -= ex / d * empurrao; nos[i].y -= ey / d * empurrao;
        nos[j].x += ex / d * empurrao; nos[j].y += ey / d * empurrao;
        moveu = true;
      }
    }
    if (!moveu) break;
  }
}

// condensação: colunas = camada pela ordem topológica (dependentes à esquerda)
function layoutCamadas(nos, arcos, ordem, L, A) {
  const camada = new Map(nos.map(n => [n.id, 0]));
  const saida = new Map(nos.map(n => [n.id, []]));
  arcos.forEach(({u, v}) => saida.get(u).push(v));
  const ord = (ordem && ordem.length === nos.length) ? ordem : nos.map(n => n.id);
  ord.forEach(u => saida.get(u).forEach(v => camada.set(v, Math.max(camada.get(v), camada.get(u) + 1))));
  const porCamada = new Map();
  nos.forEach(n => { const c = camada.get(n.id); (porCamada.get(c) || porCamada.set(c, []).get(c)).push(n); });
  const nc = Math.max(...porCamada.keys()) + 1, passoX = Math.min(190, (L - 160) / Math.max(nc - 1, 1));
  porCamada.forEach((lista, c) => lista.forEach((n, i) => {
    n.x = 80 + c * passoX; n.y = A / 2 + (i - (lista.length - 1) / 2) * 70;
  }));
}

// ---------- desenho ----------
function criar(tag, attrs, pai) {
  const e = document.createElementNS(NS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (pai) pai.appendChild(e);
  return e;
}
function marcador(id, cor) {
  const m = criar("marker", {id, viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 11,
                             markerHeight: 11, markerUnits: "userSpaceOnUse",
                             orient: "auto-start-reverse"}, defs);
  criar("path", {d: "M0,0 L10,5 L0,10 z", fill: cor}, m);
}
function prepararMarcadores() {
  defs.innerHTML = "";
  [["m-comum", COR_ARCO], ["m-ciclico", COR_CICLICO], ["m-saida", "#1565c0"],
   ["m-entrada", "#2e7d32"], ["m-ciclo", "#ef6c00"], ["m-alcance", "#6a1b9a"]].forEach(([i, c]) => marcador(i, c));
}

function raioDe(n) { return modo === "cond" ? 11 + 3 * Math.sqrt(n.membros.length) : 8; }

function caminho(a, pos, existeInverso) {
  const p = pos.get(a.u), q = pos.get(a.v);
  if (a.u === a.v) {
    const r = raioDe(p);
    return `M${p.x - 4},${p.y - r} C${p.x - 30},${p.y - r - 40} ${p.x + 30},${p.y - r - 40} ${p.x + 4},${p.y - r - 1}`;
  }
  let dx = q.x - p.x, dy = q.y - p.y; const d = Math.hypot(dx, dy) || 1;
  dx /= d; dy /= d;
  const r1 = raioDe(p) + 1, r2 = raioDe(q) + 3;
  const x1 = p.x + dx * r1, y1 = p.y + dy * r1, x2 = q.x - dx * r2, y2 = q.y - dy * r2;
  if (!existeInverso) return `M${x1},${y1} L${x2},${y2}`;
  const mx = (x1 + x2) / 2 - dy * 22, my = (y1 + y2) / 2 + dx * 22;
  return `M${x1},${y1} Q${mx},${my} ${x2},${y2}`;
}

function corDoNo(n) {
  if (modo === "grafo") {
    if (!SCC) return COR_COMUM;
    const i = SCC.comp.get(n.id);
    return SCC.cor.has(i) ? SCC.cor.get(i) : COR_COMUM;
  }
  const cic = n.membros.length > 1 || DADOS.arcos.some(([u, v]) => u === v && n.membros[0] === u);
  return cic ? "#e53935" : COR_COMUM;
}
function arcoCiclico(a) {
  if (modo !== "grafo" || !SCC) return false;
  const i = SCC.comp.get(a.u);
  return i === SCC.comp.get(a.v) && SCC.ciclica[i];
}
function arcoNoCiclo(a) {
  if (modo !== "grafo" || !ARCOS_CICLO) return false;
  const k = a.u + "\u0000" + a.v;
  if (cicloAtivo !== null) return ARCOS_CICLO[cicloAtivo].has(k);
  return mostrarCiclo && ARCOS_CICLO.some(c => c.has(k));
}

function desenhar() {
  const vz = visoes[modo];
  const pos = new Map(vz.nos.map(n => [n.id, n]));
  const chave = new Set(vz.arcos.map(a => a.u + "\u0000" + a.v));
  const {saida, entrada} = indexar(vz.nos, vz.arcos.map(a => [a.u, a.v]));
  const sel = selecionado;
  const alc = (sel && mostrarAlcance) ? alcancaveis(saida, sel) : null;
  const vizSaida = sel ? saida.get(sel) : null, vizEntrada = sel ? entrada.get(sel) : null;
  const termo = termoBusca.trim().toLowerCase();

  cena.innerHTML = "";
  const gArcos = criar("g", {}, cena), gNos = criar("g", {}, cena);

  vz.arcos.forEach(a => {
    let cor = COR_ARCO, larg = 1.4, mk = "m-comum", op = 0.75;
    if (arcoCiclico(a)) { cor = COR_CICLICO; mk = "m-ciclico"; larg = 1.8; op = 0.9; }
    if (sel && alc) {
      if (a.u === sel || alc.has(a.u)) { cor = "#6a1b9a"; mk = "m-alcance"; larg = 2.4; op = 1; }
      else op = 0.08;
    } else if (sel) {
      if (a.u === sel) { cor = "#1565c0"; mk = "m-saida"; larg = 2.6; op = 1; }
      else if (a.v === sel) { cor = "#2e7d32"; mk = "m-entrada"; larg = 2.6; op = 1; }
      else op = 0.08;
    }
    if (cicloAtivo !== null && !arcoNoCiclo(a)) op = Math.min(op, 0.08);
    if (arcoNoCiclo(a)) { cor = "#ef6c00"; mk = "m-ciclo"; larg = 4; op = 1; }
    const inverso = chave.has(a.v + "\u0000" + a.u);
    criar("path", {d: caminho(a, pos, inverso), fill: "none", stroke: cor, "stroke-width": larg,
                   "stroke-opacity": op, "marker-end": `url(#${mk})`}, gArcos);
  });

  vz.nos.forEach(n => {
    const alvoSel = sel && (alc ? (n.id === sel || alc.has(n.id))
                                : (n.id === sel || vizSaida.has(n.id) || vizEntrada.has(n.id)));
    const membrosTxt = (modo === "cond" ? n.membros.join(" ") : "").toLowerCase();
    const casa = (termo && (n.id.toLowerCase().includes(termo) || membrosTxt.includes(termo)))
              || (destaque && destaque.has(n.id));
    let cls = "no";
    if (n.id === sel) cls += " selecionado";
    if (casa) cls += " casa";
    if ((sel && !alvoSel) || ((termo || destaque) && !casa)) cls += " esmaece";
    const g = criar("g", {class: cls, transform: `translate(${n.x},${n.y})`}, gNos);
    criar("circle", {r: raioDe(n), fill: corDoNo(n)}, g);
    if (mostrarRotulos || n.id === sel || casa) {
      const t = modo === "cond"
        ? criar("text", {x: 0, y: -raioDe(n) - 7, "text-anchor": "middle"}, g)
        : criar("text", {x: raioDe(n) + 4, y: 4}, g);
      t.textContent = n.rotulo;
    }
    g.addEventListener("mousedown", ev => iniciarArrasto(ev, n));
    g.addEventListener("click", ev => { ev.stopPropagation(); if (!arrastou) selecionar(n.id); });
  });
  cena.setAttribute("transform", `translate(${vista.x},${vista.y}) scale(${vista.k})`);
}

// ---------- interação ----------
let arrastou = false;
function iniciarArrasto(ev, no) {
  ev.stopPropagation(); arrastou = false;
  const k = vista.k, x0 = ev.clientX, y0 = ev.clientY, nx = no.x, ny = no.y;
  const mover = e => {
    if (Math.abs(e.clientX - x0) + Math.abs(e.clientY - y0) > 3) arrastou = true;
    no.x = nx + (e.clientX - x0) / k; no.y = ny + (e.clientY - y0) / k; desenhar();
  };
  const soltar = () => { window.removeEventListener("mousemove", mover);
                         window.removeEventListener("mouseup", soltar);
                         setTimeout(() => arrastou = false, 0); };
  window.addEventListener("mousemove", mover); window.addEventListener("mouseup", soltar);
}
svg.addEventListener("mousedown", ev => {
  const x0 = ev.clientX, y0 = ev.clientY, vx = vista.x, vy = vista.y;
  const mover = e => { vista.x = vx + e.clientX - x0; vista.y = vy + e.clientY - y0; desenhar(); };
  const soltar = () => { window.removeEventListener("mousemove", mover); window.removeEventListener("mouseup", soltar); };
  window.addEventListener("mousemove", mover); window.addEventListener("mouseup", soltar);
});
svg.addEventListener("click", () => { selecionar(null); });
svg.addEventListener("wheel", ev => {
  ev.preventDefault();
  const r = svg.getBoundingClientRect(), mx = ev.clientX - r.left, my = ev.clientY - r.top;
  const f = ev.deltaY < 0 ? 1.15 : 1 / 1.15, k2 = Math.min(4, Math.max(0.15, vista.k * f));
  vista.x = mx - (mx - vista.x) * (k2 / vista.k); vista.y = my - (my - vista.y) * (k2 / vista.k);
  vista.k = k2; desenhar();
}, {passive: false});

function ajustar() {
  const vz = visoes[modo], r = svg.getBoundingClientRect();
  const xs = vz.nos.map(n => n.x), ys = vz.nos.map(n => n.y);
  const x0 = Math.min(...xs) - 60, x1 = Math.max(...xs) + 220, y0 = Math.min(...ys) - 60, y1 = Math.max(...ys) + 60;
  const k = Math.min(r.width / (x1 - x0), r.height / (y1 - y0), 1.25);
  vista = {k, x: (r.width - (x1 - x0) * k) / 2 - x0 * k, y: (r.height - (y1 - y0) * k) / 2 - y0 * k};
  desenhar();
}

function ul(itens, clicavel) {
  if (!itens.length) return "<i>nenhum</i>";
  return "<ul>" + itens.map(i => `<li${clicavel ? ' class="clicavel" data-id="' + i + '"' : ""}>${i}</li>`).join("") + "</ul>";
}
function ligarCliques(raiz) {
  raiz.querySelectorAll("li.clicavel").forEach(li => li.addEventListener("click", () => selecionar(li.dataset.id)));
}

function selecionar(id) {
  selecionado = id; destaque = null; cicloAtivo = null; mostrarAlcance = false; desenhar(); atualizarInfo();
}

function atualizarInfo() {
  const caixa = el("info"), vz = visoes[modo];
  if (!selecionado) { caixa.innerHTML = "Clique em um módulo para ver suas dependências."; return; }
  const {saida, entrada} = indexar(vz.nos, vz.arcos.map(a => [a.u, a.v]));
  const alc = alcancaveis(saida, selecionado);
  let html = `<div class="nome">${selecionado}</div>`;
  if (modo === "cond") {
    const n = vz.nos.find(x => x.id === selecionado);
    html += `<div class="sec">Membros</div>${ul(n.membros, false)}`;
  }
  html += `<div class="sec azul">Depende diretamente de (${saida.get(selecionado).size})</div>${ul([...saida.get(selecionado)].sort(), true)}`;
  html += `<div class="sec verde">Dependentes diretos (${entrada.get(selecionado).size})</div>${ul([...entrada.get(selecionado)].sort(), true)}`;
  html += `<div class="sec">Alcança ${alc.size} módulo(s) ao seguir dependências</div>`;
  html += `<button id="bAlcance" class="${mostrarAlcance ? "ativo" : ""}">${mostrarAlcance ? "Limpar destaque" : "Destacar alcançáveis"}</button>`;
  if (mostrarAlcance) html += ul([...alc].sort(), true);
  if (modo === "grafo" && SCC) {
    const i = SCC.comp.get(selecionado);
    if (SCC.ciclica[i]) html += `<div class="ruim"><b>Pertence a uma componente cíclica</b> (SCC com ${DADOS.sccs[i].length} módulo(s)).</div>`;
    else {
      const alcancaCiclica = [...alc].some(v => SCC.ciclica[SCC.comp.get(v)]);
      html += alcancaCiclica
        ? `<div class="aviso"><b>Não está em ciclo</b>, mas depende (direta ou indiretamente) de uma componente cíclica.</div>`
        : `<div class="ok">Não está em ciclo e não alcança nenhuma componente cíclica.</div>`;
    }
  }
  caixa.innerHTML = html; ligarCliques(caixa);
  const bAlc = el("bAlcance");
  if (bAlc) bAlc.onclick = () => { mostrarAlcance = !mostrarAlcance; desenhar(); atualizarInfo(); };
}

function escolherCiclo(i) {
  if (modo !== "grafo") return;
  if (cicloAtivo === i) { cicloAtivo = null; destaque = null; desenhar(); atualizarInfo(); return; }
  cicloAtivo = i; selecionado = null; mostrarCiclo = false;
  el("bCiclo").classList.remove("ativo");
  termoBusca = ""; el("busca").value = "";
  destaque = new Set(CICLOS[i]); desenhar();
  el("info").innerHTML = `<b>Ciclo ${i + 1} de ${CICLOS.length}</b><br>${CICLOS[i].join(" → ")}`;
}

// ---------- painel lateral ----------
function preencherPainel() {
  const av = el("avisos"), nosN = DADOS.nos.length, arcN = DADOS.arcos.length;
  el("resumo").textContent = `${nosN} módulos · ${arcN} dependências`;
  const avisos = [];
  if (!DADOS.sccs) avisos.push("SCCs não disponíveis (Kosaraju ainda não implementado ou não executado).");
  if (!CICLOS) avisos.push("Detecção de ciclos não disponível (DFS ainda não implementado ou não executado).");
  if (!DADOS.condensacao) avisos.push("Condensação não disponível.");
  av.innerHTML = avisos.map(a => `<div class="aviso">${a}</div>`).join("");
  el("bCond").disabled = !DADOS.condensacao;
  el("bCiclo").disabled = !CICLOS || CICLOS.length === 0;

  const lc = el("listaCiclos");
  if (!CICLOS) lc.innerHTML = "<i>indisponível</i>";
  else if (CICLOS.length === 0) lc.innerHTML = '<span class="ok">Grafo acíclico: nenhum ciclo.</span>';
  else {
    const mais = DADOS.ciclos_truncado ? "+" : "";
    let h = `<b class="ruim">${CICLOS.length}${mais} ciclo(s)</b>`;
    if (DADOS.ciclos_truncado) h += " (lista limitada: existem mais ciclos)";
    h += "<ul>" + CICLOS.map((c, i) => `<li class="clicavel" data-ciclo="${i}">${c.length - 1} módulo(s): ${c.join(" → ")}</li>`).join("") + "</ul>";
    lc.innerHTML = h;
    lc.querySelectorAll("li[data-ciclo]").forEach(li => li.addEventListener("click", () => escolherCiclo(+li.dataset.ciclo)));
  }

  const ls = el("listaScc");
  if (!DADOS.sccs) { ls.innerHTML = "<i>indisponível</i>"; }
  else {
    const cicl = DADOS.sccs.map((c, i) => ({c, i})).filter(x => SCC.ciclica[x.i]);
    const nao = DADOS.sccs.length - cicl.length;
    let h = `${DADOS.sccs.length} componentes: <b class="ruim">${cicl.length} cíclica(s)</b>, ${nao} trivial(is).`;
    h += "<ul>" + cicl.map(({c, i}) => `<li class="clicavel" data-scc="${i}"><span class="chip" style="background:${SCC.cor.get(i)}"></span>${c.length} módulo(s): ${c.join(", ")}</li>`).join("") + "</ul>";
    ls.innerHTML = h;
    ls.querySelectorAll("li[data-scc]").forEach(li => li.addEventListener("click", () => {
      termoBusca = ""; el("busca").value = ""; selecionado = null; cicloAtivo = null;
      destaque = new Set(DADOS.sccs[+li.dataset.scc]); desenhar(); atualizarInfo();
    }));
  }
  if (DADOS.condensacao && DADOS.condensacao.ordem) {
    el("tOrdem").style.display = ""; 
    el("ordem").innerHTML = "<ol>" + DADOS.condensacao.ordem.map(c => `<li>${c}</li>`).join("") + "</ol>" +
      "<div style='color:#777'>Dependentes antes das dependências (arcos A → B apontam de A para o que A usa).</div>";
  }
}

// ---------- botões ----------
function trocarModo(m) {
  modo = m; selecionado = null; cicloAtivo = null; destaque = null; mostrarAlcance = false;
  el("bGrafo").classList.toggle("ativo", m === "grafo");
  el("bCond").classList.toggle("ativo", m === "cond");
  el("bCiclo").style.display = m === "grafo" ? "" : "none";
  iniciarVisao(m); ajustar(); atualizarInfo();
}
function iniciarVisao(m) {
  if (visoes[m]) return;
  const r = svg.getBoundingClientRect(), L = Math.max(r.width, 600), A = Math.max(r.height, 400);
  const vz = criarVisao(m);
  if (m === "grafo") layoutForca(vz.nos, vz.arcos, L, A);
  else layoutCamadas(vz.nos, vz.arcos, DADOS.condensacao.ordem, L, A);
  visoes[m] = vz;
}
el("bGrafo").onclick = () => trocarModo("grafo");
el("bCond").onclick = () => { if (DADOS.condensacao) trocarModo("cond"); };
el("bCiclo").onclick = () => {
  mostrarCiclo = !mostrarCiclo; cicloAtivo = null; destaque = null;
  el("bCiclo").classList.toggle("ativo", mostrarCiclo); desenhar(); atualizarInfo();
};
el("bRotulos").onclick = () => { mostrarRotulos = !mostrarRotulos; el("bRotulos").classList.toggle("ativo", mostrarRotulos); desenhar(); };
el("bAjustar").onclick = ajustar;
el("busca").addEventListener("input", ev => { termoBusca = ev.target.value; destaque = null; cicloAtivo = null; desenhar(); });
window.addEventListener("resize", ajustar);

prepararMarcadores(); preencherPainel(); iniciarVisao("grafo"); ajustar();
</script>
</body>
</html>
"""
