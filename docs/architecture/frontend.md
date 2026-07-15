# Arquitetura do Frontend

## Estilo

O frontend e uma SPA separada com React, TypeScript, Vite e Tailwind CSS. A organizacao por features mantem codigo de dominio proximo de seus componentes, hooks, schemas, tipos e chamadas de API.

Stack planejada:

- React;
- TypeScript;
- Vite;
- Tailwind CSS;
- React Router;
- TanStack Query;
- Axios;
- React Hook Form;
- Zod;
- Lucide React;
- date-fns;
- Chart.js ou react-chartjs-2;
- Zustand somente se houver necessidade real.

## Estrutura-alvo

```text
frontend/
  src/
    app/
      router/
      providers/
      config/
    features/
      auth/
      leads/
      interactions/
      dashboard/
      profile/
      reports/
    components/
      ui/
      layout/
    lib/
      api/
      query/
      validation/
      date/
    hooks/
    types/
    styles/
    main.tsx
```

## Organizacao por features

Cada feature pode conter:

```text
features/leads/
  api/
  components/
  hooks/
  pages/
  schemas/
  types/
  utils/
```

Nem toda subpasta deve ser criada antecipadamente. Criar apenas quando houver uso real.

## Leads na Sprint 11

`features/leads` implementa CRUD visual com Zod, React Hook Form, TanStack Query e Axios centralizado. Busca, filtros, ordenacao e paginacao ficam em `useSearchParams`; dialogs atendem criacao/edicao/exclusao e a pagina de detalhe cobre 404. Nenhum token e persistido e Zustand continua ausente.

## Componentes compartilhados

`components/ui` deve conter apenas componentes reutilizaveis:

- Button;
- Input;
- Select;
- Modal;
- Table;
- Pagination;
- EmptyState;
- ErrorState;
- LoadingState.

`components/layout` deve conter:

- AppLayout;
- Sidebar;
- Header;
- MobileNavigation.

Nao criar componente global antes de existir reutilizacao real.

## Estado remoto

TanStack Query sera responsavel por dados vindos da API, cache, refetch, invalidacao, mutations, loading, errors, paginacao, filtros remotos e sincronizacao com backend.

Query keys iniciais:

```ts
["leads"]
["leads", filters]
["lead", leadId]
["lead-interactions", leadId, filters]
["dashboard", period]
["profile"]
```

Invalidacoes:

- Criar lead: invalidar `["leads"]` e `["dashboard"]`.
- Editar lead: invalidar `["lead", id]`, `["leads"]` e `["dashboard"]`.
- Criar interacao: invalidar `["lead-interactions", leadId]` e `["dashboard"]`.

Nao usar reload de pagina para atualizar dados.

## Estado local

`useState` deve ser usado para modal, dropdown, sidebar movel, selecao temporaria e estado local simples.

Zustand nao foi instalado na fundacao. Entrara somente se houver estado global de interface, preferencia persistente, multiplas features dependendo do mesmo estado local ou necessidade nao resolvida por Context, URL ou TanStack Query.

Zustand nao deve duplicar dados da API.

## URL como estado

Filtros relevantes devem preferencialmente estar na URL:

```text
/leads?search=maria&status=NOVO&page=2
```

Beneficios:

- compartilhamento;
- voltar/avancar do navegador;
- refresh preserva filtros;
- menor dependencia de estado global.

## Formularios

React Hook Form sera usado para estado de formulario. Zod sera usado para validacao no cliente, mensagens e transformacao do payload.

A validacao do frontend melhora a experiencia, mas nunca substitui a validacao do backend.

## Axios

Uma instancia centralizada deve existir em:

```text
src/lib/api/client.ts
```

Responsavel por base URL, credenciais, headers, timeout, interceptors, refresh e normalizacao de erros.

Chamadas Axios nao devem ficar espalhadas em componentes. Devem viver em `features/<feature>/api/` ou em camada compartilhada quando realmente global.

## Autenticacao da SPA

- Manter o access token apenas em memoria e enviá-lo como `Authorization: Bearer <token>`.
- Usar `withCredentials` somente nos endpoints de auth que dependem dos cookies de refresh/CSRF.
- Obter CSRF em `GET /api/v1/auth/csrf/` e enviar `X-CSRFToken` no refresh e logout.
- Nunca ler nem persistir o refresh token: o backend o mantem em cookie HttpOnly.
- Serializar tentativas de refresh; duas requisicoes concorrentes com o mesmo refresh fazem a primeira vencer e a segunda falhar apos a blacklist.
- Ao recarregar a pagina, recuperar uma sessao da SPA por um unico refresh controlado, sem `localStorage` para access token.

Implementacao da Sprint 10:

- `AuthProvider` usa Context para usuario e estado de bootstrap;
- access token vive somente no modulo `tokenStore` em memoria;
- uma unica `refreshPromise` serializa renovacoes concorrentes;
- Axios repete cada requisicao no maximo uma vez e nao tenta renovar endpoints de auth;
- respostas criticas de login, refresh, CSRF, usuario e erro sao validadas com Zod;
- TanStack Query gerencia dados remotos, sem guardar a sessao inteira no cache;
- `/login`, `/app`, rota protegida, rota publica e 404 formam o roteamento inicial.

## Tipagem

Separar:

- tipos da API;
- payloads;
- filtros;
- schemas de formulario;
- erros;
- paginacao.

Exemplo:

```ts
type LeadResponse = {
  id: number;
  nome: string;
  email: string;
  status: LeadStatus;
  prioridade: LeadPriority;
  criado_em: string;
};

type CreateLeadPayload = {
  nome: string;
  email: string;
  status: LeadStatus;
  prioridade: LeadPriority;
};
```

Estrategia inicial: manter o formato da API no client e transformar apenas quando houver ganho real. Evitar transformacoes automaticas invisiveis em todo o sistema.
