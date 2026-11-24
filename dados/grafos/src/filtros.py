"""Filtros opcionais sobre o grafo extraído.

São opções de VISÃO da análise: o modelo continua o mesmo (um vértice por módulo),
mas dá para deixar de fora pastas que não interessam (testes, documentação, scripts)
e módulos sem nenhuma ligação com os demais.

Nenhum filtro altera ciclos nem SCCs não triviais: um vértice sem arestas nunca
participa de ciclo. Só mudam as contagens de vértices e de SCCs triviais.
"""

from pathlib import Path
from typing import Iterable

from src.extracao import (
    EXCLUIDOS_PADRAO,
    caminho_para_modulo,
    construir_grafo,
    listar_arquivos,
)


def _com_arco(grafo: dict[str, set[str]]) -> set[str]:
    """Vértices que têm algum arco, de entrada ou de saída. O(V + E)."""
    com_arco = {u for u, destinos in grafo.items() if destinos}
    for destinos in grafo.values():
        com_arco |= destinos
    return com_arco


def sem_isolados(grafo: dict[str, set[str]]) -> dict[str, set[str]]:
    """Remove TODOS os vértices sem arco (de entrada ou de saída). O(V + E).

    Atenção: isso inclui módulos reais que não importam nem são importados
    (um script, um conf.py). Para tirar só os __init__.py isolados, use
    `sem_pacotes_isolados`.
    """
    com_arco = _com_arco(grafo)
    return {u: set(destinos) for u, destinos in grafo.items() if u in com_arco}


def sem_pacotes_isolados(
    grafo: dict[str, set[str]], pacotes: set[str]
) -> dict[str, set[str]]:
    """Remove só os vértices de PACOTE (`__init__.py`) que não têm nenhum arco.

    Módulos comuns são mantidos mesmo que isolados. `pacotes` é o conjunto de
    nomes de módulo que vêm de arquivos `__init__.py`. O(V + E).
    """
    com_arco = _com_arco(grafo)
    return {
        u: set(destinos)
        for u, destinos in grafo.items()
        if u in com_arco or u not in pacotes
    }


def _nomes_de_pacotes(raiz: Path, excluir: set[str]) -> set[str]:
    nomes = {
        caminho_para_modulo(arq, raiz)
        for arq in listar_arquivos(raiz, excluir)
        if arq.name == "__init__.py"
    }
    nomes.discard(None)
    return nomes


def carregar_grafo(
    raiz: Path | str,
    excluir: Iterable[str] = (),
    ocultar_isolados: bool = False,
    ocultar_init_isolados: bool = True,
) -> dict[str, set[str]]:
    """Extrai o grafo de `raiz` aplicando os filtros pedidos.

    - excluir: nomes de pastas (ou arquivos) a ignorar, somados aos padrões
      (.venv, __pycache__, build, dist, .git...). Ex.: ["tests", "docs", "scripts"].
    - ocultar_isolados: remove todo módulo sem dependência de/para outros.
    - ocultar_init_isolados (padrão: True): remove os `__init__.py` sem nenhuma ligação,
      que são os vértices que "parecem pastas" (src, tests, o nome do app). Um
      `__init__.py` com dependências de verdade é mantido, porque ciclos passando
      pelo pacote são comuns em Python.
    """
    raiz = Path(raiz)
    ignorar = set(EXCLUIDOS_PADRAO) | set(excluir)
    grafo = construir_grafo(raiz, ignorar)
    if ocultar_init_isolados:
        grafo = sem_pacotes_isolados(grafo, _nomes_de_pacotes(raiz, ignorar))
    if ocultar_isolados:
        grafo = sem_isolados(grafo)
    return grafo
