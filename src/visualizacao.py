"""Gera uma página HTML autocontida (sem internet, sem bibliotecas externas)
para visualizar o digrafo, os ciclos, as SCCs e a condensação.

A página só MOSTRA resultados: quem calcula são os algoritmos da equipe
(ciclos.py, scc.py, condensacao.py). O que ainda não estiver implementado
simplesmente não aparece na página.
"""

import json

from src.grafo import Digrafo


def montar_dados(
    g: Digrafo,
    titulo: str = "Dependências",
    sccs: list[list[str]] | None = None,
    ciclo: list[str] | None = None,
    g_cond: Digrafo | None = None,
    mapa_scc: dict[str, int] | None = None,
    ordem_topologica: list[str] | None = None,
) -> dict:
    """Converte os resultados da equipe no JSON que a página consome."""
    dados: dict = {
        "titulo": titulo,
        "nos": g.vertices(),
        "arcos": [list(a) for a in g.arcos()],
        "sccs": [sorted(c) for c in sccs] if sccs is not None else None,
        "ciclo": ciclo,
        "condensacao": None,
    }
    if g_cond is not None and mapa_scc is not None:
        membros: dict[int, list[str]] = {}
        for v, i in mapa_scc.items():
            membros.setdefault(i, []).append(v)
        dados["condensacao"] = {
            "nos": [{"id": c, "membros": sorted(membros.get(int(c[1:]), []))}
                    for c in g_cond.vertices()],
            "arcos": [list(a) for a in g_cond.arcos()],
            "ordem": ordem_topologica,
        }
    return dados


def gerar_html(dados: dict) -> str:
    """Devolve o HTML completo. `dados` vem de montar_dados()."""
    carga = json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")
    return _MODELO.replace("__DADOS__", carga).replace(
        "__TITULO__", dados["titulo"].replace("<", "&lt;")
    )


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
    <button id="bCiclo">Mostrar ciclo concreto</button>
    <button id="bRotulos" class="ativo">Rótulos</button>
    <button id="bAjustar">Ajustar tela</button>
  </div>
  <div id="avisos"></div>
  <h2>Selecionado</h2>
  <div id="info">Clique em um módulo para ver suas dependências.</div>
  <h2>Componentes fortemente conexas</h2>
  <div id="listaScc"></div>
  <h2 id="tOrdem" style="display:none">Ordenação topológica</h2>
  <div id="ordem"></div>
  <h2>Legenda</h2>
  <div id="legenda">
    <div><span class="chip" style="background:#90a4ae"></span>módulo fora de componente cíclica</div>
    <div><span class="chip" style="background:#e53935"></span>cor forte: módulos de uma componente cíclica (uma cor por componente)</div>
    <div><span style="color:#d32f2f">━</span> arco dentro de componente cíclica &nbsp; <span style="color:#78909c">━</span> arco comum</div>
    <div><span style="color:#ef6c00">━</span> ciclo concreto (botão acima)</div>
    <div>Ao selecionar: <span style="color:#1565c0">━</span> dependências diretas, <span style="color:#2e7d32">━</span> quem depende dele.</div>
    <div style="margin-top:6px;color:#777">Arco A → B: A importa B (A depende de B).</div>
  </div>
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
  const m = criar("marker", {id, viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 7,
                             markerHeight: 7, orient: "auto-start-reverse"}, defs);
  criar("path", {d: "M0,0 L10,5 L0,10 z", fill: cor}, m);
}
function prepararMarcadores() {
  defs.innerHTML = "";
  [["m-comum", COR_ARCO], ["m-ciclico", COR_CICLICO], ["m-saida", "#1565c0"],
   ["m-entrada", "#2e7d32"], ["m-ciclo", "#ef6c00"]].forEach(([i, c]) => marcador(i, c));
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
  const c = DADOS.ciclo;
  if (modo !== "grafo" || !mostrarCiclo || !c) return false;
  for (let i = 0; i + 1 < c.length; i++) if (c[i] === a.u && c[i + 1] === a.v) return true;
  return false;
}

