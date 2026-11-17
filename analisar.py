"""Uso: python analisar.py <pasta_do_projeto> (mostra grafo, ciclos e SCCs).

Uso:
    python analisar.py <pasta>                       # grafo + TODOS os ciclos (até o limite)
    python analisar.py <pasta> --limite-ciclos 200   # muda o limite (padrão: 50)
    python analisar.py <pasta> --so-um-ciclo         # só a Atividade A: um ciclo (DFS, O(V + E))
    python analisar.py <pasta> --so-sccs             # só a Atividade B: SCCs (Kosaraju–Sharir)
    python analisar.py <pasta> --alcancaveis <módulo>  # tudo que o módulo alcança (O(V + E))

Os dois modos usam o mesmo formato de saída.
"""

import argparse
from pathlib import Path

from src.ciclos import alcancaveis, encontrar_ciclo
from src.enumeracao import encontrar_ciclos
from src.extracao import construir_grafo
from src.grafo import Digrafo
from src.scc import analisar_relacao_ciclo, classificar_sccs, encontrar_sccs


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


def _imprimir_alcancaveis(graph: dict[str, set[str]], origem: str) -> None:
    """Todos os módulos que `origem` alcança seguindo dependências (A → B: A usa B)."""
    alc = sorted(alcancaveis(graph, origem))
    print(f"=== Alcançáveis a partir de {origem} ===")
    if not alc:
        print("Nenhum: o módulo não depende de outros módulos internos.")
        return
    print(f"{len(alc)} módulo(s):")
    for v in alc:
        print(f"  {v}")


def _imprimir_sccs(graph: dict[str, set[str]]) -> None:
    """Atividade B: SCCs (Kosaraju–Sharir) e relação dos módulos com as componentes cíclicas."""
    components = encontrar_sccs(graph)
    classifications = classificar_sccs(graph, components)
    relation = analisar_relacao_ciclo(graph, components)

    print("=== Componentes fortemente conexas ===")
    for classification in classifications:
        status = "cíclica" if classification["eh_ciclica"] else "acíclica / trivial"
        vertices = ", ".join(classification["vertices"])
        print(
            f"SCC {classification['id']}: [{vertices}] "
            f"(tamanho: {classification['tamanho']}, {status})"
        )

    print("\n=== Relação com componentes cíclicas ===")
    print(
        "Nós que pertencem a SCCs cíclicas: "
        f"{', '.join(sorted(relation['pertencem_a_scc_ciclica'])) or 'nenhum'}"
    )
    print(
        "Nós externos que alcançam SCCs cíclicas: "
        f"{', '.join(sorted(relation['alcancam_scc_ciclica_sem_pertencer'])) or 'nenhum'}"
    )


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Analisa dependências circulares de um projeto Python")
    ap.add_argument("projeto", help="pasta do projeto (raiz dos pacotes)")
    ap.add_argument("--so-um-ciclo", action="store_true",
                    help="roda só o encontrar_ciclo (Atividade A) e mostra um ciclo")
    ap.add_argument("--so-sccs", action="store_true",
                    help="roda só o Kosaraju–Sharir (Atividade B) e mostra as SCCs")
    ap.add_argument("--alcancaveis", metavar="MÓDULO",
                    help="mostra tudo que o módulo alcança (em vez da análise de ciclos)")
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

    if args.alcancaveis:
        if args.alcancaveis not in graph:
            ap.error(f"módulo não encontrado no grafo: {args.alcancaveis}")
        _imprimir_alcancaveis(graph, args.alcancaveis)
    elif args.so_um_ciclo:
        _imprimir_um(graph)
    elif args.so_sccs:
        _imprimir_sccs(graph)
    else:
        _imprimir_todos(graph, args.limite_ciclos)
        print()
        _imprimir_sccs(graph)


if __name__ == "__main__":
    main()
