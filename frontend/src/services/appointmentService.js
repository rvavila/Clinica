import api from './api';

const appointmentService = {
  // Criar novo agendamento
  create: async (appointmentData) => {
    const response = await api.post('/api/appointments', appointmentData);
    return response.data;
  },

  // Listar agendamentos
  list: async (skip = 0, limit = 100) => {
    const response = await api.get('/api/appointments', {
      params: { skip, limit },
    });
    return response.data;
  },

  // Obter agendamento por ID
  getById: async (appointmentId) => {
    const response = await api.get(`/api/appointments/${appointmentId}`);
    return response.data;
  },

  // Atualizar agendamento
  update: async (appointmentId, updateData) => {
    const response = await api.put(
      `/api/appointments/${appointmentId}`,
      updateData
    );
    return response.data;
  },

  // Cancelar agendamento
  cancel: async (appointmentId, reason = null) => {
    const response = await api.post(
      `/api/appointments/${appointmentId}/cancel`,
      null,
      { params: { reason } }
    );
    return response.data;
  },

  // Deletar agendamento
  delete: async (appointmentId) => {
    await api.delete(`/api/appointments/${appointmentId}`);
  },
};

export default appointmentService;
