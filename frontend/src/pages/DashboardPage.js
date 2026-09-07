import React from 'react';
import { useNavigate } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import PatientDashboard from '../components/Dashboard/PatientDashboard';
import DoctorDashboard from '../components/Dashboard/DoctorDashboard';
import ReceptionDashboard from '../components/Dashboard/ReceptionDashboard';
import AdminDashboard from '../components/Dashboard/AdminDashboard';
import './Dashboard.css';

const DashboardPage = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const today = new Intl.DateTimeFormat('pt-BR', {
    weekday: 'long',
    day: '2-digit',
    month: 'long',
  }).format(new Date());

  const roleNames = {
    patient: 'Paciente',
    doctor: 'Equipe médica',
    reception: 'Recepção',
    admin: 'Administrador',
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Renderizar dashboard baseado na role
  const renderDashboard = () => {
    switch (user?.role) {
      case 'patient':
        return <PatientDashboard />;
      case 'doctor':
        return <DoctorDashboard />;
      case 'reception':
        return <ReceptionDashboard />;
      case 'admin':
        return <AdminDashboard />;
      default:
        return <div>Role desconhecida</div>;
    }
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-content">
          <div className="brand-lockup">
            <span className="brand-mark" aria-hidden="true">+</span>
            <div>
              <h1>Clínica Aurora</h1>
              <span className="header-kicker">Painel de atendimento</span>
            </div>
          </div>
          <div className="header-user">
            <div className="user-meta">
              <strong>{user?.full_name}</strong>
              <span>{roleNames[user?.role] || 'Acesso interno'}</span>
            </div>
            <span className="header-date">{today}</span>
            <button onClick={handleLogout} className="btn btn-secondary">
              Sair
            </button>
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="page-intro">
          <span className="eyebrow">Visão geral</span>
          <h2>Olá, {user?.full_name?.split(' ')[0] || 'bem-vindo'}.</h2>
          <p>Acompanhe sua agenda e mantenha o cuidado em movimento.</p>
        </div>
        {renderDashboard()}
      </main>
    </div>
  );
};

export default DashboardPage;
