# ADR 0012 - Gestao de leads na SPA

## Decisao

A feature `frontend/src/features/leads` concentra tipos, schemas Zod, cliente Axios, query keys, hooks TanStack Query, componentes e paginas. Filtros, busca, ordenacao e paginacao usam a URL como fonte de estado. Formularios usam React Hook Form e Zod; criacao e edicao usam dialogos, enquanto detalhes usam pagina propria.

## Consequencias

Mutations invalidam somente listas e detalhe do lead afetado. Nao ha reload, optimistic update complexo ou Zustand. O access token continua apenas em memoria. O responsavel nao e enviado pelo cliente: a API o infere pelo usuario autenticado.
