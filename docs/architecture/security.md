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

## Autenticacao futura

Direcao planejada:

- JWT para SPA;
- access token curto;
- refresh token;
- estrategia final de armazenamento pendente;
- evitar assumir `localStorage` como padrao;
- considerar refresh token em cookie `HttpOnly`;
- CORS e CSRF conforme estrategia final;
- blacklist de refresh se adotada;
- rate limiting;
- tratar usuario inativo;
- endpoint `me`;
- troca e recuperacao de senha.

Decisao pendente: estrategia final de armazenamento e renovacao de tokens.

## API REST atual

A API v1 usa autenticacao por sessao Django nesta fase. O autenticador da API continua aplicando CSRF em escritas autenticadas e retorna contrato JSON padronizado para falhas de autenticacao, permissao e validacao.

Endpoints publicos nesta sprint:

- `GET /api/v1/health/`;
- documentacao OpenAPI em `/api/schema/`, `/api/docs/` e `/api/redoc/`.

Endpoints de dados exigem usuario autenticado. Leads sao sempre filtrados por `agente_responsavel=request.user`; leads alheios retornam 404 para evitar IDOR.

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

CORS deve ser restrito ao frontend autorizado. CORS nao foi adicionado na Sprint 8 porque ainda nao ha SPA em outro origin. CSRF permanece ativo com SessionAuthentication. Quando JWT for introduzido, a estrategia de cookies/tokens devera redefinir a relacao entre CORS e CSRF.

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
