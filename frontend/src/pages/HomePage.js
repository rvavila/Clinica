import React from 'react';
import { Link } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import './HomePage.css';

const HomePage = () => {
  const { isAuthenticated, user } = useAuth();

  return (
    <div className="home-container">
      <header className="home-header">
        <div className="header-content">
          <h1>Clínica Médica</h1>
          <nav className="header-nav">
            {isAuthenticated ? (
              <>
                <span>Bem-vindo, {user?.full_name}!</span>
                <Link to="/dashboard" className="btn btn-primary">
                  Dashboard
                </Link>
              </>
            ) : (
              <>
                <Link to="/login" className="btn btn-primary">
                  Entrar
                </Link>
                <Link to="/register" className="btn btn-secondary">
                  Criar Conta
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>

      <main className="home-main">
        <section className="hero">
          <h2>Gerenciamento Completo da Sua Clínica</h2>
          <p>
            Sistema profissional para agendamentos, prontuários e gerenciamento
            completo de clínica médica.
          </p>
          {!isAuthenticated && (
            <Link to="/register" className="btn btn-primary" style={{ fontSize: '1.125rem', padding: '1rem 2rem' }}>
              Começar Agora
            </Link>
          )}
        </section>

        <section className="features">
          <h3>Recursos Principais</h3>
          <div className="features-grid">
            <div className="feature-card">
              <h4>👨‍⚕️ Para Médicos</h4>
              <ul>
                <li>Dashboard com agendamentos</li>
                <li>Prontuários eletrônicos</li>
                <li>Gerenciar disponibilidade</li>
              </ul>
            </div>

            <div className="feature-card">
              <h4>👨‍💼 Para Recepção</h4>
              <ul>
                <li>Agendamentos</li>
                <li>Registrar pacientes</li>
                <li>Processamento de pagamentos</li>
              </ul>
            </div>

            <div className="feature-card">
              <h4>👤 Para Pacientes</h4>
              <ul>
                <li>Agendar consultas</li>
                <li>Histórico de consultas</li>
                <li>Ver prontuário</li>
              </ul>
            </div>
          </div>
        </section>
      </main>

      <footer className="home-footer">
        <p>&copy; 2026 Clínica Médica. Todos os direitos reservados. Desenvolvido por IRTECH Soluções Tecnológicas.</p>
      </footer>
    </div>
  );
};

export default HomePage;
