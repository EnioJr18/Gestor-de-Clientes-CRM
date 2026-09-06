# Convencoes da API

## Versionamento

A API inicial usara o prefixo:

```text
/api/v1/
```

Recursos iniciais:

```text
/api/v1/health/
/api/v1/users/me/
/api/v1/leads/
/api/v1/leads/{lead_id}/interactions/
/api/schema/
/api/docs/
/api/redoc/
```

Novas versoes so devem ser criadas quando houver quebra real de contrato.

## Endpoints e nomes

- Usar substantivos no plural para colecoes.
- Manter trailing slash para alinhar com convencoes Django/DRF.
- Evitar endpoints como `POST /create-lead/` quando REST ja expressa a acao.
- Acoes especificas podem existir quando representarem operacao de dominio real.

Exemplo aceitavel:

```text
POST /api/v1/leads/{id}/change-status/
```

## Metodos HTTP

```text
GET     leitura
POST    criacao
PATCH   atualizacao parcial
PUT     atualizacao completa, somente se necessario
DELETE  exclusao
```

Preferir `PATCH` para edicao parcial de leads.

## Interacoes de leads

As interacoes sao recursos aninhados porque seu escopo deriva do lead:

```text
GET    /api/v1/leads/{lead_id}/interactions/
POST   /api/v1/leads/{lead_id}/interactions/
GET    /api/v1/leads/{lead_id}/interactions/{id}/
PATCH  /api/v1/leads/{lead_id}/interactions/{id}/
DELETE /api/v1/leads/{lead_id}/interactions/{id}/
```

- A URL define o lead; `lead` nao e aceito no payload.
- `tipo` e obrigatorio e usa os valores `LIGACAO`, `EMAIL`, `REUNIAO`, `MENSAGEM` ou `NOTA`.
- `nota` e obrigatoria e nao aceita texto somente com espacos.
- `data_interacao` aceita ISO 8601; quando omitida, recebe o horario atual do servidor.
- A lista e paginada e ordenada por `-data_interacao`, `-id`, para manter a timeline deterministica.
- O lead e a interacao sao sempre resolvidos dentro do escopo do usuario autenticado. Recursos de outro usuario retornam `404`.

## Dashboard analitico

`GET /api/v1/dashboard/summary/` preserva as metricas existentes e acrescenta agregacoes de interacoes no mesmo periodo:

- `interaction_total`: quantidade de interacoes por `data_interacao`;
- `interaction_by_type`: todos os valores de `Interaction.TIPO_CHOICES`, na ordem dos choices, com `tipo`, `label` e `count`;
- `leads_with_interaction`: leads atuais do usuario com ao menos uma interacao no periodo;
- `leads_without_interaction`: leads atuais do usuario sem interacao no periodo, usando o mesmo universo da metrica anterior;
- `interaction_monthly_evolution`: quantidade mensal por `data_interacao`, em ordem cronologica e com meses sem registros preenchidos por zero.

As interacoes sao filtradas por `lead__agente_responsavel` e nunca incluem dados de outros usuarios. Os periodos `7d`, `30d`, `90d`, `12m` e `custom` reutilizam as mesmas datas inclusivas aplicadas as metricas de leads.

## Status codes

```text
200 OK
201 Created
204 No Content
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
405 Method Not Allowed
409 Conflict
422 Unprocessable Entity, apenas se houver decisao explicita
429 Too Many Requests
500 Internal Server Error
```

Validacoes comuns usarao `400 Bad Request`, alinhadas ao comportamento padrao do DRF.

## Paginacao

Formato inicial:

```json
{
  "count": 42,
  "next": "http://example.test/api/v1/leads/?page=2",
  "previous": null,
  "results": []
}
```

Padroes:

- `page_size = 20`;
- `max_page_size = 100`;
- leads e interacoes devem ser paginados;
- metricas agregadas pequenas nao precisam de paginacao;
- pagina inexistente deve retornar erro consistente do DRF;
- `page_size` acima do maximo deve ser limitado ou rejeitado de forma documentada quando implementado.

## Busca, filtros e ordenacao

Parametros iniciais:

```text
?search=joao
?status=NOVO
?prioridade=ALTA
?criado_em_de=2026-01-01
?criado_em_ate=2026-01-31
?ordering=-criado_em
?page=2
?page_size=20
```

Filtros de leads:

