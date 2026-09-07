# Sistema de Gerenciamento de Clínica Médica

Sistema profissional e completo para gestão de clínica médica particular com pediatria.

## Arquitetura

```
clinica/
├── backend/              # FastAPI + PostgreSQL
├── frontend/             # React (Web)
├── mobile/               # React Native (Mobile)
└── docs/                 # Documentação
```

## Features Principais

### 👨‍⚕️ Para Médicos
- Dashboard com agendamentos do dia
- Prontuários eletrônicos (PEP)
- Consultar histórico de pacientes
- Gerar receitas e atestados
- Visualizar resultados de exames
- Gerenciar disponibilidade

### 👨‍💼 Para Recepção
- Gerenciar agendamentos
- Registrar novos pacientes
- Controlar fila de espera
- Processar pagamentos
- Emitir comprovantes
- Visualizar relatório de ocupação

### 👤 Para Clientes/Pacientes
- Agendar consultas (web + mobile)
- Histórico de consultas
- Visualizar prontuário próprio
- Receber receitas digitais
- Suporte/comunicação com clínica

## Stack Tecnológico

| Camada | Tecnologia |
|--------|-----------|
| Backend | FastAPI + PostgreSQL |
| Frontend Web | React + Axios |
| Frontend Mobile | React Native + Expo |
| Autenticação | JWT + bcrypt |
| Docs API | Swagger/OpenAPI |

## Segurança

- ✅ Autenticação JWT
- ✅ Criptografia de senhas (bcrypt)
- ✅ Controle de acesso por roles (RBAC)
- ✅ Validação CORS
- ✅ Rate limiting

## Getting Started

Veja documentação em `/docs`

---
**Versão**: 1.0.0  
**Status**: Em desenvolvimento
