import React, { useState, useEffect } from 'react';
import appointmentService from '../../services/appointmentService';
import { appointmentStatusLabel } from '../../utils/appointmentLabels';
import medicalRecordService from '../../services/medicalRecordService';
import { sortAppointmentsByDate } from '../../utils/appointmentSort';

const PatientDashboard = () => {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [records, setRecords] = useState([]);
  const [expandedMedicationId, setExpandedMedicationId] = useState(null);
  const currentMonthKey = `${new Date().getFullYear()}-${String(new Date().getMonth() + 1).padStart(2, '0')}`;
  const nextMonthDate = new Date(new Date().getFullYear(), new Date().getMonth() + 1, 1);
  const nextMonthKey = `${nextMonthDate.getFullYear()}-${String(nextMonthDate.getMonth() + 1).padStart(2, '0')}`;
  const [selectedMonth, setSelectedMonth] = useState(currentMonthKey);

  useEffect(() => {
    const fetchAppointments = async () => {
      try {
        const [data, recordData] = await Promise.all([
          appointmentService.list(0, 50),
          medicalRecordService.list(),
        ]);
        setAppointments(data);
        setRecords(recordData);
      } catch (error) {
        console.error('Erro ao carregar agendamentos:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAppointments();
  }, []);

  const cancelAppointment = async (appointment) => {
    if (!window.confirm('Deseja cancelar esta consulta? O médico e a recepção serão avisados.')) return;

    setMessage('');
    setError('');
    try {
      await appointmentService.cancel(appointment.id);
      setAppointments((current) => current.map((item) => (
        item.id === appointment.id ? { ...item, status: 'cancelled' } : item
      )));
      setMessage('Consulta cancelada. O médico e a recepção foram avisados.');
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Não foi possível cancelar a consulta.');
    }
  };

  const monthOptions = [...new Set([currentMonthKey, nextMonthKey, ...appointments.map((appointment) => {
    const date = new Date(appointment.appointment_datetime);
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
  })])].sort().reverse();
  const monthAppointments = sortAppointmentsByDate(selectedMonth === 'all'
    ? appointments
    : appointments.filter((appointment) => {
      const date = new Date(appointment.appointment_datetime);
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}` === selectedMonth;
    }));
  const appointmentsByMonth = monthAppointments.reduce((groups, appointment) => {
    const date = new Date(appointment.appointment_datetime);
    const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
    if (!groups[key]) groups[key] = [];
    groups[key].push(appointment);
    return groups;
  }, {});
  const appointmentMonths = Object.entries(appointmentsByMonth).sort(([first], [second]) => first.localeCompare(second));

  return (
    <div>
      <h2>Meus Agendamentos</h2>
      <p>Cancelamentos pelo paciente são permitidos somente com pelo menos 24 horas de antecedência.</p>
      {message && <div className="alert alert-success">{message}</div>}
      {error && <div className="alert alert-error">{error}</div>}

      <div className="patient-month-filter" aria-label="Filtro por período">
        <div className="patient-month-filter-title">
          <span className="patient-filter-icon" aria-hidden="true">▦</span>
          <div>
            <strong>Visualizar consultas</strong>
            <small>Escolha um período rápido</small>
          </div>
        </div>
        <div className="patient-period-options">
          <button type="button" className={selectedMonth === currentMonthKey ? 'active' : ''} onClick={() => setSelectedMonth(currentMonthKey)}>Mês atual</button>
          <button type="button" className={selectedMonth === nextMonthKey ? 'active' : ''} onClick={() => setSelectedMonth(nextMonthKey)}>Próximo mês</button>
          <button type="button" className={selectedMonth === 'all' ? 'active' : ''} onClick={() => setSelectedMonth('all')}>Todos</button>
          <label className="patient-month-select" htmlFor="patient-month">
            <span className="sr-only">Outro mês</span>
            <select id="patient-month" value={![currentMonthKey, nextMonthKey, 'all'].includes(selectedMonth) ? selectedMonth : ''} onChange={(event) => event.target.value && setSelectedMonth(event.target.value)}>
              <option value="">Outro mês</option>
              {monthOptions.filter((monthKey) => ![currentMonthKey, nextMonthKey].includes(monthKey)).map((monthKey) => {
                const [year, month] = monthKey.split('-');
                return <option key={monthKey} value={monthKey}>
                  {new Date(Number(year), Number(month) - 1, 1).toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })}
                </option>;
              })}
            </select>
          </label>
        </div>
        <span className="patient-month-count">{monthAppointments.length} {monthAppointments.length === 1 ? 'consulta' : 'consultas'}</span>
      </div>

      {loading ? (
        <div className="spinner"></div>
      ) : monthAppointments.length > 0 ? (
        <div className="patient-month-list">
          {appointmentMonths.map(([monthKey, monthAppointments]) => {
            const [year, month] = monthKey.split('-');
            const monthLabel = new Date(Number(year), Number(month) - 1, 1).toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' });
            return <section className="patient-month" key={monthKey}>
              <h3>{monthLabel}</h3>
              <div className="card">
          <table className="appointments-table">
            <thead>
              <tr>
                <th>Médico</th>
                <th>Data/Hora</th>
                <th>Status</th>
                <th>Medicação receitada</th>
                <th>Ação</th>
              </tr>
            </thead>
            <tbody>
                {monthAppointments.map((appt) => (
                <React.Fragment key={appt.id}>
                <tr>
                  <td>{appt.doctor_name}</td>
                  <td>{new Date(appt.appointment_datetime).toLocaleString()}</td>
                  <td>
                    <span className={`status-badge status-${appt.status}`}>
                      {appointmentStatusLabel(appt.status)}
                    </span>
                  </td>
                  <td className="patient-prescription-cell">
                    {records.find((record) => record.appointment_id === appt.id)?.prescription ? (
                      <button
                        type="button"
                        className="btn btn-secondary medication-toggle"
                        onClick={() => setExpandedMedicationId(expandedMedicationId === appt.id ? null : appt.id)}
                      >
                        {expandedMedicationId === appt.id ? 'Fechar medicação' : 'Ver medicação'}
                      </button>
                    ) : 'Não disponível'}
                  </td>
                  <td>
                    {['scheduled', 'confirmed', 'Agendada', 'agendada'].includes(appt.status) ? (
                      <button type="button" className="btn btn-secondary" onClick={() => cancelAppointment(appt)}>
                        Cancelar
                      </button>
                    ) : ['scheduled', 'confirmed'].includes(appt.status) ? (
                      <span>Cancelamento disponível até 24h antes</span>
                    ) : (
                      <span>-</span>
                    )}
                  </td>
                </tr>
                {expandedMedicationId === appt.id && <tr className="expanded-medication-row"><td colSpan="5">
                  <div className="patient-medication-box">
                    <strong>Medicação receitada</strong>
                    <p>{records.find((record) => record.appointment_id === appt.id)?.prescription}</p>
                  </div>
                </td></tr>}
                </React.Fragment>
              ))}
            </tbody>
          </table>
              </div>
            </section>;
          })}
        </div>
      ) : (
        <div className="card">
          <div className="empty-state">
            <p>Você não possui agendamentos</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default PatientDashboard;
