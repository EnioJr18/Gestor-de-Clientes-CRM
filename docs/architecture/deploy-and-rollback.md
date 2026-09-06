# Release, Deploy e Rollback

## Estado da Sprint 19.3

O repositorio possui imagens Docker reproduziveis, health checks, migrations
separadas do processo web e CI versionada. Ele ainda nao possui um destino de
deploy, dominio, secrets provisionados, banco PostgreSQL de producao, cache
compartilhado, destino de backup ou responsavel operacional comprovados.

Por isso, a decisao desta sprint e **NO-GO**: nenhum deploy, migration remota,
acesso ao Neon ou alteracao em producao deve ser executado ate que todos os
itens abaixo tenham evidencia registrada pela operacao.

## Pre-requisitos de go-live

1. Escolher a plataforma, a regiao e o responsavel operacional do servico.
2. Provisionar PostgreSQL gerenciado ou branch Neon confirmada como producao,
   com TLS e `sslmode=require`. Manter uma credencial temporaria e auditada
   para migrations, separada da credencial limitada de runtime.
3. Cadastrar secrets somente no provedor: `SECRET_KEY` aleatoria, `DATABASE_URL`,
   `ALLOWED_HOSTS`, origens CORS/CSRF, configuracao SMTP e, quando houver mais
   de um processo ou replica, cache compartilhado com
   `REQUIRE_SHARED_THROTTLE_CACHE=True`. Nenhum secret vai para Git, imagem ou
   variavel `VITE_*`.
4. Configurar dominio, certificado HTTPS, proxy que preserve
   `X-Forwarded-Proto`, redirecionamento HTTP para HTTPS e politica HSTS. So
   habilitar `SECURE_HSTS_INCLUDE_SUBDOMAINS` e preload depois de validar todos
   os subdominios.
5. Configurar coleta de stdout, retencao, alerta para erros e responsavel de
   atendimento. O runtime produz linhas com data/hora, nivel e logger; tokens,
   cookies, senhas e `DATABASE_URL` nao podem entrar nos logs.
6. Definir e aprovar RPO, RTO, destino externo criptografado, retencao, dono do
   backup e alerta de falha. Executar e registrar um restore isolado conforme
   `backup-and-recovery.md` antes do primeiro deploy.
7. Confirmar CI verde no commit exato a publicar, incluindo PostgreSQL 18,
   migrations, `check --deploy`, OpenAPI, testes, lint, type-check, build e
   imagens Docker.

## Procedimento de deploy

Com todos os pre-requisitos aprovados, registrar a janela de mudanca e o hash
do commit. Fazer backup e verificar que ele pode ser lido antes de migrar.

1. Construir as imagens pelo commit aprovado e publicar em registro privado da
   plataforma.
2. Executar `python manage.py migrate --noinput` uma unica vez com a credencial
   de deploy. Interromper se o plano incluir uma operacao inesperada.
3. Executar `python manage.py collectstatic --noinput` na imagem ou release
   task. O `Dockerfile.backend` ja gera os assets do Django com WhiteNoise.
4. Subir o backend Gunicorn e o frontend Nginx com a configuracao de producao.
   Nunca expor PostgreSQL diretamente na internet.
5. Aguardar os health checks e validar publicamente HTTPS, `GET /health`,
   `GET /api/v1/health/`, carregamento da SPA, login, `users/me`, uma listagem
   autenticada de leads e o console do navegador sem erro CORS/CSRF.
6. Monitorar logs, erro HTTP, latencia e conexoes do banco durante a janela.

## Rollback

Rollback de aplicacao significa voltar a imagem previamente aprovada. Nao
significa apagar dados, usar `DROP`, limpar banco ou remover volumes.

1. Pausar o rollout e selecionar a imagem anterior conhecida como saudavel.
2. Verificar compatibilidade reversa das migrations antes de trocar a imagem.
   Se a migration nao for reversivel com seguranca, manter a versao atual e
   tratar o incidente com uma migration corretiva planejada.
3. Restaurar banco somente a partir de backup validado, para um incidente que
   realmente exija recuperacao e com janela aprovada. Nunca sobrescrever a
   origem por conveniencia.
4. Repetir os smoke tests e registrar horario, versao, sintomas e decisao.

## Evidencia minima para mudar de NO-GO para GO

- URL do ambiente, dominio e certificado HTTPS validados;
- CI verde no commit do release;
- backup automatizado com destino, retencao, RPO/RTO, responsavel e restore
  testado;
- banco, cache e secrets provisionados sem exposicao no repositorio;
- plano de migration revisado e rollback de aplicacao aprovado;
- smoke tests e observabilidade prontos para a janela de mudanca.
