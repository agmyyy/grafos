# Análise de dependências circulares em projetos Python

Trabalho 1 · ECO0046 Algoritmos em Grafos · UFC · 2026.2
Equipe 2: Agmy Lima Nascimento, Luis Felipe Pessoa Lacerda, Emanoel Igor de Paulo Cosmo

Analisador de dependências entre módulos Python: extrai os `import` internos de um
projeto, monta um digrafo, detecta ciclos (DFS), decompõe em componentes fortemente
conexas (Kosaraju–Sharir), constrói a condensação com ordenação topológica e simula a
remoção de dependências. Os algoritmos de grafos são implementados pela equipe.

---

## 1. Requisitos e instalação

Python 3.10 ou mais novo. A execução usa só a biblioteca padrão; o `pytest` é necessário
apenas para os testes.

---

## 2. Estrutura do projeto

```
grafos/
├── README.md                # este arquivo (atualizar a cada mudança)
├── analisar.py              # CLI: extrai o grafo, imprime dependências e ciclos (todos ou só um)
├── visualizar.py            # CLI: gera a página HTML de visualização
├── pytest.ini               # o pytest olha só tests/ (ignora dados/ e saida/)
├── src/
│   ├── __init__.py
│   ├── grafo.py             # classe Digrafo: lista de adjacência dict[str, set[str]]
│   ├── extracao.py          # extrai imports (ast) e monta o grafo de um projeto
│   ├── ciclos.py            # Atividade A: alcancaveis, tem_ciclo, encontrar_ciclo (DFS)
│   ├── scc.py               # Atividade B: kosaraju, sccs_ciclicas
│   ├── condensacao.py       # Atividade C: condensar, ordenacao_topologica
│   ├── enumeracao.py        # encontrar_ciclos(g, limite): lista vários ciclos (para visualização e exemplos)
│   ├── filtros.py           # filtros opcionais (--excluir, --sem-isolados); oculta __init__.py sem ligações
│   ├── remocao.py           # Atividade D: simular_remocao
│   └── visualizacao.py      # gera o HTML (só exibe; não calcula nada)
├── tests/
│   ├── test_grafo.py        # testes do Digrafo
│   ├── test_analisar.py     # testes da CLI analisar.py
│   ├── test_ciclos.py       # testes do DFS e da detecção de ciclos
│   ├── test_condensacao.py  # testes da condensação e da ordenação topológica
│   ├── test_determinismo.py # saída idêntica com hash seeds diferentes (uso de sorted)
│   ├── test_enumeracao.py   # testes da enumeração de ciclos
│   ├── test_exemplos.py     # garante a estrutura de cada exemplo de dados/
│   ├── test_extracao.py     # testes do extrator de imports
│   ├── test_filtros.py      # testes dos filtros
│   ├── test_remocao.py      # testes da simulação de remoção de dependências
│   ├── test_scc.py          # testes das componentes fortemente conexas
│   └── test_visualizacao.py # testes dos dados enviados à página
├── dados/                   # projetos de exemplo e projeto demonstrativo
│   ├── basic_app/           # (exemplos vindos do depcycle)
│   ├── layered_app/
│   ├── mixed_dependencies/
│   ├── cyclic_app/
│   ├── realistic_app/
│   ├── multiplos_ciclos/    # exemplo próprio: dois ciclos na mesma SCC (Atividade D)
│   ├── ciclo_simples/       # exemplo próprio: um único ciclo a → b → c → a
│   └── duas_sccs_ligadas/   # exemplo próprio: duas SCCs cíclicas ligadas em um sentido
└── saida/                   # páginas HTML geradas (ignorada pelo git)
```

---

## 3. Como rodar

Sempre a partir da raiz do repositório, com o ambiente virtual ativo.

### 3.1 Testes

```bash
python -m pytest              # todos os testes
python -m pytest -v           # detalhado (um teste por linha)
python -m pytest tests/test_extracao.py          # só um arquivo
python -m pytest tests/test_ciclos.py            # só os testes do DFS
python -m pytest tests/test_enumeracao.py        # só os testes da enumeração de ciclos
python -m pytest tests/test_scc.py              # só os testes de SCCs
python -m pytest tests/test_remocao.py          # só os testes da simulação de remoção
python -m pytest tests/test_determinismo.py      # reprodutibilidade da saída
python -m pytest tests/test_filtros.py           # filtros de pastas e módulos isolados
python -m pytest -k remover                      # só testes cujo nome contém "remover"
```