function desenhar() {
  const vz = visoes[modo];
  const pos = new Map(vz.nos.map(n => [n.id, n]));
  const chave = new Set(vz.arcos.map(a => a.u + "\u0000" + a.v));
  const {saida, entrada} = indexar(vz.nos, vz.arcos.map(a => [a.u, a.v]));
  const sel = selecionado;
  const vizSaida = sel ? saida.get(sel) : null, vizEntrada = sel ? entrada.get(sel) : null;
  const termo = termoBusca.trim().toLowerCase();

  cena.innerHTML = "";
  const gArcos = criar("g", {}, cena), gNos = criar("g", {}, cena);

  vz.arcos.forEach(a => {
    let cor = COR_ARCO, larg = 1.4, mk = "m-comum", op = 0.75;
    if (arcoCiclico(a)) { cor = COR_CICLICO; mk = "m-ciclico"; larg = 1.8; op = 0.9; }
    if (sel) {
      if (a.u === sel) { cor = "#1565c0"; mk = "m-saida"; larg = 2.6; op = 1; }
      else if (a.v === sel) { cor = "#2e7d32"; mk = "m-entrada"; larg = 2.6; op = 1; }
      else op = 0.08;
    }
    if (arcoNoCiclo(a)) { cor = "#ef6c00"; mk = "m-ciclo"; larg = 4; op = 1; }
    const inverso = chave.has(a.v + "\u0000" + a.u);
    criar("path", {d: caminho(a, pos, inverso), fill: "none", stroke: cor, "stroke-width": larg,
                   "stroke-opacity": op, "marker-end": `url(#${mk})`}, gArcos);
  });

  vz.nos.forEach(n => {
    const alvoSel = sel && (n.id === sel || vizSaida.has(n.id) || vizEntrada.has(n.id));
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
  selecionado = id; destaque = null; desenhar(); atualizarInfo();
}

function atualizarInfo() {
  const caixa = el("info"), vz = visoes[modo];
  if (!selecionado) { caixa.innerHTML = "Clique em um módulo para ver suas dependências."; return; }
  const {saida, entrada} = indexar(vz.nos, vz.arcos.map(a => [a.u, a.v]));
  const alc = alcancaveis(saida, selecionado);
  let html = `<b>${selecionado}</b>`;
  if (modo === "cond") {
    const n = vz.nos.find(x => x.id === selecionado);
    html += `<br>Membros:${ul(n.membros, false)}`;
  }
  html += `<br><span style="color:#1565c0">Depende diretamente de (${saida.get(selecionado).size}):</span>${ul([...saida.get(selecionado)].sort(), true)}`;
  html += `<span style="color:#2e7d32">Dependentes diretos (${entrada.get(selecionado).size}):</span>${ul([...entrada.get(selecionado)].sort(), true)}`;
  html += `Alcança ${alc.size} módulo(s) ao seguir dependências.`;
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
}

// ---------- painel lateral ----------
function preencherPainel() {
  const av = el("avisos"), nosN = DADOS.nos.length, arcN = DADOS.arcos.length;
  el("resumo").textContent = `${nosN} módulos · ${arcN} dependências`;
  const avisos = [];
  if (!DADOS.sccs) avisos.push("SCCs não disponíveis (Kosaraju ainda não implementado ou não executado).");
  if (!DADOS.ciclo && !DADOS.sccs) avisos.push("Detecção de ciclo concreto não disponível.");
  if (!DADOS.condensacao) avisos.push("Condensação não disponível.");
  av.innerHTML = avisos.map(a => `<div class="aviso">${a}</div>`).join("");
  el("bCond").disabled = !DADOS.condensacao;
  el("bCiclo").disabled = !DADOS.ciclo;

  const ls = el("listaScc");
  if (!DADOS.sccs) { ls.innerHTML = "<i>indisponível</i>"; }
  else {
    const cicl = DADOS.sccs.map((c, i) => ({c, i})).filter(x => SCC.ciclica[x.i]);
    const nao = DADOS.sccs.length - cicl.length;
    let h = `${DADOS.sccs.length} componentes: <b class="ruim">${cicl.length} cíclica(s)</b>, ${nao} trivial(is).`;
    h += "<ul>" + cicl.map(({c, i}) => `<li class="clicavel" data-scc="${i}"><span class="chip" style="background:${SCC.cor.get(i)}"></span>${c.length} módulo(s): ${c.join(", ")}</li>`).join("") + "</ul>";
    ls.innerHTML = h;
    ls.querySelectorAll("li[data-scc]").forEach(li => li.addEventListener("click", () => {
      termoBusca = ""; el("busca").value = ""; selecionado = null;
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
  modo = m; selecionado = null;
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
el("bCiclo").onclick = () => { mostrarCiclo = !mostrarCiclo; el("bCiclo").classList.toggle("ativo", mostrarCiclo); desenhar();
  if (mostrarCiclo && DADOS.ciclo) el("info").innerHTML = "<b>Ciclo concreto:</b><br>" + DADOS.ciclo.join(" → "); };
el("bRotulos").onclick = () => { mostrarRotulos = !mostrarRotulos; el("bRotulos").classList.toggle("ativo", mostrarRotulos); desenhar(); };
el("bAjustar").onclick = ajustar;
el("busca").addEventListener("input", ev => { termoBusca = ev.target.value; destaque = null; desenhar(); });
window.addEventListener("resize", ajustar);

prepararMarcadores(); preencherPainel(); iniciarVisao("grafo"); ajustar();
</script>
</body>
</html>
"""
