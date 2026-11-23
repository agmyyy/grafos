from src.enumeracao import encontrar_ciclos
from src.grafo import Digrafo


def _completo(vertices):
    return {u: {v for v in vertices if v != u} for u in vertices}


def _valido(g, ciclo):
    assert len(ciclo) >= 2 and ciclo[0] == ciclo[-1]
    assert len(set(ciclo[:-1])) == len(ciclo) - 1          # sem vértice repetido
    assert ciclo[0] == min(ciclo[:-1])                      # começa no menor
    for u, v in zip(ciclo, ciclo[1:]):
        assert v in g[u]


def test_aciclico_nao_tem_ciclos():
    assert encontrar_ciclos({"a": {"b", "c"}, "b": {"c"}, "c": set()}) == []


def test_ciclo_simples():
    assert encontrar_ciclos({"a": {"b"}, "b": {"c"}, "c": {"a"}}) == [["a", "b", "c", "a"]]


def test_dois_ciclos_no_mesmo_vertice():
    g = {"a": {"b", "c"}, "b": {"a"}, "c": {"a"}}
    assert encontrar_ciclos(g) == [["a", "b", "a"], ["a", "c", "a"]]


def test_laco():
    assert encontrar_ciclos({"a": {"a"}}) == [["a", "a"]]


def test_completo_com_3_vertices_tem_5_ciclos():
    g = _completo(["a", "b", "c"])
    ciclos = encontrar_ciclos(g)
    assert len(ciclos) == 5                                  # 3 de tamanho 2 + 2 de tamanho 3
    assert len({tuple(c) for c in ciclos}) == 5              # sem repetição
    for c in ciclos:
        _valido(g, c)


def test_completo_com_4_vertices_tem_20_ciclos():
    g = _completo(["a", "b", "c", "d"])
    assert len(encontrar_ciclos(g, limite=1000)) == 20       # 6 + 8 + 6


def test_limite():
    g = _completo(["a", "b", "c", "d"])
    assert len(encontrar_ciclos(g, limite=5)) == 5
    assert encontrar_ciclos(g, limite=0) == []


def test_aceita_digrafo_e_e_deterministico():
    g = Digrafo({"b": {"a"}, "a": {"b"}})
    assert encontrar_ciclos(g) == encontrar_ciclos(g) == [["a", "b", "a"]]


def test_ciclos_em_componentes_diferentes():
    g = {"a": {"b"}, "b": {"a"}, "x": {"y"}, "y": {"z"}, "z": {"x"}, "m": {"a", "x"}}
    assert encontrar_ciclos(g) == [["a", "b", "a"], ["x", "y", "z", "x"]]