### 3.2 Analisar um projeto que está em `dados/`

A pasta passada deve ser a **raiz dos pacotes**. Nos exemplos, é a pasta que contém o
pacote (por exemplo `dados/cyclic_app/` contém `cyclic_app/`).

```bash
python analisar.py dados/cyclic_app                      # grafo + TODOS os ciclos
python analisar.py dados/realistic_app --limite-ciclos 200   # muda o limite (padrão: 50)
python analisar.py dados/cyclic_app --so-um-ciclo        # só a Atividade A: um ciclo
python analisar.py dados/cyclic_app --so-sccs            # só a Atividade B: SCCs (Kosaraju–Sharir)
python analisar.py dados/realistic_app --so-condensacao  # só a Atividade C: condensação + ordem topológica
python analisar.py dados/realistic_app --alcancaveis realistic_app.api.routes   # tudo que o módulo alcança
python analisar.py dados/multiplos_ciclos --remover multiplos_ciclos.hub multiplos_ciclos.a   # Atividade D
```

Saída em todos os modos: número de módulos e dependências e a lista
`módulo -> [dependências diretas]`. Depois:

- **Modo padrão:** todos os ciclos, até o limite (`src/enumeracao.py`), cada um com o
  número de módulos (se houver mais ciclos que o limite, ou se o grafo for acíclico, avisa);
  depois as componentes fortemente conexas (SCCs), indicando quais são cíclicas e separando
  os módulos que pertencem a ciclos dos que apenas alcançam uma componente cíclica; e, por
  fim, a condensação com a ordenação topológica.
- **`--so-um-ciclo`:** roda **apenas** `ciclos.encontrar_ciclo` para a busca de ciclos
  (DFS da Atividade A, O(V + E)) e imprime um ciclo no mesmo formato da lista do modo
  padrão. A DFS para no primeiro ciclo encontrado.
- **`--so-sccs`:** roda **apenas** o Kosaraju–Sharir (Atividade B).
- **`--so-condensacao`:** mostra **apenas** o grafo de condensação (cada componente com
  seus módulos e as componentes de que depende) e a ordenação topológica (Atividade C).
  No modo padrão, essa saída aparece depois das SCCs.
- **`--remover ORIGEM DESTINO`:** Atividade D. Simula a remoção da dependência
  `ORIGEM ➔ DESTINO` e compara antes e depois (ciclos, SCCs e SCCs cíclicas). Pode ser
  repetido; cada simulação parte do grafo original. O resultado é um destes:
  - **eliminou todas as circularidades da componente:** a SCC deixou de ser cíclica
    (ex.: `dados/cyclic_app`, remover `mod_a ➔ mod_b`);
  - **não eliminou todas:** a SCC se dividiu, mas algum pedaço continua cíclico
    (ex.: `dados/multiplos_ciclos`, remover `hub ➔ a`: sai `a`, mas `hub ↔ b` continua);
  - **não altera nada:** o arco liga componentes diferentes e não está em nenhum ciclo
    (ex.: `dados/multiplos_ciclos`, remover `web ➔ hub`).
- **`--alcancaveis MÓDULO`:** lista tudo que o módulo alcança seguindo dependências
  diretas e indiretas (A → B: A usa B). Não roda a análise de ciclos nem de SCCs.
- **`--so-um-ciclo`, `--alcancaveis` e `--remover`** não calculam as SCCs.

Cada ciclo é impresso com o primeiro módulo repetido no fim, para mostrar que ele "fecha":
`a ➔ b ➔ c ➔ a` tem **3 módulos** e **3 dependências** (a→b, b→c, c→a). Em um ciclo simples,
o número de módulos é sempre igual ao de dependências.

**Filtros opcionais** (valem para `analisar.py` e `visualizar.py`):

```bash
python analisar.py . --excluir dados --excluir tests            # o próprio projeto, sem exemplos nem testes
python visualizar.py meu_projeto/src --excluir tests --abrir    # projeto com layout src/: passe a pasta src
```

- **`--excluir PASTA`:** ignora pastas com esse nome (testes, docs, exemplos); pode ser repetido.
- **`--sem-isolados`:** remove todo módulo sem dependências de/para outros, inclusive módulos reais.
- **Layout `src/`:** passe `projeto/src` como raiz. Na raiz do repositório os módulos ganham o
  prefixo `src.` e imports como `from pacote import x` não são reconhecidos.
