"""Atividade B: Kosaraju Sharir."""
"""Componentes fortemente conexas e análise de dependências cíclicas."""

from src.grafo import Digrafo


def _normalizar_grafo(grafo: dict[str, set[str]]) -> dict[str, set[str]]:
    """Inclui no grafo todos os vértices mencionados como origem ou destino."""
    vertices = set(grafo)
    for destinos in grafo.values():
        vertices.update(destinos)
    # sorted: a ordem das SCCs não pode depender do hash das strings (ver README, seção 7)
    return {vertice: set(grafo.get(vertice, set())) for vertice in sorted(vertices)}


def encontrar_sccs(grafo: dict[str, set[str]]) -> list[set[str]]:
    """Retorna as componentes fortemente conexas pelo algoritmo de Kosaraju-Sharir.

    A busca é iterativa para evitar limites de recursão e percorre todos os
    vértices, inclusive os que aparecem somente como destino. Complexidade O(V + E).
    """
    adjacencias = _normalizar_grafo(grafo)
    visitados: set[str] = set()
    ordem_termino: list[str] = []

    for inicio in adjacencias:
        if inicio in visitados:
            continue

        visitados.add(inicio)
        pilha_dfs = [(inicio, iter(sorted(adjacencias[inicio])))]
        while pilha_dfs:
            vertice, vizinhos = pilha_dfs[-1]
            try:
                vizinho = next(vizinhos)
            except StopIteration:
                pilha_dfs.pop()
                ordem_termino.append(vertice)
                continue

            if vizinho not in visitados:
                visitados.add(vizinho)
                pilha_dfs.append((vizinho, iter(sorted(adjacencias[vizinho]))))

    transposto = Digrafo(adjacencias).transposto().adj
    visitados.clear()
    componentes: list[set[str]] = []

    for inicio in reversed(ordem_termino):
        if inicio in visitados:
            continue

        componente: set[str] = set()
        pilha = [inicio]
        visitados.add(inicio)
        while pilha:
            vertice = pilha.pop()
            componente.add(vertice)
            for vizinho in transposto[vertice]:
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    pilha.append(vizinho)
        componentes.append(componente)

    return componentes


def classificar_sccs(
    grafo: dict[str, set[str]], sccs: list[set[str]]
) -> list[dict[str, object]]:
    """Classifica cada SCC como cíclica ou trivial e retorna seus metadados."""
    classificacoes: list[dict[str, object]] = []
    for identificador, componente in enumerate(sccs):
        vertices = sorted(componente)
        eh_ciclica = len(componente) > 1 or any(
            vertice in grafo.get(vertice, set()) for vertice in componente
        )
        classificacoes.append(
            {
                "id": identificador,
                "vertices": vertices,
                "tamanho": len(componente),
                "eh_ciclica": eh_ciclica,
            }
        )
    return classificacoes


def analisar_relacao_ciclo(
    grafo: dict[str, set[str]], sccs: list[set[str]]
) -> dict[str, set[str]]:
    """Separa membros de ciclos dos nós externos que alcançam algum ciclo.

    Como um arco A -> B significa que A depende de B, percorrer o transposto
    a partir dos nós cíclicos encontra os nós que chegam a esses ciclos.
    """
    classificacoes = classificar_sccs(grafo, sccs)
    nos_ciclicos = {
        vertice
        for classificacao in classificacoes
        if classificacao["eh_ciclica"]
        for vertice in classificacao["vertices"]
    }

    adjacencias = _normalizar_grafo(grafo)
    transposto = Digrafo(adjacencias).transposto().adj
    alcancam_ciclo = set(nos_ciclicos)
    pilha = list(nos_ciclicos)

    while pilha:
        vertice = pilha.pop()
        for predecessor in transposto[vertice]:
            if predecessor not in alcancam_ciclo:
                alcancam_ciclo.add(predecessor)
                pilha.append(predecessor)

    return {
        "pertencem_a_scc_ciclica": nos_ciclicos,
        "alcancam_scc_ciclica_sem_pertencer": alcancam_ciclo - nos_ciclicos,
    }


def kosaraju(g: Digrafo) -> list[list[str]]:
    """Compatibilidade com a interface anterior; retorna SCCs como listas."""
    return [sorted(componente) for componente in encontrar_sccs(g.adj)]


def sccs_ciclicas(g: Digrafo, sccs: list[list[str]]) -> list[list[str]]:
    """Retorna somente as SCCs cíclicas, mantendo a interface anterior."""
    componentes = [set(componente) for componente in sccs]
    classificacoes = classificar_sccs(g.adj, componentes)
    return [
        sorted(componente)
        for componente, classificacao in zip(componentes, classificacoes)
        if classificacao["eh_ciclica"]
    ]
