# merotec-autoflow

`merotec-autoflow` é uma biblioteca Python pequena para criar fluxos de automação
observáveis, testáveis e fáceis de compor.

A ideia inicial é simples: cada etapa recebe um dicionário de contexto, devolve
novos valores e o fluxo registra eventos de execução. Isso serve para scripts,
rotinas de ETL leves, automações internas, bots locais e protótipos que precisam
crescer sem virar um bloco único de código.

## Instalação

O pacote já está disponível no PyPI:

```bash
python -m pip install merotec-autoflow
```

Também é possível instalar direto do repositório:

```bash
python -m pip install git+https://github.com/Romero-Softwares/merotecflow.git
```

## Uso real

Na prática, a biblioteca ajuda a transformar uma automação escrita como um
script longo em uma sequência de etapas pequenas. Cada etapa recebe o mesmo
contexto, pode adicionar novos dados e deixa eventos registrados sobre início,
fim, falhas e tentativas.

Isso é útil quando você quer:

- dividir uma rotina em passos claros;
- reaproveitar etapas em fluxos diferentes;
- testar cada parte da automação sem rodar o processo inteiro;
- saber em qual etapa uma execução falhou;
- aplicar retry em etapas instáveis, como chamadas HTTP, leitura de arquivos ou
  integrações externas;
- evoluir um protótipo para algo mais organizado sem adicionar um orquestrador
  pesado.

## Exemplo

```python
from autoflow import Flow, step


@step(retries=2)
def normalize_user(ctx):
    return {"email": ctx["email"].lower()}


def make_slug(ctx):
    return {"slug": ctx["email"].split("@")[0]}


result = (
    Flow("signup")
    .add(normalize_user)
    .add(make_slug)
    .run({"email": "ADA@EXAMPLE.COM"})
)

print(result.context)
print([event.name for event in result.events])
```

Saída esperada:

```python
{"email": "ada@example.com", "slug": "ada"}
["flow_started", "step_started", "step_finished", "step_started", "step_finished", "flow_finished"]
```

## Benefícios em projetos

- **Organização:** cada função vira uma etapa independente do fluxo.
- **Observabilidade simples:** a execução gera eventos que podem ser usados em
  logs, auditoria ou diagnóstico.
- **Testabilidade:** etapas pequenas são mais fáceis de testar com `unittest`,
  `pytest` ou testes manuais.
- **Resiliência:** etapas podem ter `retries` e `delay`, evitando que falhas
  temporárias derrubem o processo na primeira tentativa.
- **Baixo acoplamento:** o fluxo usa um dicionário de contexto, sem exigir
  classes complexas ou infraestrutura externa.
- **Zero dependências em runtime:** bom para ferramentas internas, scripts
  portáveis e ambientes controlados.

## Tipos de projetos indicados

- automações internas de escritório, suporte, atendimento ou operação;
- pipelines leves de ETL, importação, limpeza e exportação de dados;
- bots locais e rotinas agendadas;
- validadores de arquivos, formulários, planilhas ou cadastros;
- integrações simples com APIs, webhooks e sistemas internos;
- protótipos de agentes, ferramentas de IA e fluxos de decisão;
- CLIs e scripts Python que precisam crescer com mais organização.

## Quando não usar

`merotec-autoflow` não tenta substituir ferramentas completas como Airflow,
Prefect, Celery, Dagster ou filas distribuídas. Para execução paralela,
agendamento distribuído, dashboards completos, workers remotos ou processamento
em larga escala, um orquestrador maior provavelmente será mais adequado.

## Recursos iniciais

- API pública enxuta: `Flow`, `step`, `FlowResult` e `FlowEvent`.
- Contexto compartilhado entre etapas.
- Merge automático de resultados em formato de dicionário.
- Retry por etapa com atraso opcional.
- Decorator flexível: `@step`, `@step("nome")` ou `@step(name="nome")`.
- Eventos para observabilidade simples, incluindo falha do fluxo.
- Resultado com helpers como `get`, `elapsed` e `events_named`.
- Validações claras para nomes, contexto inicial, retries e delay.
- Zero dependências externas em runtime.

## Desenvolvimento

```bash
python -m pip install -e .
python -m unittest
```

## Publicação no PyPI

O projeto está preparado para publicação no PyPI. Para validar o pacote
localmente antes de uma nova versão:

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine check dist/*
```

O repositório também pode publicar via GitHub Actions usando Trusted Publishing
do PyPI, sem salvar token no código. Para uma nova versão, atualize a versão em
`pyproject.toml`, gere uma tag e publique uma release/tag no GitHub.

Para testar em um índice separado antes do PyPI oficial, use TestPyPI:

```bash
python -m twine upload --repository testpypi dist/*
python -m pip install --index-url https://test.pypi.org/simple/ merotec-autoflow
```
