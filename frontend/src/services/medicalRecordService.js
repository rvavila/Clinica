import api from './api';

const medicalRecordService = {
  list: async (appointmentId = null) => {
    const response = await api.get('/api/medical-records', {
      params: appointmentId ? { appointment_id: appointmentId } : {},
    });
    return response.data;
  },
  create: async (data) => {
    const response = await api.post('/api/medical-records', data);
    return response.data;
  },
  update: async (recordId, data) => {
    const response = await api.put(`/api/medical-records/${recordId}`, data);
    return response.data;
  },
};

export default medicalRecordService;
