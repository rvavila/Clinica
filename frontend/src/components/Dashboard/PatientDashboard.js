import React, { useState, useEffect } from 'react';
import appointmentService from '../../services/appointmentService';
import { appointmentStatusLabel } from '../../utils/appointmentLabels';
import medicalRecordService from '../../services/medicalRecordService';

const PatientDashboard = () => {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [records, setRecords] = useState([]);
  const [selectedRecord, setSelectedRecord] = useState(null);
  const currentMonthKey = `${new Date().getFullYear()}-${String(new Date().getMonth() + 1).padStart(2, '0')}`;
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

  const monthOptions = [...new Set(appointments.map((appointment) => {
    const date = new Date(appointment.appointment_datetime);
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
  }))].sort();
  const monthAppointments = selectedMonth === 'all'
    ? appointments
    : appointments.filter((appointment) => {
      const date = new Date(appointment.appointment_datetime);
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}` === selectedMonth;
    });
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

      <div className="patient-month-filter">
        <label htmlFor="patient-month">Visualizar mês</label>
        <select id="patient-month" value={selectedMonth} onChange={(event) => setSelectedMonth(event.target.value)}>
          <option value="all">Todos os meses</option>
          {monthOptions.map((monthKey) => {
            const [year, month] = monthKey.split('-');
            return <option key={monthKey} value={monthKey}>
              {new Date(Number(year), Number(month) - 1, 1).toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })}
            </option>;
          })}
        </select>
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
                <th>Especialidade</th>
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
                  <td>{appt.doctor_specialty}</td>
                  <td>{new Date(appt.appointment_datetime).toLocaleString()}</td>
                  <td>
                    <span className={`status-badge status-${appt.status}`}>
                      {appointmentStatusLabel(appt.status)}
                    </span>
                  </td>
                  <td className="patient-prescription-cell">
                    {records.find((record) => record.appointment_id === appt.id)?.prescription || 'Não disponível'}
                  </td>
                  <td>
                    {records.some((record) => record.appointment_id === appt.id) && (
                      <button type="button" className="btn btn-secondary" onClick={() => setSelectedRecord(selectedRecord?.appointment_id === appt.id ? null : records.find((record) => record.appointment_id === appt.id))}>
                        {selectedRecord?.appointment_id === appt.id ? 'Fechar laudo' : 'Ver laudo'}
                      </button>
                    )}
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
                {selectedRecord?.appointment_id === appt.id && <tr className="expanded-record-row"><td colSpan="6">
                  <div className="inline-medical-record">
                    <h3>Laudo da consulta</h3>
                    <p><strong>Diagnóstico:</strong> {selectedRecord.diagnosis}</p>
                    {selectedRecord.treatment_plan && <p><strong>Tratamento:</strong> {selectedRecord.treatment_plan}</p>}
                    {selectedRecord.prescription && <p><strong>Medicamentos, horários e dias:</strong><br />{selectedRecord.prescription}</p>}
                    {selectedRecord.medical_certificate && <p><strong>Atestado:</strong><br />{selectedRecord.medical_certificate}</p>}
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
