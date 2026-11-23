from src.grafo import Digrafo
from src.remocao import ELIMINA_TODAS, PARCIAL, SEM_EFEITO, formatar_remocao, simular_remocao


def _hub():
    # hub <-> a, hub <-> b (um componente com dois ciclos); web só depende do hub
    return Digrafo({"hub": {"a", "b"}, "a": {"hub"}, "b": {"hub"}, "web": {"hub"}})


def test_ciclo_simples_e_eliminado():
    g = Digrafo({"a": {"b"}, "b": {"a"}})
    r = simular_remocao(g, "a", "b")
    assert r["veredito"] == ELIMINA_TODAS
    assert r["antes"]["tem_ciclo"] and not r["depois"]["tem_ciclo"]
    assert r["pedacos_ciclicos"] == []
    assert r["deixaram_de_estar_em_ciclo"] == ["a", "b"]


def test_remocao_parcial_nao_elimina_todas_as_circularidades():
    r = simular_remocao(_hub(), "hub", "a")
    assert r["veredito"] == PARCIAL
    assert r["scc_afetada"] == ["a", "b", "hub"]
    assert sorted(r["pedacos"]) == [["a"], ["b", "hub"]]
    assert r["pedacos_ciclicos"] == [["b", "hub"]]
    assert r["depois"]["tem_ciclo"]
    assert r["ciclos_que_usavam_o_arco"] == [["a", "hub", "a"]]
    assert r["depois"]["ciclos"] == [["b", "hub", "b"]]
    assert r["deixaram_de_estar_em_ciclo"] == ["a"]


def test_arco_entre_componentes_nao_muda_nada():
    r = simular_remocao(_hub(), "web", "hub")
    assert r["veredito"] == SEM_EFEITO
    assert r["scc_afetada"] is None and r["pedacos"] == []
    assert r["antes"]["sccs"] == r["depois"]["sccs"]
    assert r["antes"]["ciclos"] == r["depois"]["ciclos"]


def test_laco_removido():
    g = Digrafo({"a": {"a", "b"}, "b": set()})
    r = simular_remocao(g, "a", "a")
    assert r["veredito"] == ELIMINA_TODAS
    assert r["antes"]["tem_ciclo"] and not r["depois"]["tem_ciclo"]


def test_arco_redundante_dentro_da_scc_nao_divide_a_componente():
    g = Digrafo({"a": {"b", "c"}, "b": {"c"}, "c": {"a"}})   # a->c é redundante
    r = simular_remocao(g, "a", "c")
    assert r["veredito"] == PARCIAL
    assert r["pedacos"] == [["a", "b", "c"]]                  # continua uma SCC só


def test_grafo_original_nao_e_alterado():
    g = _hub()
    simular_remocao(g, "hub", "a")
    assert g.tem_arco("hub", "a") and g.num_arcos() == 5


def test_arco_inexistente_levanta_erro():
    try:
        simular_remocao(_hub(), "a", "b")
    except ValueError as e:
        assert "não existe" in str(e)
        return
    raise AssertionError("deveria levantar ValueError")


def test_pedacos_particionam_a_scc_afetada():
    g = Digrafo({"a": {"b"}, "b": {"c"}, "c": {"d"}, "d": {"a", "b"}})
    r = simular_remocao(g, "d", "b")
    juntos = sorted(v for p in r["pedacos"] for v in p)
    assert juntos == sorted(r["scc_afetada"])


def test_formatar_os_tres_resultados():
    parcial = formatar_remocao(simular_remocao(_hub(), "hub", "a"))
    assert "=== Remoção de hub ➔ a ===" in parcial
    assert "NÃO eliminou todas as circularidades" in parcial
    assert "(cíclica)" in parcial and "(sem ciclo)" in parcial

    elimina = formatar_remocao(simular_remocao(Digrafo({"a": {"b"}, "b": {"a"}}), "a", "b"))
    assert "ELIMINOU todas as circularidades" in elimina

    sem_efeito = formatar_remocao(simular_remocao(_hub(), "web", "hub"))
    assert "não altera ciclos nem SCCs" in sem_efeito
