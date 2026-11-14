# Análise de dependências circulares em projetos Python

Trabalho 1 · ECO0046 Algoritmos em Grafos · UFC · 2026.2
Equipe 2: Agmy Lima Nascimento, Luis Felipe Pessoa Lacerda, Emanoel Igor de Paulo Cosmo

Analisador de dependências entre módulos Python: extrai os `import` internos de um
projeto, monta um digrafo, detecta ciclos (DFS), decompõe em componentes fortemente
conexas (Kosaraju–Sharir), constrói a condensação com ordenação topológica e simula a
remoção de dependências. Os algoritmos de grafos são implementados pela equipe.

> **Estado atual:** base pronta (grafo, extração, visualização). Algoritmos das atividades
> A, B, C e D ainda são esqueletos. Veja a seção [Histórico e estado](#histórico-e-estado).

---

## 1. Requisitos e instalação

Python 3.10 ou mais novo. No CachyOS/Arch:

```bash
sudo pacman -S python python-pytest          # se ainda não tiver
cd ~/Projetos/grafos
python -m venv .venv
source .venv/bin/activate                    # fish: source .venv/bin/activate.fish
pip install pytest
```

Não há dependências de execução além da biblioteca padrão do Python.

---

## 2. Estrutura do projeto

```
grafos/
├── README.md                # este arquivo (atualizar a cada mudança)
├── analisar.py              # CLI: extrai o grafo de um projeto e imprime as dependências
├── visualizar.py            # CLI: gera a página HTML de visualização
├── src/
│   ├── __init__.py
│   ├── grafo.py             # classe Digrafo: lista de adjacência dict[str, set[str]]
│   ├── extracao.py          # extrai imports (ast) e monta o grafo de um projeto
│   ├── ciclos.py            # Atividade A: alcancaveis, tem_ciclo, encontrar_ciclo (DFS)
│   ├── scc.py               # Atividade B: kosaraju, sccs_ciclicas
│   ├── condensacao.py       # Atividade C: condensar, ordenacao_topologica
│   ├── remocao.py           # Atividade D: simular_remocao
│   └── visualizacao.py      # gera o HTML (só exibe; não calcula nada)
├── tests/
│   ├── test_grafo.py        # testes do Digrafo
│   ├── test_extracao.py     # testes do extrator de imports
│   └── test_visualizacao.py # testes dos dados enviados à página
├── dados/                   # projetos de exemplo e projeto demonstrativo
│   ├── basic_app/           # (exemplos vindos do depcycle)
│   ├── layered_app/
│   ├── mixed_dependencies/
│   ├── cyclic_app/
│   └── realistic_app/
└── saida/                   # páginas HTML geradas (ignorada pelo git)
```

Responsáveis (proposta de divisão):

- **Luis:** `grafo.py`, `extracao.py`, `scc.py`.
- **Agmy:** `ciclos.py`, `condensacao.py`.
- **Emanoel:** `remocao.py`, exemplos pequenos e projeto demo em `dados/`, testes e README.
- **Relatório:** cada um escreve a seção dos seus algoritmos (correção e complexidade).

---

## 3. Como rodar

Sempre a partir da raiz do repositório, com o ambiente virtual ativo.

### 3.1 Testes

```bash
python -m pytest              # todos os testes
python -m pytest -v           # detalhado (um teste por linha)
python -m pytest tests/test_extracao.py          # só um arquivo
python -m pytest -k remover                      # só testes cujo nome contém "remover"
```

### 3.2 Analisar um projeto que está em `dados/`

A pasta passada deve ser a **raiz dos pacotes**. Nos exemplos, é a pasta que contém o
pacote (por exemplo `dados/cyclic_app/` contém `cyclic_app/`).

```bash
python analisar.py dados/cyclic_app
python analisar.py dados/realistic_app
```

Saída: número de módulos e dependências, e a lista `módulo -> [dependências diretas]`.
Usando no código:

```python
from pathlib import Path
from src.extracao import construir_grafo
from src.grafo import Digrafo

g = Digrafo(construir_grafo(Path("dados/cyclic_app")))
print(g.vizinhos("cyclic_app.direct.mod_a"))
```

Projeto com layout `src/` (ex.: `meu_projeto/src/pacote/...`): passe `meu_projeto/src`.

### 3.3 Visualizar no navegador

```bash
python visualizar.py dados/cyclic_app                 # gera saida/cyclic_app.html
python visualizar.py dados/realistic_app --abrir      # gera e abre no navegador
python visualizar.py dados/cyclic_app -o saida/demo.html
```

Se preferir, abra o arquivo manualmente: `xdg-open saida/cyclic_app.html`.
A página funciona offline (um único arquivo, sem bibliotecas externas).

O script usa os algoritmos da equipe **à medida que forem implementados**. O que ainda
levanta `NotImplementedError` é omitido, com um aviso no terminal e na página.

---

## 4. A página de visualização

- **Grafo:** módulos como pontos e dependências como setas (A → B: A importa B).
  Arraste o fundo para mover, use a roda do mouse para zoom e arraste um módulo para
  reposicioná-lo. "Ajustar tela" enquadra tudo.
- **Buscar módulo:** destaca os módulos cujo nome contém o texto digitado.
- **Clique em um módulo:** mostra dependências diretas (azul), dependentes diretos
  (verde) e quantos módulos ele alcança. Com as SCCs disponíveis, diz se o módulo
  **pertence** a uma componente cíclica ou **apenas depende** de uma (a distinção pedida
  na Atividade B).
- **Cores:** cada componente cíclica tem uma cor; setas internas a ela ficam vermelhas.
  Módulos fora de ciclo ficam cinza.
- **Componentes fortemente conexas:** lista das SCCs; clique em uma para destacar seus
  membros. *(precisa de `kosaraju`)*
- **Mostrar ciclo concreto:** destaca em laranja o ciclo devolvido por
  `encontrar_ciclo`. *(precisa de `encontrar_ciclo`)*
- **Condensação:** alterna para o grafo de componentes, organizado em colunas pela
  ordenação topológica (dependentes à esquerda, dependências à direita), com a ordem
  listada ao lado. *(precisa de `kosaraju`, `condensar` e `ordenacao_topologica`)*

Para usar na apresentação e no relatório, gere uma página por exemplo
(acíclico, ciclo simples, vários ciclos, duas SCCs ligadas, projeto demo) e tire capturas.

---

## 5. Modelo de extração (o que é reconhecido e o que é ignorado)

Implementado em `src/extracao.py`. Documentar no relatório.

- **Vértice:** módulo (arquivo `.py`). `__init__.py` representa o pacote.
- **Arco A → B:** o módulo A importa B, e B é um módulo interno do projeto.
- **Reconhecido:** `import a.b`, `from a import b`, `from a.b import c`, imports
  relativos (resolvidos para o nome absoluto), imports dentro de funções e dentro de
  `if TYPE_CHECKING`.
- **`from pkg import x`:** se `pkg.x` é módulo interno, o arco vai para `pkg.x`; senão
  (`x` é função/classe do `__init__`), vai para `pkg`.
- **Ignorado:** bibliotecas externas (stdlib e terceiros), `from __future__`,
  autoimportação (laços só existem em grafos construídos à mão), pastas como `.venv`,
  `__pycache__`, `build`, `dist`, `.git`.
- **Não modelado:** `import a.b.c` não gera arcos para `a` e `a.b` (importações
  implícitas dos pacotes).
- Arquivos com erro de sintaxe são pulados com aviso.

---

## 6. Representação do grafo e contrato entre as partes

Lista de adjacência com `dict[str, set[str]]`, encapsulada em `Digrafo` (`src/grafo.py`):

```python
g = Digrafo({"a": {"b"}, "b": {"c"}, "c": {"a"}})
g.vertices()          # ['a', 'b', 'c']   (ordem alfabética, determinística)
g.vizinhos("a")       # ['b']             dependências diretas
g.tem_arco("a", "b")  # True
g.adicionar_arco("c", "d");  g.remover_arco("c", "d")
g.transposto()        # grafo com arcos invertidos (Kosaraju)
g.copia()             # cópia independente (simulação de remoções)
```

Tipos trocados entre os módulos: SCCs são `list[list[str]]`, um ciclo é `list[str]`
(`['a', 'b', 'c', 'a']`), a condensação é um `Digrafo` cujos vértices são `'C0'`, `'C1'`, ...

Complexidades (V vértices, E arcos): espaço O(V + E); adicionar, remover e testar arco
O(1) esperado; listar vizinhos O(grau); DFS, Kosaraju, condensação e ordenação
topológica O(V + E). Ordenar os vizinhos (`sorted`) para tornar a saída reproduzível
acrescenta O(E log E) no pior caso, sem afetar a correção.

---

## 7. Onde cada algoritmo vai

- **`src/ciclos.py` (Atividade A):** `alcancaveis(g, origem)`, `tem_ciclo(g)` e
  `encontrar_ciclo(g)`, todos por DFS.
- **`src/scc.py` (Atividade B):** `kosaraju(g)` devolve a lista de SCCs; `sccs_ciclicas`
  filtra as que têm ciclo (mais de um vértice, ou um vértice com laço).
- **`src/condensacao.py` (Atividade C):** `condensar(g, sccs)` devolve o grafo de
  condensação e o mapa vértice → índice da SCC; `ordenacao_topologica(g_cond)` ordena o DAG.
- **`src/remocao.py` (Atividade D):** `simular_remocao(g, u, v)` remove o arco numa
  **cópia** e compara ciclos e SCCs antes e depois.

Cada função tem assinatura e docstring prontas, lançando `NotImplementedError` até ser
implementada. Ao implementar, **não altere as assinaturas** sem avisar o grupo, e
escreva testes em `tests/` com grafos feitos à mão, por exemplo
`Digrafo({"a": {"b"}, "b": {"a"}})`.

---

## 8. DepCycle como ferramenta auxiliar

O [DepCycle](https://pypi.org/project/depcycle/) (MIT) é um analisador de dependências de
projetos Python. A extração de imports deste trabalho se inspira nele. Ele também serve
como ferramenta externa para **conferir** os resultados e gerar visualizações extras
(os algoritmos centrais continuam sendo da equipe):

```bash
pip install depcycle                                   # fora do requisito do projeto
depcycle analyze dados/cyclic_app -o saida/depcycle_cyclic.html     # página interativa
depcycle analyze dados/cyclic_app --format json -o saida/cyclic.json
depcycle analyze dados/cyclic_app --format dot  -o saida/cyclic.dot # Graphviz: dot -Tpng
depcycle inspect dados/cyclic_app --cycles             # lista os ciclos no terminal
depcycle inspect dados/cyclic_app cyclic_app.direct.mod_a   # dependências de um módulo
depcycle analyze dados/cyclic_app --fail-on-cycles     # sai com erro se houver ciclo
depcycle analyze dados/cyclic_app --no-stdlib --no-third-party --no-unknown
```

Uso sugerido: comparar os ciclos do `depcycle inspect --cycles` com os do nosso DFS e as
SCCs do nosso Kosaraju. Diferenças indicam bug ou diferença de modelo (o DepCycle, por
exemplo, não cria arcos para submódulos em `from pkg import mod`), e vale uma nota no
relatório. Os arquivos `.dot` podem ser convertidos em imagem se o Graphviz estiver
instalado (`sudo pacman -S graphviz`).

---

## 9. Fluxo de trabalho com git

```bash
git checkout -b feature/nome-do-bloco     # uma branch por bloco
git add <arquivos> && git commit -m "mensagem"
git push -u origin feature/nome-do-bloco  # depois, abrir Pull Request
git pull origin main                      # antes de começar a trabalhar
```

Ninguém commita direto na `main`; outro integrante revisa cada Pull Request.

---

## Histórico e estado

Atualize esta seção a cada mudança que altere como rodar o projeto.

**Estado dos algoritmos**

- [x] `Digrafo` (`src/grafo.py`)
- [x] Extração de imports (`src/extracao.py`)
- [x] Visualização (`src/visualizacao.py`, `visualizar.py`)
- [ ] Atividade A: `alcancaveis`, `tem_ciclo`, `encontrar_ciclo` (`src/ciclos.py`)
- [ ] Atividade B: `kosaraju`, `sccs_ciclicas` (`src/scc.py`)
- [ ] Atividade C: `condensar`, `ordenacao_topologica` (`src/condensacao.py`)
- [ ] Atividade D: `simular_remocao` (`src/remocao.py`)
- [ ] Exemplos pequenos (acíclico, ciclo simples, vários ciclos, duas SCCs ligadas)
- [ ] Projeto demonstrativo de 10 a 50 módulos
- [ ] Relatório e apresentação

**Mudanças**

- **Base do projeto.** `Digrafo`, extrator e esqueletos dos algoritmos.
  Rodar: `python -m pytest` e `python analisar.py dados/cyclic_app`.
- **Visualização.** Página HTML interativa com busca, destaque de dependências, SCCs,
  ciclo concreto e condensação.
  Rodar: `python visualizar.py dados/cyclic_app --abrir`. Os recursos que dependem de
  algoritmos ainda não implementados aparecem desativados.

---

## Créditos

A ideia de extrair dependências com `ast` e parte da lógica de resolução de imports
relativos se baseiam no projeto **DepCycle** (MIT, Copyright (c) 2025 Kishan Thanki).
Os algoritmos de grafos (DFS, Kosaraju–Sharir, condensação, ordenação topológica,
simulação de remoções) são de autoria da equipe.
