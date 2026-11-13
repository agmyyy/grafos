"""Atividade A: alcançabilidade e DFS para ciclos."""

from src.grafo import Digrafo


def alcancaveis(g: Digrafo, origem: str) -> set[str]:
    """Todos os vértices alcançáveis a partir de `origem` (ela só entra no
    resultado se estiver em um ciclo). O(V + E)."""
    raise NotImplementedError


def tem_ciclo(g: Digrafo) -> bool:
    """True se existe ciclo direcionado (DFS com cores). O(V + E)."""
    raise NotImplementedError


def encontrar_ciclo(g: Digrafo) -> list[str] | None:
    """Um ciclo concreto, ex.: ['a', 'b', 'c', 'a'], ou None. O(V + E)."""
    raise NotImplementedError
