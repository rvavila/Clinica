# Backend - Clínica Médica

API FastAPI para gerenciamento de clínica médica.

## Setup

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar banco de dados
python alembic/env.py upgrade head

# Executar servidor
uvicorn main:app --reload
```

## Documentação API

Acesse `http://localhost:8000/docs` após iniciar o servidor.

## Estrutura

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Aplicação principal
│   ├── core/
│   │   ├── config.py           # Configurações
│   │   ├── security.py         # JWT e autenticação
│   │   └── constants.py        # Constantes
│   ├── models/                 # Modelos de banco de dados
│   │   ├── user.py
│   │   ├── doctor.py
│   │   ├── patient.py
│   │   ├── appointment.py
│   │   ├── medical_record.py
│   │   ├── payment.py
│   │   ├── room.py
│   │   └── specialty.py
│   ├── schemas/                # Schemas de validação
│   ├── routes/                 # Rotas da API
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── doctors.py
│   │   ├── patients.py
│   │   ├── appointments.py
│   │   ├── medical_records.py
│   │   └── payments.py
│   ├── crud/                   # Operações de banco de dados
│   ├── db/
│   │   ├── database.py         # Conexão com BD
│   │   └── base.py
│   └── dependencies.py         # Injeções de dependência
├── requirements.txt
├── .env.example
└── alembic/                    # Migrações de BD
```
