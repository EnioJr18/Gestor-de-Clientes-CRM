# ADR 0013 - Dashboard analitico, identidade visual e graficos

## Contexto

A SPA precisa de indicadores de leads sem receber dados de outros usuarios ou calcular agregacoes no navegador. O dominio atual ja possui timestamps, status, prioridade e indices de propriedade suficientes para uma primeira entrega.

## Decisao

Manter o dashboard no modulo de API de `leads` e expor `GET /api/v1/dashboard/summary/`. A view exige autenticacao, inicia todas as consultas com `agente_responsavel=request.user` e devolve metricas, distribuicoes, evolucao mensal e no maximo cinco leads recentes.

Os periodos permitidos sao `7d`, `30d`, `90d`, `12m` e `custom`. O periodo custom exige datas ISO inclusivas e aceita no maximo 366 dias. A conversao usa exclusivamente `status=VENDIDO` e a taxa e `vendidos_no_periodo / criados_no_periodo * 100`, com `0.0` quando nao ha criacoes. Status e prioridades ausentes retornam zero na ordem dos choices. As agregacoes ocorrem no PostgreSQL com `Count` e `TruncMonth`; nao ha cache, tabela resumida, Celery ou novo dominio nesta etapa.

## Consequencias

O endpoint preserva o isolamento e evita transferir todos os leads para a SPA. Consultas passam a depender do volume de leads de um usuario; antes de adicionar cache ou pre-agregacoes, o projeto deve observar metricas e planos de execucao em PostgreSQL. A implementacao nao exige migration e nao altera contratos de CRUD de leads. Esta ADR documenta somente o backend; nao afirma que interface ou graficos foram implementados.
