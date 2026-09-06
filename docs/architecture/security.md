# Estrategia de Seguranca

## Regra central

Todo recurso de negocio deve estar associado ao usuario autenticado, direta ou indiretamente.

Modelo atual:

```text
Lead.agente_responsavel = usuario autenticado
Interaction.lead.agente_responsavel = usuario autenticado
```

`Lead.agente_responsavel` e obrigatorio no banco. A exclusao de usuario usa CASCADE, removendo leads e interacoes associados, pois o projeto ainda nao possui retencao, auditoria formal ou organizacoes.

O projeto atual possui isolamento por usuario. Ele nao possui multi-tenancy real por organizacao.

Organizacao, membership e roles nao entram agora. Uma evolucao futura pode adicionar organizacoes, mas isso nao deve ser antecipado sem necessidade.

## IDOR

Querysets devem nascer limitados:

```python
Lead.objects.filter(agente_responsavel=request.user)
```

Evitar:

```python
lead = Lead.objects.get(pk=pk)
if lead.agente_responsavel != request.user:
    ...
```

Recursos de outros usuarios devem preferencialmente responder como nao encontrados, evitando confirmar existencia.

## Validacao server-side

O backend sempre e a fonte final de validacao. Validacao no frontend melhora UX, mas nao substitui serializers, permissions e regras de dominio no servidor.

## Autenticacao JWT para SPA

- Access token HS256 de 5 minutos no JSON, mantido apenas em memoria pela SPA; nenhum acesso a `localStorage` ou `sessionStorage` e usado para autenticacao.
- Refresh token de 7 dias somente em cookie HttpOnly, Path `/api/v1/auth/`, SameSite configuravel e Secure obrigatorio em producao.
- Rotacao e blacklist a cada refresh; logout revoga o token corrente.
- O segredo padrao e `SECRET_KEY`; rotaciona-lo invalida todos os JWT existentes.
- Login aceita somente JSON, impedindo submissao simples por formulario cross-site; CORS exige origem explicita para o preflight. Refresh e logout exigem cookie CSRF + header `X-CSRFToken`; nao ha `csrf_exempt`.
- Login e refresh rejeitam usuario inativo e usam mensagem generica contra enumeracao.
- Throttling local por IP: login 5/min, refresh 20/min e CSRF 60/min, todos configuraveis. Cache local nao coordena limites entre multiplas instancias; Redis continua fora desta sprint.
- A sessao Django permanece ativa e continua exigindo CSRF para escrita.
- O bootstrap obtem CSRF, tenta refresh uma vez e consulta `users/me` antes de liberar rotas.
- Refreshes concorrentes compartilham uma unica promessa; falha definitiva limpa usuario e access token sem loop de retry.

## API REST atual

A API v1 usa JWT Bearer para SPA e sessao Django para compatibilidade. O contrato JSON padronizado continua cobrindo autenticacao, permissao, CSRF, validacao e throttling.

Endpoints publicos nesta sprint:

- `GET /api/v1/health/`;
- documentacao OpenAPI em `/api/schema/`, `/api/docs/` e `/api/redoc/`.

Endpoints de dados exigem usuario autenticado. Leads sao sempre filtrados por `agente_responsavel=request.user`; leads alheios retornam 404 para evitar IDOR.

O resumo do dashboard aplica o mesmo escopo antes de qualquer agregacao. A resposta de recentes nao inclui `agente_responsavel`, e parametros de periodo invalidos retornam erro de validacao sem revelar dados de outros usuarios.

Sessao e JWT recusam usuarios inativos: uma sessao existente nao permanece valida depois da desativacao do usuario.

## XSS e erros

- Nao expor traceback em producao.
- Nao retornar SQL, secrets, nomes de variaveis internas ou detalhes de infraestrutura.
- Tratar dados vindos do backend como nao confiaveis no frontend.
- Evitar `dangerouslySetInnerHTML` salvo justificativa forte.

## CSV Injection

