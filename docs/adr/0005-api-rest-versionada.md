# ADR 0005 - API REST versionada

## Status

Aceito

## Contexto

A SPA React consumira uma API do backend Django. O contrato precisa ser estavel o suficiente para permitir evolucao sem quebrar consumidores.

## Decisao

Usar API REST versionada com prefixo:

```text
/api/v1/
```

Convencoes iniciais:

- recursos no plural;
- trailing slash;
- `GET`, `POST`, `PATCH`, `DELETE` conforme semantica REST;
- `400 Bad Request` para validacoes comuns;
- paginacao em formato DRF;
- contrato de erros padronizado.

## Alternativas consideradas

- API sem versao: rejeitada por dificultar evolucao.
- GraphQL: rejeitado por complexidade desnecessaria para o escopo atual.
- Endpoints verbosos como `/create-lead/`: rejeitados quando REST ja expressa a operacao.

## Consequencias

- Mudancas incompatíveis devem entrar em nova versao.
- Documentacao OpenAPI deve refletir contratos reais quando DRF entrar.
- Frontend pode tipar respostas e payloads com mais previsibilidade.
