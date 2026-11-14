"""Extrai o grafo de dependências de um projeto e analisa seus ciclos.

Uso:
    python analisar.py <pasta>                       # grafo + TODOS os ciclos (até o limite)
    python analisar.py <pasta> --limite-ciclos 200   # muda o limite (padrão: 50)
    python analisar.py <pasta> --so-um-ciclo         # só a Atividade A: um ciclo (DFS, O(V + E))

Os dois modos usam o mesmo formato de saída.
"""

import argparse
from pathlib import Path

from src.ciclos import encontrar_ciclo
from src.enumeracao import encontrar_ciclos
from src.extracao import construir_grafo
from src.grafo import Digrafo


def _linha_ciclo(i: int, ciclo: list[str]) -> str:
    # O ciclo repete o primeiro vértice no fim para "fechar": k módulos distintos, k dependências.
    return f"  {i}) {' ➔ '.join(ciclo)}  ({len(ciclo) - 1} módulo(s))"


def _imprimir_todos(graph: dict[str, set[str]], limite: int) -> None:
    """Lista todos os ciclos (até `limite`). Pode ser exponencial: ver enumeracao.py."""
    ciclos = encontrar_ciclos(graph, limite + 1)
    truncado = len(ciclos) > limite
    ciclos = ciclos[:limite]

    print(f"=== Ciclos (todos, limite {limite}) ===")
    if not ciclos:
        print("Nenhum ciclo foi encontrado; o grafo é acíclico neste escopo.")
        return

    print(f"{len(ciclos)}{'+' if truncado else ''} ciclo(s) encontrado(s):")
    for i, ciclo in enumerate(ciclos, start=1):
        print(_linha_ciclo(i, ciclo))
    if truncado:
        print(f"Lista limitada a {limite}; há mais ciclos (use --limite-ciclos).")


def _imprimir_um(graph: dict[str, set[str]]) -> None:
    """Atividade A: só o encontrar_ciclo (DFS, O(V + E)), que para no primeiro ciclo."""
    ciclo = encontrar_ciclo(graph)

    print("=== Ciclo (Atividade A: encontrar_ciclo) ===")
    if ciclo is None:
        print("Nenhum ciclo foi encontrado; o grafo é acíclico neste escopo.")
        return

    print("1 ciclo encontrado (a DFS para no primeiro; omita --so-um-ciclo para ver todos):")
    print(_linha_ciclo(1, ciclo))


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Analisa dependências circulares de um projeto Python")
    ap.add_argument("projeto", help="pasta do projeto (raiz dos pacotes)")
    ap.add_argument("--so-um-ciclo", action="store_true",
                    help="roda só o encontrar_ciclo (Atividade A) e mostra um ciclo")
    ap.add_argument("--limite-ciclos", type=int, default=50,
                    help="máximo de ciclos listados no modo padrão (padrão: 50)")
    args = ap.parse_args(argv)

    raiz = Path(args.projeto)
    if not raiz.is_dir():
        ap.error(f"pasta não encontrada: {raiz}")

    graph = construir_grafo(raiz)
    g = Digrafo(graph)
    print(g)
    for u in g.vertices():
        print(f"{u} -> {g.vizinhos(u)}")
    print()

    if args.so_um_ciclo:
        _imprimir_um(graph)
    else:
        _imprimir_todos(graph, args.limite_ciclos)


if __name__ == "__main__":
    main()
