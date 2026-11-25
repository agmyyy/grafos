"""
Enumeração de TODOS os ciclos elementares (simples) de um digrafo.

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

# Importa a classe que representa um grafo direcionado.
from src.grafo import Digrafo

# Define os tipos de grafo aceitos pelas funções:
# - Digrafo: objeto da classe Digrafo.
# - dict[str, set[str]]: dicionário em que cada vértice aponta
#   para um conjunto de vértices vizinhos.
GraphType = Digrafo | dict[str, set[str]]


# Função auxiliar que encontra os vértices alcançáveis a partir de s,
# permitindo percorrer somente vértices maiores ou iguais a s
# em ordem alfabética.
#
# Isso ajuda a garantir que cada ciclo seja encontrado uma única vez,
# começando sempre pelo seu menor vértice.
def _alcance(d: Digrafo, s: str) -> set[str]:
    """Vértices >= s alcançáveis de s usando só vértices >= s (inclui s)."""

    # Inicializa o conjunto de vértices visitados com o próprio s.
    visto = {s}

    # Cria uma pilha contendo o vértice inicial.
    # A pilha será utilizada para realizar uma busca em profundidade (DFS).
    pilha = [s]

    # Continua enquanto existirem vértices na pilha.
    while pilha:
        # Remove o último vértice inserido na pilha.
        # Isso caracteriza o comportamento LIFO (último a entrar,
        # primeiro a sair), utilizado na DFS.
        u = pilha.pop()

        # Percorre os vizinhos do vértice atual.
        for v in d.adj[u]:
            # Só permite visitar vizinhos que sejam maiores ou iguais a s
            # alfabeticamente e que ainda não tenham sido visitados.
            if v >= s and v not in visto:
                # Marca o vizinho como visitado.
                visto.add(v)

                # Adiciona o vizinho à pilha para continuar a busca
                # a partir dele.
                pilha.append(v)

    # Retorna o conjunto de todos os vértices alcançáveis a partir de s,
    # respeitando a restrição de ordem alfabética.
    return visto


# Função principal responsável por enumerar os ciclos elementares
# existentes no grafo, respeitando o limite estabelecido.
def encontrar_ciclos(g: GraphType, limite: int = 50) -> list[list[str]]:
    """Até `limite` ciclos elementares de `g`, sem repetição.

    Devolve [] se o grafo é acíclico. Se houver mais ciclos que o limite,
    devolve os `limite` primeiros (ordem determinística).
    """

    # Verifica se o limite é menor ou igual a zero.
    # Nesse caso, não há necessidade de procurar ciclos.
    if limite <= 0:
        # Retorna uma lista vazia.
        return []

    # Verifica se g já é um objeto da classe Digrafo.
    # Se for, utiliza o próprio objeto.
    # Caso contrário, converte o dicionário recebido para Digrafo.
    d = g if isinstance(g, Digrafo) else Digrafo(g)

    # Cria o grafo transposto.
    # No grafo transposto, todos os arcos têm suas direções invertidas.
    # Isso permite descobrir quais vértices conseguem alcançar s
    # no grafo original.
    transposto = d.transposto()

    # Inicializa a lista que armazenará os ciclos encontrados.
    # Cada elemento dessa lista será uma lista de vértices.
    ciclos: list[list[str]] = []

    # Percorre todos os vértices do grafo.
    # Cada vértice será considerado como possível início de um ciclo.
    for s in d.vertices():
        # Calcula os vértices que são úteis para formar um ciclo
        # começando e terminando em s.
        #
        # _alcance(d, s):
        # Encontra os vértices alcançáveis a partir de s no grafo original.
        #
        # _alcance(transposto, s):
        # Encontra os vértices que conseguem alcançar s no grafo original.
        #
        # O operador & realiza a interseção entre os dois conjuntos.
        # Assim, uteis contém somente os vértices que satisfazem
        # as duas condições.
        uteis = _alcance(d, s) & _alcance(transposto, s)

        # Verifica se não existe nenhum outro vértice útil além de s
        # e se também não existe um arco de s para ele mesmo.
        #
        # Se essas condições forem verdadeiras, nenhum ciclo pode
        # começar e terminar em s utilizando apenas vértices >= s.
        if len(uteis) == 1 and not d.tem_arco(s, s):
            # Interrompe a análise deste vértice inicial
            # e passa para o próximo vértice do grafo.
            continue  # nenhum ciclo passa por s usando só vértices >= s

        # Inicializa o caminho atual com o vértice inicial s.
        # Essa lista representa o caminho que a DFS está percorrendo.
        caminho = [s]

        # Conjunto que guarda os vértices que estão atualmente
        # no caminho da DFS.
        # Ele impede que um vértice seja repetido dentro do mesmo ciclo.
        no_caminho = {s}

        # Inicializa a pilha da DFS com um iterador dos vizinhos de s.
        #
        # d.vizinhos(s) retorna os vizinhos de s.
        # O filtro "if w in uteis" mantém somente os vértices
        # que podem participar de um ciclo com início em s.
        #
        # iter() transforma a sequência em um iterador, permitindo
        # percorrer os vizinhos um por vez.
        pilha = [iter([w for w in d.vizinhos(s) if w in uteis])]

        # Enquanto houver iteradores na pilha, a DFS continua.
        while pilha:
            try:
                # Obtém o próximo vizinho do iterador que está
                # no topo da pilha.
                w = next(pilha[-1])

            # Quando não existem mais vizinhos para percorrer
            # no iterador atual, ocorre StopIteration.
            except StopIteration:
                # Remove o iterador esgotado da pilha.
                pilha.pop()

                # Remove o último vértice do caminho.
                # Esse vértice não faz mais parte do caminho atual da DFS.
                #
                # discard() também o remove do conjunto no_caminho,
                # caso esteja presente, sem gerar erro se não estiver.
                no_caminho.discard(caminho.pop())

                # Continua o while para retomar a busca
                # no nível anterior da DFS.
                continue

            # Verifica se o vizinho encontrado é o próprio vértice inicial.
            # Se for, encontramos um caminho que retorna a s,
            # formando um ciclo.
            if w == s:
                # Adiciona o ciclo encontrado à lista.
                # caminho contém os vértices percorridos e [s]
                # fecha o ciclo, repetindo o vértice inicial.
                ciclos.append(caminho + [s])

                # Verifica se a quantidade de ciclos encontrados
                # atingiu o limite estabelecido pelo usuário.
                if len(ciclos) >= limite:
                    # Retorna imediatamente os ciclos encontrados.
                    # Não continua procurando outros ciclos.
                    return ciclos

            # Se o vizinho não é o vértice inicial e ainda não está
            # no caminho atual, podemos avançar a DFS por ele.
            #
            # Essa condição evita repetir vértices dentro de um mesmo ciclo.
            elif w not in no_caminho:
                # Adiciona o vizinho ao caminho atual.
                caminho.append(w)

                # Marca o vizinho como pertencente ao caminho atual.
                no_caminho.add(w)

                # Adiciona à pilha um iterador com os vizinhos de w
                # que também pertencem ao conjunto de vértices úteis.
                #
                # Dessa maneira, a DFS continua explorando os caminhos
                # que podem eventualmente retornar ao vértice inicial s.
                pilha.append(iter([x for x in d.vizinhos(w) if x in uteis]))

    # Se a busca terminar sem atingir o limite,
    # retorna todos os ciclos encontrados.
    return ciclos
