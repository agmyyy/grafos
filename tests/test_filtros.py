import sys
from pathlib import Path

import visualizar
from src.filtros import carregar_grafo, sem_isolados, sem_pacotes_isolados


def _escrever(raiz: Path, arquivos: dict[str, str]) -> None:
    for caminho, conteudo in arquivos.items():
        arq = raiz / caminho
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(conteudo, encoding="utf-8")


def _projeto(raiz: Path) -> Path:
    _escrever(raiz, {
        "app/__init__.py": "",               # pacote vazio, ninguém importa: isolado
        "app/a.py": "from app import b\n",
        "app/b.py": "",
        "tests/__init__.py": "",
        "tests/test_a.py": "from app import a\n",
        "docs/conf.py": "",
    })
    return raiz


def test_sem_isolados_remove_so_quem_nao_tem_arco():
    g = {"a": {"b"}, "b": set(), "c": set(), "d": {"d"}}
    assert sem_isolados(g) == {"a": {"b"}, "b": set(), "d": {"d"}}   # c some; laço de d fica


def test_sem_isolados_nao_muda_o_grafo_original():
    g = {"a": set(), "b": {"a"}}
    sem_isolados(g)
    assert set(g) == {"a", "b"}


def test_sem_pacotes_isolados_mantem_modulos_comuns():
    g = {"pkg": set(), "pkg.a": {"pkg.b"}, "pkg.b": set(), "solto": set(), "base": {"util"}, "util": set()}
    r = sem_pacotes_isolados(g, {"pkg"})
    assert "pkg" not in r                      # pacote sem arco: some
    assert "solto" in r                        # módulo comum isolado: fica


def test_sem_pacotes_isolados_mantem_pacote_com_arco():
    g = {"pkg": set(), "uso": {"pkg"}}          # alguém depende do pacote
    assert set(sem_pacotes_isolados(g, {"pkg"})) == {"pkg", "uso"}


def test_padrao_nao_mostra_pacotes_vazios(tmp_path):
    g = carregar_grafo(_projeto(tmp_path))
    # somem app e tests (__init__.py sem arco); docs.conf (módulo comum isolado) fica
    assert set(g) == {"app.a", "app.b", "tests.test_a", "docs.conf"}


def test_padrao_mantem_init_com_dependencias(tmp_path):
    _escrever(tmp_path, {
        "app/__init__.py": "from app import a\n",   # o pacote depende do submódulo
        "app/a.py": "",
    })
    assert carregar_grafo(tmp_path) == {"app": {"app.a"}, "app.a": set()}


def test_pode_desligar_o_padrao(tmp_path):
    g = carregar_grafo(_projeto(tmp_path), ocultar_init_isolados=False)
    assert set(g) == {"app", "app.a", "app.b", "tests", "tests.test_a", "docs.conf"}


def test_excluir_pastas(tmp_path):
    g = carregar_grafo(_projeto(tmp_path), excluir=["tests", "docs"])
    assert set(g) == {"app.a", "app.b"}


def test_ocultar_isolados(tmp_path):
    g = carregar_grafo(_projeto(tmp_path), ocultar_isolados=True)
    assert set(g) == {"app.a", "app.b", "tests.test_a"}      # some também o docs.conf


def test_visualizar_aceita_os_parametros(tmp_path):
    import json
    import re

    projeto = _projeto(tmp_path / "proj")
    saida = tmp_path / "saida.html"
    antigo = sys.argv
    sys.argv = ["visualizar.py", str(projeto), "-o", str(saida),
                "--excluir", "tests", "--excluir", "docs", "--sem-isolados"]
    try:
        visualizar.main()
    finally:
        sys.argv = antigo
    html = saida.read_text(encoding="utf-8")
    dados = json.loads(re.search(r"const DADOS = (.*?);\nconst NS", html, re.S).group(1))
    assert dados["nos"] == ["app.a", "app.b"]
