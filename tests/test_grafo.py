from src.grafo import Digrafo


def test_arco_cria_vertices():
    g = Digrafo()
    g.adicionar_arco("a", "b")
    assert g.vertices() == ["a", "b"]
    assert g.tem_arco("a", "b")
    assert not g.tem_arco("b", "a")


def test_arco_duplicado_nao_acumula():
    g = Digrafo()
    g.adicionar_arco("a", "b")
    g.adicionar_arco("a", "b")
    assert g.num_arcos() == 1


def test_remover_arco():
    g = Digrafo({"a": {"b"}})
    g.remover_arco("a", "b")
    assert not g.tem_arco("a", "b")
    g.remover_arco("a", "b")  # remover de novo não dá erro


def test_construtor_cria_vertices_so_destino():
    g = Digrafo({"a": {"b"}})
    assert g.vertices() == ["a", "b"]
    assert g.vizinhos("b") == []


def test_vizinhos_ordenados():
    g = Digrafo({"a": {"z", "c", "b"}})
    assert g.vizinhos("a") == ["b", "c", "z"]


def test_transposto():
    g = Digrafo({"a": {"b"}, "b": {"c"}})
    t = g.transposto()
    assert t.tem_arco("b", "a") and t.tem_arco("c", "b")
    assert not t.tem_arco("a", "b")
    assert t.vertices() == g.vertices()


def test_copia_independente():
    g = Digrafo({"a": {"b"}})
    c = g.copia()
    c.remover_arco("a", "b")
    assert g.tem_arco("a", "b")


def test_laco():
    g = Digrafo()
    g.adicionar_arco("a", "a")
    assert g.tem_arco("a", "a")
