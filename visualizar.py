"""Gera a página HTML de visualização de um projeto.

Uso:
    python visualizar.py dados/cyclic_app
    python visualizar.py dados/cyclic_app --abrir

Usa os algoritmos ciclos.py, scc.py, condensacao.py.
"""

import argparse
import webbrowser
from pathlib import Path
from src import ciclos, condensacao, enumeracao, scc
from src.filtros import carregar_grafo
from src.grafo import Digrafo
from src.visualizacao import gerar_html, montar_dados


# Função auxiliar que recebe uma funcao e seus paramentros, executa essa função com seus parâmetros e retorna o valor; trata o caso em que
# ele ainda não foi implementado.
def _tentar(nome: str, funcao, *args):
    """Executa um algoritmo; se ainda for stub, avisa e devolve None."""
    try:
        return funcao(*args)
    except NotImplementedError:
        print(f"[aviso] {nome} ainda não implementado: omitido da página")
        return None


# Função principal: organiza e executa todas as etapas do programa.
def main() -> None:

    # Cria o interpretador de argumentos da linha de comando.
    ap = argparse.ArgumentParser(
        description="Visualiza dependências de um projeto Python"
    )

    ap.add_argument("projeto", help="pasta do projeto (raiz dos pacotes)")

    ap.add_argument(
        "-o", "--saida", help="arquivo HTML de saída (padrão: saida/<pasta>.html)"
    )
    ap.add_argument(
        "--excluir",
        action="append",
        default=[],
        metavar="PASTA",
        help="ignora pastas com esse nome, ex.: --excluir tests --excluir docs (pode repetir)",
    )
    ap.add_argument(
        "--sem-isolados",
        action="store_true",
        help="remove TODO módulo sem nenhuma dependência de/para outros (inclusive módulos reais)",
    )
    ap.add_argument("--abrir", action="store_true", help="abre a página no navegador")

    ap.add_argument(
        "--limite-ciclos",
        type=int,
        default=50,
        help="máximo de ciclos listados na página (padrão: 50)",
    )

    # Lê e interpreta os argumentos fornecidos pelo usuário no terminal.
    # Os valores ficam armazenados no objeto args.
    args = ap.parse_args()

    # Converte o caminho informado pelo usuário em um objeto Path,
    # que facilita operações com arquivos e diretórios.
    raiz = Path(args.projeto)
    if not raiz.is_dir():
        ap.error(f"pasta não encontrada: {raiz}")

    # Carrega as dependências encontradas no projeto.
    # args.excluir contém as pastas que devem ser ignoradas.
    # args.sem_isolados indica se os módulos isolados serão removidos.
    #
    # O resultado é utilizado para criar um objeto Digrafo,
    # que representa as dependências entre os módulos.
    g = Digrafo(carregar_grafo(raiz, args.excluir, args.sem_isolados))
    print(f"{raiz.name}: {g.num_vertices()} módulos, {g.num_arcos()} dependências")

    # Executa o algoritmo que procura um ciclo no grafo.
    ciclo = _tentar("encontrar_ciclo", ciclos.encontrar_ciclo, g)

    # Executa o algoritmo de enumeração de ciclos.
    # O limite é aumentado em 1 para permitir identificar
    # se existem mais ciclos do que o limite solicitado.
    lista = _tentar(
        "encontrar_ciclos", enumeracao.encontrar_ciclos, g, args.limite_ciclos + 1
    )

    # Verifica se a quantidade de ciclos encontrados ultrapassou
    # o limite que o usuário deseja exibir.
    # Se ultrapassou, truncado recebe True.
    # Se lista for None, truncado recebe False.
    truncado = lista is not None and len(lista) > args.limite_ciclos

    # Só executa esse bloco se a enumeração de ciclos tiver retornado
    # uma lista válida.
    if lista is not None:
        # Mantém somente a quantidade máxima de ciclos permitida.
        # Por exemplo, se o limite for 50, mantém os 50 primeiros.
        lista = lista[: args.limite_ciclos]

        print(
            f"ciclos listados: {len(lista)}"
            + (" (há mais; use --limite-ciclos)" if truncado else "")
        )

    # Executa o algoritmo de Kosaraju para encontrar as
    # componentes fortemente conexas (SCCs) do grafo.
    sccs = _tentar("kosaraju", scc.kosaraju, g)

    # Inicializa as variáveis com None.
    # Isso indica que, inicialmente, ainda não existem resultados
    # da condensação nem da ordenação topológica.
    g_cond = mapa = ordem = None

    # Só tenta realizar a condensação se o algoritmo de Kosaraju
    # tiver retornado alguma componente fortemente conexa.
    if sccs is not None:
        # Executa a condensação do grafo.
        # O algoritmo agrupa cada componente fortemente conexa
        # em um único vértice, criando um novo grafo.
        # O resultado contém:
        # - g_cond: o grafo condensado;
        # - mapa: a relação entre os vértices originais e suas componentes.
        resultado = _tentar("condensar", condensacao.condensar, g, sccs)

        # Verifica se a condensação foi executada com sucesso.
        if resultado is not None:
            # Desempacota a tupla retornada pela função condensar.
            g_cond, mapa = resultado

            # Executa a ordenação topológica no grafo condensado.
            # Como a condensação de um grafo sempre produz um DAG(Directed Acyclic Graph, ou Grafo Acíclico Dirigido),
            # é possível realizar essa ordenação.
            ordem = _tentar(
                "ordenacao_topologica", condensacao.ordenacao_topologica, g_cond
            )

    # Reúne os resultados de todos os algoritmos em uma estrutura
    # de dados que será utilizada para construir a página HTML.
    #
    # São enviados o grafo original, o nome do projeto,
    # as SCCs, os ciclos, o grafo condensado, o mapa,
    # a ordenação topológica e as informações sobre o limite de ciclos.
    dados = montar_dados(
        g, raiz.name, sccs, ciclo, g_cond, mapa, ordem, lista, truncado
    )

    # Define o caminho onde o arquivo HTML será salvo.
    # Se o usuário informou --saida, utiliza o caminho informado.
    # Caso contrário, cria o caminho padrão:
    # saida/nome_do_projeto.html.
    destino = Path(args.saida) if args.saida else Path("saida") / f"{raiz.name}.html"

    # Cria a pasta de destino, caso ela ainda não exista.
    # parents=True também cria as pastas intermediárias necessárias.
    # exist_ok=True evita erro caso a pasta já exista.
    destino.parent.mkdir(parents=True, exist_ok=True)

    # Gera o conteúdo HTML a partir dos dados preparados anteriormente.
    # Em seguida, grava esse conteúdo no arquivo de destino.
    # encoding="utf-8" permite salvar corretamente caracteres especiais.
    destino.write_text(gerar_html(dados), encoding="utf-8")

    # Informa ao usuário onde a página HTML foi gerada.
    print(f"página gerada: {destino}")

    # Verifica se o usuário solicitou a abertura automática da página.
    if args.abrir:
        # Converte o caminho do arquivo em uma URI válida
        # e abre a página no navegador padrão do sistema.
        webbrowser.open(destino.resolve().as_uri())


# Verifica se este arquivo está sendo executado diretamente.
# Quando isso acontece, __name__ recebe o valor "__main__".
# Se o arquivo for importado por outro módulo, esse bloco não será executado.
if __name__ == "__main__":
    # Inicia a execução do programa chamando a função principal.
    main()
