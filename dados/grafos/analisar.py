"""
Uso:
    python analisar.py <pasta>                       # grafo + TODOS os ciclos (até o limite) e SCCs
    python analisar.py <pasta> --limite-ciclos 200   # muda o limite (padrão: 50)
    python analisar.py <pasta> --so-um-ciclo         # só a Atividade A: um ciclo (DFS, O(V + E))
    python analisar.py <pasta> --so-sccs             # só a Atividade B: SCCs (Kosaraju–Sharir)
    python analisar.py <pasta> --so-condensacao      # só a Atividade C: condensação + ordem topológica
    python analisar.py <pasta> --alcancaveis <módulo>  # tudo que o módulo alcança (O(V + E))
    python analisar.py <pasta> --remover <origem> <destino>   # Atividade D: simula remover a dependência
"""

import argparse
from pathlib import Path

# Importa os algoritmos responsáveis por cada análise.
from src.ciclos import alcancaveis, encontrar_ciclo
from src.condensacao import condensar, ordenacao_topologica
from src.enumeracao import encontrar_ciclos
from src.extracao import construir_grafo
from src.grafo import Digrafo
from src.remocao import formatar_remocao, simular_remocao
from src.scc import (
    analisar_relacao_ciclo,
    classificar_sccs,
    encontrar_sccs,
    kosaraju,
)


def _linha_ciclo(i: int, ciclo: list[str]) -> str:
    # recebe uma lista de strings com os módulos do ciclo e formata sua apresentação, além de calcular a quantidade de módulos distintos.
    return f"  {i}) {' ➔ '.join(ciclo)}  ({len(ciclo) - 1} módulo(s))"


def _imprimir_todos(graph: dict[str, set[str]], limite: int) -> None:
    """Lista todos os ciclos encontrados, respeitando um limite."""

    # Busca limite + 1 para descobrir se existem mais ciclos do que o permitido.
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
    """Atividade A: encontra somente o primeiro ciclo usando DFS."""

    # Executa a busca em profundidade e interrompe quando encontra um ciclo.
    ciclo = encontrar_ciclo(graph)

    print("=== Ciclo (Atividade A: encontrar_ciclo) ===")
    if ciclo is None:
        print("Nenhum ciclo foi encontrado; o grafo é acíclico neste escopo.")
        return

    print(
        "1 ciclo encontrado (a DFS para no primeiro; omita --so-um-ciclo para ver todos):"
    )
    print(_linha_ciclo(1, ciclo))


def _imprimir_alcancaveis(graph: dict[str, set[str]], origem: str) -> None:
    """Mostra todos os módulos alcançáveis a partir de um módulo."""

    # Ordena os módulos encontrados para apresentar uma saída organizada.
    alc = sorted(alcancaveis(graph, origem))

    print(f"=== Alcançáveis a partir de {origem} ===")
    if not alc:
        print("Nenhum: o módulo não depende de outros módulos internos.")
        return

    print(f"{len(alc)} módulo(s):")
    for v in alc:
        print(f"  {v}")


def _imprimir_sccs(graph: dict[str, set[str]]) -> None:
    """Atividade B: identifica e classifica as componentes fortemente conexas."""

    # Encontra os grupos de vértices que possuem alcançabilidade mútua.
    components = encontrar_sccs(graph)

    # Identifica quais componentes possuem ciclos.
    classifications = classificar_sccs(graph, components)

    # Analisa a relação dos módulos com as componentes cíclicas.
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
    """Atividade C: constrói o grafo de condensação e sua ordem topológica."""

    # Encontra as SCCs usando o algoritmo de Kosaraju-Sharir.
    sccs = kosaraju(g)

    # Substitui cada SCC por um único vértice, formando um novo grafo.
    g_cond, _ = condensar(g, sccs)

    # Calcula uma ordenação topológica do grafo condensado.
    ordem = ordenacao_topologica(g_cond)

    # Recupera os módulos originais representados por cada componente.
    def rotulo(c: str) -> str:
        return f"{c} {{{', '.join(sccs[int(c[1:])])}}}"

    print("=== Condensação (Atividade C) ===")
    print(
        f"{g_cond.num_vertices()} componente(s), "
        f"{g_cond.num_arcos()} dependência(s) entre componentes"
    )

    for c in ordem:
        deps = ", ".join(g_cond.vizinhos(c)) or "nenhuma"
        print(f"  {rotulo(c)} -> {deps}")

    print(
        "\n=== Ordenação topológica (quem depende vem antes das suas dependências) ==="
    )
    for i, c in enumerate(ordem, 1):
        print(f"  {i}) {rotulo(c)}")


def main(argv: list[str] | None = None) -> None:
    # Configura a leitura dos argumentos recebidos pelo terminal.
    ap = argparse.ArgumentParser(
        description="Analisa dependências circulares de um projeto Python"
    )

    # Define os argumentos e os modos de execução disponíveis.
    ap.add_argument("projeto", help="pasta do projeto (raiz dos pacotes)")

    ap.add_argument(
        "--so-um-ciclo",
        action="store_true",
        help="roda só o encontrar_ciclo (Atividade A) e mostra um ciclo",
    )

    ap.add_argument(
        "--so-sccs",
        action="store_true",
        help="roda só o Kosaraju–Sharir (Atividade B) e mostra as SCCs",
    )

    ap.add_argument(
        "--so-condensacao",
        action="store_true",
        help="mostra só a condensação e a ordenação topológica (Atividade C)",
    )

    ap.add_argument(
        "--alcancaveis",
        metavar="MÓDULO",
        help="mostra tudo que o módulo alcança (em vez da análise de ciclos)",
    )

    ap.add_argument(
        "--remover",
        nargs=2,
        action="append",
        metavar=("ORIGEM", "DESTINO"),
        help="simula a remoção de uma dependência",
    )

    ap.add_argument(
        "--limite-ciclos",
        type=int,
        default=50,
        help="máximo de ciclos listados no modo padrão (padrão: 50)",
    )

    # Interpreta os argumentos fornecidos pelo usuário.
    args = ap.parse_args(argv)

    # Verifica se o caminho informado realmente corresponde a uma pasta.
    raiz = Path(args.projeto)
    if not raiz.is_dir():
        ap.error(f"pasta não encontrada: {raiz}")

    # Extrai as dependências entre os módulos e constrói o grafo.
    graph = construir_grafo(raiz)

    # Converte a representação do grafo para a classe Digrafo.
    g = Digrafo(graph)

    # Exibe os vértices e suas respectivas conexões.
    print(g)
    for u in g.vertices():
        print(f"{u} -> {g.vizinhos(u)}")
    print()

    # Seleciona o modo de análise solicitado pelo usuário.
    if args.remover:
        for origem, destino in args.remover:
            try:
                # Cada simulação utiliza uma cópia do grafo original.
                resultado = simular_remocao(Digrafo(graph), origem, destino)
            except ValueError as erro:
                ap.error(str(erro))

            print(formatar_remocao(resultado))
            print()

    elif args.alcancaveis:
        # Verifica se o módulo informado existe no grafo.
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
        # Modo padrão: executa as três análises principais.
        _imprimir_todos(graph, args.limite_ciclos)
        print()

        _imprimir_sccs(graph)
        print()

        _imprimir_condensacao(g)


# Garante que main() seja executada somente quando este arquivo
# for executado diretamente, e não quando for importado por outro módulo.
if __name__ == "__main__":
    main()
