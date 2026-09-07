# Clínica Médica - Sistema Profissional Completo

## 🎯 Objetivo

Criar um sistema profissional, escalável e seguro para gerenciamento completo de clínica médica com:
- ✅ Controle de acesso por roles (Médico, Recepção, Paciente, Admin)
- ✅ Agendamento de consultas
- ✅ Prontuário eletrônico (PEP)
- ✅ Gerenciamento de pagamentos
- ✅ Relatórios e estatísticas
- ✅ Autenticação segura com JWT

## 🚀 Quick Start

### Usando Docker Compose (Recomendado)

```bash
# 1. Clonar repositório
cd ~/Desktop/Projetos/Clinica

# 2. Criar arquivo .env
cp .env.example .env

# 3. Iniciar tudo
docker-compose up

# 4. Acessar
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Instalação Manual

#### Backend

```bash
cd backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Editar .env com suas credenciais

# Iniciar servidor
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Configurar .env
cp .env.example .env

# Iniciar servidor
npm start
```

#### Banco de Dados

```bash
# Criar banco PostgreSQL
createdb clinica -U seu_usuario
```

## 📋 Criar Primeiro Usuário

### 1. Registrar como Paciente
```
URL: http://localhost:3000/register
Email: paciente@test.com
CPF: 12345678901
Senha: teste1234
Role: Paciente
```

### 2. Registrar como Médico
```
Email: medico@test.com
CPF: 98765432101
Senha: teste1234
Role: Médico
```

### 3. Registrar como Recepção
```
Email: recepcao@test.com
CPF: 55555555555
Senha: teste1234
Role: Recepção
```

### 4. Registrar como Admin
Use o painel e altere role manualmente no banco (futura feature)

## 🏗️ Estrutura do Projeto

```
clinica/
├── backend/          # API FastAPI + PostgreSQL
├── frontend/         # React Web
├── mobile/           # React Native (futuro)
├── docs/             # Documentação
├── docker-compose.yml
└── README.md
```

## 🔑 Recursos Principais

### 👨‍⚕️ Para Médicos
- Dashboard com agendamentos do dia
- Prontuários eletrônicos
- Consultar histórico de pacientes
- Gerar receitas e atestados
- Gerenciar disponibilidade

### 👨‍💼 Para Recepção
- Gerenciar agendamentos
- Registrar novos pacientes
- Controlar fila de espera
- Processar pagamentos
- Visualizar relatório de ocupação

### 👤 Para Pacientes
- Agendar consultas
- Histórico de consultas
- Visualizar prontuário
- Receber receitas digitais

## 🛠️ Tecnologias

| Camada | Tecnologia |
|--------|-----------|
| **Backend** | FastAPI + PostgreSQL |
| **Frontend Web** | React + Axios |
| **Frontend Mobile** | React Native (futuro) |
| **Autenticação** | JWT + bcrypt |
| **DevOps** | Docker + Docker Compose |

## 📚 Documentação

- [Guia de Instalação](docs/SETUP.md)
- [Arquitetura do Sistema](docs/ARCHITECTURE.md)
- [Documentação da API](docs/API.md)

## 🔐 Segurança

- ✅ Autenticação JWT
- ✅ Senhas com bcrypt
- ✅ Validação CORS
- ✅ RBAC (Role-Based Access Control)
- ✅ Validação de entrada (Pydantic)
- ✅ Proteção contra SQL Injection

## 📊 Endpoints Principais

### Autenticação
```
POST   /api/auth/register          - Registrar usuário
POST   /api/auth/login             - Fazer login
GET    /api/auth/me                - Obter usuário atual
```

### Usuários
```
GET    /api/users                  - Listar usuários (Admin)
GET    /api/users/{id}             - Obter usuário
PUT    /api/users/{id}             - Atualizar usuário
DELETE /api/users/{id}             - Deletar usuário (Admin)
```

### Médicos
```
GET    /api/doctors                - Listar médicos
GET    /api/doctors/{id}           - Obter médico
POST   /api/doctors                - Criar médico
PUT    /api/doctors/{id}           - Atualizar médico
DELETE /api/doctors/{id}           - Deletar médico (Admin)
```

### Pacientes
```
GET    /api/patients               - Listar pacientes
GET    /api/patients/{id}          - Obter paciente
POST   /api/patients               - Criar paciente
PUT    /api/patients/{id}          - Atualizar paciente
DELETE /api/patients/{id}          - Deletar paciente (Admin)
```

### Agendamentos
```
GET    /api/appointments           - Listar agendamentos
GET    /api/appointments/{id}      - Obter agendamento
POST   /api/appointments           - Criar agendamento
PUT    /api/appointments/{id}      - Atualizar agendamento
POST   /api/appointments/{id}/cancel - Cancelar agendamento
DELETE /api/appointments/{id}      - Deletar agendamento (Admin)
```

## 🧪 Testar API

### Login com cURL
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "paciente@test.com",
    "password": "teste1234"
  }'
```

### Usar Swagger UI
Acesse: `http://localhost:8000/docs`

## 🚀 Próximas Fases

- [ ] Mobile (React Native)
- [ ] Relatórios avançados
- [ ] Integração com pagamento
- [ ] Notificações (Email/SMS)
- [ ] Videoconsulta
- [ ] Sistema de faturamento
- [ ] Integração com prontuário de farmácia
- [ ] Backup automático

## 🐛 Troubleshooting

### Erro: "Database connection refused"
```bash
# Certifique-se que PostgreSQL está rodando
# Linux/Mac
brew services start postgresql
# Windows
# Use PostgreSQL GUI ou CMD
```

### Erro: "Port already in use"
```bash
# Mudar porta no docker-compose.yml ou usar
docker-compose up -p clinica_alt
```

### Erro de CORS
- Verifique se frontend está em `CORS_ORIGINS`
- Reinicie o backend após alteração

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação em `/docs`
2. Veja os logs: `docker-compose logs backend`
3. Teste endpoints com Swagger: `http://localhost:8000/docs`

## 📄 Licença

Este projeto é de código aberto e pode ser usado para fins comerciais.

---

**Versão**: 1.0.0  
**Status**: Pronto para MVP  
**Última atualização**: Janeiro 2024
