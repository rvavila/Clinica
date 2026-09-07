# Migração Cloudflare

Esta pasta contém a preparação para executar a API da clínica em Cloudflare Workers com Cloudflare D1.

## Estado atual

- `schema.sql` reproduz as tabelas usadas pela aplicação atual.
- `wrangler.toml` define o Worker e o binding D1.
- O backend FastAPI/PostgreSQL original continua preservado até a nova API ser validada.

## Próximas etapas

1. Criar o banco D1 e substituir `database_id` em `wrangler.toml`.
2. Portar autenticação, usuários, pacientes, médicos, consultas, laudos e avisos para o Worker.
3. Configurar `REACT_APP_API_URL` no Cloudflare Pages.
4. Executar os testes de integração e publicar a API.

Nunca coloque valores reais de `SECRET_KEY`, senhas ou tokens neste repositório.
