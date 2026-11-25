from pathlib import Path

from src.extracao import construir_grafo


def _escrever(raiz: Path, arquivos: dict[str, str]) -> None:
    for caminho, conteudo in arquivos.items():
        arq = raiz / caminho
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(conteudo, encoding="utf-8")


def test_extracao_basica(tmp_path):
    _escrever(tmp_path, {
        "pkg/__init__.py": "",
        "pkg/a.py": "from pkg import b\n",          # submódulo
        "pkg/b.py": "import pkg.a\n",                # import qualificado
        "pkg/c.py": "from . import a\n",             # relativo
        "pkg/d.py": "from .a import algo\n",         # relativo com símbolo
        "pkg/e.py": "import os\nimport requests\n",  # externos ignorados
        "pkg/f.py": "def g():\n    import pkg.a\n",  # import dentro de função
    })
    g = construir_grafo(tmp_path)
    assert g["pkg.a"] == {"pkg.b"}
    assert g["pkg.b"] == {"pkg.a"}
    assert g["pkg.c"] == {"pkg.a"}
    assert g["pkg.d"] == {"pkg.a"}
    assert g["pkg.e"] == set()
    assert g["pkg.f"] == {"pkg.a"}
    assert g["pkg"] == set()


def test_from_pacote_com_simbolo_vai_para_o_pacote(tmp_path):
    _escrever(tmp_path, {
        "pkg/__init__.py": "VERSAO = 1\n",
        "pkg/a.py": "from pkg import VERSAO\n",
    })
    assert construir_grafo(tmp_path)["pkg.a"] == {"pkg"}


def test_exclui_venv_e_ignora_autoimport(tmp_path):
    _escrever(tmp_path, {
        "m.py": "import m\n",
        ".venv/lib/x.py": "import m\n",
    })
    g = construir_grafo(tmp_path)
    assert list(g) == ["m"]
    assert g["m"] == set()


def test_arquivo_com_erro_de_sintaxe_e_pulado(tmp_path):
    _escrever(tmp_path, {"ok.py": "", "quebrado.py": "def (:\n"})
    g = construir_grafo(tmp_path)
    assert g["quebrado"] == set()
    assert "ok" in g
