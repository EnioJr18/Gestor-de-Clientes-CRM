# CRM.Pro SPA

Fundacao React + TypeScript da interface do CRM.Pro. Esta etapa cobre autenticacao, bootstrap por refresh HttpOnly, rotas e infraestrutura compartilhada; o CRUD visual de leads ainda nao faz parte do frontend.

## Ambiente

Copie `.env.example` para `.env` e informe uma API v1 valida:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

O backend deve aceitar `http://localhost:5173` em `CORS_ALLOWED_ORIGINS` e `CSRF_TRUSTED_ORIGINS`.

## Comandos

```bash
npm install
npm run dev
npm run lint
npm run typecheck
npm run test:run
npm run build
```

O access token existe somente em memoria. Nao adicionar `localStorage`, `sessionStorage` ou Zustand para persistir autenticacao.
