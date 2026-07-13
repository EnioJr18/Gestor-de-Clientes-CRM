# Falhas conhecidas da Sprint 3

Este arquivo registra bugs confirmados por testes de caracterizacao. Eles nao foram corrigidos nesta sprint.

## KF-001 - Filtro de prioridade alta usa valor minusculo

- Severidade: media
- Teste atual: `leads.tests.test_filters_and_pagination.ShortcutFilterTests.test_high_priority_route_current_behavior_uses_lowercase_and_returns_empty`
- Teste esperado: `leads.tests.test_filters_and_pagination.ShortcutFilterTests.test_high_priority_route_expected_to_return_uppercase_alta`
- Comportamento atual: a rota `prioridade-alta/` filtra por `prioridade='alta'` e retorna lista vazia.
- Comportamento esperado: retornar leads do usuario autenticado com `prioridade='ALTA'`.
- Sprint indicada para correcao: Sprint 4.

## KF-002 - Card "Novos Hoje" esta hardcoded como zero

- Severidade: media
- Teste atual: `leads.tests.test_dashboard.DashboardCharacterizationTests.test_dashboard_current_template_hardcodes_new_leads_today_zero`
- Teste esperado: `leads.tests.test_dashboard.DashboardCharacterizationTests.test_dashboard_expected_to_count_new_leads_today`
- Comportamento atual: o template do dashboard exibe `0` para "Novos Hoje" mesmo quando existem leads criados hoje.
- Comportamento esperado: calcular leads criados no periodo esperado para o usuario autenticado.
- Sprint indicada para correcao: Sprint 4.

## KF-003 - Exportacao CSV de leads permite CSV Injection

- Severidade: alta
- Teste atual: `leads.tests.test_csv_exports.LeadCsvExportTests.test_csv_injection_currently_outputs_dangerous_values`
- Teste esperado: `leads.tests.test_csv_exports.LeadCsvExportTests.test_csv_injection_expected_to_prefix_dangerous_values`
- Comportamento atual: campos iniciados por `=`, `+`, `-`, `@` ou tabulacao saem sem neutralizacao.
- Comportamento esperado: prefixar ou sanitizar valores perigosos antes de escrever no CSV.
- Sprint indicada para correcao: Sprint 4.

## KF-004 - Exportacao CSV de interacoes permite CSV Injection

- Severidade: alta
- Teste atual: `leads.tests.test_csv_exports.InteractionCsvExportTests.test_interaction_csv_injection_currently_outputs_dangerous_note`
- Teste esperado: `leads.tests.test_csv_exports.InteractionCsvExportTests.test_interaction_csv_injection_expected_to_prefix_dangerous_note`
- Comportamento atual: notas iniciadas por formula saem sem neutralizacao.
- Comportamento esperado: prefixar ou sanitizar valores perigosos antes de escrever no CSV.
- Sprint indicada para correcao: Sprint 4.
