"""Uso: python analisar.py <pasta_do_projeto> (mostra grafo, ciclos e SCCs).

Uso:
    python analisar.py <pasta>                       # grafo + TODOS os ciclos (até o limite)
    python analisar.py <pasta> --limite-ciclos 200   # muda o limite (padrão: 50)
    python analisar.py <pasta> --so-um-ciclo         # só a Atividade A: um ciclo (DFS, O(V + E))
    python analisar.py <pasta> --so-sccs             # só a Atividade B: SCCs (Kosaraju–Sharir)
    python analisar.py <pasta> --so-condensacao      # só a Atividade C: condensação + ordem topológica
    python analisar.py <pasta> --alcancaveis <módulo>  # tudo que o módulo alcança (O(V + E))
    python analisar.py <pasta> --remover <origem> <destino>   # Atividade D: simula remover a dependência
    python analisar.py <pasta> --excluir tests --excluir docs # ignora pastas (pode repetir)
    python analisar.py <pasta> --sem-isolados        # remove módulos sem nenhuma dependência de/para outros

Os dois modos usam o mesmo formato de saída.
"""

import argparse
from pathlib import Path

from src.ciclos import alcancaveis, encontrar_ciclo
from src.condensacao import condensar, ordenacao_topologica
from src.enumeracao import encontrar_ciclos
from src.filtros import carregar_grafo
from src.grafo import Digrafo
from src.remocao import formatar_remocao, simular_remocao
from src.scc import analisar_relacao_ciclo, classificar_sccs, encontrar_sccs, kosaraju


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


def _imprimir_condensacao(g: Digrafo) -> None:
    """Atividade C: grafo de condensação (DAG das SCCs) e ordenação topológica."""
    sccs = kosaraju(g)
    g_cond, _ = condensar(g, sccs)
    ordem = ordenacao_topologica(g_cond)

    def rotulo(c: str) -> str:
        return f"{c} {{{', '.join(sccs[int(c[1:])])}}}"

    print("=== Condensação (Atividade C) ===")
    print(f"{g_cond.num_vertices()} componente(s), {g_cond.num_arcos()} dependência(s) entre componentes")
    for c in ordem:
        deps = ", ".join(g_cond.vizinhos(c)) or "nenhuma"
        print(f"  {rotulo(c)} -> {deps}")
    print("\n=== Ordenação topológica (quem depende vem antes das suas dependências) ===")
    for i, c in enumerate(ordem, 1):
        print(f"  {i}) {rotulo(c)}")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Analisa dependências circulares de um projeto Python")
    ap.add_argument("projeto", help="pasta do projeto (raiz dos pacotes)")
    ap.add_argument("--so-um-ciclo", action="store_true",
                    help="roda só o encontrar_ciclo (Atividade A) e mostra um ciclo")
    ap.add_argument("--so-sccs", action="store_true",
                    help="roda só o Kosaraju–Sharir (Atividade B) e mostra as SCCs")
    ap.add_argument("--so-condensacao", action="store_true",
                    help="mostra só a condensação e a ordenação topológica (Atividade C)")
    ap.add_argument("--alcancaveis", metavar="MÓDULO",
                    help="mostra tudo que o módulo alcança (em vez da análise de ciclos)")
    ap.add_argument("--remover", nargs=2, action="append", metavar=("ORIGEM", "DESTINO"),
                    help="simula a remoção da dependência ORIGEM ➔ DESTINO (pode repetir; cada "
                         "simulação parte do grafo original)")
    ap.add_argument("--excluir", action="append", default=[], metavar="PASTA",
                    help="ignora pastas com esse nome, ex.: --excluir tests --excluir docs (pode repetir)")
    ap.add_argument("--sem-isolados", action="store_true",
                    help="remove TODO módulo sem nenhuma dependência de/para outros (inclusive módulos reais)")
    ap.add_argument("--limite-ciclos", type=int, default=50,
                    help="máximo de ciclos listados no modo padrão (padrão: 50)")
    args = ap.parse_args(argv)

    raiz = Path(args.projeto)
    if not raiz.is_dir():
        ap.error(f"pasta não encontrada: {raiz}")

    graph = carregar_grafo(raiz, args.excluir, args.sem_isolados)
    g = Digrafo(graph)
    print(g)
    for u in g.vertices():
        print(f"{u} -> {g.vizinhos(u)}")
    print()

    if args.remover:
        for origem, destino in args.remover:
            try:
                resultado = simular_remocao(Digrafo(graph), origem, destino)
            except ValueError as erro:
                ap.error(str(erro))
            print(formatar_remocao(resultado))
            print()
    elif args.alcancaveis:
        if args.alcancaveis not in graph:
            ap.error(f"módulo não encontrado no grafo: {args.alcancaveis}")
        _imprimir_alcancaveis(graph, args.alcancaveis)
    elif args.so_um_ciclo:
        _imprimir_um(graph)
    elif args.so_sccs:
        _imprimir_sccs(graph)
    elif args.so_condensacao:
        _imprimir_condensacao(g)
    else:
        _imprimir_todos(graph, args.limite_ciclos)
        print()
        _imprimir_sccs(graph)
        print()
        _imprimir_condensacao(g)


if __name__ == "__main__":
    main()
