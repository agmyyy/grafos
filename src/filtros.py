"""
Filtros opcionais sobre o grafo extraído.

São opções de VISÃO da análise: o modelo continua o mesmo (um vértice por módulo),
mas dá para deixar de fora pastas que não interessam (testes, documentação, scripts)
e módulos sem nenhuma ligação com os demais.

Nenhum filtro altera ciclos nem SCCs não triviais: um vértice sem arestas nunca
participa de ciclo. Só mudam as contagens de vértices e de SCCs triviais.
"""

# Importa Path para trabalhar com caminhos de arquivos e diretórios.
from pathlib import Path

# Importa Iterable, utilizado na tipagem dos parâmetros
# que podem receber diferentes tipos de coleções iteráveis.
from typing import Iterable

# Importa funções e constantes do módulo de extração:
#
# EXCLUIDOS_PADRAO: pastas e arquivos que são ignorados por padrão.
# caminho_para_modulo: converte o caminho de um arquivo em nome de módulo.
# construir_grafo: constrói o grafo de dependências do projeto.
# listar_arquivos: lista os arquivos Python encontrados no projeto.
from src.extracao import (
    EXCLUIDOS_PADRAO,
    caminho_para_modulo,
    construir_grafo,
    listar_arquivos,
)


# Função auxiliar que encontra todos os vértices que possuem
# pelo menos uma ligação, seja de entrada ou de saída.
def _com_arco(grafo: dict[str, set[str]]) -> set[str]:
    """Vértices que têm algum arco, de entrada ou de saída. O(V + E)."""

    # Percorre os pares do dicionário:
    # u representa o vértice de origem.
    # destinos representa o conjunto de vértices para os quais u aponta.
    #
    # Se destinos não estiver vazio, significa que u possui
    # pelo menos uma aresta de saída.
    #
    # Cria um conjunto contendo esses vértices.
    com_arco = {u for u, destinos in grafo.items() if destinos}

    # Percorre todos os conjuntos de destinos do grafo.
    # Aqui queremos identificar também os vértices que possuem
    # apenas arestas de entrada.
    for destinos in grafo.values():
        # O operador |= realiza a união dos conjuntos.
        # Adiciona ao conjunto com_arco todos os vértices
        # que aparecem como destinos de alguma aresta.
        com_arco |= destinos

    # Retorna os vértices que possuem pelo menos uma ligação,
    # independentemente de serem origem ou destino.
    return com_arco


# Função que remove todos os vértices isolados do grafo.
# Um vértice isolado não possui nenhuma aresta de entrada nem de saída.
def sem_isolados(grafo: dict[str, set[str]]) -> dict[str, set[str]]:
    """Remove TODOS os vértices sem arco (de entrada ou de saída). O(V + E).

    Atenção: isso inclui módulos reais que não importam nem são importados
    (um script, um conf.py). Para tirar só os __init__.py isolados, use
    `sem_pacotes_isolados`.
    """

    # Obtém o conjunto dos vértices que possuem pelo menos uma ligação.
    com_arco = _com_arco(grafo)

    # Cria e retorna um novo dicionário contendo somente
    # os vértices que estão no conjunto com_arco.
    #
    # u representa cada vértice do grafo.
    # destinos representa suas arestas de saída.
    #
    # O if u in com_arco funciona como filtro:
    # somente os vértices que possuem alguma ligação são mantidos.
    #
    # set(destinos) cria uma cópia do conjunto de destinos,
    # evitando reutilizar diretamente o conjunto original.
    return {u: set(destinos) for u, destinos in grafo.items() if u in com_arco}


