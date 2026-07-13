# Arquitetura do Backend

## Estilo

O backend sera um monolito modular com Django e Django REST Framework. A separacao sera por dominio, mantendo o Django ORM como camada de persistencia principal.

Nao serao usados:

- microservicos;
- Kubernetes;
- repositories genericos sobre o Django ORM;
- services para CRUD trivial;
- pastas/classes vazias sem uso real.

## Estrutura atual

```text
backend/
  config/
    settings/
    urls.py
    asgi.py
    wsgi.py
  apps/
    leads/
      migrations/
      static/
      templates/
      tests/
  manage.py
  requirements.txt
```

`backend/apps/leads/apps.py` usa `name = "apps.leads"` e preserva `label = "leads"` para manter o historico de migrations e o app label existente.

## Estrutura futura de referencia

```text
backend/
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
```

Essa estrutura futura e referencia de evolucao. Nao criar pastas vazias antes de necessidade real.

## Modulos previstos

### accounts

Responsavel por usuario autenticado, perfil, cadastro, autenticacao, alteracao de senha, recuperacao de senha e endpoint `me`.

### leads

Responsavel por cadastro, listagem, busca, filtros, atualizacao, exclusao, status, prioridade e propriedade dos dados.

Estado atual de dominio:

- `Lead.agente_responsavel` e obrigatorio e usa `on_delete=CASCADE`.
- `Lead.email` e obrigatorio e unico por usuario responsavel, com comparacao case-insensitive no banco.
- Usuarios diferentes podem cadastrar o mesmo e-mail de lead.
- `status` e `prioridade` mantem valores persistidos estaveis e possuem constraints de banco.
- `Interaction.lead` e obrigatorio e usa `on_delete=CASCADE`.
- `Interaction.nota` e obrigatoria; o form e a validacao de model rejeitam valores vazios ou somente espacos, e o banco rejeita string vazia.

Indices atuais justificados pelas consultas existentes:

- `lead_owner_status_idx`: dashboard e filtros por status dentro do usuario.
- `lead_owner_priority_idx`: dashboard e filtros por prioridade dentro do usuario.
- `lead_owner_created_idx`: listagem, recentes e novos por usuario.
- `inter_lead_date_idx`: historico e interacoes recentes por lead em ordem temporal.

Compatibilidade de banco:

- PostgreSQL 18 local e o banco principal de desenvolvimento.
- SQLite continua suportado apenas como fallback explicito de diagnostico.
- PostgreSQL/Neon suporta a unicidade funcional por `LOWER(email)`, validada em PostgreSQL local.
- SQLite recria tabelas ao aplicar algumas constraints; isso e esperado para desenvolvimento local.

## Banco de dados

Desenvolvimento usa PostgreSQL local via Docker Compose:

```text
Dockerfile.postgres -> FROM postgres:18-alpine
docker-compose.yml -> image crm-pro-postgres:18
DATABASE_URL=postgresql://crm_user:crm_password@localhost:5432/crm_pro
TEST_DATABASE_URL=postgresql://crm_user:crm_password@localhost:5432/crm_pro_test
```

`USE_SQLITE=True` e `USE_SQLITE_FOR_TESTS=True` existem somente para diagnostico local. A ausencia de `DATABASE_URL` nao faz fallback silencioso para SQLite.

Producao exige PostgreSQL com `sslmode=require`, sem fallback para SQLite. Neon deve ser validado em banco ou branch explicitamente descartavel antes de aplicar migrations remotas.

O driver mantido e `psycopg2-binary==2.9.11`, ja presente no projeto e validado com Django 6 e Python 3.14 nesta sprint.

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
