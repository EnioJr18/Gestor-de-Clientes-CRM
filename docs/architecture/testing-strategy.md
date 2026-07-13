# Estrategia de Testes

## Backend

Categorias:

- settings;
- models;
- forms atuais;
- views atuais;
- autenticacao;
- isolamento por usuario;
- CSV;
- dashboard;
- serializers futuros;
- permissions;
- services;
- selectors;
- endpoints;
- integracao;
- regressao;
- seguranca.

## Casos obrigatorios

Nao testar apenas caminho feliz. Cobrir:

- campo ausente;
- campo vazio;
- formato invalido;
- tipo invalido;
- choice invalido;
- valor muito longo;
- recurso inexistente;
- recurso de outro usuario;
- usuario nao autenticado;
- metodo nao permitido;
- conflito;
- falha controlada;
- edge cases de datas;
- paginacao invalida;
- filtros invalidos;
- CSV Injection;
- dados nulos;
- ausencia de vazamento de informacao.

## Testes de caracterizacao

Antes de refatorar views, dominio ou templates, criar testes que descrevam o comportamento atual:

- login/logout/cadastro;
- perfil;
- CRUD de leads;
- filtros e busca atuais;
- criacao, edicao e exclusao de interacoes;
- dashboard;
- exportacao CSV;
- isolamento entre usuario A e usuario B.

Esses testes podem inicialmente refletir bugs conhecidos. A correcao deve acontecer em sprint posterior, com ajuste explicito do comportamento esperado.

## Fixtures e factories

Futuramente o backend devera usar factories para:

- usuarios;
- leads;
- interacoes.

Evitar fixtures JSON rigidas para a maior parte dos testes.

Factories devem permitir:

- usuario A;
- usuario B;
- lead de A;
- lead de B;
- status variados;
- prioridades variadas;
- datas controladas.

Nao instalar Factory Boy nesta sprint.

## Frontend

Ferramentas planejadas:

- Vitest;
- React Testing Library;
- MSW;
- testes por comportamento;
- acessibilidade essencial.

Cobrir:

- formularios;
- validacoes;
- loading;
- empty state;
- error state;
- sucesso;
- falha da API;
- sessao expirada;
- rota protegida;
- invalidacao de queries;
- filtros na URL.

Nao testar detalhes internos de bibliotecas.

Exemplo de comportamento:

> Apos criar um lead, a listagem deve exibir o novo registro sem recarregar a pagina.

## Piramide inicial

- Muitos testes unitarios/integrais de backend para dominio e API.
- Testes de views/templates atuais enquanto o monolito existir.
- Testes de frontend focados em comportamento de usuario.
- Poucos testes end-to-end, para fluxos criticos.
