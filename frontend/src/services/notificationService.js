import api from './api';

const notificationService = {
  list: async (limit = 30) => {
    const response = await api.get('/api/notifications', { params: { limit } });
    return response.data;
  },
};

export default notificationService;
