"""Gera a página HTML de visualização de um projeto.

Uso:
    python visualizar.py dados/cyclic_app
    python visualizar.py dados/cyclic_app -o saida/ciclos.html --abrir

Usa os algoritmos da equipe quando já estão implementados
(ciclos.py, scc.py, condensacao.py). O que ainda levanta
NotImplementedError é simplesmente omitido da página.
"""

import argparse
import webbrowser
from pathlib import Path

from src import ciclos, condensacao, enumeracao, scc
from src.extracao import construir_grafo
from src.grafo import Digrafo
from src.visualizacao import gerar_html, montar_dados


def _tentar(nome: str, funcao, *args):
    """Executa um algoritmo; se ainda for stub, avisa e devolve None."""
    try:
        return funcao(*args)
    except NotImplementedError:
        print(f"[aviso] {nome} ainda não implementado: omitido da página")
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description="Visualiza dependências de um projeto Python")
    ap.add_argument("projeto", help="pasta do projeto (raiz dos pacotes)")
    ap.add_argument("-o", "--saida", help="arquivo HTML de saída (padrão: saida/<pasta>.html)")
    ap.add_argument("--abrir", action="store_true", help="abre a página no navegador")
    ap.add_argument("--limite-ciclos", type=int, default=50,
                    help="máximo de ciclos listados na página (padrão: 50)")
    args = ap.parse_args()

    raiz = Path(args.projeto)
    if not raiz.is_dir():
        ap.error(f"pasta não encontrada: {raiz}")

    g = Digrafo(construir_grafo(raiz))
    print(f"{raiz.name}: {g.num_vertices()} módulos, {g.num_arcos()} dependências")

    ciclo = _tentar("encontrar_ciclo", ciclos.encontrar_ciclo, g)
    lista = _tentar("encontrar_ciclos", enumeracao.encontrar_ciclos, g, args.limite_ciclos + 1)
    truncado = lista is not None and len(lista) > args.limite_ciclos
    if lista is not None:
        lista = lista[: args.limite_ciclos]
        print(f"ciclos listados: {len(lista)}" + (" (há mais; use --limite-ciclos)" if truncado else ""))
    sccs = _tentar("kosaraju", scc.kosaraju, g)
    g_cond = mapa = ordem = None
    if sccs is not None:
        resultado = _tentar("condensar", condensacao.condensar, g, sccs)
        if resultado is not None:
            g_cond, mapa = resultado
            ordem = _tentar("ordenacao_topologica", condensacao.ordenacao_topologica, g_cond)

    dados = montar_dados(g, raiz.name, sccs, ciclo, g_cond, mapa, ordem, lista, truncado)
    destino = Path(args.saida) if args.saida else Path("saida") / f"{raiz.name}.html"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(gerar_html(dados), encoding="utf-8")
    print(f"página gerada: {destino}")
    if args.abrir:
        webbrowser.open(destino.resolve().as_uri())


if __name__ == "__main__":
    main()
