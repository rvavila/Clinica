import React, { useState, useEffect } from 'react';
import appointmentService from '../../services/appointmentService';
import notificationService from '../../services/notificationService';
import medicalRecordService from '../../services/medicalRecordService';
import { appointmentStatusLabel, consultationTypeLabel } from '../../utils/appointmentLabels';
import { ageLabel } from '../../utils/patientInfo';

const DoctorDashboard = () => {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [notifications, setNotifications] = useState([]);
  const [records, setRecords] = useState([]);
  const [recordForm, setRecordForm] = useState(null);
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [recordMessage, setRecordMessage] = useState('');
  const [activeTab, setActiveTab] = useState('dashboard');
  const [agendaStatus, setAgendaStatus] = useState('all');
  const [agendaSearch, setAgendaSearch] = useState('');
  const [agendaMonth, setAgendaMonth] = useState(() => {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  });

  useEffect(() => {
    const fetchAppointments = async () => {
      try {
        const [data, notificationData, recordData] = await Promise.all([
          appointmentService.list(0, 50),
          notificationService.list(),
          medicalRecordService.list(),
        ]);
        setAppointments(data);
        setNotifications(notificationData);
        setRecords(recordData);
      } catch (error) {
        console.error('Erro ao carregar agendamentos:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAppointments();
  }, []);

  const todayAppointments = appointments.filter((appt) => {
    const apptDate = new Date(appt.appointment_datetime).toDateString();
    const today = new Date().toDateString();
    return apptDate === today && appt.status !== 'cancelled';
  });
  const todayOpenAppointments = todayAppointments
    .filter((appt) => ['scheduled', 'confirmed', 'in_progress'].includes(appt.status))
    .sort((first, second) => new Date(first.appointment_datetime) - new Date(second.appointment_datetime));
  const todayCompletedAppointments = todayAppointments.filter((appt) => appt.status === 'completed');

  // A agenda operacional do médico mostra somente consultas pendentes ou em atendimento.
  // Consultas encerradas continuam no histórico para permitir a edição do laudo.
  const visibleAppointments = appointments.filter((appt) => {
    const appointmentDate = new Date(appt.appointment_datetime);
    const appointmentMonth = `${appointmentDate.getFullYear()}-${String(appointmentDate.getMonth() + 1).padStart(2, '0')}`;
    const search = agendaSearch.trim().toLowerCase();
    const matchesSearch = !search || appt.patient_name?.toLowerCase().includes(search);
    const matchesStatus = agendaStatus === 'all'
      || (agendaStatus === 'open' && ['scheduled', 'confirmed', 'in_progress'].includes(appt.status))
      || appt.status === agendaStatus;
    const matchesMonth = agendaMonth === 'all' || appointmentMonth === agendaMonth;
    return matchesSearch && matchesMonth && matchesStatus;
  });
  const agendaMonthOptions = [...new Set(appointments.map((appt) => {
    const date = new Date(appt.appointment_datetime);
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
  }))].sort().reverse();
  const activeAppointment = appointments.find((appt) => appt.status === 'in_progress');
  const nextAppointment = todayOpenAppointments.find((appt) => ['scheduled', 'confirmed'].includes(appt.status));

  const isToday = (appointment) => (
    new Date(appointment.appointment_datetime).toDateString() === new Date().toDateString()
  );

  const cancelAppointment = async (appointment) => {
    if (!window.confirm('Cancelar esta consulta? O paciente e a recepção serão avisados.')) return;
    try {
      await appointmentService.cancel(appointment.id);
      setAppointments((current) => current.map((item) => (
        item.id === appointment.id ? { ...item, status: 'cancelled' } : item
      )));
    } catch (error) {
      window.alert(error.response?.data?.detail || 'Não foi possível cancelar a consulta.');
    }
  };

  const changeAppointmentStatus = async (appointment, nextStatus) => {
    try {
      const updated = await appointmentService.update(appointment.id, { status: nextStatus });
      setAppointments((current) => current.map((item) => item.id === updated.id ? updated : item));
      if (nextStatus === 'in_progress') openRecord({ ...updated, patient_name: appointment.patient_name });
    } catch (error) {
      window.alert(error.response?.data?.detail || 'Não foi possível atualizar o atendimento.');
    }
  };

  const saveRecord = async (event) => {
    event.preventDefault();
    try {
      const recordData = {
        ...recordForm,
        patient_id: Number(recordForm.patient_id),
        doctor_id: Number(recordForm.doctor_id),
        appointment_id: Number(recordForm.appointment_id),
      };
      const saved = recordForm.id
        ? await medicalRecordService.update(recordForm.id, recordData)
        : await medicalRecordService.create(recordData);
      setRecords((current) => [saved, ...current.filter((item) => item.appointment_id !== saved.appointment_id)]);
      setAppointments((current) => current.map((item) => (
        item.id === Number(recordForm.appointment_id) ? { ...item, status: 'completed' } : item
      )));
      setRecordForm(null);
      setActiveTab('dashboard');
      setRecordMessage('Laudo salvo com sucesso.');
    } catch (error) {
      setRecordMessage(error.response?.data?.detail || 'Não foi possível salvar o laudo.');
    }
  };

  const printCertificate = (record) => {
    const printWindow = window.open('', '_blank', 'width=800,height=700');
    printWindow.document.write(`<html><head><title>Atestado médico</title><style>body{font-family:Arial;padding:48px;line-height:1.6}h1{text-align:center}.signature{margin-top:80px;text-align:center}</style></head><body><h1>Atestado médico</h1><p>${record.medical_certificate || 'Atestado não informado.'}</p><div class="signature">__________________________________<br/>Assinatura médica</div></body></html>`);
    printWindow.document.close();
    printWindow.print();
  };

  const printMedicalRecord = (record, appointment) => {
    const printWindow = window.open('', '_blank', 'width=850,height=750');
    printWindow.document.write(`<html><head><title>Laudo médico</title><style>body{font-family:Arial;padding:48px;color:#1f3032;line-height:1.55}h1{color:#214f50;border-bottom:2px solid #d8e9e4;padding-bottom:14px}.meta{margin-bottom:28px}.field{margin:18px 0}.field strong{display:block;color:#214f50;margin-bottom:4px}.signature{margin-top:70px;text-align:center}</style></head><body><h1>Laudo médico</h1><div class="meta"><strong>Paciente:</strong> ${appointment.patient_name}<br/><strong>Data:</strong> ${new Date(appointment.appointment_datetime).toLocaleString('pt-BR')}</div><div class="field"><strong>Queixa principal</strong>${record.chief_complaint || 'Não informado.'}</div><div class="field"><strong>Diagnóstico</strong>${record.diagnosis || 'Não informado.'}</div><div class="field"><strong>Plano de tratamento</strong>${record.treatment_plan || 'Não informado.'}</div><div class="field"><strong>Prescrição</strong>${record.prescription || 'Não informada.'}</div><div class="signature">__________________________________<br/>Assinatura médica</div></body></html>`);
    printWindow.document.close();
    printWindow.print();
  };

  const openRecord = (appointment) => {
    setSelectedAppointment(appointment);
    const existing = records.find((record) => record.appointment_id === appointment.id);
    setRecordForm(existing ? { ...existing } : {
      patient_id: appointment.patient_id,
      doctor_id: appointment.doctor_id,
      appointment_id: appointment.id,
      chief_complaint: '', diagnosis: '', treatment_plan: '', prescription: '', medical_certificate: '',
    });
    setActiveTab('care');
  };

  return (
    <div>
      <div className="doctor-tabs" role="tablist" aria-label="Navegação do médico">
        <button type="button" className={activeTab === 'dashboard' ? 'active' : ''} onClick={() => setActiveTab('dashboard')}>Dashboard</button>
        <button type="button" className={activeTab === 'agenda' ? 'active' : ''} onClick={() => setActiveTab('agenda')}>Agenda completa</button>
        <button type="button" className={activeTab === 'care' ? 'active' : ''} onClick={() => { if (!recordForm && activeAppointment) openRecord(activeAppointment); else setActiveTab('care'); }} disabled={!recordForm && !activeAppointment}>Atendimento</button>
      </div>
      {activeTab === 'dashboard' && <>
      <div className="doctor-summary-hidden">
        <div className="dashboard-card">
          <h3>Agendamentos de Hoje</h3>
          <div className="stat-value">{todayAppointments.length}</div>
          <div className="stat-label">Consultas agendadas</div>
        </div>

        <div className="dashboard-card">
          <h3>Total de Agendamentos</h3>
          <div className="stat-value">{visibleAppointments.length}</div>
          <div className="stat-label">Todos os períodos</div>
        </div>
      </div>

      <div className="doctor-call-panel">
        <div>
          <span className="doctor-call-kicker">Atendimento da vez</span>
          <h2>{activeAppointment
            ? activeAppointment.patient_name
            : nextAppointment
              ? `Próximo: ${nextAppointment.patient_name}`
              : 'Atendimentos do dia encerrados'}</h2>
          <p>{activeAppointment
            ? 'Paciente chamado. O atendimento está em andamento.'
            : nextAppointment
              ? 'O próximo paciente está aguardando para ser chamado.'
              : 'Não há mais pacientes aguardando atendimento hoje.'}</p>
        </div>
        {activeAppointment && !recordForm && (
          <button type="button" className="btn btn-primary doctor-call-button" onClick={() => openRecord(activeAppointment)}>
            Retomar atendimento {activeAppointment.patient_name}
          </button>
        )}
        {!activeAppointment && nextAppointment && (
          <button type="button" className="btn btn-primary doctor-call-button" onClick={() => changeAppointmentStatus(nextAppointment, 'in_progress')}>
            Chamar paciente {nextAppointment.patient_name}
          </button>
        )}
      </div>

      <div className="dashboard-section today-open-section">
        <h2>Consultas de hoje</h2>
        {todayOpenAppointments.length > 0 ? (
          <div className="reception-today-list">
            {todayOpenAppointments.map((appt) => (
              <div className={`today-appointment-card ${appt.status === 'in_progress' ? 'is-active' : ''}`} key={appt.id}>
                <div className="today-appointment-main">
                  <strong>{appt.patient_name}</strong>
                  <span>{ageLabel(appt.patient_date_of_birth)} · {appt.doctor_specialty} · {consultationTypeLabel(appt.consultation_type)} · {new Date(appt.appointment_datetime).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}</span>
                </div>
                <div className="today-appointment-actions">
                  <span className={`status-badge status-${appt.status}`}>{appointmentStatusLabel(appt.status)}</span>
                  {['scheduled', 'confirmed'].includes(appt.status) && <button type="button" className="btn btn-primary" disabled={Boolean(activeAppointment)} onClick={() => changeAppointmentStatus(appt, 'in_progress')}>Chamar paciente</button>}
                </div>
              </div>
            ))}
          </div>
        ) : <div className="card"><div className="empty-state"><p>Os atendimentos de hoje foram encerrados.</p></div></div>}
      </div>

      <div className="doctor-agenda-inline-hidden">
        <h2>Agenda completa</h2>

        <div className="appointment-filters" aria-label="Filtros da agenda médica">
          <input type="search" placeholder="Buscar paciente" value={agendaSearch} onChange={(event) => setAgendaSearch(event.target.value)} />
          <select value={agendaStatus} onChange={(event) => setAgendaStatus(event.target.value)}>
            <option value="open">Em aberto e em atendimento</option>
            <option value="all">Todas as consultas</option>
            <option value="completed">Concluídas</option>
          </select>
          <select value={agendaMonth} onChange={(event) => setAgendaMonth(event.target.value)}>
            <option value="all">Todos os meses</option>
            {agendaMonthOptions.map((month) => <option key={month} value={month}>{new Date(`${month}-01T12:00:00`).toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })}</option>)}
          </select>
        </div>

        {loading ? (
          <div className="spinner"></div>
        ) : visibleAppointments.length > 0 ? (
          <div className="card">
            <table className="appointments-table">
              <thead>
                <tr>
                  <th>Paciente</th>
                  <th>Data</th>
                  <th>Hora</th>
                  <th>Tipo</th>
                  <th>Status</th>
                  <th>Ação</th>
                </tr>
              </thead>
              <tbody>
                {visibleAppointments.map((appt) => (
                  <tr key={appt.id}>
                    <td>{appt.patient_name}</td>
                    <td>{new Date(appt.appointment_datetime).toLocaleDateString('pt-BR')}</td>
                    <td>{new Date(appt.appointment_datetime).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}</td>
                    <td>{consultationTypeLabel(appt.consultation_type)}</td>
                    <td>
                      <span className={`status-badge status-${appt.status}`}>
                        {appointmentStatusLabel(appt.status)}
                      </span>
                    </td>
                    <td>
                      {appt.status !== 'cancelled' && <button type="button" className="btn btn-secondary" onClick={() => openRecord(appt)} disabled={!['in_progress', 'completed'].includes(appt.status)}>
                        {records.some((record) => record.appointment_id === appt.id) ? 'Editar laudo' : 'Laudo'}
                      </button>}{' '}
                      {['scheduled', 'confirmed'].includes(appt.status) && isToday(appt) && <button type="button" className="btn btn-primary" disabled={Boolean(activeAppointment)} title={activeAppointment ? 'Encerre o atendimento atual antes de chamar outro paciente' : ''} onClick={() => changeAppointmentStatus(appt, 'in_progress')}>Chamar paciente</button>}{' '}
                      {appt.status === 'in_progress' && <button type="button" className="btn btn-success" onClick={() => changeAppointmentStatus(appt, 'completed')}>Encerrar consulta</button>}{' '}
                      {records.find((record) => record.appointment_id === appt.id)?.medical_certificate && <button type="button" className="btn btn-secondary" onClick={() => printCertificate(records.find((record) => record.appointment_id === appt.id))}>Imprimir atestado</button>}{' '}
                      {['scheduled', 'confirmed'].includes(appt.status) ? (
                        <button type="button" className="btn btn-danger" onClick={() => cancelAppointment(appt)}>
                          Cancelar
                        </button>
                      ) : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="card">
            <div className="empty-state">
              <p>Nenhuma consulta agendada para hoje</p>
            </div>
          </div>
        )}
      </div>

      <div className="dashboard-section completed-appointments-section">
        <h2>Consultas concluídas</h2>
        {todayCompletedAppointments.length > 0 ? (
          <div className="card">
            <table className="appointments-table">
              <thead><tr><th>Paciente</th><th>Hora</th><th>Tipo</th><th>Ação</th></tr></thead>
              <tbody>{todayCompletedAppointments.map((appt) => (
                <tr key={appt.id}>
                  <td>{appt.patient_name}</td>
                  <td>{new Date(appt.appointment_datetime).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}</td>
                  <td>{consultationTypeLabel(appt.consultation_type)}</td>
                  <td>
                    <button type="button" className="btn btn-secondary" onClick={() => openRecord(appt)}>{records.some((record) => record.appointment_id === appt.id) ? 'Editar laudo' : 'Laudo'}</button>{' '}
                    {records.find((record) => record.appointment_id === appt.id) && <button type="button" className="btn btn-secondary" onClick={() => printMedicalRecord(records.find((record) => record.appointment_id === appt.id), appt)}>Imprimir laudo</button>}{' '}
                    {records.find((record) => record.appointment_id === appt.id)?.medical_certificate && <button type="button" className="btn btn-secondary" onClick={() => printCertificate(records.find((record) => record.appointment_id === appt.id))}>Imprimir atestado</button>}
                  </td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        ) : <div className="card"><div className="empty-state"><p>Nenhuma consulta concluída hoje.</p></div></div>}
      </div>
      </>}
      {activeTab === 'agenda' && <div className="dashboard-section doctor-full-agenda">
        <h2>Agenda completa</h2>
        <div className="appointment-filters" aria-label="Filtros da agenda médica">
          <input type="search" placeholder="Buscar paciente" value={agendaSearch} onChange={(event) => setAgendaSearch(event.target.value)} />
          <select value={agendaMonth} onChange={(event) => setAgendaMonth(event.target.value)}>
            <option value="all">Todos os meses</option>
            {agendaMonthOptions.map((month) => <option key={month} value={month}>{new Date(`${month}-01T12:00:00`).toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })}</option>)}
          </select>
          <select value={agendaStatus} onChange={(event) => setAgendaStatus(event.target.value)}>
            <option value="all">Todos os status</option>
            <option value="open">Em aberto e em atendimento</option>
            <option value="scheduled">Agendadas</option>
            <option value="in_progress">Em atendimento</option>
            <option value="completed">Concluídas</option>
            <option value="cancelled">Canceladas</option>
          </select>
          <span className="filter-result-count">{visibleAppointments.length} resultado(s)</span>
        </div>
        {loading ? <div className="spinner"></div> : visibleAppointments.length > 0 ? (
          <div className="card">
            <table className="appointments-table">
              <thead><tr><th>Paciente</th><th>Data</th><th>Hora</th><th>Tipo</th><th>Status</th><th>Ação</th></tr></thead>
              <tbody>{visibleAppointments.map((appt) => {
                const record = records.find((item) => item.appointment_id === appt.id);
                return <tr key={appt.id}>
                  <td>{appt.patient_name}</td>
                  <td>{new Date(appt.appointment_datetime).toLocaleDateString('pt-BR')}</td>
                  <td>{new Date(appt.appointment_datetime).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}</td>
                  <td>{consultationTypeLabel(appt.consultation_type)}</td>
                  <td><span className={`status-badge status-${appt.status}`}>{appointmentStatusLabel(appt.status)}</span></td>
                  <td>
                    {['in_progress', 'completed'].includes(appt.status) && <button type="button" className="btn btn-secondary" onClick={() => openRecord(appt)}>{record ? 'Editar laudo' : 'Laudo'}</button>}{' '}
                    {record && <button type="button" className="btn btn-secondary" onClick={() => printMedicalRecord(record, appt)}>Imprimir laudo</button>}{' '}
                    {record?.medical_certificate && <button type="button" className="btn btn-secondary" onClick={() => printCertificate(record)}>Imprimir atestado</button>}{' '}
                    {['scheduled', 'confirmed'].includes(appt.status) && isToday(appt) && <button type="button" className="btn btn-primary" disabled={Boolean(activeAppointment)} onClick={() => changeAppointmentStatus(appt, 'in_progress')}>Chamar paciente</button>}
                  </td>
                </tr>;
              })}</tbody>
            </table>
          </div>
        ) : <div className="card"><div className="empty-state"><p>Nenhuma consulta encontrada para os filtros selecionados.</p></div></div>}
      </div>}
      {activeTab === 'care' && recordForm && <div className="dashboard-section card doctor-care-panel">
        <div className="care-active-patient">
          <span>ATENDIMENTO EM ANDAMENTO</span>
          <strong>{selectedAppointment?.patient_name || activeAppointment?.patient_name || 'Paciente selecionado'}</strong>
          <em>Laudo vinculado a esta consulta</em>
        </div>
        <h2>Laudo do paciente {selectedAppointment?.patient_name || 'selecionado'}</h2>
        <p className="form-help">Preencha o laudo após chamar o paciente. Ele ficará vinculado a esta consulta.</p>
        <form className="appointment-form" onSubmit={saveRecord}>
          <label>Queixa principal<textarea required value={recordForm.chief_complaint || ''} onChange={(e) => setRecordForm({ ...recordForm, chief_complaint: e.target.value })} /></label>
          <label>Diagnóstico<textarea required value={recordForm.diagnosis || ''} onChange={(e) => setRecordForm({ ...recordForm, diagnosis: e.target.value })} /></label>
          <label>Plano de tratamento<textarea value={recordForm.treatment_plan || ''} onChange={(e) => setRecordForm({ ...recordForm, treatment_plan: e.target.value })} /></label>
          <label>Medicamentos, horários e dias<textarea placeholder="Ex.: Amoxicilina 500mg — 1 comprimido às 8h e 20h por 7 dias" value={recordForm.prescription || ''} onChange={(e) => setRecordForm({ ...recordForm, prescription: e.target.value })} /></label>
          <label>Atestado médico<textarea placeholder="Texto do atestado para impressão" value={recordForm.medical_certificate || ''} onChange={(e) => setRecordForm({ ...recordForm, medical_certificate: e.target.value })} /></label>
          <div className="form-actions"><button className="btn btn-primary">Salvar laudo</button><button type="button" className="btn btn-secondary" onClick={() => { setRecordForm(null); setActiveTab('dashboard'); }}>Voltar</button></div>
        </form>
      </div>}
      {activeTab === 'dashboard' && recordMessage && <div className="alert alert-success">{recordMessage}</div>}
      {activeTab === 'dashboard' && <div className="dashboard-section doctor-notifications">
        <h2>Cancelamentos recentes</h2>
        <div className="card notification-list">
          {notifications.length > 0 ? notifications.map((notification) => (
            <p key={notification.id}>{notification.message}</p>
          )) : <p>Nenhum cancelamento recente.</p>}
        </div>
      </div>}
    </div>
  );
};

export default DoctorDashboard;
