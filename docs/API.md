# Documentação da API - Clínica Médica

## Base URL
```
http://localhost:8000
```

## Documentação Interativa
```
http://localhost:8000/docs (Swagger UI)
http://localhost:8000/redoc (ReDoc)
```

## Autenticação

### Header Padrão
```
Authorization: Bearer {token}
Content-Type: application/json
```

### Obter Token
**POST** `/api/auth/login`

**Request:**
```json
{
  "email": "user@email.com",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@email.com",
    "full_name": "João Silva",
    "role": "patient",
    "status": "active"
  }
}
```

## Endpoints

### Autenticação

#### Registrar
**POST** `/api/auth/register`

**Request:**
```json
{
  "email": "novo@email.com",
  "full_name": "Maria Silva",
  "cpf": "12345678901",
  "phone": "(11) 99999-9999",
  "password": "senha123",
  "role": "patient"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "email": "novo@email.com",
  "full_name": "Maria Silva",
  "cpf": "12345678901",
  "role": "patient",
  "status": "active",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

#### Obter Usuário Atual
**GET** `/api/auth/me`

**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@email.com",
  "full_name": "João Silva",
  "role": "patient",
  "status": "active"
}
```

### Usuários

#### Listar Usuários (Admin only)
**GET** `/api/users?skip=0&limit=100`

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "email": "user@email.com",
    "full_name": "João Silva",
    "role": "patient",
    "status": "active"
  }
]
```

#### Obter Usuário
**GET** `/api/users/{user_id}`

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@email.com",
  "full_name": "João Silva",
  "phone": "(11) 99999-9999",
  "cpf": "12345678901",
  "role": "patient",
  "status": "active",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "last_login": "2024-01-15T15:45:00"
}
```

#### Atualizar Usuário
**PUT** `/api/users/{user_id}`

**Request:**
```json
{
  "full_name": "João Silva Santos",
  "phone": "(11) 98888-8888",
  "status": "active"
}
```

### Médicos

#### Listar Médicos
**GET** `/api/doctors?skip=0&limit=100&specialty=Pediatria`

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user_id": 2,
    "crm": "123456-SP",
    "specialty": "Pediatria",
    "bio": "Pediatra com 10 anos de experiência",
    "office_phone": "(11) 3000-0000",
    "full_name": "Dra. Ana Silva",
    "email": "ana@clinic.com",
    "phone": "(11) 99999-9999"
  }
]
```

#### Criar Médico
**POST** `/api/doctors`

**Request:**
```json
{
  "user_id": 2,
  "crm": "123456-SP",
  "specialty": "Pediatria",
  "bio": "Pediatra com experiência",
  "office_phone": "(11) 3000-0000"
}
```

### Pacientes

#### Listar Pacientes
**GET** `/api/patients?skip=0&limit=100`

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user_id": 3,
    "date_of_birth": "1990-05-15",
    "gender": "Masculino",
    "blood_type": "O+",
    "allergies": "Penicilina",
    "medical_conditions": "Asma",
    "address": "Rua das Flores, 123",
    "city": "São Paulo",
    "state": "SP",
    "zip_code": "01234-567",
    "full_name": "João Silva",
    "email": "joao@email.com",
    "cpf": "12345678901"
  }
]
```

#### Criar Paciente
**POST** `/api/patients`

**Request:**
```json
{
  "user_id": 3,
  "date_of_birth": "1990-05-15",
  "gender": "Masculino",
  "blood_type": "O+",
  "allergies": "Penicilina",
  "medical_conditions": "Asma",
  "address": "Rua das Flores, 123",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01234-567"
}
```

### Agendamentos

