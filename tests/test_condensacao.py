"""Testes da Atividade C: condensação e ordenação topológica."""

from pathlib import Path

import pytest

from src.ciclos import tem_ciclo
from src.condensacao import condensar, ordenacao_topologica
from src.extracao import construir_grafo
from src.grafo import Digrafo
from src.scc import kosaraju

DADOS = Path(__file__).resolve().parent.parent / "dados"


def _condensar(adj: dict[str, set[str]]):
    g = Digrafo(adj)
    sccs = kosaraju(g)
    g_cond, mapa = condensar(g, sccs)
    return g, sccs, g_cond, mapa


def _membros(sccs, mapa, v):
    return set(sccs[mapa[v]])


def _verificar_propriedades(g: Digrafo, sccs, g_cond: Digrafo, mapa):
    """Invariantes que toda condensação + ordem topológica deve cumprir."""
    # um super-vértice por SCC e cada vértice original mapeado
    assert g_cond.num_vertices() == len(sccs)
    assert set(mapa) == set(g.adj)
    # arco Cx -> Cy existe  <=>  há arco original entre vértices de Cx e Cy (x != y)
    esperados = {(f"C{mapa[u]}", f"C{mapa[v]}") for u, v in g.arcos() if mapa[u] != mapa[v]}
    assert set(g_cond.arcos()) == esperados
    # sem laços e sem ciclos: é um DAG
    assert all(x != y for x, y in g_cond.arcos())
    assert not tem_ciclo(g_cond)
    # ordem topológica: permutação dos super-vértices e X antes de Y para todo arco X -> Y
    ordem = ordenacao_topologica(g_cond)
    assert sorted(ordem) == sorted(g_cond.vertices())
    pos = {c: i for i, c in enumerate(ordem)}
    for x, y in g_cond.arcos():
        assert pos[x] < pos[y]
    # coerente com o grafo original: se u depende de v (SCCs diferentes), u vem antes
    for u, v in g.arcos():
        if mapa[u] != mapa[v]:
            assert pos[f"C{mapa[u]}"] < pos[f"C{mapa[v]}"]
    return ordem


# --- experimentos mínimos com grafos pequenos -------------------------------

def test_acíclico_cada_vertice_vira_uma_componente():
    g, sccs, g_cond, mapa = _condensar({"a": {"b", "c"}, "b": {"d"}, "c": {"d"}, "d": set()})
    assert g_cond.num_vertices() == 4 and g_cond.num_arcos() == 4
    ordem = _verificar_propriedades(g, sccs, g_cond, mapa)
    membros = [sccs[int(c[1:])] for c in ordem]
    assert membros[0] == ["a"] and membros[-1] == ["d"]


def test_ciclo_simples_vira_um_unico_vertice():
    g, sccs, g_cond, mapa = _condensar({"a": {"b"}, "b": {"c"}, "c": {"a"}})
    assert g_cond.num_vertices() == 1 and g_cond.num_arcos() == 0
    assert ordenacao_topologica(g_cond) == ["C0"]
    _verificar_propriedades(g, sccs, g_cond, mapa)


def test_componente_com_varios_ciclos():
    # a<->b, b<->c, a->c->a: vários ciclos na mesma SCC; d fora dela
    g, sccs, g_cond, mapa = _condensar(
        {"a": {"b", "c"}, "b": {"a", "c"}, "c": {"a", "b", "d"}, "d": set()}
    )
    assert g_cond.num_vertices() == 2
    assert _membros(sccs, mapa, "a") == {"a", "b", "c"}
    ordem = _verificar_propriedades(g, sccs, g_cond, mapa)
    assert ordem == [f"C{mapa['a']}", f"C{mapa['d']}"]


def test_duas_componentes_ciclicas_ligadas_em_um_sentido():
    # {a,b} cíclica -> {c,d} cíclica (vários arcos entre elas viram um só)
    g, sccs, g_cond, mapa = _condensar(
        {"a": {"b", "c"}, "b": {"a", "d"}, "c": {"d"}, "d": {"c"}}
    )
    ca, cc = f"C{mapa['a']}", f"C{mapa['c']}"
    assert ca != cc
    assert g_cond.arcos() == [(ca, cc)]                      # um único arco, sentido a -> c
    assert ordenacao_topologica(g_cond) == [ca, cc]          # quem depende vem antes
    _verificar_propriedades(g, sccs, g_cond, mapa)


