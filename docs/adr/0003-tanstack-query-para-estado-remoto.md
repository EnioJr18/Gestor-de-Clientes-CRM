# ADR 0003 - TanStack Query para estado remoto

## Status

Aceito

## Contexto

A SPA consumira dados remotos da API: leads, interacoes, perfil, dashboard e relatorios. Esses dados precisam de cache, refetch, loading, errors, mutations e invalidacao.

## Decisao

Usar TanStack Query para estado remoto.

Zustand nao deve duplicar dados da API. Filtros relevantes devem preferencialmente ficar na URL.

## Alternativas consideradas

- `useState`/Context para dados remotos: rejeitado por exigir cache e invalidacao manuais.
- Zustand para tudo: rejeitado por misturar estado remoto com estado local/global.
- Reload de pagina apos mutation: rejeitado por pior experiencia e por nao combinar com SPA.

## Consequencias

- Query keys e invalidacoes precisam ser padronizadas.
- Mutations devem invalidar dados relacionados, como leads e dashboard.
- Estado local continua simples e perto da UI.
