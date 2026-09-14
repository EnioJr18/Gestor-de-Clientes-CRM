# CRM.Pro

CRM para organizacao de leads, acompanhamento de interacoes e visao comercial em um so lugar.

## 📌 Visão geral

O CRM.Pro centraliza o acompanhamento de relacionamentos comerciais. A aplicacao permite que cada usuario organize seus leads, registre interacoes e acompanhe indicadores do proprio funil em uma interface web responsiva.

## Demonstração

- Frontend em producao: [gestor-de-clientes-crm.vercel.app](https://gestor-de-clientes-crm.vercel.app)
- API health check: [crm-pro-api-b86l.onrender.com/api/v1/health/](https://crm-pro-api-b86l.onrender.com/api/v1/health/)
- Documentacao OpenAPI: [crm-pro-api-b86l.onrender.com/api/docs/](https://crm-pro-api-b86l.onrender.com/api/docs/)

O frontend esta publicado na Vercel e a API Django esta publicada no Render, usando PostgreSQL hospedado no Neon.

## ✨ Principais funcionalidades

- Autenticacao, cadastro de usuarios e encerramento de sessao.
- Gerenciamento do proprio perfil e alteracao de senha.
- Dashboard com metricas, graficos e resumo comercial por periodo.
- CRUD de leads com busca, filtros, ordenacao e paginacao.
- Registro de interacoes em timeline por lead.
- Isolamento de dados por usuario e protecao contra acesso cruzado.
- Validacoes de entrada e mensagens de erro consistentes.
- API REST documentada com OpenAPI, Swagger UI e ReDoc.

## 🛠️ Tecnologias

### Frontend

- React, TypeScript e Vite
- Tailwind CSS
- TanStack Query
- React Hook Form e Zod
- Axios e React Router
- Chart.js e Lucide React
- Vitest, Testing Library e MSW

### Backend

- Python e Django
- Django REST Framework
- PostgreSQL
- Simple JWT
- drf-spectacular e django-filter

### Infraestrutura

- Docker e Docker Compose
- GitHub Actions
- Vercel
- Render
- Neon

## 🧱 Arquitetura

```text
Vercel
  |
  v
React / Vite
  | HTTPS
  v
Render
  |
  v
Django / Django REST Framework
  |
  v
Neon PostgreSQL
```

Frontend e backend sao projetos separados no mesmo repositorio. A SPA consome a API REST por HTTPS e a producao utiliza PostgreSQL. O container do backend aplica migrations antes de iniciar o Gunicorn, para que o schema seja atualizado de forma controlada no deploy.

## 🛡️ Seguranca

- Autenticacao JWT com refresh token em cookie `HttpOnly`.
- CSRF aplicado aos fluxos baseados em cookie.
- CORS com origens explicitas.
- Cookies seguros em producao.
- Ownership por usuario e protecao contra IDOR nos recursos da API.
- Validacao de payloads e limites de requisicao nos endpoints sensiveis.
- Segredos e configuracoes de ambiente fornecidos por variaveis de ambiente.

Nenhum valor sensivel e versionado no repositorio.

## Qualidade

- 281 testes no backend, com PostgreSQL no fluxo de testes e CI.
- 71 testes no frontend.
- Typecheck, lint e build da SPA.
- Validacao de migrations, `manage.py check` e schema OpenAPI.
- Pipeline GitHub Actions para pull requests e branches `main` e `develop`.

## Estrutura do projeto

```text
.
|-- backend/                 # Django, DRF, apps e migrations
|-- frontend/                # SPA React/TypeScript/Vite
|-- docs/                    # Arquitetura e decisoes tecnicas
|-- .github/workflows/       # Pipeline de CI
|-- Dockerfile.backend       # Imagem do backend
|-- docker-compose.yml       # Ambiente local com PostgreSQL 18
|-- Dockerfile.postgres
|-- vercel.json              # Configuracao da SPA na Vercel
`-- README.md
```

## Execucao local

### Ambiente completo com Docker

O fluxo recomendado usa Docker Compose e PostgreSQL 18 local.

1. Crie o arquivo de ambiente a partir do exemplo:

   ```bash
   cp .env.example .env
   ```

   No Windows PowerShell, use:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Ajuste os valores locais de `POSTGRES_*` e `SECRET_KEY` em `.env`.

3. Suba a aplicacao:

   ```bash
   docker compose up --build
   ```

4. Acesse `http://localhost:8080`.

O Compose inicia PostgreSQL, aplica migrations pelo servico `migrate`, inicia o backend e publica o frontend. O backend fica disponivel internamente na porta `8000`; o frontend e a unica porta exposta no host.

Para encerrar o ambiente preservando os dados locais:

```bash
docker compose down
```

Use `docker compose down -v` apenas para remover volumes locais comprovadamente descartaveis.

### Frontend fora do Docker

Para executar somente a SPA contra uma API local, crie `frontend/.env` a partir de `frontend/.env.example`, instale as dependencias e inicie o Vite:

```bash
cd frontend
npm ci
npm run dev
```

`VITE_API_BASE_URL` deve apontar para a API local, por exemplo `http://localhost:8000/api/v1`.

### 🧪 Testes e validacoes

Com a stack Docker disponivel:

```bash
docker compose --profile test run --rm backend-tests
docker compose --profile test run --rm frontend-tests
```

Validacoes do frontend fora do Docker:

```bash
cd frontend
npm run test:run
npm run typecheck
npm run lint
npm run build
```

## Deploy

```text
GitHub -> Vercel  -> frontend React/Vite
GitHub -> Render  -> backend Django/DRF
Render -> Neon    -> PostgreSQL
```

O Vercel gera e publica os arquivos estaticos da SPA. O Render constroi a imagem Docker do backend, executa as migrations no startup controlado do container e inicia o Gunicorn. O backend usa a `DATABASE_URL` configurada no ambiente para se conectar ao Neon.

## Status

Projeto em desenvolvimento ativo e publicado em producao.

## 🤝 Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## 📄 Licenca

Distribuido sob a licenca MIT. Consulte [LICENSE](LICENSE).

## Autor

Desenvolvido por **Enio Jr** para fins de estudo e portfólio 💻

📧 Entre em contato: eniojr100@gmail.com <br>
🔗 LinkedIn: https://www.linkedin.com/in/enioeduardojr/ <br>
📷 Instagram: https://www.instagram.com/enio_juniorrr/ <br>