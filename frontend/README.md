# Frontend - Clínica Médica (React)

Aplicação web React para gerenciamento de clínica médica.

## Setup

```bash
# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm start

# Build para produção
npm run build
```

## Estrutura

```
frontend/
├── src/
│   ├── components/
│   │   ├── Auth/              # Componentes de autenticação
│   │   ├── Dashboard/         # Dashboards específicos por role
│   │   ├── Appointments/      # Gerenciamento de agendamentos
│   │   ├── Doctors/           # Listagem e detalhes de médicos
│   │   ├── Patients/          # Gerenciamento de pacientes
│   │   ├── Common/            # Componentes reutilizáveis
│   │   └── Layout/            # Header, Sidebar, Footer
│   ├── pages/
│   │   ├── LoginPage
│   │   ├── RegisterPage
│   │   ├── HomePage
│   │   ├── DashboardPage
│   │   └── NotFoundPage
│   ├── services/
│   │   ├── api.js             # Cliente HTTP (axios)
│   │   ├── authService.js
│   │   ├── appointmentService.js
│   │   └── ...
│   ├── hooks/
│   │   ├── useAuth.js
│   │   ├── useFetch.js
│   │   └── ...
│   ├── context/
│   │   ├── AuthContext.js
│   │   └── ...
│   ├── styles/
│   │   ├── App.css
│   │   └── ...
│   ├── App.js
│   └── index.js
├── public/
├── package.json
└── .env.example
```

## Features

- ✅ Autenticação JWT
- ✅ Dashboard por role (Médico, Recepção, Paciente)
- ✅ Agendamento de consultas
- ✅ Gerenciamento de médicos e especialidades
- ✅ Histórico de consultas
- ✅ Perfil do usuário
- ✅ Responsivo (Mobile + Desktop)

## Variáveis de Ambiente

Crie um arquivo `.env` baseado em `.env.example`:

```
REACT_APP_API_URL=http://localhost:8000
```
