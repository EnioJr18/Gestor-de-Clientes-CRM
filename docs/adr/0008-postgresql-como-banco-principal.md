# ADR 0008 - PostgreSQL como banco principal

## Status

Aceito

## Contexto

O projeto precisava validar as migrations e constraints reais fora do SQLite antes de iniciar a fundacao da API. A Sprint 7 definiu PostgreSQL como banco principal de desenvolvimento e testes, mantendo SQLite apenas como fallback explicito de diagnostico.

## Decisao

- Usar PostgreSQL 18 local via Docker Compose.
- Construir a imagem local `crm-pro-postgres:18` a partir de `Dockerfile.postgres`, baseado em `postgres:18-alpine`.
- Subir apenas o servico de banco; backend e frontend nao sao containerizados nesta sprint.
- Usar `DATABASE_URL` para desenvolvimento e `TEST_DATABASE_URL` para testes.
- Rejeitar fallback silencioso para SQLite.
- Exigir PostgreSQL em producao com `sslmode=require`.
- Manter `psycopg2-binary==2.9.11` nesta sprint.

## Motivos

- PostgreSQL 18 e a versao de trabalho preferida pelo projeto.
- O Dockerfile torna explicita a base PostgreSQL 18 usada pelo projeto sem criar Dockerfile do backend.
- `psycopg2-binary` ja estava instalado, passou em `pip check` e validou a suite completa com Python 3.14 e Django 6.
- Migrar para Psycopg 3 fica como opcao futura, quando houver necessidade real ou janela dedicada de dependencias.

## Consequencias

- O arquivo `.env` local precisa definir `DATABASE_URL` e `TEST_DATABASE_URL`.
- `python backend/manage.py test` usa PostgreSQL por padrao.
- `USE_SQLITE=True` e `USE_SQLITE_FOR_TESTS=True` sao apenas fallback explicito.
- Neon nao deve receber comandos destrutivos nem migrations sem confirmacao de banco ou branch descartavel.
- O volume Docker local pode ser removido com `docker compose down -v`, apagando o banco local.
