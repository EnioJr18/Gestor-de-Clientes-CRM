# ADR 0002 - Frontend organizado por features

## Status

Aceito

## Contexto

O frontend atual e Django Templates com Bootstrap. A arquitetura futura sera uma SPA em React + TypeScript.

Uma estrutura por tipo tecnico puro tende a espalhar codigo de uma mesma funcionalidade em muitos lugares.

## Decisao

Organizar o frontend por features:

- auth;
- leads;
- interactions;
- dashboard;
- profile;
- reports.

Cada feature pode conter `api`, `components`, `hooks`, `pages`, `schemas`, `types` e `utils` quando houver necessidade real.

Componentes compartilhados ficam em `components/ui` e `components/layout` apenas quando forem realmente reutilizaveis.

## Alternativas consideradas

- Organizacao por tipo tecnico global: rejeitada por baixa coesao por funcionalidade.
- Criar todos os componentes compartilhados no inicio: rejeitado por risco de abstrair cedo demais.

## Consequencias

- Melhor proximidade entre pagina, API, schema e tipos da feature.
- Menos estado global desnecessario.
- Exige criterio para nao duplicar componentes que realmente deveriam ser compartilhados.
