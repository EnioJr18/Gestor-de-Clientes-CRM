# Plano de Migracao

## Fase 1 - Protecao do comportamento atual

Entrada:

- ambiente e settings estabilizados;
- 16 testes atuais passando.

Escopo:

- testes de caracterizacao;
- autenticacao;
- CRUD;
- isolamento;
- interacoes;
- dashboard;
- CSV;
- perfil.

Saida:

- comportamento atual documentado por testes.

Riscos:

- testes reproduzirem bugs atuais sem sinalizacao.

Criterio para avancar:

- fluxos principais cobertos para usuario anonimo, dono e outro usuario.

## Fase 2 - Correcoes do monolito atual

Escopo:

- bugs de filtros;
- metricas inconsistentes;
- CSV Injection;
- mensagens e fluxos inconsistentes;
- problemas simples de permissao ou consulta.

Criterio para avancar:

- testes de caracterizacao ajustados para o comportamento corrigido.

## Fase 3 - Dominio e banco

Escopo:

- constraints;
- nullable;
- indices;
- migrations de dados;
- PostgreSQL/Neon;
- diferencas SQLite/PostgreSQL.

Riscos:

- dados existentes exigirem limpeza;
- constraints quebrarem registros legados.

Criterio para avancar:

- migrations testadas e banco PostgreSQL validado.

## Fase 4 - API

Escopo:

- DRF;
- serializers;
- permissions;
- erros;
- paginacao;
- filtros;
- OpenAPI;
- JWT;
- endpoints de leads, interacoes, dashboard e relatorios.

Dependencias:

- testes de dominio;
- regras de isolamento formalizadas;
- banco estabilizado.

Criterio para avancar:

- API cobre os fluxos necessarios para o frontend.

## Fase 5 - Frontend

Escopo:

- React;
- autenticacao;
- leads;
- interacoes;
- dashboard;
- perfil;
- relatorios;
- testes frontend.

Riscos:

- duplicar regra de negocio no frontend;
- nao preservar fluxos atuais.

Criterio para avancar:

- SPA cobre as funcionalidades principais sem depender de templates Django.

## Fase 6 - Infraestrutura

Escopo:

- Docker;
- CI;
- deploy;
- Neon;
- documentacao operacional;
- AWS somente depois da estabilizacao.

Riscos:

- complexidade operacional antes da maturidade do app.

Criterio para avancar:

- pipeline reproduzivel e deploy com checks automatizados.

## Decisoes pendentes

- estrategia final de JWT;
- cookie, memoria ou outro armazenamento;
- politica de refresh;
- organizacao futura ou somente usuario;
- soft delete ou exclusao definitiva;
- auditoria de alteracoes;
- campos adicionais do lead;
- valor estimado;
- origem;
- pipeline;
- tarefas assincronas;
- politica de retencao de dados;
- provider de e-mail;
- deploy inicial do backend;
- dominio;
- observabilidade;
- AWS.