def test_laco_nao_aparece_na_condensacao():
    g, sccs, g_cond, mapa = _condensar({"a": {"a", "b"}, "b": set()})
    assert g_cond.num_vertices() == 2
    assert g_cond.arcos() == [(f"C{mapa['a']}", f"C{mapa['b']}")]
    _verificar_propriedades(g, sccs, g_cond, mapa)


def test_vertices_isolados_e_grafo_vazio():
    g, sccs, g_cond, mapa = _condensar({"a": set(), "b": set()})
    assert g_cond.num_vertices() == 2 and g_cond.num_arcos() == 0
    _verificar_propriedades(g, sccs, g_cond, mapa)

    g_vazio = Digrafo()
    g_cond, mapa = condensar(g_vazio, kosaraju(g_vazio))
    assert g_cond.num_vertices() == 0 and mapa == {}
    assert ordenacao_topologica(g_cond) == []


def test_nomes_e_mapa_seguem_a_ordem_das_sccs():
    g = Digrafo({"a": {"b"}, "b": {"a", "c"}, "c": set()})
    sccs = [["c"], ["a", "b"]]
    g_cond, mapa = condensar(g, sccs)
    assert mapa == {"c": 0, "a": 1, "b": 1}
    assert g_cond.vertices() == ["C0", "C1"]
    assert g_cond.arcos() == [("C1", "C0")]
    assert ordenacao_topologica(g_cond) == ["C1", "C0"]


def test_condensar_nao_altera_o_grafo_original():
    adj = {"a": {"b"}, "b": {"a", "c"}, "c": set()}
    g = Digrafo(adj)
    condensar(g, kosaraju(g))
    assert g.adj == adj


# --- ordenação topológica ---------------------------------------------------

def test_ordem_topologica_desempate_numerico():
    # C2 e C10 sem arcos: C2 vem antes (ordem numérica, não alfabética)
    g_cond = Digrafo({f"C{i}": set() for i in range(12)})
    assert ordenacao_topologica(g_cond) == [f"C{i}" for i in range(12)]


def test_ordem_topologica_respeita_arcos_em_cadeia():
    g_cond = Digrafo({"C0": set(), "C1": {"C0"}, "C2": {"C1"}, "C3": {"C1", "C0"}})
    ordem = ordenacao_topologica(g_cond)
    pos = {c: i for i, c in enumerate(ordem)}
    for x, y in g_cond.arcos():
        assert pos[x] < pos[y]
    assert ordem[-1] == "C0"


def test_ordem_topologica_rejeita_grafo_com_ciclo():
    with pytest.raises(ValueError):
        ordenacao_topologica(Digrafo({"C0": {"C1"}, "C1": {"C0"}}))


def test_condensar_rejeita_particao_invalida():
    g = Digrafo({"a": {"b"}, "b": set()})
    with pytest.raises(ValueError):
        condensar(g, [["a"]])                 # b sem SCC
    with pytest.raises(ValueError):
        condensar(g, [["a", "b"], ["b"]])     # b repetido


# --- projetos de dados/ -----------------------------------------------------

@pytest.mark.parametrize("projeto", sorted(p.name for p in DADOS.iterdir() if p.is_dir()))
def test_projetos_de_exemplo(projeto):
    g = Digrafo(construir_grafo(DADOS / projeto))
    sccs = kosaraju(g)
    g_cond, mapa = condensar(g, sccs)
    _verificar_propriedades(g, sccs, g_cond, mapa)


def test_cyclic_app_agrupa_os_ciclos():
    g = Digrafo(construir_grafo(DADOS / "cyclic_app"))
    sccs = kosaraju(g)
    g_cond, mapa = condensar(g, sccs)
    a, b = "cyclic_app.direct.mod_a", "cyclic_app.direct.mod_b"
    x, y, z = (f"cyclic_app.long_cycle.mod_{n}" for n in "xyz")
    assert mapa[a] == mapa[b]
    assert mapa[x] == mapa[y] == mapa[z]
    assert g_cond.num_vertices() < g.num_vertices()
