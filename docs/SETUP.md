# Guia de Instalação e Configuração

## Pré-requisitos

- Python 3.9+
- Node.js 16+ e npm
- PostgreSQL 12+
- Git

## Setup Backend

### 1. Clonar repositório e entrar na pasta
```bash
cd backend
```

### 2. Criar ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar banco de dados
Crie um arquivo `.env` baseado em `.env.example`:
```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais:
```
DATABASE_URL=postgresql://usuario:senha@localhost:5432/clinica
SECRET_KEY=sua-chave-secreta-super-segura-aqui
```

### 5. Criar banco de dados
```bash
# Se usando PostgreSQL
createdb clinica -U usuario
```

### 6. Iniciar servidor
```bash
uvicorn app.main:app --reload
```

O servidor estará em: `http://localhost:8000`
Documentação: `http://localhost:8000/docs`

## Setup Frontend

### 1. Entrar na pasta do frontend
```bash
cd frontend
```

### 2. Instalar dependências
```bash
npm install
```

### 3. Configurar variáveis de ambiente
```bash
cp .env.example .env
```

Edite `.env`:
```
REACT_APP_API_URL=http://localhost:8000
```

### 4. Iniciar servidor de desenvolvimento
```bash
npm start
```

A aplicação estará em: `http://localhost:3000`

## Usando Docker

### Backend com Docker
```bash
docker build -t clinica-backend ./backend
docker run -p 8000:8000 --env-file .env clinica-backend
```

### Frontend com Docker
```bash
docker build -t clinica-frontend ./frontend
docker run -p 3000:3000 clinica-frontend
```

### Docker Compose (completo)
```bash
docker-compose up
```

## Variáveis de Ambiente

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/clinica
SECRET_KEY=chave-super-secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
APP_NAME=Clínica Médica API
DEBUG=True
CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001"]
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_NAME=Clínica Médica
```

## Testando a API

### Registrar novo usuário
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@email.com",
    "full_name": "João Silva",
    "cpf": "12345678901",
    "password": "senha123",
    "role": "patient"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@email.com",
    "password": "senha123"
  }'
```

## Endpoints Principais

### Autenticação
- `POST /api/auth/register` - Registrar novo usuário
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Informações do usuário autenticado

### Usuários
- `GET /api/users` - Listar usuários (apenas ADMIN)
- `GET /api/users/{user_id}` - Obter usuário
- `PUT /api/users/{user_id}` - Atualizar usuário

### Médicos
- `GET /api/doctors` - Listar médicos
- `GET /api/doctors/{doctor_id}` - Obter médico
- `POST /api/doctors` - Criar médico (apenas ADMIN/DOCTOR)
- `PUT /api/doctors/{doctor_id}` - Atualizar médico

### Pacientes
- `GET /api/patients` - Listar pacientes
- `GET /api/patients/{patient_id}` - Obter paciente
- `POST /api/patients` - Criar paciente
- `PUT /api/patients/{patient_id}` - Atualizar paciente

### Agendamentos
- `GET /api/appointments` - Listar agendamentos
- `GET /api/appointments/{appointment_id}` - Obter agendamento
- `POST /api/appointments` - Criar agendamento
- `PUT /api/appointments/{appointment_id}` - Atualizar agendamento
- `POST /api/appointments/{appointment_id}/cancel` - Cancelar agendamento

## Resolução de Problemas

### Erro de conexão com banco de dados
- Verifique se PostgreSQL está rodando
- Verifique as credenciais em `.env`
- Certifique-se de que o banco de dados foi criado

### Erro de CORS
- Verifique se a URL do frontend está em `CORS_ORIGINS`

### Token inválido
- Certifique-se de que `SECRET_KEY` é o mesmo em todas as instâncias

## Produção

### Backend
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
npm run build
# Servir com nginx ou outro servidor web
```

Veja `docker-compose.prod.yml` para configuração de produção.
