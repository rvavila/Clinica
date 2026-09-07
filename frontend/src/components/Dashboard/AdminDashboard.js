import React, { useState, useEffect } from 'react';

const AdminDashboard = () => {
  const [stats, setStats] = useState({
    users: 0,
    doctors: 0,
    patients: 0,
    appointments: 0,
  });
  useEffect(() => {
    // Simular carregamento de estatísticas
    setStats({
      users: 0,
      doctors: 0,
      patients: 0,
      appointments: 0,
    });
  }, []);

  return (
    <div>
      <h2>Administração</h2>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h3>Usuários</h3>
          <div className="stat-value">{stats.users}</div>
          <div className="stat-label">Total de usuários</div>
        </div>

        <div className="dashboard-card">
          <h3>Médicos</h3>
          <div className="stat-value">{stats.doctors}</div>
          <div className="stat-label">Médicos cadastrados</div>
        </div>

        <div className="dashboard-card">
          <h3>Pacientes</h3>
          <div className="stat-value">{stats.patients}</div>
          <div className="stat-label">Pacientes cadastrados</div>
        </div>

        <div className="dashboard-card">
          <h3>Agendamentos</h3>
          <div className="stat-value">{stats.appointments}</div>
          <div className="stat-label">Total de agendamentos</div>
        </div>
      </div>

      <div className="dashboard-section">
        <h2>Ações de Administração</h2>
        <div className="card">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <button className="btn btn-primary">Gerenciar Usuários</button>
            <button className="btn btn-primary">Gerenciar Médicos</button>
            <button className="btn btn-primary">Gerenciar Pacientes</button>
            <button className="btn btn-primary">Relatórios</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
