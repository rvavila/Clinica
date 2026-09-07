# Estrutura do Projeto - Clínica Médica

## Visão Geral

Sistema profissional e completo para gerenciamento de clínica médica com controle de acesso baseado em roles (RBAC).

## Estrutura de Pastas

```
clinica/
│
├── backend/                    # API FastAPI
│   ├── app/
│   │   ├── core/               # Configurações e constantes
│   │   │   ├── config.py       # Settings da aplicação
│   │   │   ├── constants.py    # Enums e constantes
│   │   │   ├── security.py     # JWT e autenticação
│   │   │   └── __init__.py
│   │   │
│   │   ├── db/                 # Database
│   │   │   ├── database.py     # Conexão e sessão
│   │   │   └── __init__.py
│   │   │
│   │   ├── models/             # Modelos SQLAlchemy
│   │   │   ├── user.py
│   │   │   ├── doctor.py
│   │   │   ├── patient.py
│   │   │   ├── appointment.py
│   │   │   ├── medical_record.py
│   │   │   ├── payment.py
│   │   │   ├── room.py
│   │   │   ├── doctor_schedule.py
│   │   │   └── __init__.py
│   │   │
│   │   ├── schemas/            # Pydantic schemas
│   │   │   ├── user_schema.py
│   │   │   ├── doctor_schema.py
│   │   │   ├── patient_schema.py
│   │   │   ├── appointment_schema.py
│   │   │   ├── medical_record_schema.py
│   │   │   ├── payment_schema.py
│   │   │   ├── room_schema.py
│   │   │   ├── doctor_schedule_schema.py
│   │   │   └── __init__.py
│   │   │
│   │   ├── crud/               # Operações de banco de dados
│   │   │   ├── user_crud.py
│   │   │   ├── doctor_crud.py
│   │   │   ├── patient_crud.py
│   │   │   ├── appointment_crud.py
│   │   │   └── __init__.py
│   │   │
│   │   ├── routes/             # Rotas da API
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── doctors.py
│   │   │   ├── patients.py
│   │   │   ├── appointments.py
│   │   │   └── __init__.py
│   │   │
│   │   ├── main.py             # Aplicação principal
│   │   └── __init__.py
│   │
│   ├── requirements.txt        # Dependências Python
│   ├── .env.example            # Exemplo de variáveis
│   ├── Dockerfile              # Docker
│   └── README.md
│
├── frontend/                   # Aplicação React
│   ├── src/
│   │   ├── components/
│   │   │   ├── Auth/
│   │   │   ├── Dashboard/
│   │   │   ├── Common/
│   │   │   ├── Layout/
│   │   │   └── ...
│   │   │
│   │   ├── pages/
│   │   │   ├── LoginPage.js
│   │   │   ├── RegisterPage.js
│   │   │   ├── HomePage.js
│   │   │   ├── DashboardPage.js
│   │   │   └── ...
│   │   │
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   ├── authService.js
│   │   │   ├── appointmentService.js
│   │   │   ├── doctorService.js
│   │   │   ├── patientService.js
│   │   │   └── ...
│   │   │
│   │   ├── hooks/
│   │   │   ├── useAuth.js
│   │   │   ├── useFetch.js
│   │   │   └── ...
│   │   │
│   │   ├── context/
│   │   │   ├── AuthContext.js
│   │   │   └── ...
│   │   │
│   │   ├── App.js
│   │   ├── App.css
│   │   └── index.js
│   │
│   ├── public/
│   │   └── index.html
│   │
│   ├── package.json
│   ├── .env.example
│   ├── Dockerfile
│   └── README.md
│
├── mobile/                     # React Native (futuro)
│   └── ...
│
├── docs/                       # Documentação
│   ├── SETUP.md                # Guia de instalação
│   ├── API.md                  # Documentação da API
│   └── ARCHITECTURE.md         # Arquitetura
│
├── docker-compose.yml          # Docker Compose
├── .gitignore
└── README.md
```

## Tecnologias Utilizadas

### Backend
- **FastAPI**: Framework web moderno para APIs
- **SQLAlchemy**: ORM para banco de dados
- **PostgreSQL**: Banco de dados
- **JWT**: Autenticação
- **Pydantic**: Validação de dados
- **Alembic**: Migrações de banco de dados

### Frontend
- **React**: Biblioteca UI
- **React Router**: Navegação
- **Axios**: Cliente HTTP
- **CSS**: Estilização

