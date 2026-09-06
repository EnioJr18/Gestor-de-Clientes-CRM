# Backup e Recuperacao PostgreSQL

## Escopo

PostgreSQL e o banco de producao do CRM.Pro. Backups, restores e validacoes devem ser executados somente por operadores autorizados e nunca em Neon ou producao sem uma janela de mudanca aprovada.

O dump nao deve ser colocado no repositorio, frontend, imagem Docker ou documentacao publica. O `.gitignore` cobre `backups/`, `*.backup`, `*.dump` e `*.sql.gz`; em operacao real, o arquivo deve ficar fora do workspace ou em armazenamento restrito.

## Estrategia inicial recomendada

- Ferramenta: `pg_dump` em formato custom (`-Fc`), por preservar objetos e permitir `pg_restore` seletivo.
- Frequencia: backup diario automatizado, mais backup antes de migrations ou mudancas operacionais relevantes.
- Retencao recomendada: 30 diarios, 12 semanais e 12 mensais, sujeita a capacidade e requisitos legais definidos pela operacao.
- Armazenamento: fora do host principal, com acesso restrito e auditavel; criptografado em repouso quando o provedor suportar.
- Credenciais: usar variaveis ou mecanismo de secrets do provedor; nunca inclui-las em comandos versionados, dumps ou logs.
- Validacao: restaurar periodicamente em banco isolado e conferir migrations, constraints, indices e fluxos da aplicacao.

Essa e uma politica inicial recomendada, nao substitui a definicao formal de RPO, RTO, responsavel operacional e provedor de backup.

## Procedimento local controlado

Antes de qualquer comando, confirmar host, porta e nome do banco. Os exemplos abaixo usam placeholders e devem apontar para PostgreSQL local/controlado.

```powershell
$env:DATABASE_URL = "postgresql://<user>:<password>@127.0.0.1:5432/<source_db>"
python backend/manage.py showmigrations
pg_dump -Fc --no-owner --no-privileges -f <temporary_path>/crm-pro.backup $env:DATABASE_URL
pg_restore --list <temporary_path>/crm-pro.backup
```

O restore deve usar um banco novo, jamais sobrescrever o banco de origem:

```powershell
createdb -h 127.0.0.1 -U <user> <restore_db>
pg_restore --exit-on-error --no-owner --no-privileges -h 127.0.0.1 -U <user> -d <restore_db> <temporary_path>/crm-pro.backup
```

Nao usar `--clean`, `DROP DATABASE`, `flush` ou reset indiscriminado no procedimento de recuperacao. Se o banco de restore ja existir, interromper e escolher outro nome controlado.

## Validacao apos restore

Apontar `DATABASE_URL` explicitamente para o banco restaurado e executar:

```powershell
python backend/manage.py check
python backend/manage.py showmigrations
python backend/manage.py migrate --plan
python backend/manage.py makemigrations --check --dry-run
```

Validar tambem `auth_user`, `leads_lead`, `leads_interaction`, `django_migrations`, as constraints de ownership/choices/not-null e os indices de owner, email e data. A aplicacao deve consultar leads, interactions e dashboard contra o banco restaurado.

## Runtime, migrations e RLS

Em producao, a credencial runtime deve ter somente privilegios necessarios para a aplicacao. Migrations devem usar uma credencial de deploy separada, temporaria e auditada. RLS nao esta ativo: ownership permanece responsabilidade da aplicacao ate existir contexto transacional de usuario e arquitetura de pooling compativel.

## RPO e RTO

RPO e RTO ainda nao foram definidos pelo projeto. Eles precisam ser aprovados pela operacao antes do go-live, junto com responsavel pelo restore, destino do backup, monitoramento de falhas e exercicio periodico de recuperacao.