- `search`: busca parcial e case-insensitive por nome, sobrenome, email e telefone; texto vazio ou somente espacos nao restringe resultados;
- `status`: valores de `Lead.STATUS_CHOICES`;
- `prioridade`: valores de `Lead.PRIORITY_CHOICES`;
- `criado_em_de` e `criado_em_ate`: intervalo inclusivo por data sobre `criado_em`;
- `ordering`: somente `nome`, `email`, `status`, `prioridade`, `criado_em` e `atualizado_em`, com prefixo `-` para ordem decrescente.

A listagem padrao usa `-criado_em`, `-id`. Quando ha ordering explicito, `id` e usado apenas como desempate interno na mesma direcao do primeiro campo, mantendo paginas estaveis sem expor `id` como parametro ordenavel.

Filtros invalidos nao devem ser silenciosamente ignorados se isso gerar comportamento confuso. A API deve retornar erro consistente.

Valores de choices devem preferir o contrato canonico atual (`NOVO`, `ALTA`, etc.). Normalizacao de caixa pode ser adicionada se documentada.

## Datas

- Persistir em UTC.
- Responder em ISO 8601.
- Usar timezone configurado no backend para interpretacao quando necessario.
- `date-fns` no frontend deve cuidar de exibicao e manipulacao de interface.

Exemplo:

```json
{
  "criado_em": "2026-07-13T22:30:00Z"
}
```

Filtros por data devem documentar limites inclusivos/exclusivos no endpoint concreto.

## Campos somente leitura

Campos como `id`, `criado_em`, `atualizado_em` e usuario proprietario devem ser somente leitura na API.

## Exclusao

Inicialmente usar `DELETE` com `204 No Content` quando a exclusao for definitiva. Soft delete e auditoria seguem como decisoes pendentes.

## Contrato de erros

Formato padrao:

```json
{
  "status": 400,
  "code": "validation_error",
  "message": "Os dados enviados sao invalidos.",
  "errors": {
    "email": [
      "Informe um endereco de e-mail valido."
    ]
  }
}
```

Campo obrigatorio:

```json
{
  "status": 400,
  "code": "validation_error",
  "message": "Os dados enviados sao invalidos.",
  "errors": {
    "nome": [
      "Este campo e obrigatorio."
    ]
  }
}
```

Choice invalido:

```json
{
  "status": 400,
  "code": "validation_error",
  "message": "Os dados enviados sao invalidos.",
  "errors": {
    "prioridade": [
      "Valor invalido."
    ]
  }
}
```

Nao autenticado:

```json
{
  "status": 401,
  "code": "not_authenticated",
  "message": "Autenticacao obrigatoria.",
  "errors": {}
}
```

Nao encontrado:

```json
{
  "status": 404,
  "code": "not_found",
  "message": "Recurso nao encontrado.",
  "errors": {}
}
```

Erro interno:

```json
{
  "status": 500,
  "code": "server_error",
  "message": "Erro interno do servidor.",
  "errors": {}
}
```

Nunca expor traceback, SQL, nomes de variaveis internas, secrets ou detalhes de infraestrutura.

## Autenticacao e CSRF

A API v1 aceita `Authorization: Bearer <access>` e sessao Django. Operacoes comuns autenticadas por Bearer nao dependem de CSRF; escritas por sessao continuam exigindo CSRF.

Contrato de autenticacao:

- `GET /api/v1/auth/csrf/`: emite cookie `csrftoken` legivel pela SPA e retorna o token.
- `POST /api/v1/auth/login/`: aceita somente JSON com username/password, retorna access e usuario; refresh somente no cookie HttpOnly.
- `POST /api/v1/auth/refresh/`: payload vazio, refresh no cookie e `X-CSRFToken` obrigatorio; rotaciona e revoga o anterior.
- `POST /api/v1/auth/logout/`: payload vazio e `X-CSRFToken` obrigatorio; revoga quando houver token, apaga o cookie e retorna 204 de forma idempotente.
- `GET /api/v1/users/me/`: aceita JWT e sessao e retorna apenas campos seguros.

Payloads de auth rejeitam campos desconhecidos. Falhas de credencial nao distinguem usuario inexistente, senha incorreta ou usuario inativo. Refresh nunca aparece no JSON.

## Campos protegidos

`id`, `agente_responsavel`, `criado_em` e `atualizado_em` nao podem ser enviados em payloads de lead. Campos desconhecidos tambem sao rejeitados com erro de validacao.
