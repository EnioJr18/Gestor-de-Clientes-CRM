# ADR 0004 - Isolamento de dados por usuario

## Status

Aceito

## Contexto

O projeto atual associa `Lead` ao usuario por `agente_responsavel`. `Interaction` pertence a um `Lead`, entao seu escopo vem de `lead.agente_responsavel`.

O README antigo usa a expressao multi-tenant, mas o sistema nao possui organizacoes, memberships ou roles.

## Decisao

Formalizar o modelo atual como isolamento por usuario, nao multi-tenancy real.

Querysets devem nascer escopados:

```python
Lead.objects.filter(agente_responsavel=request.user)
```

Recursos de outro usuario devem preferencialmente responder como nao encontrados.

## Alternativas consideradas

- Chamar o modelo atual de multi-tenant: rejeitado por imprecisao.
- Adicionar organizacoes agora: rejeitado por falta de necessidade confirmada.
- Buscar objeto global e validar depois: rejeitado por maior risco de IDOR.

## Consequencias

- Permissoes e querysets ficam mais consistentes.
- Testes devem cobrir usuario dono e outro usuario.
- Organizacoes continuam como decisao futura, nao antecipada.