### DevOps
- **Docker**: Containerização
- **Docker Compose**: Orquestração

## Fluxo de Autenticação

1. Usuário se registra com email, CPF, senha e role
2. Sistema cria hash da senha com bcrypt
3. Usuário faz login
4. Backend valida credenciais e retorna JWT
5. Frontend armazena token no localStorage
6. Requisições subsequentes incluem token no header
7. Backend valida token e autoriza baseado na role

## Controle de Acesso (RBAC)

### Roles
- **Admin**: Acesso total ao sistema
- **Doctor**: Acesso a agendamentos e prontuários próprios
- **Reception**: Acesso a gerenciamento de agendamentos
- **Patient**: Acesso a próprio agendamento e prontuário

### Permissões por Endpoint

```
GET /api/users               → Admin
GET /api/doctors             → Todos
POST /api/doctors            → Admin, Doctor
GET /api/patients            → Doctor, Reception, Admin (Patient vê só a si)
POST /api/appointments       → Patient (próprio), Reception, Doctor
PUT /api/appointments/{id}   → Doctor (próprio), Reception, Admin
```

## Modelos de Dados

### User
- id
- email
- full_name
- phone
- cpf
- hashed_password
- role
- status
- created_at, updated_at, last_login

### Doctor (herda de User)
- user_id
- crm
- specialty
- bio
- office_phone
- doctor_schedules

### Patient (herda de User)
- user_id
- date_of_birth
- gender
- address, city, state, zip_code
- blood_type
- allergies
- medical_conditions
- responsible_name (para pediatria)

### Appointment
- id
- patient_id
- doctor_id
- room_id
- appointment_datetime
- duration_minutes
- status
- consultation_type
- notes, cancel_reason

### MedicalRecord
- id
- patient_id
- doctor_id
- appointment_id
- chief_complaint
- history_of_present_illness
- physical_examination
- diagnosis
- treatment_plan
- prescription
- medical_certificate
- referral

### Payment
- id
- patient_id
- appointment_id
- amount
- status
- payment_method
- transaction_id
- due_date, payment_date

### Room
- id
- name
- room_number
- description
- equipment
- is_active

### DoctorSchedule
- id
- doctor_id
- day_of_week
- start_time, end_time
- interval_minutes
- is_active

## APIs Principais

### Autenticação
```
POST /api/auth/register
POST /api/auth/login
GET /api/auth/me
```

### Usuários
```
GET /api/users
GET /api/users/{user_id}
PUT /api/users/{user_id}
DELETE /api/users/{user_id}
GET /api/users/role/{role}
```

### Médicos
```
GET /api/doctors
GET /api/doctors/{doctor_id}
POST /api/doctors
PUT /api/doctors/{doctor_id}
DELETE /api/doctors/{doctor_id}
```

### Pacientes
```
GET /api/patients
GET /api/patients/{patient_id}
POST /api/patients
PUT /api/patients/{patient_id}
DELETE /api/patients/{patient_id}
```

### Agendamentos
```
GET /api/appointments
GET /api/appointments/{appointment_id}
POST /api/appointments
PUT /api/appointments/{appointment_id}
POST /api/appointments/{appointment_id}/cancel
DELETE /api/appointments/{appointment_id}
```

## Como Estender

### Adicionar Nova Feature

1. **Backend**
   - Criar modelo em `app/models/`
   - Criar schema em `app/schemas/`
   - Criar CRUD em `app/crud/`
   - Criar rotas em `app/routes/`

2. **Frontend**
   - Criar serviço em `src/services/`
   - Criar componentes em `src/components/`
   - Criar página em `src/pages/`
   - Adicionar rotas em `App.js`

## Segurança

- ✅ Senhas com hash bcrypt
- ✅ JWT para autenticação
- ✅ CORS configurado
- ✅ RBAC para autorização
- ✅ Validação de entrada (Pydantic)
- ✅ SQL Injection previsto (SQLAlchemy ORM)

## Performance

- ✅ Banco de dados indexado
- ✅ Paginação em listagens
- ✅ Cache no frontend
- ✅ Lazy loading de imagens

## Próximas Fases

- [ ] Mobile (React Native)
- [ ] Relatórios avançados
- [ ] Integração com pagamento online
- [ ] Notificações por email/SMS
- [ ] Videoconsulta
- [ ] Prontuário eletrônico avançado
- [ ] Integração com sistemas de faturamento
