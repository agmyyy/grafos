"""Uso: python analisar.py <pasta_do_projeto>   (mostra o grafo extraído)"""

import sys
from pathlib import Path

from src.ciclos import encontrar_ciclo, imprimir_resultado_dfs
from src.extracao import construir_grafo
from src.grafo import Digrafo


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("uso: python analisar.py <pasta_do_projeto>")
    graph = construir_grafo(Path(sys.argv[1]))
    g = Digrafo(graph)
    print(g)
    for u in g.vertices():
        print(f"{u} -> {g.vizinhos(u)}")

    cycle = encontrar_ciclo(graph)
    imprimir_resultado_dfs(graph, cycle)


if __name__ == "__main__":
    main()
