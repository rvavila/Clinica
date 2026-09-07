import api from './api';

const doctorService = {
  listUnassignedUsers: async () => {
    const response = await api.get('/api/doctors/users/unassigned');
    return response.data;
  },

  createProfile: async (doctorData) => {
    const response = await api.post('/api/doctors/profile', doctorData);
    return response.data;
  },

  // Criar novo médico
  create: async (doctorData) => {
    const response = await api.post('/api/doctors', doctorData);
    return response.data;
  },

  // Listar médicos
  list: async (skip = 0, limit = 100, specialty = null) => {
    const response = await api.get('/api/doctors', {
      params: { skip, limit, specialty },
    });
    return response.data;
  },

  // Obter médico por ID
  getById: async (doctorId) => {
    const response = await api.get(`/api/doctors/${doctorId}`);
    return response.data;
  },

  // Atualizar médico
  update: async (doctorId, updateData) => {
    const response = await api.put(`/api/doctors/${doctorId}`, updateData);
    return response.data;
  },

  // Deletar médico
  delete: async (doctorId) => {
    await api.delete(`/api/doctors/${doctorId}`);
  },
};

export default doctorService;
