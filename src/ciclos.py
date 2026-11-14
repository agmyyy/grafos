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


def imprimir_resultado_dfs(
    grafo: dict[str, set[str]], ciclo: list[str] | None
) -> None:
    """Imprime um resumo do grafo e o resultado da detecção de ciclos."""
    vertices = set(grafo)
    for destinations in grafo.values():
        vertices.update(destinations)

    total_edges = sum(len(destinations) for destinations in grafo.values())

    print("=== Resumo da análise DFS ===")
    print(f"Total de nós: {len(vertices)}")
    print(f"Total de arestas: {total_edges}")

    if ciclo is not None:
        cycle_nodes = set(ciclo)
        cycle_edge_count = max(len(ciclo) - 1, 0)
        cycle_path = " ➔ ".join(ciclo) if ciclo else "(caminho vazio)"

        print("\n Dependência circular detectada!")
        print(f"Caminho do ciclo: {cycle_path}")
        print(f"Módulos envolvidos: {len(cycle_nodes)}")
        print(f"Dependências envolvidas: {cycle_edge_count}")
        return

    print("Nenhum ciclo foi encontrado; o grafo é acíclico neste escopo.")


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
