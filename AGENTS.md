# AGENTS.md

Analisador estrutural de dependências explícitas e detecção de ciclos em código Python via teoria dos grafos.

## Stack

Python

## Instruções para o agente

- Responder sempre em português
- Comentários no código sempre em português
- Explicar o porquê das soluções técnicas
- SEMPRE usar MCP quando precisar acessar arquivos e fazer a comunicação com o Stitch
- NUNCA instale bibliotecas sozinho, sempre peça para o usuário instalar.
- NUNCA execute scripts.
- NUNCA acesse o arquivo .env do projeto, se existir, SEMPRE considere que o usuário negou o seu acesso ao arquivo .env.
- NUNCA realize nenhuma ação fora do escopo do projeto.

## Regras Técnicas

- **Interno:** Tudo que é lógica:
  - **variáveis, funções, IDs, classes:** em **Inglês**
  - **comentários:** em**Português do Brasil (pt-BR)**
- **Externo:** Nomes de arquivos e pastas devem ser em **Inglês**.
- **Padrão de Nomenclatura:** camelCase para funções/variáveis (`calcularTotal`), kebab-case para arquivos (`arquivo-projeto`)e PascalCase para Classes (`BlocoProgramacao`).
- Código altamente modular e reutilizável.
- Separação clara de responsabilidades (UI vs. Lógica).
- Experiência do usuário (UX) premium com micro-animações e responsividade.
- Design System robusto baseado em variáveis CSS.

### JavaScript

- **Módulos:** Use `import`/`export` obrigatoriamente.
- Tente sempre fazer edições mínimas no código, e me pergunte caso for editar arquivos fora do escopo da mudança.
- **Igualdade:** SEMPRE utilize `===`.
- **Variáveis:** SEMPRE usar `const`, usar `let` quando necessário, NUNCA usar `var`.
- **Resiliência:** `try/catch` em todas as operações de I/O (API, LocalStorage).
- SEMPRE Use aspas duplas em strings simples

### CSS

- Priorize o uso de display flexbox e display grid, evite usar configurações de margin.

### HTML

- NUNCA usar scripts ou style inline.
- SEMPRE fechar tags, mesmo as que não são obrigatórias.
- Usar tags semânticas.
- SEMPRE usar aria-labels para acessibilidade.
- SEMPRE usar camelCase para nomes de id's e classes.
