"""Garante que cada exemplo de dados/ tem a estrutura que o relatório descreve."""

from pathlib import Path

from src.condensacao import condensar, ordenacao_topologica
from src.enumeracao import encontrar_ciclos
from src.extracao import construir_grafo
from src.grafo import Digrafo
from src.scc import kosaraju, sccs_ciclicas

DADOS = Path(__file__).resolve().parent.parent / "dados"


def _analisar(nome: str):
    g = Digrafo(construir_grafo(DADOS / nome))
    sccs = kosaraju(g)
    return g, sccs, sccs_ciclicas(g, sccs), encontrar_ciclos(g, 100)


def test_aciclicos():
    for nome in ("basic_app", "layered_app", "mixed_dependencies"):
        _, _, ciclicas, ciclos = _analisar(nome)
        assert ciclicas == [] and ciclos == [], nome


def test_ciclo_simples():
    _, _, ciclicas, ciclos = _analisar("ciclo_simples")
    assert ciclos == [["ciclo_simples.a", "ciclo_simples.b", "ciclo_simples.c", "ciclo_simples.a"]]
    assert ciclicas == [["ciclo_simples.a", "ciclo_simples.b", "ciclo_simples.c"]]


def test_componente_com_varios_ciclos():
    _, _, ciclicas, ciclos = _analisar("multiplos_ciclos")
    assert len(ciclicas) == 1 and len(ciclicas[0]) == 3      # uma SCC com 3 módulos...
    assert len(ciclos) == 2                                    # ...e dois ciclos dentro dela


def test_duas_sccs_ciclicas_ligadas_em_um_sentido():
    g, sccs, ciclicas, ciclos = _analisar("duas_sccs_ligadas")
    p = "duas_sccs_ligadas."
    comp_a = [p + "a1", p + "a2"]
    comp_b = [p + "b1", p + "b2", p + "b3"]
    assert sorted(ciclicas) == [comp_a, comp_b]
    assert len(ciclos) == 2

    g_cond, mapa = condensar(g, sccs)
    ca, cb = f"C{mapa[p + 'a1']}", f"C{mapa[p + 'b1']}"
    assert g_cond.tem_arco(ca, cb)                 # A depende de B...
    assert not g_cond.tem_arco(cb, ca)             # ...mas B não depende de A
    ordem = ordenacao_topologica(g_cond)
    assert ordem.index(ca) < ordem.index(cb)       # quem depende vem antes
