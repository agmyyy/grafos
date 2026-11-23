"""Digrafo como lista de adjacência: dict[str, set[str]].

adj["a"] = {"b", "c"} significa arcos a -> b e a -> c
(o módulo "a" depende de "b" e de "c").
Todo vértice tem entrada no dicionário, mesmo sem dependências.
"""


class Digrafo:
    def __init__(self, adj: dict[str, set[str]] | None = None):
        self.adj: dict[str, set[str]] = {}
        for u, vizinhos in (adj or {}).items():
            self.adicionar_vertice(u)
            for v in vizinhos:
                self.adicionar_arco(u, v)

    # --- construção -------------------------------------------------
    def adicionar_vertice(self, v: str) -> None:
        """O(1) esperado."""
        self.adj.setdefault(v, set())

    def adicionar_arco(self, u: str, v: str) -> None:
        """Adiciona u -> v (cria os vértices se faltarem). O(1) esperado."""
        self.adicionar_vertice(u)
        self.adicionar_vertice(v)
        self.adj[u].add(v)

    def remover_arco(self, u: str, v: str) -> None:
        """Remove u -> v se existir. O(1) esperado."""
        if u in self.adj:
            self.adj[u].discard(v)

    # --- consultas --------------------------------------------------
    def vertices(self) -> list[str]:
        """Vértices em ordem alfabética (saída determinística)."""
        return sorted(self.adj)

    def vizinhos(self, u: str) -> list[str]:
        """Dependências diretas de u, em ordem alfabética. O(grau log grau)."""
        return self.vizinhos_saida(u)

    def vizinhos_saida(self, vertex: str) -> list[str]:
        """Retorna os destinos dos arcos que saem de um vértice."""
        return sorted(self.adj.get(vertex, set()))

    def vizinhos_entrada(self, target: str) -> list[str]:
        """Retorna, em ordem alfabética, os vértices que apontam para target."""
        return sorted(
            source
            for source, destinations in self.adj.items()
            if target in destinations
        )

    def alcancaveis(self, source: str) -> set[str]:
        """Retorna os vértices alcançáveis a partir de source por um ou mais arcos.

        A origem só aparece no resultado se existir um caminho de volta até ela.
        """
        if source not in self.adj:
            return set()

        reached: set[str] = set()
        pending = list(self.adj[source])

        while pending:
            vertex = pending.pop()
            if vertex in reached:
                continue

            reached.add(vertex)
            pending.extend(self.adj.get(vertex, set()))

        return reached

    def tem_arco(self, u: str, v: str) -> bool:
        """O(1) esperado."""
        return u in self.adj and v in self.adj[u]

    def arcos(self) -> list[tuple[str, str]]:
        return [(u, v) for u in self.vertices() for v in self.vizinhos(u)]

    def num_vertices(self) -> int:
        return len(self.adj)

    def num_arcos(self) -> int:
        return sum(len(vs) for vs in self.adj.values())

    # --- derivados --------------------------------------------------
    def transposto(self) -> "Digrafo":
        """Grafo com todos os arcos invertidos. O(V + E)."""
        t = Digrafo()
        for u in self.adj:
            t.adicionar_vertice(u)
        for u in self.adj:
            for v in self.adj[u]:
                t.adicionar_arco(v, u)
        return t

    def copia(self) -> "Digrafo":
        """Cópia independente (útil para simular remoções). O(V + E)."""
        return Digrafo({u: set(vs) for u, vs in self.adj.items()})

    def __repr__(self) -> str:
        return f"Digrafo(V={self.num_vertices()}, E={self.num_arcos()})"
