import api from './api';

const patientService = {
  register: async (patientData) => {
    const response = await api.post('/api/patients/register', patientData);
    return response.data;
  },

  // Criar novo paciente
  create: async (patientData) => {
    const response = await api.post('/api/patients', patientData);
    return response.data;
  },

  // Listar pacientes
  list: async (skip = 0, limit = 100) => {
    const response = await api.get('/api/patients', {
      params: { skip, limit },
    });
    return response.data;
  },

  // Obter paciente por ID
  getById: async (patientId) => {
    const response = await api.get(`/api/patients/${patientId}`);
    return response.data;
  },

  // Atualizar paciente
  update: async (patientId, updateData) => {
    const response = await api.put(`/api/patients/${patientId}`, updateData);
    return response.data;
  },

  // Deletar paciente
  delete: async (patientId) => {
    await api.delete(`/api/patients/${patientId}`);
  },
};

export default patientService;
