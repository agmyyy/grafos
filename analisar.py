"""Uso: python analisar.py <pasta_do_projeto> (mostra grafo, ciclos e SCCs)."""

import sys
from pathlib import Path

from src.ciclos import encontrar_ciclo, imprimir_resultado_dfs
from src.extracao import construir_grafo
from src.grafo import Digrafo
from src.scc import analisar_relacao_ciclo, classificar_sccs, encontrar_sccs


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

    components = encontrar_sccs(graph)
    classifications = classificar_sccs(graph, components)
    relation = analisar_relacao_ciclo(graph, components)

    print("\n=== Componentes fortemente conexas ===")
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


if __name__ == "__main__":
    main()
