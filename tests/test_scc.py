from pathlib import Path

from src.extracao import construir_grafo
from src.grafo import Digrafo
from src.scc import (
    analisar_relacao_ciclo,
    classificar_sccs,
    encontrar_sccs,
    kosaraju,
    sccs_ciclicas,
)


def _componentes_por_vertices(grafo):
    return {frozenset(componente) for componente in encontrar_sccs(grafo)}


def test_digrafo_aciclico_tem_sccs_triviais():
    grafo = {"A": {"B", "C"}, "B": {"D"}, "C": {"D"}, "D": set(), "E": set()}

    componentes = encontrar_sccs(grafo)
    classificacoes = classificar_sccs(grafo, componentes)

    assert _componentes_por_vertices(grafo) == {
        frozenset({"A"}),
        frozenset({"B"}),
        frozenset({"C"}),
        frozenset({"D"}),
        frozenset({"E"}),
    }
    assert all(not componente["eh_ciclica"] for componente in classificacoes)
    assert all(componente["tamanho"] == 1 for componente in classificacoes)


def test_ciclo_simples_forma_uma_scc():
    grafo = {"A": {"B"}, "B": {"C"}, "C": {"A"}}

    componentes = encontrar_sccs(grafo)

    assert _componentes_por_vertices(grafo) == {frozenset({"A", "B", "C"})}
    assert classificar_sccs(grafo, componentes)[0]["eh_ciclica"] is True


def test_ciclos_cruzados_sao_agrupados_na_mesma_scc():
    grafo = {"A": {"B"}, "B": {"A", "C"}, "C": {"B", "D"}, "D": set()}

    componentes = encontrar_sccs(grafo)

    assert _componentes_por_vertices(grafo) == {
        frozenset({"A", "B", "C"}),
        frozenset({"D"}),
    }


def test_vertice_presente_somente_como_destino_e_incluido():
    grafo = {"origem": {"destino"}}

    assert _componentes_por_vertices(grafo) == {
        frozenset({"origem"}),
        frozenset({"destino"}),
    }


def test_self_loop_em_vertice_isolado_e_ciclico():
    grafo = {"isolado": {"isolado"}}

    classificacao = classificar_sccs(grafo, encontrar_sccs(grafo))

    assert classificacao == [
        {
            "id": 0,
            "vertices": ["isolado"],
            "tamanho": 1,
            "eh_ciclica": True,
        }
    ]


def test_no_externo_alcanca_ciclo_sem_pertencer_a_scc():
    grafo = {
        "externo": {"intermediario"},
        "intermediario": {"A"},
        "A": {"B"},
        "B": {"A"},
    }
    componentes = encontrar_sccs(grafo)
    relacao = analisar_relacao_ciclo(grafo, componentes)

    assert relacao["pertencem_a_scc_ciclica"] == {"A", "B"}
    assert relacao["alcancam_scc_ciclica_sem_pertencer"] == {
        "externo",
        "intermediario",
    }


def test_grafo_transposto_mantem_vertices_sem_arestas_de_saida():
    transposto = Digrafo({"origem": {"destino"}}).transposto()

    assert transposto.vertices() == ["destino", "origem"]
    assert transposto.tem_arco("destino", "origem")
    assert transposto.vizinhos_saida("origem") == []


def test_interfaces_legadas_de_scc_continuam_compativeis():
    grafo = Digrafo({"A": {"B"}, "B": {"A"}, "C": set()})
    componentes = kosaraju(grafo)

    assert {frozenset(componente) for componente in componentes} == {
        frozenset({"A", "B"}),
        frozenset({"C"}),
    }
    assert sccs_ciclicas(grafo, componentes) == [["A", "B"]]


def test_integracao_com_cyclic_app():
    raiz = Path(__file__).resolve().parents[1] / "dados" / "cyclic_app"
    grafo = construir_grafo(raiz)

    classificacoes = classificar_sccs(grafo, encontrar_sccs(grafo))
    tamanhos_ciclicos = sorted(
        componente["tamanho"]
        for componente in classificacoes
        if componente["eh_ciclica"]
    )

    assert tamanhos_ciclicos == [2, 3]


def test_integracao_com_layered_app_nao_tem_scc_ciclica():
    raiz = Path(__file__).resolve().parents[1] / "dados" / "layered_app"
    grafo = construir_grafo(raiz)

    classificacoes = classificar_sccs(grafo, encontrar_sccs(grafo))

    assert classificacoes
    assert all(not componente["eh_ciclica"] for componente in classificacoes)
