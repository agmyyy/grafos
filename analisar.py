"""Uso: python analisar.py <pasta_do_projeto>   (mostra o grafo extraído)"""

import sys
from pathlib import Path

from src.extracao import construir_grafo
from src.grafo import Digrafo


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("uso: python analisar.py <pasta_do_projeto>")
    g = Digrafo(construir_grafo(Path(sys.argv[1])))
    print(g)
    for u in g.vertices():
        print(f"{u} -> {g.vizinhos(u)}")


if __name__ == "__main__":
    main()
