from pathlib import Path

from analisar import main


def _projeto(raiz: Path) -> Path:
    pacote = raiz / "app"
    pacote.mkdir()
    (pacote / "__init__.py").write_text("")
    (pacote / "a.py").write_text("from app import b, c\n")
    (pacote / "b.py").write_text("from app import a\n")
    (pacote / "c.py").write_text("from app import a\n")
    return raiz


def test_padrao_lista_todos_os_ciclos(tmp_path, capsys):
    main([str(_projeto(tmp_path))])
    saida = capsys.readouterr().out
    assert "2 ciclo(s) encontrado(s)" in saida
    assert "app.a ➔ app.b ➔ app.a" in saida
    assert "app.a ➔ app.c ➔ app.a" in saida


def test_so_um_ciclo_roda_apenas_a_dfs(tmp_path, capsys):
    main([str(_projeto(tmp_path)), "--so-um-ciclo"])
    saida = capsys.readouterr().out
    assert "=== Ciclo (Atividade A: encontrar_ciclo) ===" in saida
    assert "1 ciclo encontrado" in saida
    assert "app.a ➔ app.b ➔ app.a  (2 módulo(s))" in saida
    assert "app.a ➔ app.c ➔ app.a" not in saida      # só um ciclo
    assert "=== Ciclos (todos" not in saida


def test_limite_de_ciclos(tmp_path, capsys):
    main([str(_projeto(tmp_path)), "--limite-ciclos", "1"])
    saida = capsys.readouterr().out
    assert "1+ ciclo(s) encontrado(s)" in saida
    assert "há mais ciclos" in saida


def test_grafo_aciclico(tmp_path, capsys):
    (tmp_path / "x.py").write_text("")
    (tmp_path / "y.py").write_text("import x\n")
    main([str(tmp_path)])
    assert "Nenhum ciclo foi encontrado" in capsys.readouterr().out


def test_alcancaveis(tmp_path, capsys):
    main([str(_projeto(tmp_path)), "--alcancaveis", "app.b"])
    saida = capsys.readouterr().out
    assert "=== Alcançáveis a partir de app.b ===" in saida
    assert "app.a" in saida and "app.c" in saida          # b -> a -> {b, c}
    assert "=== Ciclos" not in saida


def test_alcancaveis_modulo_inexistente(tmp_path):
    try:
        main([str(_projeto(tmp_path)), "--alcancaveis", "nao.existe"])
    except SystemExit:
        return
    raise AssertionError("deveria sair com erro")


def test_so_um_ciclo_nao_roda_o_kosaraju(tmp_path, capsys):
    main([str(_projeto(tmp_path)), "--so-um-ciclo"])
    assert "Componentes fortemente conexas" not in capsys.readouterr().out


def test_so_sccs_roda_apenas_o_kosaraju(tmp_path, capsys):
    main([str(_projeto(tmp_path)), "--so-sccs"])
    saida = capsys.readouterr().out
    assert "=== Componentes fortemente conexas ===" in saida
    assert "=== Ciclos" not in saida and "=== Ciclo (" not in saida


def test_padrao_mostra_ciclos_e_sccs(tmp_path, capsys):
    main([str(_projeto(tmp_path))])
    saida = capsys.readouterr().out
    assert "=== Ciclos (todos" in saida and "=== Componentes fortemente conexas ===" in saida


def test_so_condensacao_mostra_dag_e_ordem(tmp_path, capsys):
    pacote = tmp_path / "app"
    pacote.mkdir()
    (pacote / "__init__.py").write_text("")
    (pacote / "a.py").write_text("from app import b\n")
    (pacote / "b.py").write_text("from app import a, c\n")
    (pacote / "c.py").write_text("")
    main([str(tmp_path), "--so-condensacao"])
    saida = capsys.readouterr().out
    assert "=== Condensação (Atividade C) ===" in saida
    # componentes: {a, b}, {c} e {app} (o __init__, isolado); só {a, b} -> {c} entre elas
    assert "3 componente(s), 1 dependência(s) entre componentes" in saida
    linhas = saida.split("=== Ordenação topológica")[1].splitlines()[1:]
    ordem = [l for l in linhas if l.strip()]
    # app (o __init__) não depende de ninguém; {a, b} vem antes de {c}
    pos_ab = next(i for i, l in enumerate(ordem) if "app.a, app.b" in l)
    pos_c = next(i for i, l in enumerate(ordem) if "{app.c}" in l)
    assert pos_ab < pos_c
    assert "=== Componentes fortemente conexas ===" not in saida
