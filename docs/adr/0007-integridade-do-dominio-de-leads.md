# ADR 0007 - Integridade do dominio de leads

## Status

Aceito

## Contexto

O app `leads` e a base do isolamento atual por usuario. Antes de introduzir PostgreSQL definitivo, DRF e frontend React, o dominio precisava reduzir estados ambiguos: leads sem responsavel, e-mails duplicados para o mesmo usuario e valores fora dos choices.

O banco local atual continha somente dados de teste e nao apresentou registros incompativeis durante a Sprint 6.

## Decisao

- `Lead.agente_responsavel` passa a ser obrigatorio.
- A exclusao de usuario continua usando `CASCADE`.
- `Lead.email` permanece obrigatorio.
- O mesmo usuario nao pode ter dois leads com o mesmo e-mail, ignorando maiusculas/minusculas.
- Usuarios diferentes podem ter leads com o mesmo e-mail.
- O form normaliza e-mail com trim e lowercase no fluxo web atual.
- `status` e `prioridade` mantem os valores persistidos atuais.
- `Interaction.nota` continua `TextField`, mas valores vazios sao rejeitados pelo banco e valores vazios ou somente espacos sao rejeitados por form/model validation.
- Nao foram adicionados campos especulativos, soft delete, auditoria, organizacoes ou multi-tenancy real.

## Constraints

- `lead_owner_email_ci_uniq`: unicidade por `agente_responsavel` e `Lower(email)`.
- `lead_status_valid_chk`: limita status aos valores oficiais.
- `lead_priority_valid_chk`: limita prioridade aos valores oficiais.
- `lead_nome_not_empty_chk`: impede nome vazio no banco.
- `lead_email_not_empty_chk`: impede e-mail vazio no banco.
- `interaction_nota_not_empty_chk`: impede nota vazia no banco.

## Indices

- `lead_owner_status_idx`: consultas de dashboard/filtro por usuario e status.
- `lead_owner_priority_idx`: consultas de dashboard/filtro por usuario e prioridade.
- `lead_owner_created_idx`: listagens, recentes e ordenacao por criacao dentro do usuario.
- `inter_lead_date_idx`: historico e interacoes recentes por lead.

## Consequencias

- Um banco com leads orfaos ou duplicidades por usuario deve ser limpo antes da migration de schema.
- A migration `0004_validate_domain_integrity` falha cedo se encontrar dados incompativeis, sem criar usuario ficticio ou apagar dados.
- SQLite segue suportado, mas recria tabelas para aplicar algumas constraints.
- PostgreSQL local foi validado na Sprint 7.
- Neon deve ser validado em banco descartavel antes de receber migrations remotas.
- A API futura deve reutilizar a mesma politica de dominio nos serializers.
