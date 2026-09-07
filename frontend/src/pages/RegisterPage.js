import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import authService from '../services/authService';
import './Auth.css';

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    cpf: '',
    phone: '',
    password: '',
    confirmPassword: '',
    role: 'reception',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validações
    if (formData.password !== formData.confirmPassword) {
      setError('As senhas não correspondem');
      return;
    }

    if (formData.password.length < 8) {
      setError('Senha deve ter no mínimo 8 caracteres');
      return;
    }

    setLoading(true);

    try {
      const { confirmPassword, ...registerData } = formData;
      await authService.register(registerData);
      navigate('/login', {
        state: { message: 'Registro realizado com sucesso! Faça login agora.' },
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao registrar');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-form" style={{ maxWidth: '500px' }}>
        <h1>Clínica Médica</h1>
        <h2>Criar Conta</h2>

        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="full_name">Nome Completo</label>
            <input
              id="full_name"
              name="full_name"
              type="text"
              value={formData.full_name}
              onChange={handleChange}
              required
              placeholder="João Silva"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="seu@email.com"
            />
          </div>

          <div className="form-group">
            <label htmlFor="cpf">CPF</label>
            <input
              id="cpf"
              name="cpf"
              type="text"
              value={formData.cpf}
              onChange={handleChange}
              required
              placeholder="12345678901"
            />
          </div>

          <div className="form-group">
            <label htmlFor="phone">Telefone</label>
            <input
              id="phone"
              name="phone"
              type="tel"
              value={formData.phone}
              onChange={handleChange}
              placeholder="(11) 99999-9999"
            />
          </div>

          <div className="form-group">
            <label htmlFor="role">Tipo de Conta</label>
            <select
              id="role"
              name="role"
              value={formData.role}
              onChange={handleChange}
            >
              <option value="doctor">Médico</option>
              <option value="reception">Recepção</option>
            </select>
            <small>Pacientes são cadastrados pela recepção após o acesso ao sistema.</small>
          </div>

          <div className="form-group">
            <label htmlFor="password">Senha</label>
            <input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="••••••••"
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirmar Senha</label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
              placeholder="••••••••"
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Criando conta...' : 'Criar Conta'}
          </button>
        </form>

        <p className="auth-link">
          Já tem conta? <Link to="/login">Fazer login</Link>
        </p>
      </div>
    </div>
  );
};

export default RegisterPage;
