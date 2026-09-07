# Migração Cloudflare

Esta pasta contém a preparação para executar a API da clínica em Cloudflare Workers com Cloudflare D1.

## Estado atual

- `schema.sql` reproduz as tabelas usadas pela aplicação atual.
- `wrangler.toml` define o Worker e o binding D1.
- `src/index.js` contém a API migrada para Workers + D1: autenticação, usuários, pacientes, médicos, consultas, cancelamentos, avisos e laudos editáveis.
- O banco local usado nos testes foi limpo. O banco remoto deve ser criado vazio no primeiro deploy.
- O backend FastAPI/PostgreSQL original continua preservado como referência até a validação em produção.

## Próximas etapas

1. Criar o banco D1 e substituir `database_id` em `wrangler.toml`.
2. Executar `schema.sql` remotamente e definir `SECRET_KEY` como secret do Worker.
3. Publicar o Worker e copiar a URL gerada.
4. Configurar `REACT_APP_API_URL` no Cloudflare Pages.
5. Executar os testes de integração e publicar o frontend.

## Publicação

```bash
cd cloudflare
npm install
npx wrangler login
npx wrangler d1 create clinica-db
# copie o database_id retornado para wrangler.toml
npx wrangler d1 execute clinica-db --remote --file=schema.sql
npx wrangler secret put SECRET_KEY
npx wrangler deploy
```

No Cloudflare Pages, importe o repositório `rvavila/Clinica`, use `frontend` como diretório raiz, `npm run build` como comando e `build` como diretório de saída. Configure `REACT_APP_API_URL` com a URL do Worker antes da publicação.

## Alternativa sem conexão Git do Pages

Se o painel do Pages continuar mostrando `Missing git connection`, o workflow `.github/workflows/deploy-cloudflare.yml` publica o Worker e o Pages diretamente pelo GitHub Actions. Nesse caso, crie o projeto Pages uma vez:

```bash
npx wrangler pages project create clinica
```

Depois, adicione em **Settings > Secrets and variables > Actions** do GitHub:

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`
- `REACT_APP_API_URL` (a URL publicada do Worker)

O workflow será executado a cada push na `main` e não depende da conexão Git integrada do painel Pages.

Nunca coloque valores reais de `SECRET_KEY`, senhas ou tokens neste repositório.
