# ADR 0006 - Services e selectors

## Status

Aceito

## Contexto

O codigo atual concentra regras e consultas em views. A evolucao para API pode se beneficiar de services e selectors, mas criar camadas vazias ou genericas aumentaria complexidade sem ganho.

## Decisao

Criar services apenas para operacoes de negocio com regra real, transacao, mudanca de estado reutilizavel, auditoria, integracao externa ou efeito colateral.

Criar selectors para consultas complexas, agregadas, reutilizaveis ou otimizadas.

Nao criar repository generico sobre o Django ORM.

## Alternativas consideradas

- Services para todo CRUD: rejeitado por excesso de indirecao.
- Toda consulta dentro de views/viewsets: rejeitado para dashboard e relatorios complexos.
- Repository generico: rejeitado por duplicar a API do ORM.

## Consequencias

- CRUD simples pode ficar em serializer/viewset.
- Dashboard e relatorios tendem a usar selectors.
- Operacoes transacionais ficam mais testaveis em services.
- A equipe precisa justificar novas abstracoes.
