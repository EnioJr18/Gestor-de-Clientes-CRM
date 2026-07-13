# Estrategia de Seguranca

## Regra central

Todo recurso de negocio deve estar associado ao usuario autenticado, direta ou indiretamente.

Modelo atual:

```text
Lead.agente_responsavel = usuario autenticado
Interaction.lead.agente_responsavel = usuario autenticado
```

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

## CORS e CSRF

CORS deve ser restrito ao frontend autorizado. CSRF depende da estrategia final de JWT/cookies. Se refresh token for cookie `HttpOnly`, CSRF precisa ser tratado explicitamente.

## Dependencias

Dependencias devem ser atualizadas de forma controlada, com testes e changelog quando houver risco.

## Checklist por feature

Antes de concluir uma feature:

- rotas exigem autenticacao quando necessario;
- queryset e objeto sao escopados pelo usuario;
- recurso alheio nao vaza existencia;
- serializers validam campos e choices;
- erros seguem contrato;
- logs nao expõem dados sensiveis;
- testes cobrem usuario anonimo, usuario dono e outro usuario;
- exportacoes sanitizam CSV;
- endpoints mutaveis usam metodo HTTP correto;
- filtros invalidos sao tratados de modo consistente.
