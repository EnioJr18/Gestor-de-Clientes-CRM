# ADR 0010 - Autenticacao JWT para a SPA

## Status

Aceita na Sprint 9.

## Contexto

A futura SPA React precisa autenticar chamadas cross-origin sem remover o frontend Django atual. A stack e Python 3.14.3, Django 6.0.1 e DRF 3.17.1. O Simple JWT 5.5.1 nao declara suporte oficial a essas versoes: sua matriz estavel termina em Python 3.13, Django 5.1 e DRF 3.15.

## Decisao

- Validar Simple JWT 5.5.1 no projeto, sem downgrade e sem JWT manual.
- Retornar access token HS256 de 5 minutos no JSON e envia-lo como Bearer; a SPA devera mante-lo apenas em memoria.
- Guardar refresh de 7 dias somente em cookie HttpOnly, com Path de auth, flags por ambiente e Secure obrigatorio em producao.
- Rotacionar refresh e colocar o anterior na blacklist oficial.
- Exigir CSRF em refresh e logout, pois usam credencial em cookie.
- Preservar SessionAuthentication e os fluxos Django legados.
- Permitir CORS somente para origens explicitas e configurar CSRF trusted origins separadamente.
- Limitar login/refresh por IP com throttling DRF e cache local nesta fase.

## Consequencias

Rotacionar `SECRET_KEY` invalida todos os JWT. O frontend deve serializar refreshes concorrentes. A blacklist adiciona tabelas e exige limpeza periodica com `flushexpiredtokens`. O throttling em cache local nao e global entre replicas.

A compatibilidade da biblioteca foi validada por imports, emissao, autenticacao, refresh, usuario inativo, rotacao, blacklist, CRUD JWT, CORS, CSRF, OpenAPI e suite PostgreSQL 18. Isso reduz o risco, mas nao converte a combinacao em oficialmente suportada; upgrades devem repetir a prova.