- Nenhum filtro altera ciclos nem SCCs não triviais; só mudam as contagens de vértices.

### 3.3 Visualizar no navegador

```bash
python visualizar.py dados/cyclic_app                 # gera saida/cyclic_app.html
python visualizar.py dados/realistic_app --abrir      # gera e abre no navegador
python visualizar.py dados/cyclic_app -o saida/demo.html    # gera saida/demo.html
python visualizar.py dados/realistic_app --limite-ciclos 100   # lista até 100 ciclos (padrão: 50)
```

### 3.4 Exemplos pequenos (um para cada caso do enunciado)

- **Digrafo acíclico:** `dados/basic_app`, `dados/layered_app`, `dados/mixed_dependencies`.
- **Ciclo simples:** `dados/ciclo_simples` (`a ➔ b ➔ c ➔ a`, três módulos).
- **Componente com vários ciclos:** `dados/multiplos_ciclos` (`hub ↔ a` e `hub ↔ b`: uma SCC
  de 3 módulos com 2 ciclos).
- **Duas componentes cíclicas ligadas em um único sentido:** `dados/duas_sccs_ligadas`
  (`{a1, a2}` e `{b1, b2, b3}`; o único arco entre elas é `a1 ➔ b1`).

```bash
python analisar.py dados/ciclo_simples
python analisar.py dados/duas_sccs_ligadas                  # veja a condensação: C(a) ➔ C(b)
python visualizar.py dados/duas_sccs_ligadas --abrir        # botão "Condensação"
python analisar.py dados/duas_sccs_ligadas --remover duas_sccs_ligadas.a1 duas_sccs_ligadas.b1   # arco entre SCCs: sem efeito
```

`tests/test_exemplos.py` confere a estrutura de cada exemplo.

---

## 4. A página de visualização

- **Grafo:** módulos como pontos e dependências como setas (A → B: A importa B).
  Arraste o fundo para mover, use a roda do mouse para zoom e arraste um módulo para
  reposicioná-lo. "Ajustar tela" enquadra tudo.
- **Buscar módulo:** destaca os módulos cujo nome contém o texto digitado.
- **Clique em um módulo:** mostra dependências diretas (azul), dependentes diretos
  (verde) e quantos módulos ele alcança. O botão **"Destacar alcançáveis"** pinta de roxo
  tudo que ele alcança e lista esses módulos. Com as SCCs disponíveis, diz se o módulo
  **pertence** a uma componente cíclica ou **apenas depende** de uma (a distinção pedida
  na Atividade B).
- **Cores:** cada componente cíclica tem uma cor; setas internas a ela ficam vermelhas.
  Módulos fora de ciclo ficam cinza.
- **Componentes fortemente conexas:** lista das SCCs e quantas são cíclicas; clique em uma
  para destacar seus membros. _(precisa de `kosaraju`)_
- **Ciclos encontrados:** lista de ciclos do projeto; clique em um para destacá-lo em
  laranja (clique de novo para limpar). "Destacar todos os ciclos" pinta de uma vez todos
  os arcos que participam de algum ciclo. Se o grafo é acíclico, a página avisa.
  _(precisa de `encontrar_ciclo` e/ou `encontrar_ciclos`)_