#### Listar Agendamentos
**GET** `/api/appointments?skip=0&limit=100`

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "patient_id": 1,
    "doctor_id": 1,
    "room_id": 1,
    "appointment_datetime": "2024-01-20T14:00:00",
    "duration_minutes": 30,
    "status": "scheduled",
    "consultation_type": "follow_up",
    "notes": "Acompanhamento",
    "patient_name": "João Silva",
    "doctor_name": "Dra. Ana Silva",
    "doctor_specialty": "Pediatria",
    "room_name": "Sala 1"
  }
]
```

#### Criar Agendamento
**POST** `/api/appointments`

**Request:**
```json
{
  "patient_id": 1,
  "doctor_id": 1,
  "appointment_datetime": "2024-01-20T14:00:00",
  "room_id": 1,
  "duration_minutes": 30,
  "consultation_type": "follow_up",
  "notes": "Consulta de rotina"
}
```

#### Cancelar Agendamento
**POST** `/api/appointments/{appointment_id}/cancel?reason=Paciente%20cancelou`

**Response (200 OK):**
```json
{
  "id": 1,
  "status": "cancelled",
  "cancel_reason": "Paciente cancelou",
  "updated_at": "2024-01-15T16:00:00"
}
```

## Códigos de Status HTTP

- **200 OK**: Requisição bem-sucedida
- **201 Created**: Recurso criado
- **204 No Content**: Sucesso, sem retorno
- **400 Bad Request**: Erro na requisição
- **401 Unauthorized**: Não autenticado
- **403 Forbidden**: Sem permissão
- **404 Not Found**: Recurso não encontrado
- **500 Internal Server Error**: Erro do servidor

## Tratamento de Erros

**Response (400 Bad Request):**
```json
{
  "detail": "Email já registrado"
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Credenciais inválidas"
}
```

**Response (403 Forbidden):**
```json
{
  "detail": "Acesso negado: permissões insuficientes"
}
```

## Paginação

Todos os endpoints de listagem suportam:
- `skip`: Número de registros a pular (padrão: 0)
- `limit`: Número máximo de registros (padrão: 100, máximo: 1000)

**Exemplo:**
```
GET /api/doctors?skip=0&limit=10
```

## Filtros

Alguns endpoints suportam filtros:

### Médicos
- `specialty`: Filtrar por especialidade

**Exemplo:**
```
GET /api/doctors?specialty=Pediatria
```

## Roles e Permissões

### Admin
- ✅ Acesso total
- ✅ Gerenciar usuários
- ✅ Gerenciar médicos
- ✅ Ver todos os dados

### Doctor
- ✅ Ver/atualizar próprios dados
- ✅ Ver agendamentos próprios
- ✅ Criar/editar prontuários
- ✅ Gerenciar disponibilidade

### Reception
- ✅ Gerenciar agendamentos
- ✅ Registrar pacientes
- ✅ Ver dados de pacientes
- ✅ Processar pagamentos

### Patient
- ✅ Ver próprios dados
- ✅ Agendar consultas
- ✅ Ver histórico de consultas
- ✅ Ver próprio prontuário

## Exemplos de Uso

### Fluxo Completo: Paciente Agendando Consulta

1. **Registrar Paciente**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "paciente@email.com",
    "full_name": "Maria Silva",
    "cpf": "12345678901",
    "password": "senha123",
    "role": "patient"
  }'
```

2. **Login**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "paciente@email.com",
    "password": "senha123"
  }'
```

3. **Listar Médicos Disponíveis**
```bash
curl -X GET "http://localhost:8000/api/doctors?specialty=Pediatria" \
  -H "Authorization: Bearer {token}"
```

4. **Agendar Consulta**
```bash
curl -X POST http://localhost:8000/api/appointments \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "doctor_id": 1,
    "appointment_datetime": "2024-01-20T14:00:00",
    "consultation_type": "first_visit"
  }'
```

5. **Ver Agendamentos**
```bash
curl -X GET "http://localhost:8000/api/appointments" \
  -H "Authorization: Bearer {token}"
```

## Rate Limiting

Atualmente não implementado. Será adicionado em versão futura.

## Webhooks

Atualmente não implementado. Será adicionado em versão futura.
