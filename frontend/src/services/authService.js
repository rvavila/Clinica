import api from './api';

const authService = {
  // Registrar novo usuário
  register: async (userData) => {
    const response = await api.post('/api/auth/register', userData);
    return response.data;
  },

  // Fazer login
  login: async (email, password) => {
    const response = await api.post('/api/auth/login', {
      email,
      password,
    });
    return response.data;
  },

  // Obter informações do usuário atual
  getCurrentUser: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },

  // Logout (limpar token)
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },
};

export default authService;