Exportacoes devem sanitizar celulas que comecem com caracteres perigosos para planilhas:

```text
=
-
+
@
```

Essa protecao deve entrar antes de expor CSV pela API.

## Secrets e logs

- Secrets devem vir de variaveis de ambiente.
- Logs nao devem conter tokens, senhas, `DATABASE_URL`, cookies ou dados sensiveis desnecessarios.
- Produção deve usar HTTPS e cookies seguros.
- URLs reais de Neon nao devem ser exibidas em logs, documentacao ou relatorios.
- Migrations remotas so devem rodar em banco ou branch Neon confirmado como descartavel, salvo operacao de producao explicitamente aprovada.

## CORS e CSRF

CORS usa apenas origens HTTP(S) explicitas e `CORS_ALLOW_CREDENTIALS=True`; wildcard e origem sem esquema sao rejeitados. Em producao, `SPA_ENABLED=True` exige `CORS_ALLOWED_ORIGINS` e `CSRF_TRUSTED_ORIGINS`. CORS e CSRF continuam controles separados.

Simple JWT 5.5.1 nao declara suporte oficial a Python 3.14, Django 6.0 ou DRF 3.17. A compatibilidade foi validada localmente em PostgreSQL 18, mas upgrades dessas quatro pecas exigem repetir os testes de auth antes de producao.

## Rate limiting e cache compartilhado

Login, refresh e bootstrap CSRF usam throttles DRF por IP e retornam `429` com `Retry-After` ao exceder o limite. O backend padrao e `LocMemCache`, adequado apenas para desenvolvimento ou uma unica instancia de processo.

O deploy pode configurar qualquer backend de cache Django por `CACHE_BACKEND`, `CACHE_LOCATION` e `CACHE_TIMEOUT`. Quando houver mais de um processo ou replica, o deploy deve fornecer um backend realmente compartilhado e ativar `REQUIRE_SHARED_THROTTLE_CACHE=True`; a configuracao de producao recusa os backends locais conhecidos nesse modo. A escolha e as credenciais do cache pertencem a infraestrutura e nao sao versionadas.

`manage.py check --deploy` alerta enquanto `SECURE_HSTS_INCLUDE_SUBDOMAINS` e `SECURE_HSTS_PRELOAD` permanecem falsos. Esses valores so devem ser ativados depois de confirmar que todos os subdominios atendem exclusivamente por HTTPS e que a inclusao na lista de preload e desejada; essa confirmacao faz parte da checklist de go-live.

## RLS, privilegios e recuperacao

RLS PostgreSQL nao esta habilitado. A aplicacao usa uma unica credencial de banco e o contexto do usuario autenticado nao e propagado de modo seguro por conexao/transacao, especialmente na presenca de pooling. Assim, policies por usuario seriam uma falsa protecao nesta arquitetura. Ownership no ORM continua obrigatorio; uma futura adocao de RLS exige credenciais runtime separadas das de migration, contexto transacional de usuario e testes PostgreSQL das policies.

Antes do go-live, a operacao deve definir backup automatizado do PostgreSQL, retencao, responsavel, teste periodico de restore e procedimento de incidente. O usuario runtime deve receber somente privilegios de aplicacao; migrations devem usar uma credencial de deploy separada e temporaria. Sem estrategia de backup/restore validada, o release fica bloqueado.

## Dependencias

Dependencias devem ser atualizadas de forma controlada, com testes e changelog quando houver risco.

## Checklist por feature

Antes de concluir uma feature:

- rotas exigem autenticacao quando necessario;
- queryset e objeto sao escopados pelo usuario;
- recurso alheio nao vaza existencia;
- serializers validam campos e choices;
- constraints de banco protegem responsavel, choices e unicidade essencial;
- erros seguem contrato;
- logs nao expõem dados sensiveis;
- testes cobrem usuario anonimo, usuario dono e outro usuario;
- exportacoes sanitizam CSV;
- endpoints mutaveis usam metodo HTTP correto;
- filtros invalidos sao tratados de modo consistente.
