# Análise de dependências circulares em projetos Python

Trabalho 1 - ECO0046 Algoritmos em Grafos (UFC, 2026.2)
Equipe 2: Agmy Lima Nascimento, Luis Felipe Pessoa Lacerda, Emanoel Igor de Paulo Cosmo

## Estrutura

- `src/`: algoritmos e extração
- `tests/`: testes
- `dados/`: exemplos e projeto demonstrativo

## Como executar

Execute os comandos a partir da raiz do repositório.

### Executar os testes

```powershell
python -m pytest
```

Para executar somente os testes de ciclos:

```powershell
python -m pytest tests/test_ciclos.py
```

### Analisar o exemplo

```powershell
python analisar.py "dados/realistic_app"
```

Esse comando extrai e imprime o grafo de dependências do exemplo. A detecção de ciclos pode ser verificada pelos testes em `tests/test_ciclos.py`.
