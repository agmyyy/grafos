"""Atividade B: Kosaraju–Sharir."""

from src.grafo import Digrafo


def kosaraju(g: Digrafo) -> list[list[str]]:
    """Lista de SCCs; cada SCC é uma lista de vértices. O(V + E)."""
    raise NotImplementedError


def sccs_ciclicas(g: Digrafo, sccs: list[list[str]]) -> list[list[str]]:
    """SCCs com ciclo: tamanho > 1, ou tamanho 1 com laço (v -> v)."""
    raise NotImplementedError