# Função que remove somente os pacotes isolados,
# mantendo os módulos comuns mesmo quando não possuem ligações.
def sem_pacotes_isolados(
    grafo: dict[str, set[str]], pacotes: set[str]
) -> dict[str, set[str]]:
    """Remove só os vértices de PACOTE (`__init__.py`) que não têm nenhum arco.

    Módulos comuns são mantidos mesmo que isolados. `pacotes` é o conjunto de
    nomes de módulo que vêm de arquivos `__init__.py`. O(V + E).
    """

    # Obtém todos os vértices que possuem alguma aresta
    # de entrada ou de saída.
    com_arco = _com_arco(grafo)

    # Cria um novo dicionário filtrando os vértices.
    return {
        # Mantém o vértice e copia seu conjunto de destinos.
        u: set(destinos)
        # Percorre todos os vértices e seus respectivos destinos.
        for u, destinos in grafo.items()
        # Mantém o vértice se:
        # 1. Ele possui alguma ligação (está em com_arco); OU
        # 2. Ele não é um pacote (não veio de um __init__.py).
        #
        # Portanto, pacotes isolados são removidos,
        # mas módulos comuns isolados continuam no grafo.
        if u in com_arco or u not in pacotes
    }


# Função auxiliar que identifica os nomes dos módulos
# correspondentes aos arquivos __init__.py do projeto.
def _nomes_de_pacotes(raiz: Path, excluir: set[str]) -> set[str]:

    # Cria um conjunto com os nomes dos módulos que correspondem
    # a arquivos chamados __init__.py.
    nomes = {
        # Converte o caminho do arquivo para o nome do módulo Python.
        caminho_para_modulo(arq, raiz)
        # Percorre os arquivos encontrados dentro da pasta raiz,
        # respeitando as pastas que devem ser excluídas.
        for arq in listar_arquivos(raiz, excluir)
        # Considera somente arquivos chamados __init__.py.
        if arq.name == "__init__.py"
    }

    # Remove o valor None do conjunto, caso exista.
    # Isso é necessário porque caminho_para_modulo pode retornar None.
    nomes.discard(None)

    # Retorna os nomes dos módulos que representam pacotes.
    return nomes


# Função principal responsável por carregar o grafo do projeto
# e aplicar os filtros solicitados.
def carregar_grafo(
    raiz: Path | str,  # Caminho da pasta raiz do projeto.
    excluir: Iterable[str] = (),  # Pastas ou arquivos que devem ser ignorados.
    ocultar_isolados: bool = False,  # Indica se todos os módulos isolados serão removidos.
    ocultar_init_isolados: bool = True,  # Indica se pacotes __init__.py isolados serão removidos.
) -> dict[str, set[str]]:
    """Extrai o grafo de `raiz` aplicando os filtros pedidos.

    - excluir: nomes de pastas (ou arquivos) a ignorar, somados aos padrões
      (.venv, __pycache__, build, dist, .git...). Ex.: ["tests", "docs", "scripts"].
    - ocultar_isolados: remove todo módulo sem dependência de/para outros.
    - ocultar_init_isolados (padrão: True): remove os `__init__.py` sem nenhuma ligação,
      que são os vértices que "parecem pastas" (src, tests, o nome do app). Um
      `__init__.py` com dependências de verdade é mantido, porque ciclos passando
      pelo pacote são comuns em Python.
    """

    # Converte raiz em um objeto Path.
    # Isso permite trabalhar com o caminho independentemente
    # de ele ter sido recebido como string ou Path.
    raiz = Path(raiz)

    # Cria um conjunto com:
    # - Os padrões de exclusão definidos no projeto.
    # - Os nomes adicionais informados pelo usuário.
    #
    # O operador | realiza a união dos conjuntos.
    # Assim, os padrões padrão e os filtros personalizados
    # são aplicados juntos.
    ignorar = set(EXCLUIDOS_PADRAO) | set(excluir)

    # Constrói o grafo de dependências do projeto.
    # Utiliza a pasta raiz e o conjunto de itens que devem ser ignorados.
    grafo = construir_grafo(raiz, ignorar)

    # Verifica se o usuário deseja ocultar pacotes isolados.
    if ocultar_init_isolados:
        # Identifica os módulos correspondentes aos arquivos __init__.py
        # e remove aqueles que não possuem nenhuma ligação no grafo.
        grafo = sem_pacotes_isolados(grafo, _nomes_de_pacotes(raiz, ignorar))

    # Verifica se o usuário deseja ocultar TODOS os módulos isolados.
    if ocultar_isolados:
        # Remove todos os vértices que não possuem nenhuma ligação,
        # incluindo módulos comuns e pacotes.
        grafo = sem_isolados(grafo)

    # Retorna o grafo após a aplicação dos filtros.
    return grafo
