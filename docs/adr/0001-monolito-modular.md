# ADR 0001 - Monolito modular

## Status

Aceito

## Contexto

O projeto atual e um monolito Django Templates pequeno, com um app principal chamado `leads`. A evolucao planejada inclui Django REST Framework, PostgreSQL/Neon e frontend React separado.

Microservicos adicionariam custo operacional sem necessidade atual.

## Decisao

Manter Django e evoluir para um monolito modular com DRF, separando responsabilidades por dominio:

- accounts;
- leads;
- interactions;
- dashboard;
- reports;
- common apenas para recursos compartilhados reais.

## Alternativas consideradas

- Microservicos por dominio: rejeitado por complexidade operacional.
- Manter tudo em um app unico: rejeitado por limitar manutencao e API futura.
- Repository generico sobre ORM: rejeitado por duplicar o Django ORM sem ganho claro.

## Consequencias

- Menor custo de migracao.
- Melhor separacao de responsabilidades.
- Exige disciplina para nao criar dependencias circulares.
- Permite evoluir para DRF sem reescrever tudo de uma vez.
