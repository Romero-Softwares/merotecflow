# merotec-autoflow

`merotec-autoflow` e uma biblioteca Python pequena para criar fluxos de automacao
observaveis, testaveis e faceis de compor.

A ideia inicial e simples: cada etapa recebe um dicionario de contexto, devolve
novos valores e o fluxo registra eventos de execucao. Isso serve para scripts,
rotinas de ETL leves, automacoes internas, bots locais e prototipos que precisam
crescer sem virar um bloco unico de codigo.

## Instalacao

O pacote ja esta disponivel no PyPI:

```bash
python -m pip install merotec-autoflow
```

Tambem e possivel instalar direto do repositorio:

```bash
python -m pip install git+https://github.com/Romero-Softwares/merotecflow.git
```

## Uso real

Na pratica, a biblioteca ajuda a transformar uma automacao escrita como um
script longo em uma sequencia de etapas pequenas. Cada etapa recebe o mesmo
contexto, pode adicionar novos dados e deixa eventos registrados sobre inicio,
fim, falhas e tentativas.

Isso e util quando voce quer:

- dividir uma rotina em passos claros;
- reaproveitar etapas em fluxos diferentes;
- testar cada parte da automacao sem rodar o processo inteiro;
- saber em qual etapa uma execucao falhou;
- aplicar retry em etapas instaveis, como chamadas HTTP, leitura de arquivos ou
  integracoes externas;
- evoluir um prototipo para algo mais organizado sem adicionar um orquestrador
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

Saida esperada:

```python
{"email": "ada@example.com", "slug": "ada"}
["flow_started", "step_started", "step_finished", "step_started", "step_finished", "flow_finished"]
```

## Beneficios em projetos

- **Organizacao:** cada funcao vira uma etapa independente do fluxo.
- **Observabilidade simples:** a execucao gera eventos que podem ser usados em
  logs, auditoria ou diagnostico.
- **Testabilidade:** etapas pequenas sao mais faceis de testar com `unittest`,
  `pytest` ou testes manuais.
- **Resiliencia:** etapas podem ter `retries` e `delay`, evitando que falhas
  temporarias derrubem o processo na primeira tentativa.
- **Baixo acoplamento:** o fluxo usa um dicionario de contexto, sem exigir
  classes complexas ou infraestrutura externa.
- **Zero dependencias em runtime:** bom para ferramentas internas, scripts
  portaveis e ambientes controlados.

## Tipos de projetos indicados

- automacoes internas de escritorio, suporte, atendimento ou operacao;
- pipelines leves de ETL, importacao, limpeza e exportacao de dados;
- bots locais e rotinas agendadas;
- validadores de arquivos, formularios, planilhas ou cadastros;
- integrações simples com APIs, webhooks e sistemas internos;
- prototipos de agentes, ferramentas de IA e fluxos de decisao;
- CLIs e scripts Python que precisam crescer com mais organizacao.

## Quando nao usar

`merotec-autoflow` nao tenta substituir ferramentas completas como Airflow,
Prefect, Celery, Dagster ou filas distribuidas. Para execucao paralela,
agendamento distribuido, dashboards completos, workers remotos ou processamento
em larga escala, um orquestrador maior provavelmente sera mais adequado.

## Recursos iniciais

- API publica enxuta: `Flow`, `step`, `FlowResult` e `FlowEvent`.
- Contexto compartilhado entre etapas.
- Merge automatico de resultados em formato de dicionario.
- Retry por etapa com atraso opcional.
- Decorator flexivel: `@step`, `@step("nome")` ou `@step(name="nome")`.
- Eventos para observabilidade simples, incluindo falha do fluxo.
- Resultado com helpers como `get`, `elapsed` e `events_named`.
- Validacoes claras para nomes, contexto inicial, retries e delay.
- Zero dependencias externas em runtime.

## Desenvolvimento

```bash
python -m pip install -e .
python -m unittest
```

## Publicacao no PyPI

O projeto esta preparado para publicacao no PyPI. Para validar o pacote
localmente antes de uma nova versao:

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine check dist/*
```

O repositorio tambem pode publicar via GitHub Actions usando Trusted Publishing
do PyPI, sem salvar token no codigo. Para uma nova versao, atualize a versao em
`pyproject.toml`, gere uma tag e publique uma release/tag no GitHub.

Para testar em um indice separado antes do PyPI oficial, use TestPyPI:

```bash
python -m twine upload --repository testpypi dist/*
python -m pip install --index-url https://test.pypi.org/simple/ merotec-autoflow
```
