"""Testes da busca em profundidade e da detecção de ciclos."""

from src.ciclos import encontrar_ciclo, imprimir_resultado_dfs, tem_ciclo


def _assert_valid_cycle(graph: dict[str, set[str]], cycle: list[str] | None) -> None:
    """Verifica se o caminho retornado fecha e contém apenas arestas do grafo."""
    assert cycle is not None
    assert len(cycle) >= 2
    assert cycle[0] == cycle[-1]

    for source, target in zip(cycle, cycle[1:]):
        assert target in graph[source]


def test_acyclic_graph_has_no_cycle() -> None:
    graph = {
        "A": {"B", "C"},
        "B": {"D"},
        "C": {"D"},
        "D": set(),
        "E": set(),
    }

    assert tem_ciclo(graph) is False
    assert encontrar_ciclo(graph) is None


def test_simple_cycle_returns_closed_path() -> None:
    graph = {
        "ClasseA": {"ClasseB"},
        "ClasseB": {"ClasseC"},
        "ClasseC": {"ClasseA"},
    }

    assert tem_ciclo(graph) is True
    assert encontrar_ciclo(graph) == [
        "ClasseA",
        "ClasseB",
        "ClasseC",
        "ClasseA",
    ]


def test_multiple_or_cross_edges_return_a_valid_cycle() -> None:
    graph = {
        "A": {"B", "C"},
        "B": {"A", "D"},
        "C": {"D"},
        "D": {"B", "C"},
    }

    cycle = encontrar_ciclo(graph)

    assert tem_ciclo(graph) is True
    _assert_valid_cycle(graph, cycle)


def test_print_dfs_summary_without_cycle(capsys) -> None:
    graph = {"A": {"B"}, "C": set()}

    imprimir_resultado_dfs(graph, None)

    output = capsys.readouterr().out
    assert "Total de nós: 3" in output
    assert "Total de arestas: 1" in output
    assert "Nenhum ciclo foi encontrado" in output
    assert "acíclico" in output


def test_print_dfs_summary_with_cycle(capsys) -> None:
    graph = {
        "A": {"B"},
        "B": {"C"},
        "C": {"A"},
    }
    cycle = ["A", "B", "C", "A"]

    imprimir_resultado_dfs(graph, cycle)

    output = capsys.readouterr().out
    assert "Total de nós: 3" in output
    assert "Total de arestas: 3" in output
    assert "Dependência circular detectada" in output
    assert "A ➔ B ➔ C ➔ A" in output
    assert "Módulos envolvidos: 3" in output
    assert "Dependências envolvidas: 3" in output
