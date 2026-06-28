# merotec-autoflow

`merotec-autoflow` e uma biblioteca Python pequena para criar fluxos de automacao
observaveis, testaveis e faceis de compor.

A ideia inicial e simples: cada etapa recebe um dicionario de contexto, devolve
novos valores e o fluxo registra eventos de execucao. Isso serve para scripts,
rotinas de ETL leves, automacoes internas, bots locais e prototipos que precisam
crescer sem virar um bloco unico de codigo.

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

## Instalacao pelo repositorio

Depois que o codigo estiver no GitHub, a biblioteca pode ser instalada direto do
repositorio:

```bash
python -m pip install git+https://github.com/Romero-Softwares/merotecflow.git
```

## Publicacao no PyPI

Antes de publicar, gere e valide o pacote localmente:

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine check dist/*
```

Para testar em um indice separado antes do PyPI oficial:

```bash
python -m twine upload --repository testpypi dist/*
python -m pip install --index-url https://test.pypi.org/simple/ merotec-autoflow
```

Para publicar no PyPI oficial:

```bash
python -m twine upload dist/*
```

Use um token de API do PyPI quando o `twine` pedir a senha. O usuario pode ser
`__token__` e a senha deve ser o token completo gerado na conta do PyPI.
