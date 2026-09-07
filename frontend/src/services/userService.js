import api from './api';

const userService = {
  update: async (userId, userData) => {
    const response = await api.put(`/api/users/${userId}`, userData);
    return response.data;
  },

  resetPassword: async (userId, password) => {
    const response = await api.put(`/api/users/${userId}/password`, { password });
    return response.data;
  },
};

export default userService;
