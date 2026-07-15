# 🚀 CRM.Pro - Sistema de Gestão de Clientes

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.0-092E20?style=for-the-badge&logo=django&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)
![Status](https://img.shields.io/badge/Development%2520Status-Active-green?style=for-the-badge&logo=github&label=Status)

Sistema de Gestão de Relacionamento com Clientes (CRM) desenvolvido com **Django**. Focado em produtividade, organização de leads e acompanhamento de métricas de vendas. O projeto oferece uma interface elegante (Dark Mode) e isolamento de dados por usuário, funcionando como um SaaS (Software as a Service).

---

## 📸 Vídeo Demonstração
![Image](https://github.com/user-attachments/assets/b3bf4080-0c75-497e-a54f-9dd092621988)

## ✨ Funcionalidades Principais

- **🔐 Autenticação Segura:** Sistema completo de Login/Cadastro e Recuperação de Senha.
- **🛡️ Multi-Tenant (Isolamento de Dados):** Cada usuário vê apenas os seus próprios leads. Acesso cruzado é bloqueado.
- **🌑 UI/UX Moderna:** Interface responsiva com tema **Dark/Cyberpunk**, Sidebar fixa e componentes Bootstrap customizados.
- **📊 Dashboard Interativo:** Gráficos em tempo real (Chart.js) para análise de Status e Prioridade.
- **📝 Gestão de Leads (CRUD):** CRUD completo (Criar, Listar, Editar, Excluir) com segurança por usuário.
- **⚙️ Perfil de Usuário:** Área para atualização de dados cadastrais.
- **🗄 Histórico de Interações:** Registro detalhado de contatos com cada cliente.
- **📈 Exportação de Dados:** Relatórios em CSV para análise externa.

## 🛠️ Tecnologias Utilizadas

- **Back-end e Core:** Python, Django 5.
- **Front-end:** HTML5, CSS3, Bootstrap 5 e Chart.js.
- **Banco de Dados:** SQLite (Desenvolvimento) / PostgreSQL (Planejado para Produção).
- **DevOps & Deploy:** Render, WhiteNoise, Gunicorne Git & GitHub.
- **Qualidade:** Class Based Views, Crispy Forms, Testes Automatizados

## Arquitetura

A documentacao arquitetural esta disponivel em `docs/architecture/`.
As principais decisoes estao registradas em `docs/adr/`.
Estrutura resumida:

```text
CRM_Portfolio/
├── backend/
│   ├── apps/
│   │   └── leads/
│   ├── config/
│   ├── manage.py
│   └── requirements.txt
├── docs/
└── frontend/  # SPA React + TypeScript
```

## API REST

A API v1 esta disponivel em:

```text
/api/v1/health/
/api/v1/auth/csrf/
/api/v1/auth/login/
/api/v1/auth/refresh/
/api/v1/auth/logout/
/api/v1/users/me/
/api/v1/leads/
/api/schema/
/api/docs/
/api/redoc/
```

A API aceita JWT Bearer para a SPA React e preserva sessao Django para o frontend legado. O access token curto fica somente em memoria no browser; o refresh token fica em cookie HttpOnly, rotaciona a cada uso e e revogado por blacklist. Refresh e logout exigem CSRF.

Origens CORS sao explicitas em `CORS_ALLOWED_ORIGINS`; wildcard nao e aceito. Configure separadamente `CSRF_TRUSTED_ORIGINS` para origens autorizadas a enviar cookies.

### 🌐 Demo Online
Você pode testar o sistema funcionando em tempo real clicando no link abaixo:

👉 **[Acessar CRM Online (Render)](https://gestor-de-relacionamento-crm.onrender.com)**

*(Nota: Como o servidor é gratuito, pode levar alguns segundos para "acordar" no primeiro acesso).*

---

## 🚀 Como rodar o projeto localmente

### Pré-requisitos
* Python instalado
* Conta no Neon (ou PostgreSQL local)

### Passo a Passo

1.  **Clone o repositório**
    ```bash
    git clone https://github.com/EnioJr18/Gestor-de-Clientes-CRM.git
    cd crm-portfolio
    ```

2.  **Crie e ative o ambiente virtual**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Instale as dependências**
    ```bash
    pip install -r backend/requirements.txt
    ```

4.  **Inicie o PostgreSQL local**
    ```bash
    docker compose up -d postgres
    docker compose ps
    ```

    Para parar o banco local:
    ```bash
    docker compose stop postgres
    ```

    Para apagar o volume local descartavel:
    ```bash
    docker compose down -v
    ```
5.  **Configure as Variáveis de Ambiente**
    Crie um arquivo `.env` na raiz do projeto. O backend carrega esse arquivo a partir da raiz do repositorio:
    ```env
    SECRET_KEY=sua_chave_secreta
    DEBUG=True
    USE_SQLITE=False
    DATABASE_URL=postgresql://crm_user:crm_password@localhost:5432/crm_pro
    TEST_DATABASE_URL=postgresql://crm_user:crm_password@localhost:5432/crm_pro_test
    ```

6.  **Execute as Migrations**
    ```bash
    python backend/manage.py migrate
    ```

7.  **Crie um Superusuário (para acessar o Admin, opcional)**
    ```bash
    python backend/manage.py createsuperuser
    ```

8.  **Inicie o servidor**
    ```bash
    python backend/manage.py runserver
    ```

    Alternativamente, entre na pasta `backend/` e execute `python manage.py runserver`.

9.  **Execute os testes**
    ```bash
    python backend/manage.py test -v 2
    ```

10. **Acesse**
http://127.0.0.1:8000/

## SPA React

Configure `frontend/.env` a partir de `frontend/.env.example`, mantendo o backend em `http://localhost:8000` e liberando `http://localhost:5173` nas variaveis `CORS_ALLOWED_ORIGINS` e `CSRF_TRUSTED_ORIGINS` do backend.

```bash
cd frontend
npm install
npm run dev
```

Validacao do frontend:

```bash
npm run lint
npm run typecheck
npm run test:run
npm run build
```

### Gestao visual de leads

A SPA possui login JWT com access token somente em memoria e refresh em cookie HttpOnly. Apos autenticar, use `/app/leads` para listar, buscar, filtrar, ordenar, paginar, criar, editar, visualizar e excluir leads sem recarregar a pagina. Os filtros permanecem na URL.

Configure `frontend/.env` com:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Use `localhost` de forma consistente no backend e no Vite para que CORS, CSRF e o cookie de refresh tenham a mesma origem esperada. O PostgreSQL local e iniciado com `docker compose up -d postgres`; crie um administrador com `python backend/manage.py createsuperuser`.

Estado atual: autenticacao SPA e gestao de leads estao implementadas. Dashboard completo, interacoes, perfil editavel, relatorios e exportacao permanecem pendentes.



## 🤝 Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---
Desenvolvido por **Enio Jr** para fins de estudo e portfólio 💻

📧 Entre em contato: eniojr100@gmail.com <br>
🔗 LinkedIn: https://www.linkedin.com/in/enioeduardojr/ <br>
📷 Instagram: https://www.instagram.com/enio_juniorrr/ <br>
