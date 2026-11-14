"""Extração de dependências entre módulos de um projeto Python.

MODELO (documentar no relatório):
- Vértice = módulo (arquivo .py). __init__.py representa o pacote.
- Arco A -> B: A importa B, com B interno ao projeto.
- Reconhecidos: `import a.b`, `from a import b`, `from a.b import c`,
  imports relativos (resolvidos para nome absoluto).
  Em `from pkg import x`: se `pkg.x` é módulo interno, o arco vai para
  `pkg.x`; caso contrário (x é função/classe do pacote), vai para `pkg`.
- Contados: imports dentro de funções e dentro de `if TYPE_CHECKING`.
- Ignorados: módulos externos (stdlib, terceiros), `from __future__`,
  autoimportação (laços não são extraídos).
- `import a.b.c` gera arco só para `a.b.c` (não modela a, a.b implícitos).
"""

import ast
from pathlib import Path

EXCLUIDOS_PADRAO = {
    "venv",
    ".venv",
    "env",
    "__pycache__",
    ".git",
    "node_modules",
    "build",
    "dist",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
}


def caminho_para_modulo(arquivo: Path, raiz: Path) -> str | None:
    """pkg/sub/mod.py -> 'pkg.sub.mod'; pkg/__init__.py -> 'pkg'."""
    partes = list(arquivo.resolve().relative_to(raiz.resolve()).with_suffix("").parts)
    if partes and partes[-1] == "__init__":
        partes.pop()
    return ".".join(partes) or None


def listar_arquivos(raiz: Path, excluir: set[str] = EXCLUIDOS_PADRAO) -> list[Path]:
    arquivos = []
    for arq in sorted(raiz.rglob("*.py")):
        partes = arq.relative_to(raiz).parts
        if any(p in excluir or p.endswith(".egg-info") for p in partes):
            continue
        arquivos.append(arq)
    return arquivos


def _base_do_from(no: ast.ImportFrom, pacote: str) -> str | None:
    """Nome absoluto do módulo em `from <base> import ...`."""
    if not no.level:
        return no.module or None
    partes = pacote.split(".") if pacote else []
    sobe = no.level - 1
    if sobe > len(partes):
        return None
    partes = partes[: len(partes) - sobe]
    if no.module:
        partes += no.module.split(".")
    return ".".join(partes) or None


def importados(arquivo: Path, modulo: str, internos: set[str]) -> set[str]:
    """Módulos internos dos quais `arquivo` depende diretamente."""
    arvore = ast.parse(arquivo.read_text(encoding="utf-8"), filename=str(arquivo))
    pacote = modulo if arquivo.name == "__init__.py" else modulo.rpartition(".")[0]
    alvos: set[str] = set()

    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            alvos.update(a.name for a in no.names)
        elif isinstance(no, ast.ImportFrom):
            if no.module == "__future__":
                continue
            base = _base_do_from(no, pacote)
            if base is None:
                continue
            usa_base = False
            for a in no.names:
                sub = f"{base}.{a.name}"
                if a.name != "*" and sub in internos:
                    alvos.add(sub)
                else:
                    usa_base = True
            if usa_base:
                alvos.add(base)

    alvos.discard(modulo)
    return {t for t in alvos if t in internos}


def construir_grafo(
    raiz: Path | str, excluir: set[str] = EXCLUIDOS_PADRAO
) -> dict[str, set[str]]:
    """Lê o projeto em `raiz` e devolve {módulo: {módulos internos importados}}.

    Se o projeto usa layout src/, passe raiz = projeto/src.
    Arquivos com erro de sintaxe/encoding são pulados com aviso.
    """
    raiz = Path(raiz)
    arquivos: dict[str, Path] = {}
    for arq in listar_arquivos(raiz, excluir):
        mod = caminho_para_modulo(arq, raiz)
        if mod:
            arquivos[mod] = arq

    internos = set(arquivos)
    grafo: dict[str, set[str]] = {m: set() for m in arquivos}
    for mod, arq in arquivos.items():
        try:
            grafo[mod] = importados(arq, mod, internos)
        except (SyntaxError, UnicodeDecodeError) as erro:
            print(f"[aviso] {arq} ignorado: {erro}")
    return grafo
