# ADR 0009 - Fundacao da API REST

## Status

Aceito

## Contexto

O projeto precisava iniciar a API REST versionada sem substituir as paginas Django existentes e sem antecipar JWT ou frontend React.

## Decisao

- Usar Django REST Framework como base da API.
- Usar `django-filter` para filtros declarativos.
- Usar `drf-spectacular` para OpenAPI, Swagger UI e ReDoc.
- Criar a primeira versao em `/api/v1/`.
- Manter autenticacao por sessao Django nesta sprint.
- Manter CSRF ativo para escritas autenticadas por sessao.
- Aplicar `IsAuthenticated` como permissao padrao, com `AllowAny` apenas em health e documentacao.
- Implementar CRUD de leads escopado por `agente_responsavel=request.user`.
- Retornar 404 para recursos inexistentes ou pertencentes a outro usuario.
- Rejeitar campos desconhecidos e campos protegidos em payloads de lead.

## Consequencias

- A API coexiste com templates, rotas Django tradicionais, admin, CSV, dashboard e interacoes.
- JWT, CORS e a SPA continuam para sprint futura.
- O contrato de erros JSON passa a ser responsabilidade do handler da API.
- A documentacao OpenAPI fica publica nesta fase para desenvolvimento e validacao.
- A seguranca de escrita continua dependendo de CSRF enquanto a autenticacao for por sessao.
