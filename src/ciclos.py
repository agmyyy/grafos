"""Alcançabilidade e busca em profundidade para ciclos direcionados."""

from collections.abc import Iterator

from src.grafo import Digrafo


GraphType = Digrafo | dict[str, set[str]]


def _to_digraph(graph: GraphType) -> Digrafo:
    """Converte a representação recebida para a classe usada pelo projeto."""
    if isinstance(graph, Digrafo):
        return graph
    return Digrafo(graph)


def alcancaveis(g: GraphType, origem: str) -> set[str]:
    """Retorna os vértices alcançáveis a partir de `origem`.

    A origem só aparece no resultado se houver um caminho de volta até ela.
    O custo é O(V + E).
    """
    return _to_digraph(g).alcancaveis(origem)


def tem_ciclo(g: GraphType) -> bool:
    """Indica se existe algum ciclo direcionado no grafo (DFS em O(V + E))."""
    return encontrar_ciclo(g) is not None


def encontrar_ciclo(g: GraphType) -> list[str] | None:
    """Retorna um ciclo direcionado concreto ou None se não houver ciclo.

    O ciclo retornado começa e termina no mesmo vértice, por exemplo:
    ["a", "b", "c", "a"].
    """
    digraph = _to_digraph(g)
    visited: set[str] = set()

    for start in digraph.vertices():
        if start in visited:
            continue

        path: list[str] = [start]
        active_positions: dict[str, int] = {start: 0}
        dfs_stack: list[tuple[str, Iterator[str]]] = [
            (start, iter(digraph.vizinhos_saida(start)))
        ]
        visited.add(start)

        while dfs_stack:
            current_vertex, neighbors = dfs_stack[-1]

            try:
                neighbor = next(neighbors)
            except StopIteration:
                dfs_stack.pop()
                path.pop()
                del active_positions[current_vertex]
                continue

            if neighbor in active_positions:
                cycle_start = active_positions[neighbor]
                return path[cycle_start:] + [neighbor]

            if neighbor not in visited:
                visited.add(neighbor)
                active_positions[neighbor] = len(path)
                path.append(neighbor)
                dfs_stack.append(
                    (neighbor, iter(digraph.vizinhos_saida(neighbor)))
                )

    return None
