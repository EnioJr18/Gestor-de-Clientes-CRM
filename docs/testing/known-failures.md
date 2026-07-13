# Falhas conhecidas

Este arquivo registra bugs confirmados por testes de caracterizacao e preserva a rastreabilidade das correcoes.

## Falhas abertas

Nenhuma falha conhecida aberta apos a Sprint 4.

## Falhas corrigidas

### KF-001 - Filtro de prioridade alta usa valor minusculo

- Severidade: media
- Status: corrigido na Sprint 4
- Teste de regressao: `apps.leads.tests.test_filters_and_pagination.ShortcutFilterTests.test_high_priority_route_returns_uppercase_alta`
- Comportamento atual: a rota `prioridade-alta/` filtra por `prioridade='alta'` e retorna lista vazia.
- Comportamento esperado: retornar leads do usuario autenticado com `prioridade='ALTA'`.
- Correcao: o filtro passou a usar o valor oficial definido em `Lead.PRIORITY_CHOICES`.

### KF-002 - Card "Novos Hoje" esta hardcoded como zero

- Severidade: media
- Status: corrigido na Sprint 4
- Teste de regressao: `apps.leads.tests.test_dashboard.DashboardCharacterizationTests.test_dashboard_counts_new_leads_today`
- Comportamento atual: o template do dashboard exibe `0` para "Novos Hoje" mesmo quando existem leads criados hoje.
- Comportamento esperado: calcular leads criados no periodo esperado para o usuario autenticado.
- Correcao: a view calcula a metrica com `timezone.localdate()` e filtra por usuario autenticado.

### KF-003 - Exportacao CSV de leads permite CSV Injection

- Severidade: alta
- Status: corrigido na Sprint 4
- Teste de regressao: `apps.leads.tests.test_csv_exports.LeadCsvExportTests.test_csv_injection_prefixes_dangerous_values`
- Comportamento atual: campos iniciados por `=`, `+`, `-`, `@` ou tabulacao saem sem neutralizacao.
- Comportamento esperado: prefixar ou sanitizar valores perigosos antes de escrever no CSV.
- Correcao: todas as celulas exportadas em leads passam por sanitizacao antes da escrita.

### KF-004 - Exportacao CSV de interacoes permite CSV Injection

- Severidade: alta
- Status: corrigido na Sprint 4
- Teste de regressao: `apps.leads.tests.test_csv_exports.InteractionCsvExportTests.test_interaction_csv_injection_prefixes_dangerous_note`
- Comportamento atual: notas iniciadas por formula saem sem neutralizacao.
- Comportamento esperado: prefixar ou sanitizar valores perigosos antes de escrever no CSV.
- Correcao: notas de interacoes exportadas passam pela mesma sanitizacao de CSV.