- **Condensação:** alterna para o grafo de componentes, organizado em colunas pela
  ordenação topológica (dependentes à esquerda, dependências à direita), com a ordem
  listada ao lado. _(precisa de `kosaraju`, `condensar` e `ordenacao_topologica`)_
  **Simular remoção de dependência:** clique numa seta dentro de um ciclo (ou escolha na lista);
  **Aplicar remoção:** redesenha o grafo sem ela (tracejada) e recolore as SCCs."

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
- **`__init__.py` sem ligações** (os vértices que parecem pastas: o nome do app, `src`, `tests`)
  **não aparece no grafo**; um `__init__.py` com dependências é mantido.
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
g.vizinhos_entrada("b")  # quem depende de "b" (dependentes diretos)
g.alcancaveis("a")     # tudo que "a" alcança por um ou mais arcos
g.transposto()        # grafo com arcos invertidos (Kosaraju)
g.copia()             # cópia independente (simulação de remoções)
```

Tipos trocados entre os módulos: SCCs são `list[list[str]]`, um ciclo é `list[str]`
(`['a', 'b', 'c', 'a']`), a condensação é um `Digrafo` cujos vértices são `'C0'`, `'C1'`, ...

Complexidades (V vértices, E arcos): espaço O(V + E); adicionar, remover e testar arco
O(1) esperado; listar vizinhos O(grau); DFS, Kosaraju, condensação e ordenação
topológica O(V + E), sem contar a ordenação usada para tornar a saída reproduzível
(ver 6.1, que mostra o custo extra de cada algoritmo).

### 6.1 Reprodutibilidade e o uso de `sorted`

**Problema.** Um `set` não tem ordem garantida, e o Python usa um hash aleatório para
strings, que muda a cada execução. Percorrer um conjunto pode dar ordens diferentes de
uma execução para outra. Isso não torna nada incorreto, mas muda **qual ciclo** a DFS
encontra primeiro, **a ordem e a numeração das SCCs** ("SCC 0, SCC 1...", "C0, C1...") e a
ordenação topológica. Os resultados do relatório não seriam reproduzíveis.

**Solução.** Percorrer sempre em ordem alfabética (`sorted`). O `sorted` só muda a
**ordem de visita**: qualquer ordem produz ciclos válidos e SCCs corretas, a ordem fixa
apenas torna a saída a mesma em toda execução.

**Onde é usado:**

- `src/grafo.py`: `vertices()`, `vizinhos()`, `vizinhos_saida()`, `vizinhos_entrada()` e
  `arcos()` devolvem listas ordenadas. É por aqui que a DFS, a enumeração e a
  visualização percorrem o grafo.
- `src/ciclos.py`: `encontrar_ciclo` usa `vertices()` e `vizinhos_saida()`.
- `src/enumeracao.py`: `encontrar_ciclos` usa `vertices()` e `vizinhos()`.
- `src/scc.py`: ordena os vértices ao normalizar o grafo, os vizinhos na **primeira** DFS
  do Kosaraju e os membros de cada SCC ao devolvê-la. A segunda DFS não ordena: a SCC é
  um conjunto, então a ordem de visita dentro dela não altera o resultado.
- `src/extracao.py`: `sorted(raiz.rglob("*.py"))`, para a ordem dos arquivos não
  depender do sistema de arquivos.
- `analisar.py` e `src/visualizacao.py`: ordenam listas apenas para exibição.

**Efeito na complexidade.** Seja d o grau de saída de um vértice e Δ o maior grau do grafo.

- Ordenar os vizinhos de um vértice custa O(d log d). Cada vértice tem os vizinhos
  ordenados uma vez por DFS, então o total é Σ d log d ≤ E log Δ.
- Ordenar os vértices uma vez custa O(V log V).
- **DFS (`encontrar_ciclo`) e Kosaraju–Sharir:** de O(V + E) passam a
  O(V + E + V log V + E log Δ), que é no máximo O((V + E) log V). Para ordenar também as
  SCCs devolvidas no Kosaraju, soma-se Σ |SCC| log |SCC| ≤ V log V, já incluído acima.
- **`vizinhos_entrada`:** O(V + k log k) por chamada (varre todos os vértices, k é o grau
  de entrada). Evite chamá-la em laço; para todos os vértices use o grafo transposto.
- **`encontrar_ciclos` (enumeração):** ordena os vizinhos cada vez que um vértice entra
  no caminho, multiplicando cada passo por log Δ. Como o algoritmo já é exponencial no
  número de ciclos (por isso existe o limite), isso é desprezível.
- **Exibição:** ordenar uma lista de n itens para imprimir custa O(n log n).
- Para manter O(V + E) **estrito**, não ordene: a saída passa a variar entre execuções.
  Nos projetos de 10 a 50 módulos o fator logarítmico é irrelevante.

**Teste.** `tests/test_determinismo.py` roda o Kosaraju e a enumeração com cinco valores
de `PYTHONHASHSEED` e confere que a saída é sempre a mesma.

---

## 7. Onde cada algoritmo vai

- **`src/ciclos.py` (Atividade A, pronta):** `alcancaveis(g, origem)`, `tem_ciclo(g)` e
  `encontrar_ciclo(g)`. O DFS é iterativo (sem limite de recursão) e aceita `Digrafo` ou
  `dict[str, set[str]]`. O ciclo devolvido fecha no mesmo vértice, por exemplo
  `['a', 'b', 'a']`. `imprimir_resultado_dfs` (mantida no arquivo) imprime um resumo do DFS, mas o
  `analisar.py` usa agora o próprio formato, igual nos dois modos.
- **`src/enumeracao.py` (apoio à visualização e aos exemplos):** `encontrar_ciclos(g, limite=50)`
  devolve até `limite` ciclos elementares, cada um uma vez, começando pelo menor vértice.
  O número de ciclos pode ser **exponencial**, então o limite é obrigatório e o custo não
  é O(V + E) (é proporcional ao número de ciclos devolvidos). Para apenas detectar, use
  `encontrar_ciclo`, que é O(V + E).
- **`src/scc.py` (Atividade B):** `kosaraju(g)` devolve a lista de SCCs; `sccs_ciclicas`
  filtra as que têm ciclo (mais de um vértice, ou um vértice com laço).
- **`src/condensacao.py` (Atividade C, pronta):** `condensar(g, sccs)` devolve o grafo de
  condensação e o mapa vértice → índice da SCC; `ordenacao_topologica(g_cond)` ordena o DAG
  (algoritmo de Kahn, por graus de entrada). Ambas O(V + E), mais a ordenação para
  desempate determinístico (ver 6.1). Detalhes na seção 7.1.
- **`src/remocao.py` (Atividade D):** `simular_remocao(g, u, v)` remove o arco numa
  **cópia** e compara ciclos e SCCs antes e depois. Custo: cópia e remoção O(V + E); reavaliar
  (DFS e Kosaraju) O(V + E) por simulação; a lista de ciclos é limitada por `limite_ciclos`.

### 7.1 Condensação: construção, justificativa e interpretação (Atividade C)

**Construção.** Cada SCC `i` (na ordem devolvida por `kosaraju`) vira o super-vértice `Ci`.
Existe o arco `Cx → Cy` (x ≠ y) quando há pelo menos um arco original `u → v` com `u` em
`Cx` e `v` em `Cy`. Arcos internos a uma componente (incluindo laços) desaparecem, e vários
arcos entre as mesmas duas componentes viram um só.

**Por que a condensação é um DAG.** Se houvesse um ciclo `Cx → … → Cy → … → Cx` com x ≠ y,
todo vértice de `Cx` alcançaria todo vértice de `Cy` e vice-versa, porque cada SCC é
fortemente conexa internamente. Então `Cx ∪ Cy` seria fortemente conexo, o que contradiz a
maximalidade das SCCs. Logo a condensação não tem ciclos, e todo DAG admite ordenação
topológica.

**Ordenação topológica.** Usa o algoritmo de Kahn: começa pelas componentes com grau de
entrada 0 e remove seus arcos repetidamente. Se sobrar alguma componente, há ciclo e a
função levanta `ValueError`, o que nunca acontece em uma condensação.

**Sentido dos arcos.** `A → B` significa "A depende de B". Para todo arco `X → Y`, a ordem
põe `X` antes de `Y`:

- **Primeiras componentes:** nível mais alto, ninguém depende delas (por exemplo `main`
  ou a API).
- **Últimas componentes:** a base, não dependem de nenhuma componente interna (por exemplo
  modelos e utilitários).
- **Ordem de compilação ou carregamento:** como cada componente precisa vir depois das suas
  dependências, basta ler a lista **ao contrário**.

Uma componente cíclica aparece como um único bloco nessa hierarquia: seus módulos não podem
ser ordenados entre si e só podem ser tratados juntos.

---

## Histórico e estado

Atualize esta seção a cada mudança que altere como rodar o projeto.

**Estado dos algoritmos**

- [x] `Digrafo` (`src/grafo.py`)
- [x] Extração de imports (`src/extracao.py`)
- [x] Visualização (`src/visualizacao.py`, `visualizar.py`)
- [x] Atividade A: `alcancaveis`, `tem_ciclo`, `encontrar_ciclo` (`src/ciclos.py`)
- [x] Enumeração de ciclos (`src/enumeracao.py`)
- [x] Atividade B: `kosaraju`, `sccs_ciclicas` e análise da relação com ciclos (`src/scc.py`)
- [x] Atividade C: `condensar`, `ordenacao_topologica` (`src/condensacao.py`)
- [x] Atividade D: `simular_remocao` (`src/remocao.py`)
- [x] Exemplos pequenos (acíclico, ciclo simples, vários ciclos, duas SCCs ligadas)
- [ ] Projeto demonstrativo de 10 a 50 módulos
- [ ] Relatório e apresentação

---

## Créditos

Extração de imports baseada na ideia do DepCycle (MIT, Copyright (c) 2025 Kishan Thanki).
