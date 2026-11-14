"""Enumeração de TODOS os ciclos elementares (simples) de um digrafo.

Um ciclo elementar não repete vértices (exceto o primeiro, que fecha o ciclo).
Cada ciclo é devolvido uma única vez, começando pelo seu menor vértice
(ordem alfabética), ex.: ['a', 'b', 'c', 'a'].

ATENÇÃO: o número de ciclos elementares pode ser EXPONENCIAL em V (um grafo
completo com n vértices tem mais de (n-1)! ciclos). Por isso a função exige
um `limite`, e o custo NÃO é O(V + E): é proporcional ao número de ciclos
devolvidos vezes o custo de percorrer o grafo. Para só detectar um ciclo,
use `ciclos.encontrar_ciclo` (O(V + E)).

Método: para cada vértice inicial s, procura-se por DFS só os ciclos cujo
menor vértice é s, usando apenas vértices >= s que são alcançáveis a partir
de s e que alcançam s (poda). Isso garante que cada ciclo aparece uma vez.
A DFS é iterativa (sem limite de recursão).
"""

from src.grafo import Digrafo

GraphType = Digrafo | dict[str, set[str]]


def _alcance(d: Digrafo, s: str) -> set[str]:
    """Vértices >= s alcançáveis de s usando só vértices >= s (inclui s)."""
    visto = {s}
    pilha = [s]
    while pilha:
        u = pilha.pop()
        for v in d.vizinhos(u):
            if v >= s and v not in visto:
                visto.add(v)
                pilha.append(v)
    return visto


def encontrar_ciclos(g: GraphType, limite: int = 50) -> list[list[str]]:
    """Até `limite` ciclos elementares de `g`, sem repetição.

    Devolve [] se o grafo é acíclico. Se houver mais ciclos que o limite,
    devolve os `limite` primeiros (ordem determinística).
    """
    if limite <= 0:
        return []
    d = g if isinstance(g, Digrafo) else Digrafo(g)
    transposto = d.transposto()
    ciclos: list[list[str]] = []

    for s in d.vertices():
        uteis = _alcance(d, s) & _alcance(transposto, s)
        if len(uteis) == 1 and not d.tem_arco(s, s):
            continue  # nenhum ciclo passa por s usando só vértices >= s

        caminho = [s]
        no_caminho = {s}
        pilha = [iter([w for w in d.vizinhos(s) if w in uteis])]

        while pilha:
            try:
                w = next(pilha[-1])
            except StopIteration:
                pilha.pop()
                no_caminho.discard(caminho.pop())
                continue

            if w == s:
                ciclos.append(caminho + [s])
                if len(ciclos) >= limite:
                    return ciclos
            elif w not in no_caminho:
                caminho.append(w)
                no_caminho.add(w)
                pilha.append(iter([x for x in d.vizinhos(w) if x in uteis]))

    return ciclos
