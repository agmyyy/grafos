"""Atividade C: condensação e ordenação topológica.  (Responsável: Agmy)"""

from src.grafo import Digrafo


def condensar(g: Digrafo, sccs: list[list[str]]) -> tuple[Digrafo, dict[str, int]]:
    """Grafo de condensação (um vértice por SCC, nomeado 'C0', 'C1', ...)
    e o mapa vértice -> índice da SCC. O(V + E)."""
    raise NotImplementedError


def ordenacao_topologica(g_cond: Digrafo) -> list[str]:
    """Ordem topológica do DAG de condensação. O(V' + E')."""
    raise NotImplementedError
