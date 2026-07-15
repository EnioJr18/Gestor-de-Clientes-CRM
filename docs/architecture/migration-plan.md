# Plano de Migracao

## Fase 1 - Protecao do comportamento atual

Entrada:

- ambiente e settings estabilizados;
- suite de caracterizacao atual passando.

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

## Fase 1.5 - Reorganizacao estrutural do backend

Estado:

- concluida na Sprint 5.

Escopo realizado:

- criacao de `backend/`;
- substituicao de `setup/` por `backend/config/`;
- movimentacao de `leads/` para `backend/apps/leads/`;
- preservacao do app label `leads`;
- manutencao de templates, static, migrations e testes dentro do app;
- manutencao do `.env` na raiz do repositorio;
- banco SQLite local resolvido em `backend/db.sqlite3`.

Fora de escopo:

- DRF;
- JWT;
- React;
- Docker;
- CI;
- alteracoes de dominio.

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

Estado:

- estabilizacao inicial concluida na Sprint 6.

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

- migrations testadas;
- banco limpo migrando do zero;
- SQLite validado;
- PostgreSQL local validado;
- Neon validado somente quando houver banco ou branch explicitamente descartavel.

Decisoes ja aplicadas:

- lead sem responsavel nao e permitido;
- excluir usuario remove seus leads e interacoes por CASCADE;
- e-mail de lead e unico por usuario com comparacao case-insensitive;
- usuarios diferentes podem cadastrar o mesmo e-mail;
- choices de status e prioridade sao protegidos por constraints;
- indices compostos foram adicionados para consultas por usuario, status, prioridade, criacao e interacoes por data.
- PostgreSQL 18 local passou a ser o banco principal de desenvolvimento e testes.
- SQLite ficou restrito a fallback explicito de diagnostico.
- Neon segue como destino de producao, exigindo `sslmode=require`.

## Fase 4 - API

Estado:

- fundacao REST concluida na Sprint 8;
- DRF, django-filter e drf-spectacular instalados;
- `/api/v1/health/`, `/api/v1/users/me/` e CRUD de leads implementados;
- OpenAPI, Swagger e ReDoc disponiveis;
- JWT seguro concluido na Sprint 9, com refresh HttpOnly, rotacao, blacklist, CSRF e CORS explicito;
- sessao Django preservada para as paginas legadas.

Escopo:

- endpoints de interacoes, dashboard e relatorios;
- revisao da matriz Simple JWT quando houver release com suporte formal a stack atual.

Dependencias:

- testes de dominio;
- regras de isolamento formalizadas;
- banco estabilizado.

Criterio para avancar:

- API cobre os fluxos necessarios para o frontend inicial, com isolamento por usuario e schema validado.

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

- estrategia de logout global ou revogacao de todos os dispositivos;
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
