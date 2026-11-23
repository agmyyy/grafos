"""A saída dos algoritmos não pode depender do hash aleatório das strings do Python."""

import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

SCRIPT = """
from src.enumeracao import encontrar_ciclos
from src.grafo import Digrafo
from src.scc import kosaraju
g = Digrafo({
    "a": {"b", "c"}, "b": {"a", "d"}, "c": {"a", "d"}, "d": {"a"},
    "m": {"n"}, "n": {"o"}, "o": {"m"}, "p": {"a", "m"}, "q": set(),
})
print(kosaraju(g))
print(encontrar_ciclos(g))
"""


def _rodar(seed: str) -> str:
    env = {**os.environ, "PYTHONHASHSEED": seed}
    r = subprocess.run([sys.executable, "-c", SCRIPT], cwd=RAIZ, env=env,
                       capture_output=True, text=True, check=True)
    return r.stdout


def test_saida_igual_com_hash_seeds_diferentes():
    saidas = {_rodar(seed) for seed in ("1", "2", "3", "4", "5")}
    assert len(saidas) == 1
