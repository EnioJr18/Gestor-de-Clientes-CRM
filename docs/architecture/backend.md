# Arquitetura do Backend

## Estilo

O backend sera um monolito modular com Django e Django REST Framework. A separacao sera por dominio, mantendo o Django ORM como camada de persistencia principal.

Nao serao usados:

- microservicos;
- Kubernetes;
- repositories genericos sobre o Django ORM;
- services para CRUD trivial;
- pastas/classes vazias sem uso real.

## Estrutura-alvo de referencia

```text
backend/
  config/
    settings/
    urls.py
    asgi.py
    wsgi.py
  apps/
    accounts/
    leads/
    interactions/
    dashboard/
    reports/
  common/
    exceptions.py
    pagination.py
    permissions.py
    validators.py
  tests/
  manage.py
  requirements/
```

Essa estrutura e referencia futura. Nao e uma ordem para mover os arquivos agora.

## Modulos previstos

### accounts

Responsavel por usuario autenticado, perfil, cadastro, autenticacao, alteracao de senha, recuperacao de senha e endpoint `me`.

### leads

Responsavel por cadastro, listagem, busca, filtros, atualizacao, exclusao, status, prioridade e propriedade dos dados.

### interactions

Responsavel por historico de interacoes, notas, contatos, datas, vinculo com lead e operacoes futuras de timeline.

### dashboard

Responsavel por metricas, agregacoes, funil, atividade, graficos e consultas por periodo.

### reports

Responsavel por CSV, exportacoes, relatorios, sanitizacao, limites e possiveis tarefas assincronas futuras.

## Camadas

### Models

Devem conter persistencia, relacionamentos, constraints, invariantes simples e comportamentos diretamente ligados a entidade.

Nao devem conter request, logica HTTP, geracao de response ou fluxos grandes envolvendo varios dominios.

### Serializers

Devem conter validacao da API, transformacao de entrada/saida, campos gravaveis, campos somente leitura e validacoes relacionadas ao contrato HTTP.

Nao devem concentrar fluxos transacionais complexos, consultas pesadas, relatorios ou agregacoes.

### Views e ViewSets

Devem receber a requisicao, selecionar serializer, aplicar permissoes, limitar queryset, chamar services/selectors quando necessario e retornar resposta.

Nao devem concentrar regras complexas, fazer multiplas operacoes de negocio sem transacao ou repetir filtros de propriedade de maneira inconsistente.

### Services

Services so devem existir quando houver:

- multiplas operacoes relacionadas;
- transacao;
- regra de negocio reutilizavel;
- mudanca de estado relevante;
- auditoria;
- integracao externa;
- efeito colateral.

Exemplos futuros:

```python
create_lead_with_initial_interaction(...)
change_lead_status(...)
convert_lead(...)
delete_user_data(...)
```

Nao criar service para encapsular apenas:

```python
Lead.objects.create(...)
```

### Selectors

Selectors devem existir para dashboard, metricas, relatorios, consultas agregadas, filtros reutilizaveis e consultas com otimizacao especifica.

Exemplos:

```python
get_leads_summary_for_user(...)
get_conversion_funnel_for_user(...)
get_recent_interactions_for_user(...)
```

### Permissions

Devem garantir autenticacao, escopo por usuario, objeto pertencente ao usuario, comportamento consistente para recursos alheios e ausencia de IDOR.

### Common

`common/` deve conter somente recursos realmente compartilhados. Nao deve virar deposito generico.

## Dependencias entre modulos

Direcao preferencial:

```text
accounts
   ^
leads
   ^
interactions

dashboard -> consulta accounts, leads e interactions
reports   -> consulta leads e interactions
```

Regras:

- `leads` nao deve depender de `dashboard`.
- `interactions` pode depender de `leads`.
- `dashboard` nao deve conter persistencia de dominio.
- `reports` nao deve alterar leads.
- Modulos nao devem importar views uns dos outros.
- Regras compartilhadas precisam de justificativa antes de ir para `common`.

## Transacoes

Usar `transaction.atomic()` quando:

- criar ou alterar multiplos registros;
- registrar interacao junto com mudanca de lead;
- importar dados;
- realizar operacao indivisivel;
- criar auditoria junto com acao principal.

Nao usar indiscriminadamente em toda view.
