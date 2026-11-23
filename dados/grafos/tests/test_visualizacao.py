import json
import re

from src.grafo import Digrafo
from src.visualizacao import gerar_html, montar_dados


def _extrair_json(html: str) -> dict:
    m = re.search(r"const DADOS = (.*?);\nconst NS", html, re.S)
    return json.loads(m.group(1).replace("<\\/", "</"))


def test_montar_dados_so_com_grafo():
    g = Digrafo({"a": {"b"}, "b": set()})
    d = montar_dados(g, "demo")
    assert d["nos"] == ["a", "b"]
    assert d["arcos"] == [["a", "b"]]
    assert d["sccs"] is None and d["ciclo"] is None and d["condensacao"] is None


def test_montar_dados_com_condensacao():
    g = Digrafo({"a": {"b"}, "b": {"a", "c"}, "c": set()})
    sccs = [["c"], ["b", "a"]]
    mapa = {"c": 0, "a": 1, "b": 1}
    gc = Digrafo({"C1": {"C0"}, "C0": set()})
    d = montar_dados(g, "demo", sccs, ["a", "b", "a"], gc, mapa, ["C1", "C0"])
    assert d["sccs"] == [["c"], ["a", "b"]]
    assert d["condensacao"]["arcos"] == [["C1", "C0"]]
    membros = {n["id"]: n["membros"] for n in d["condensacao"]["nos"]}
    assert membros == {"C0": ["c"], "C1": ["a", "b"]}
    assert d["condensacao"]["ordem"] == ["C1", "C0"]


def test_gerar_html_embute_dados_validos():
    g = Digrafo({"a": {"b"}})
    html = gerar_html(montar_dados(g, "meu projeto"))
    assert "<svg" in html and "meu projeto" in html
    assert _extrair_json(html)["arcos"] == [["a", "b"]]


def test_html_nao_quebra_com_script_no_nome():
    g = Digrafo({"</script><b>": set()})
    html = gerar_html(montar_dados(g, "x"))
    assert html.count("</script>") == 1          # só o fechamento do próprio script
    assert _extrair_json(html)["nos"] == ["</script><b>"]


def test_lista_de_ciclos_nos_dados():
    g = Digrafo({"a": {"b", "c"}, "b": {"a"}, "c": {"a"}})
    d = montar_dados(g, "demo", ciclos=[["a", "b", "a"], ["a", "c", "a"]], ciclos_truncado=True)
    assert d["ciclos"] == [["a", "b", "a"], ["a", "c", "a"]]
    assert d["ciclos_truncado"] is True


def test_um_ciclo_vira_lista_e_aciclico_e_lista_vazia():
    g = Digrafo({"a": {"b"}, "b": {"a"}})
    assert montar_dados(g, "x", ciclo=["a", "b", "a"])["ciclos"] == [["a", "b", "a"]]
    assert montar_dados(g, "x", ciclos=[])["ciclos"] == []
    assert montar_dados(g, "x")["ciclos"] is None
