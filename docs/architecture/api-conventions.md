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
?ordering=-criado_em
?page=2
?page_size=20
```

Filtros de leads:

- `search`: busca parcial por nome, sobrenome, email e telefone;
- `status`: valores de `Lead.STATUS_CHOICES`;
- `prioridade`: valores de `Lead.PRIORITY_CHOICES`;
- `criado_em_de` e `criado_em_ate`: intervalo inclusivo por data;
- `ordering`: campos permitidos somente.

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

A Sprint 8 usa autenticacao por sessao Django na API. Escritas autenticadas (`POST`, `PATCH`, `PUT`, `DELETE`) exigem CSRF quando a sessao real e usada. Essa decisao preserva a seguranca atual ate a introducao planejada de JWT.

## Campos protegidos

`id`, `agente_responsavel`, `criado_em` e `atualizado_em` nao podem ser enviados em payloads de lead. Campos desconhecidos tambem sao rejeitados com erro de validacao.
