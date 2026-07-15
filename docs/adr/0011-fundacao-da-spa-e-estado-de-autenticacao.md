# ADR 0011 - Fundacao da SPA e estado de autenticacao

## Status

Aceita na Sprint 10.

## Contexto

O backend ja oferece login JWT, refresh HttpOnly rotativo, logout com blacklist, CSRF e `users/me`. A SPA precisa consumir esse contrato sem persistir credenciais acessiveis ao JavaScript e sem antecipar as features completas do CRM.

## Decisao

- Criar a SPA com React, TypeScript, Vite e Tailwind CSS.
- Organizar o codigo por features e manter infraestrutura compartilhada em `src/lib`.
- Manter o access token somente em uma variavel de modulo em memoria.
- Manter usuario e estado de bootstrap em Context, sem Zustand.
- Obter CSRF e usar o refresh cookie HttpOnly para restaurar a sessao apos reload.
- Compartilhar uma unica promessa durante refreshes concorrentes.
- Repetir requisicoes 401 no maximo uma vez e nunca renovar login, CSRF, refresh ou logout.
- Usar TanStack Query para dados remotos, sem transformar seu cache em armazenamento da sessao.
- Validar respostas criticas com Zod e normalizar erros antes de exibi-los.

## Consequencias

Recarregar a pagina perde o access token por design e gera uma rotacao de refresh durante o bootstrap. O frontend deve continuar serializando renovacoes para evitar corrida de blacklist. Fechar ou recarregar a aba nao grava access token em `localStorage` nem `sessionStorage`.

A primeira interface cobre apenas login, logout, rota protegida, saudacao e placeholders. CRUD visual de leads, dashboard completo, graficos, perfil e relatorios permanecem fora desta decisao.
