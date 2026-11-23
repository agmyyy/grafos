"""Atividade D: simulação de remoção de dependências.

Pergunta respondida: se a dependência u -> v for removida, o que muda nos ciclos
e nas componentes fortemente conexas (SCCs)?

Regra que a simulação confirma (e que vale a pena explicar no relatório):
- Se u e v NÃO estão na mesma SCC, o arco não participa de nenhum ciclo: remover
  não altera ciclos nem SCCs.
- Se u e v estão na mesma SCC, o arco é interno a ela. A remoção pode dividir a SCC
  em pedaços menores, e esses pedaços podem continuar cíclicos. Quando isso
  acontece, a remoção NÃO eliminou todas as circularidades da componente.

Complexidade: a cópia e a remoção custam O(V + E); reavaliar cada versão do grafo
(DFS de ciclo e Kosaraju–Sharir) custa O(V + E); a lista de ciclos vem de
`enumeracao.encontrar_ciclos`, limitada por `limite_ciclos` (o número de ciclos
pode ser exponencial).
"""

from src.ciclos import tem_ciclo
from src.enumeracao import encontrar_ciclos
from src.grafo import Digrafo
from src.scc import kosaraju, sccs_ciclicas

SEM_EFEITO = "sem_efeito"          # o arco não está em nenhum ciclo
ELIMINA_TODAS = "elimina_todas"    # a SCC deixa de ser cíclica
PARCIAL = "parcial"                # ainda sobra circularidade na componente


def _avaliar(g: Digrafo, limite_ciclos: int) -> dict:
    """Estado de um grafo: existência de ciclo, SCCs, SCCs cíclicas e ciclos."""
    sccs = kosaraju(g)
    ciclos = encontrar_ciclos(g, limite_ciclos + 1)
    return {
        "tem_ciclo": tem_ciclo(g),
        "sccs": sccs,
        "sccs_ciclicas": sccs_ciclicas(g, sccs),
        "ciclos": ciclos[:limite_ciclos],
        "ciclos_truncado": len(ciclos) > limite_ciclos,
    }


def _modulos(componentes: list[list[str]]) -> set[str]:
    return {v for c in componentes for v in c}


def simular_remocao(g: Digrafo, u: str, v: str, limite_ciclos: int = 50) -> dict:
    """Remove u -> v numa CÓPIA de g e compara antes e depois.

    O grafo original não é alterado. Levanta ValueError se u -> v não existe.

    Devolve um dicionário com:
    - arco: (u, v)
    - antes / depois: {tem_ciclo, sccs, sccs_ciclicas, ciclos, ciclos_truncado}
    - scc_afetada: a SCC que continha u e v (None se o arco liga componentes
      diferentes, isto é, não participa de nenhum ciclo)
    - pedacos: SCCs em que scc_afetada ficou dividida depois da remoção
    - pedacos_ciclicos: dos pedaços, os que ainda são cíclicos
    - ciclos_que_usavam_o_arco: ciclos de "antes" que passavam por u -> v
    - deixaram_de_estar_em_ciclo: módulos que saíram de SCCs cíclicas
    - veredito: SEM_EFEITO, ELIMINA_TODAS ou PARCIAL
    """
    if not g.tem_arco(u, v):
        raise ValueError(f"a dependência {u} -> {v} não existe no grafo")

    apos = g.copia()
    apos.remover_arco(u, v)

    antes = _avaliar(g, limite_ciclos)
    depois = _avaliar(apos, limite_ciclos)

    scc_afetada = next((c for c in antes["sccs"] if u in c and v in c), None)
    if scc_afetada is None:
        pedacos, pedacos_ciclicos, veredito = [], [], SEM_EFEITO
    else:
        membros = set(scc_afetada)
        pedacos = [c for c in depois["sccs"] if set(c) <= membros]
        pedacos_ciclicos = [c for c in depois["sccs_ciclicas"] if set(c) <= membros]
        veredito = PARCIAL if pedacos_ciclicos else ELIMINA_TODAS

    usavam = [c for c in antes["ciclos"] if (u, v) in zip(c, c[1:])]
    saiu = _modulos(antes["sccs_ciclicas"]) - _modulos(depois["sccs_ciclicas"])

    return {
        "arco": (u, v),
        "antes": antes,
        "depois": depois,
        "scc_afetada": scc_afetada,
        "pedacos": pedacos,
        "pedacos_ciclicos": pedacos_ciclicos,
        "ciclos_que_usavam_o_arco": usavam,
        "deixaram_de_estar_em_ciclo": sorted(saiu),
        "veredito": veredito,
    }


def _resumo_estado(estado: dict) -> str:
    mais = "+" if estado["ciclos_truncado"] else ""
    return (f"{len(estado['sccs'])} SCC(s), {len(estado['sccs_ciclicas'])} cíclica(s), "
            f"{len(estado['ciclos'])}{mais} ciclo(s)")


def formatar_remocao(r: dict) -> str:
    """Texto legível do resultado de simular_remocao (usado por analisar.py --remover)."""
    u, v = r["arco"]
    linhas = [
        f"=== Remoção de {u} ➔ {v} ===",
        f"Antes : {_resumo_estado(r['antes'])}",
        f"Depois: {_resumo_estado(r['depois'])}",
    ]

    if r["scc_afetada"] is None:
        linhas.append("O arco liga componentes diferentes: não participa de nenhum ciclo.")
        linhas.append("Resultado: a remoção não altera ciclos nem SCCs.")
        return "\n".join(linhas)

    linhas.append(f"SCC afetada ({len(r['scc_afetada'])} módulo(s)): {', '.join(r['scc_afetada'])}")
    linhas.append("Depois da remoção ela ficou assim:")
    ciclicos = {tuple(c) for c in r["pedacos_ciclicos"]}
    for pedaco in sorted(r["pedacos"]):
        marca = "cíclica" if tuple(pedaco) in ciclicos else "sem ciclo"
        linhas.append(f"  - {', '.join(pedaco)}  ({marca})")

    usavam = r["ciclos_que_usavam_o_arco"]
    linhas.append(f"Ciclos que usavam o arco ({len(usavam)}):")
    linhas.extend(f"  {' ➔ '.join(c)}" for c in usavam)
    restantes = r["depois"]["ciclos"]
    linhas.append(f"Ciclos restantes na versão sem o arco ({len(restantes)}):")
    linhas.extend(f"  {' ➔ '.join(c)}" for c in restantes)
    if r["deixaram_de_estar_em_ciclo"]:
        linhas.append(f"Deixaram de estar em ciclo: {', '.join(r['deixaram_de_estar_em_ciclo'])}")

    if r["veredito"] == ELIMINA_TODAS:
        linhas.append("Resultado: a remoção ELIMINOU todas as circularidades da componente.")
    elif r["veredito"] == PARCIAL:
        linhas.append("Resultado: a remoção NÃO eliminou todas as circularidades da componente.")
    return "\n".join(linhas)
