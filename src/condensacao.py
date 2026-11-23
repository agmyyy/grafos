"""Atividade C: condensação e ordenação topológica.  (Responsável: Agmy)

Condensação
-----------
Cada SCC vira um super-vértice 'Ci' (i = posição da SCC na lista recebida).
Existe o arco Ci -> Cj (i != j) quando há pelo menos um arco original u -> v
com u em Ci e v em Cj. Arcos internos a uma SCC (incluindo laços) somem.

Por que a condensação é um DAG: suponha um ciclo Ci -> ... -> Cj -> ... -> Ci
com i != j. Como cada SCC é fortemente conexa, qualquer vértice de Ci
alcançaria qualquer vértice de Cj e vice-versa, então Ci e Cj seriam a mesma
componente, o que contradiz a maximalidade das SCCs. Logo não há ciclos e a
ordenação topológica sempre existe.

Sentido dos arcos: A -> B significa "A depende de B". Na ordem topológica
produzida aqui, cada componente aparece ANTES das componentes de que depende:
as primeiras são as de nível mais alto (ninguém depende delas, por exemplo o
ponto de entrada da aplicação) e as últimas são as bases (não dependem de
ninguém). Para a ordem de compilação/carregamento (dependências primeiro),
basta ler a lista ao contrário.
"""

from collections import deque

from src.grafo import Digrafo


def _nome(i: int) -> str:
    return f"C{i}"


def _indice(nome: str) -> int:
    """'C12' -> 12 (ordena C2 antes de C10, ao contrário da ordem alfabética)."""
    return int(nome[1:])


def condensar(g: Digrafo, sccs: list[list[str]]) -> tuple[Digrafo, dict[str, int]]:
    """Grafo de condensação (um vértice por SCC, nomeado 'C0', 'C1', ...)
    e o mapa vértice -> índice da SCC. O(V + E).

    As SCCs devem particionar os vértices de g (como as devolvidas por
    scc.kosaraju). Levanta ValueError se algum vértice ficou de fora ou
    aparece em duas componentes.
    """
    mapa: dict[str, int] = {}
    for i, componente in enumerate(sccs):
        for v in componente:
            if v in mapa:
                raise ValueError(f"vértice {v!r} aparece em mais de uma SCC")
            mapa[v] = i

    faltando = [v for v in g.adj if v not in mapa]
    if faltando:
        raise ValueError(f"vértices sem SCC: {sorted(faltando)}")

    g_cond = Digrafo()
    for i in range(len(sccs)):
        g_cond.adicionar_vertice(_nome(i))

    for u, destinos in g.adj.items():
        cu = mapa[u]
        for v in destinos:
            cv = mapa[v]
            if cu != cv:  # arcos internos à SCC não aparecem na condensação
                g_cond.adicionar_arco(_nome(cu), _nome(cv))  # set: arcos repetidos viram um só

    return g_cond, mapa


def ordenacao_topologica(g_cond: Digrafo) -> list[str]:
    """Ordem topológica do DAG de condensação (algoritmo de Kahn). O(V' + E').

    Para todo arco X -> Y (X depende de Y), X aparece antes de Y.
    Empates são resolvidos pelo menor índice da componente, para a saída ser
    reproduzível (custo extra da ordenação: O(V' log V' + E' log Δ)).
    Levanta ValueError se o grafo tiver ciclo (não é um DAG).
    """
    grau_entrada: dict[str, int] = {v: 0 for v in g_cond.adj}
    for u in g_cond.adj:
        for v in g_cond.adj[u]:
            grau_entrada[v] += 1

    fila = deque(sorted((v for v, d in grau_entrada.items() if d == 0), key=_chave))
    ordem: list[str] = []
    while fila:
        u = fila.popleft()
        ordem.append(u)
        for v in sorted(g_cond.adj[u], key=_chave):
            grau_entrada[v] -= 1
            if grau_entrada[v] == 0:
                fila.append(v)

    if len(ordem) != len(grau_entrada):
        restantes = sorted((v for v in grau_entrada if grau_entrada[v] > 0), key=_chave)
        raise ValueError(f"o grafo tem ciclo; não há ordenação topológica (restam {restantes})")
    return ordem


def _chave(nome: str) -> tuple[int, int | str]:
    """Ordena 'C0', 'C1', ..., 'C10' numericamente; outros nomes, alfabeticamente."""
    if len(nome) > 1 and nome[0] == "C" and nome[1:].isdigit():
        return (0, _indice(nome))
    return (1, nome)
