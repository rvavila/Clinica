import React, { useState, useEffect } from 'react';
import appointmentService from '../../services/appointmentService';
import doctorService from '../../services/doctorService';
import patientService from '../../services/patientService';
import userService from '../../services/userService';
import notificationService from '../../services/notificationService';
import { appointmentStatusLabel, consultationTypeLabel } from '../../utils/appointmentLabels';
import { sortAppointmentsByDate } from '../../utils/appointmentSort';
import { ageLabel } from '../../utils/patientInfo';

const appointmentTimeSlots = Array.from({ length: 29 }, (_, index) => {
  const totalMinutes = 8 * 60 + index * 30;
  return `${String(Math.floor(totalMinutes / 60)).padStart(2, '0')}:${String(totalMinutes % 60).padStart(2, '0')}`;
});

const localDateKey = (date = new Date()) => (
  `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
);

const ReceptionDashboard = () => {
  const [activeView, setActiveView] = useState('dashboard');
  const [appointments, setAppointments] = useState([]);
  const [patients, setPatients] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [unassignedDoctors, setUnassignedDoctors] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [patientSaving, setPatientSaving] = useState(false);
  const [formError, setFormError] = useState('');
  const [formSuccess, setFormSuccess] = useState('');
  const [patientError, setPatientError] = useState('');
  const [patientSuccess, setPatientSuccess] = useState('');
  const [editingPatient, setEditingPatient] = useState(null);
  const [editPatientData, setEditPatientData] = useState({
    full_name: '',
    email: '',
    cpf: '',
    phone: '',
    date_of_birth: '',
    gender: '',
    password: '',
  });
  const [patientFormData, setPatientFormData] = useState({
    full_name: '',
    email: '',
    cpf: '',
    phone: '',
    password: '12345678',
    date_of_birth: '',
    gender: '',
  });
  const [formData, setFormData] = useState({
    patient_id: '',
    doctor_id: '',
    appointment_date: '',
    appointment_time: '',
    consultation_type: 'follow_up',
  });
  const [doctorFormData, setDoctorFormData] = useState({
    user_id: '',
    crm: '',
    specialty: 'Medicina Geral',
  });
  const [doctorError, setDoctorError] = useState('');
  const [doctorSuccess, setDoctorSuccess] = useState('');
  const [doctorSaving, setDoctorSaving] = useState(false);
  const [editingDoctor, setEditingDoctor] = useState(null);
  const [appointmentSearch, setAppointmentSearch] = useState('');
  const [appointmentStatus, setAppointmentStatus] = useState('all');
  const [appointmentPeriod, setAppointmentPeriod] = useState('today');
  const [appointmentPage, setAppointmentPage] = useState(1);
  const [editDoctorData, setEditDoctorData] = useState({
    full_name: '',
    email: '',
    phone: '',
    crm: '',
    specialty: '',
    office_phone: '',
    vacation_start: '',
    vacation_end: '',
    password: '',
  });

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [appointmentData, patientData, doctorData, unassignedDoctorData, notificationData] = await Promise.all([
          appointmentService.list(0, 100),
          patientService.list(0, 100),
          doctorService.list(0, 100),
          doctorService.listUnassignedUsers(),
          notificationService.list(),
        ]);
        setAppointments(appointmentData);
        setPatients(patientData);
        setDoctors(doctorData);
        setUnassignedDoctors(unassignedDoctorData);
        setNotifications(notificationData);
      } catch (error) {
        setFormError(error.response?.data?.detail || 'Erro ao carregar dados da recepção');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  useEffect(() => {
    const refreshReceptionBoard = async () => {
      try {
        const [appointmentData, notificationData] = await Promise.all([
          appointmentService.list(0, 100),
          notificationService.list(),
        ]);
        setAppointments(appointmentData);
        setNotifications(notificationData);
      } catch (error) {
        console.error('Erro ao atualizar o painel da recepção:', error);
      }
    };
    const interval = window.setInterval(refreshReceptionBoard, 5000);
    return () => window.clearInterval(interval);
  }, []);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((previous) => ({
      ...previous,
      [name]: value,
      ...(name === 'doctor_id' || name === 'appointment_date' ? { appointment_time: '' } : {}),
    }));
  };

  const selectedDate = formData.appointment_date;
  const todayKey = localDateKey();
  const currentTime = `${String(new Date().getHours()).padStart(2, '0')}:${String(new Date().getMinutes()).padStart(2, '0')}`;
  const bookedTimes = appointments
    .filter((appointment) => (
      appointment.doctor_id === Number(formData.doctor_id)
      && appointment.status !== 'cancelled'
      && selectedDate
    ))
    .map((appointment) => {
      const date = new Date(appointment.appointment_datetime);
      const dateKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
      return dateKey === selectedDate
        ? `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
        : null;
    })
    .filter(Boolean);
  const availableTimeSlots = appointmentTimeSlots.filter((time) => (
    !bookedTimes.includes(time) && !(selectedDate === todayKey && time <= currentTime)
  ));

  const handleCreateAppointment = async (event) => {
    event.preventDefault();
    setFormError('');
    setFormSuccess('');
    setSaving(true);

    try {
      await appointmentService.create({
        consultation_type: formData.consultation_type,
        appointment_datetime: `${formData.appointment_date}T${formData.appointment_time}`,
        patient_id: Number(formData.patient_id),
        doctor_id: Number(formData.doctor_id),
      });
      setFormData({
        patient_id: '',
        doctor_id: '',
        appointment_date: '',
        appointment_time: '',
        consultation_type: 'follow_up',
      });
      setFormSuccess('Agendamento criado com sucesso.');
      setAppointments(await appointmentService.list(0, 100));
    } catch (error) {
      setFormError(error.response?.data?.detail || 'Erro ao criar agendamento');
    } finally {
      setSaving(false);
    }
  };

  const handleReceptionCancel = async (appointment) => {
    if (!window.confirm('Cancelar esta consulta? O médico e o paciente serão avisados.')) return;
    try {
      await appointmentService.cancel(appointment.id);
      setAppointments(await appointmentService.list(0, 100));
      setFormSuccess('Consulta cancelada. Médico e paciente foram avisados.');
    } catch (error) {
      setFormError(error.response?.data?.detail || 'Não foi possível cancelar a consulta.');
    }
  };

  const handleReceptionReschedule = async (appointment) => {
    const current = new Date(appointment.appointment_datetime);
    const value = window.prompt('Nova data e hora (AAAA-MM-DDTHH:mm):', current.toISOString().slice(0, 16));
    if (!value || value === appointment.appointment_datetime) return;
    try {
      await appointmentService.update(appointment.id, { appointment_datetime: value });
      setAppointments(await appointmentService.list(0, 100));
      setFormSuccess('Consulta remarcada. Médico e paciente foram avisados.');
    } catch (error) {
      setFormError(error.response?.data?.detail || 'Não foi possível remarcar a consulta.');
    }
  };

  const handlePatientChange = (event) => {
    const { name, value } = event.target;
    setPatientFormData((previous) => ({ ...previous, [name]: value }));
  };

  const handleCreatePatient = async (event) => {
    event.preventDefault();
    setPatientError('');
    setPatientSuccess('');
    setPatientSaving(true);

    try {
      await patientService.register({
        full_name: patientFormData.full_name,
        email: patientFormData.email,
        cpf: patientFormData.cpf,
        phone: patientFormData.phone || null,
        password: patientFormData.password,
        date_of_birth: patientFormData.date_of_birth || null,
        gender: patientFormData.gender || null,
      });

      setPatients(await patientService.list(0, 100));
      setPatientFormData({
        full_name: '',
        email: '',
        cpf: '',
        phone: '',
        password: '12345678',
        date_of_birth: '',
        gender: '',
      });
      setPatientSuccess('Paciente cadastrado com sucesso.');
    } catch (error) {
      setPatientError(error.response?.data?.detail || 'Erro ao cadastrar paciente');
    } finally {
      setPatientSaving(false);
    }
  };

  const startEditingPatient = (patient) => {
    setPatientError('');
    setPatientSuccess('');
    setEditingPatient(patient);
    setEditPatientData({
      full_name: patient.full_name,
      email: patient.email,
      cpf: patient.cpf,
      phone: patient.phone || '',
      date_of_birth: patient.date_of_birth || '',
      gender: patient.gender || '',
      password: '',
    });
  };

  const handleEditPatientChange = (event) => {
    const { name, value } = event.target;
    setEditPatientData((previous) => ({ ...previous, [name]: value }));
  };

  const handleUpdatePatient = async (event) => {
    event.preventDefault();
    setPatientError('');
    setPatientSuccess('');
    setPatientSaving(true);

    try {
      await userService.update(editingPatient.user_id, {
        full_name: editPatientData.full_name,
        email: editPatientData.email,
        cpf: editPatientData.cpf,
        phone: editPatientData.phone || null,
      });
      await patientService.update(editingPatient.id, {
        date_of_birth: editPatientData.date_of_birth || null,
        gender: editPatientData.gender || null,
      });
      if (editPatientData.password) {
        await userService.resetPassword(editingPatient.user_id, editPatientData.password);
      }

      setPatients(await patientService.list(0, 100));
      setEditingPatient(null);
      setPatientSuccess('Cadastro do paciente atualizado com sucesso.');
    } catch (error) {
      setPatientError(error.response?.data?.detail || 'Erro ao atualizar paciente');
    } finally {
      setPatientSaving(false);
    }
  };

  const handleDoctorChange = (event) => {
    const { name, value } = event.target;
    setDoctorFormData((previous) => ({ ...previous, [name]: value }));
  };

  const handleCreateDoctorProfile = async (event) => {
    event.preventDefault();
    setDoctorError('');
    setDoctorSuccess('');
    try {
      await doctorService.createProfile({
        user_id: Number(doctorFormData.user_id),
        crm: doctorFormData.crm,
        specialty: doctorFormData.specialty,
      });
      setDoctors(await doctorService.list(0, 100));
      setUnassignedDoctors(await doctorService.listUnassignedUsers());
      setDoctorFormData({ user_id: '', crm: '', specialty: 'Medicina Geral' });
      setDoctorSuccess('Médico disponibilizado para agendamento.');
    } catch (error) {
      setDoctorError(error.response?.data?.detail || 'Erro ao cadastrar médico');
    }
  };

  const startEditingDoctor = (doctor) => {
    setDoctorError('');
    setDoctorSuccess('');
    setEditingDoctor(doctor);
    setEditDoctorData({
      full_name: doctor.full_name,
      email: doctor.email,
      phone: doctor.phone || '',
      crm: doctor.crm,
      specialty: doctor.specialty,
      office_phone: doctor.office_phone || '',
      vacation_start: doctor.vacation_start ? doctor.vacation_start.slice(0, 16) : '',
      vacation_end: doctor.vacation_end ? doctor.vacation_end.slice(0, 16) : '',
      password: '',
    });
  };

  const handleEditDoctorChange = (event) => {
    const { name, value } = event.target;
    setEditDoctorData((previous) => ({ ...previous, [name]: value }));
  };

  const handleUpdateDoctor = async (event) => {
    event.preventDefault();
    setDoctorError('');
    setDoctorSuccess('');
    setDoctorSaving(true);

    try {
      await userService.update(editingDoctor.user_id, {
        full_name: editDoctorData.full_name,
        email: editDoctorData.email,
        phone: editDoctorData.phone || null,
      });
      await doctorService.update(editingDoctor.id, {
        crm: editDoctorData.crm,
        specialty: editDoctorData.specialty,
        office_phone: editDoctorData.office_phone || null,
        vacation_start: editDoctorData.vacation_start || null,
        vacation_end: editDoctorData.vacation_end || null,
      });
      if (editDoctorData.password) {
        await userService.resetPassword(editingDoctor.user_id, editDoctorData.password);
      }

      setDoctors(await doctorService.list(0, 100));
      setEditingDoctor(null);
      setDoctorSuccess('Cadastro do médico atualizado com sucesso.');
    } catch (error) {
      setDoctorError(error.response?.data?.detail || 'Erro ao atualizar médico');
    } finally {
      setDoctorSaving(false);
    }
  };

  const todayAppointments = appointments.filter((appt) => {
    const apptDate = new Date(appt.appointment_datetime).toDateString();
    const today = new Date().toDateString();
    return apptDate === today;
  });
  const calledAppointment = todayAppointments.find((appt) => appt.status === 'in_progress');
  const todayOpenAppointments = todayAppointments
    .filter((appt) => ['scheduled', 'confirmed', 'in_progress'].includes(appt.status))
    .sort((first, second) => new Date(first.appointment_datetime) - new Date(second.appointment_datetime));

  const vacationLabel = (doctor) => {
    if (!doctor.vacation_start || !doctor.vacation_end) return { text: 'Disponível', className: 'status-confirmed' };
    const start = new Date(doctor.vacation_start);
    const end = new Date(doctor.vacation_end);
    const now = new Date();
    const format = (date) => date.toLocaleDateString('pt-BR');
    if (now >= start && now <= end) return { text: `Em férias até ${format(end)}`, className: 'status-cancelled' };
    if (now < start) return { text: `Férias programadas: ${format(start)} a ${format(end)}`, className: 'status-completed' };
    return { text: 'Disponível', className: 'status-confirmed' };
  };

  const scheduledAppointments = appointments.filter(
    (appt) => ['scheduled', 'confirmed'].includes(appt.status)
  );

  const filteredAppointments = sortAppointmentsByDate(appointments.filter((appointment) => {
    const search = appointmentSearch.trim().toLowerCase();
    const appointmentDate = new Date(appointment.appointment_datetime);
    const today = new Date();
    const matchesSearch = !search
      || appointment.patient_name?.toLowerCase().includes(search)
      || appointment.doctor_name?.toLowerCase().includes(search);
    const matchesStatus = appointmentStatus === 'all'
      || (appointmentStatus === 'open' && ['scheduled', 'confirmed', 'in_progress'].includes(appointment.status))
      || appointment.status === appointmentStatus;
    const matchesPeriod = appointmentPeriod === 'all'
      || (appointmentPeriod === 'today' && appointmentDate.toDateString() === today.toDateString())
      || (appointmentPeriod === 'upcoming' && appointmentDate >= today && appointment.status !== 'cancelled')
      || (appointmentPeriod === 'history' && ['completed', 'cancelled'].includes(appointment.status));
    return matchesSearch && matchesStatus && matchesPeriod;
  }));
  const appointmentsPerPage = 10;
  const appointmentTotalPages = Math.max(1, Math.ceil(filteredAppointments.length / appointmentsPerPage));
  const visibleAppointments = filteredAppointments.slice(
    (appointmentPage - 1) * appointmentsPerPage,
    appointmentPage * appointmentsPerPage,
  );

  return (
    <div>
      <nav className="reception-nav" aria-label="Navegação da recepção">
        <button type="button" className={activeView === 'dashboard' ? 'active' : ''} onClick={() => setActiveView('dashboard')}>Dashboard</button>
        <button type="button" className={activeView === 'appointments' ? 'active' : ''} onClick={() => setActiveView('appointments')}>Novo agendamento</button>
        <button type="button" className={activeView === 'patients' ? 'active' : ''} onClick={() => setActiveView('patients')}>Pacientes</button>
        <button type="button" className={activeView === 'doctors' ? 'active' : ''} onClick={() => setActiveView('doctors')}>Médicos</button>
      </nav>

      {activeView === 'patients' && <div className="dashboard-section">
        <h2>Cadastrar Paciente</h2>
        {patientError && <div className="alert alert-error">{patientError}</div>}
        {patientSuccess && <div className="alert alert-success">{patientSuccess}</div>}
        <form className="appointment-form patient-register-form" onSubmit={handleCreatePatient}>
          <fieldset className="form-section-card">
            <legend>Dados pessoais</legend>
            <div className="form-section-grid">
              <label>Nome completo<input name="full_name" value={patientFormData.full_name} onChange={handlePatientChange} required /></label>
              <label>Email<input name="email" type="email" value={patientFormData.email} onChange={handlePatientChange} required /></label>
              <label>CPF<input name="cpf" value={patientFormData.cpf} onChange={handlePatientChange} minLength="11" required /></label>
              <label>Telefone<input name="phone" value={patientFormData.phone} onChange={handlePatientChange} /></label>
            </div>
          </fieldset>

          <fieldset className="form-section-card">
            <legend>Informações do paciente</legend>
            <div className="form-section-grid">
              <label>Data de nascimento<input name="date_of_birth" type="date" value={patientFormData.date_of_birth} onChange={handlePatientChange} /></label>
              <label>Sexo<select name="gender" value={patientFormData.gender} onChange={handlePatientChange}><option value="">Não informado</option><option value="Feminino">Feminino</option><option value="Masculino">Masculino</option></select></label>
            </div>
          </fieldset>

          <fieldset className="form-section-card form-section-access">
            <legend>Acesso</legend>
            <div className="form-section-grid">
              <label>Senha inicial<input name="password" type="password" value={patientFormData.password} onChange={handlePatientChange} minLength="8" required /></label>
            </div>
          </fieldset>
          <button type="submit" className="btn btn-primary" disabled={patientSaving}>
            {patientSaving ? 'Salvando...' : 'Cadastrar paciente'}
          </button>
        </form>
      </div>}

      {activeView === 'appointments' && <div className="dashboard-section">
        <h2>Novo Agendamento</h2>
        {formError && <div className="alert alert-error">{formError}</div>}
        {formSuccess && <div className="alert alert-success">{formSuccess}</div>}
        <form className="appointment-form" onSubmit={handleCreateAppointment}>
          <label>
            Paciente
            <select name="patient_id" value={formData.patient_id} onChange={handleChange} required>
              <option value="">Selecione um paciente</option>
              {patients.map((patient) => (
                <option key={patient.id} value={patient.id}>
                  {patient.full_name} - {patient.cpf}
                </option>
              ))}
            </select>
          </label>
          <label>
            Médico
            <select name="doctor_id" value={formData.doctor_id} onChange={handleChange} required>
              <option value="">Selecione um médico</option>
              {doctors.map((doctor) => (
                <option key={doctor.id} value={doctor.id}>
                  {doctor.full_name} - {doctor.specialty}
                </option>
              ))}
            </select>
          </label>
          <label>
            Data da consulta
            <input name="appointment_date" type="date" min={todayKey} value={formData.appointment_date} onChange={handleChange} required />
          </label>
          <label>
            Horário — das 08:00 às 22:00
            <select name="appointment_time" value={formData.appointment_time} onChange={handleChange} required>
              <option value="">Selecione um horário</option>
              {availableTimeSlots.map((time) => <option key={time} value={time}>{time}</option>)}
            </select>
            {formData.doctor_id && formData.appointment_date && availableTimeSlots.length === 0 && <span className="form-help">Não há horários disponíveis para este médico nesta data.</span>}
          </label>
          <label>
            Tipo de consulta
            <select name="consultation_type" value={formData.consultation_type} onChange={handleChange}>
              <option value="first_visit">Primeira consulta</option>
              <option value="follow_up">Retorno</option>
              <option value="emergency">Emergência</option>
              <option value="procedure">Procedimento</option>
            </select>
          </label>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={saving || patients.length === 0 || doctors.length === 0}
          >
            {saving ? 'Salvando...' : 'Criar agendamento'}
          </button>
          {(patients.length === 0 || doctors.length === 0) && !loading && (
            <p className="form-help">É necessário ter pelo menos um paciente e um médico cadastrados.</p>
          )}
        </form>
      </div>}

      {activeView === 'patients' && <div className="dashboard-section">
        <h2>Pacientes cadastrados</h2>
        {editingPatient && (
          <form className="appointment-form" onSubmit={handleUpdatePatient}>
            <label>
              Nome completo
              <input name="full_name" value={editPatientData.full_name} onChange={handleEditPatientChange} required />
            </label>
            <label>
              Email
              <input name="email" type="email" value={editPatientData.email} onChange={handleEditPatientChange} required />
            </label>
            <label>
              CPF
              <input name="cpf" value={editPatientData.cpf} onChange={handleEditPatientChange} minLength="11" required />
            </label>
            <label>
              Telefone
              <input name="phone" value={editPatientData.phone} onChange={handleEditPatientChange} />
            </label>
            <label>
              Data de nascimento
              <input name="date_of_birth" type="date" value={editPatientData.date_of_birth} onChange={handleEditPatientChange} />
            </label>
            <label>
              Sexo
              <select name="gender" value={editPatientData.gender} onChange={handleEditPatientChange}>
                <option value="">Não informado</option>
                <option value="Feminino">Feminino</option>
                <option value="Masculino">Masculino</option>
              </select>
            </label>
            <label>
              Nova senha (opcional)
              <input name="password" type="password" value={editPatientData.password} onChange={handleEditPatientChange} minLength="8" placeholder="Deixe vazio para manter" />
            </label>
            <div className="form-actions">
              <button type="submit" className="btn btn-primary" disabled={patientSaving}>
                {patientSaving ? 'Salvando...' : 'Salvar alterações'}
              </button>
              <button type="button" className="btn btn-secondary" onClick={() => setEditingPatient(null)}>
                Cancelar
              </button>
            </div>
          </form>
        )}
        {patients.length > 0 ? (
          <div className="card">
            <table className="appointments-table">
              <thead>
                <tr>
                  <th>Paciente</th>
                  <th>Email</th>
                  <th>CPF</th>
                  <th>Idade</th>
                  <th>Telefone</th>
                  <th>Ação</th>
                </tr>
              </thead>
              <tbody>
                {patients.map((patient) => (
                  <tr key={patient.id}>
                    <td>{patient.full_name}</td>
                    <td>{patient.email}</td>
                    <td>{patient.cpf}</td>
                    <td>{ageLabel(patient.date_of_birth)}</td>
                    <td>{patient.phone || 'Não informado'}</td>
                    <td>
                      <button type="button" className="btn btn-secondary" onClick={() => startEditingPatient(patient)}>
                        Editar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          !loading && <div className="card"><div className="empty-state"><p>Nenhum paciente cadastrado</p></div></div>
        )}
      </div>}

      {activeView === 'doctors' && <div className="dashboard-section">
        <h2>Disponibilizar médico</h2>
        {doctorError && <div className="alert alert-error">{doctorError}</div>}
        {doctorSuccess && <div className="alert alert-success">{doctorSuccess}</div>}
        <form className="appointment-form" onSubmit={handleCreateDoctorProfile}>
          <label>
            Conta do médico
            <select name="user_id" value={doctorFormData.user_id} onChange={handleDoctorChange} required>
              <option value="">Selecione um médico</option>
              {unassignedDoctors.map((doctor) => <option key={doctor.id} value={doctor.id}>{doctor.full_name} - {doctor.email}</option>)}
            </select>
          </label>
          <label>
            CRM
            <input name="crm" value={doctorFormData.crm} onChange={handleDoctorChange} minLength="4" required placeholder="CRM 123456" />
          </label>
          <label>
            Especialidade
            <select name="specialty" value={doctorFormData.specialty} onChange={handleDoctorChange}>
              <option>Pediatria</option>
              <option>Cardiologia</option>
              <option>Dermatologia</option>
              <option>Medicina Geral</option>
              <option>Ortopedia</option>
            </select>
          </label>
          <button type="submit" className="btn btn-primary" disabled={unassignedDoctors.length === 0}>Salvar médico</button>
          {unassignedDoctors.length === 0 && <p className="form-help">Não há contas de médicos aguardando cadastro profissional.</p>}
        </form>

        <h2 className="subsection-title">Médicos disponíveis</h2>
        {editingDoctor && (
          <form className="appointment-form" onSubmit={handleUpdateDoctor}>
            <label>
              Nome completo
              <input name="full_name" value={editDoctorData.full_name} onChange={handleEditDoctorChange} required />
            </label>
            <label>
              Email
              <input name="email" type="email" value={editDoctorData.email} onChange={handleEditDoctorChange} required />
            </label>
            <label>
              Telefone
              <input name="phone" value={editDoctorData.phone} onChange={handleEditDoctorChange} />
            </label>
            <label>
              CRM
              <input name="crm" value={editDoctorData.crm} onChange={handleEditDoctorChange} minLength="4" required />
            </label>
            <label>
              Especialidade
              <select name="specialty" value={editDoctorData.specialty} onChange={handleEditDoctorChange} required>
                <option>Pediatria</option>
                <option>Cardiologia</option>
                <option>Dermatologia</option>
                <option>Medicina Geral</option>
                <option>Ortopedia</option>
              </select>
            </label>
            <label>
              Telefone do consultório
              <input name="office_phone" value={editDoctorData.office_phone} onChange={handleEditDoctorChange} />
            </label>
            <label>
              Início das férias (opcional)
              <input name="vacation_start" type="datetime-local" value={editDoctorData.vacation_start} onChange={handleEditDoctorChange} />
            </label>
            <label>
              Fim das férias (opcional)
              <input name="vacation_end" type="datetime-local" value={editDoctorData.vacation_end} onChange={handleEditDoctorChange} />
            </label>
            <label>
              Nova senha (opcional)
              <input name="password" type="password" value={editDoctorData.password} onChange={handleEditDoctorChange} minLength="8" placeholder="Deixe vazio para manter" />
            </label>
            <div className="form-actions">
              <button type="submit" className="btn btn-primary" disabled={doctorSaving}>
                {doctorSaving ? 'Salvando...' : 'Salvar alterações'}
              </button>
              <button type="button" className="btn btn-secondary" onClick={() => setEditingDoctor(null)}>
                Cancelar
              </button>
            </div>
          </form>
        )}
        {doctors.length > 0 ? (
          <div className="card">
            <table className="appointments-table">
              <thead>
                <tr>
                  <th>Médico</th>
                  <th>CRM</th>
                  <th>Status de agenda</th>
                  <th>Especialidade</th>
                  <th>Email</th>
                  <th>Ação</th>
                </tr>
              </thead>
              <tbody>
                {doctors.map((doctor) => (
                  <tr key={doctor.id}>
                    <td>{doctor.full_name}</td>
                    <td>{doctor.crm}</td>
                    <td><span className={`status-badge ${vacationLabel(doctor).className}`}>{vacationLabel(doctor).text}</span></td>
                    <td>{doctor.specialty}</td>
                    <td>{doctor.email}</td>
                    <td>
                      <button type="button" className="btn btn-secondary" onClick={() => startEditingDoctor(doctor)}>
                        Editar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="card"><div className="empty-state"><p>Nenhum médico disponibilizado</p></div></div>
        )}
      </div>}

      {activeView === 'dashboard' && <div className="reception-summary-hidden">
        <div className="dashboard-card">
          <h3>Agendamentos Hoje</h3>
          <div className="stat-value">{todayAppointments.length}</div>
          <div className="stat-label">Consultas do dia</div>
        </div>

        <div className="dashboard-card">
          <h3>Agendamentos Pendentes</h3>
          <div className="stat-value">{scheduledAppointments.length}</div>
          <div className="stat-label">Consultas em aberto</div>
        </div>

        <div className="dashboard-card">
          <h3>Total de Agendamentos</h3>
          <div className="stat-value">{appointments.length}</div>
          <div className="stat-label">Todos os registros</div>
        </div>
      </div>}

      {activeView === 'dashboard' && <>
      <div className={`reception-call-panel ${calledAppointment ? 'is-called' : ''}`}>
        <div>
          {calledAppointment && <strong className="reception-called-patient">{calledAppointment.patient_name}</strong>}
          <span className="reception-call-kicker">Chamada do consultório</span>
          <h2>{calledAppointment ? `Dr. ${calledAppointment.doctor_name} está chamando` : 'Nenhum paciente chamado agora'}</h2>
          <p>{calledAppointment ? `Favor orientar ${calledAppointment.patient_name} a entrar para o atendimento.` : 'A recepção será avisada assim que o médico chamar o próximo paciente.'}</p>
        </div>
        {calledAppointment && <span className="reception-call-badge">ENTRAR AGORA</span>}
      </div>

      <div className="dashboard-section today-open-section">
        <h2>Consultas de hoje</h2>
        {todayOpenAppointments.length > 0 ? (
          <div className="reception-today-list">
            {todayOpenAppointments.map((appt) => (
              <div className={`today-appointment-card ${appt.status === 'in_progress' ? 'is-active' : ''}`} key={appt.id}>
                <div className="today-appointment-main">
                  <strong>{appt.patient_name}</strong>
                  <span>{ageLabel(appt.patient_date_of_birth)} · {appt.doctor_name} ({appt.doctor_specialty}) · {consultationTypeLabel(appt.consultation_type)} · {new Date(appt.appointment_datetime).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}</span>
                </div>
                <span className={`status-badge status-${appt.status}`}>{appointmentStatusLabel(appt.status)}</span>
              </div>
            ))}
          </div>
        ) : <div className="card"><div className="empty-state"><p>Os atendimentos de hoje foram encerrados.</p></div></div>}
      </div>

      <div className="dashboard-section">
        <h2>Agenda completa</h2>

        <div className="appointment-filters" aria-label="Filtros da agenda">
          <input type="search" placeholder="Buscar paciente ou médico" value={appointmentSearch} onChange={(event) => { setAppointmentSearch(event.target.value); setAppointmentPage(1); }} />
          <select value={appointmentPeriod} onChange={(event) => { setAppointmentPeriod(event.target.value); setAppointmentPage(1); }}>
            <option value="all">Todos os períodos</option>
            <option value="today">Hoje</option>
            <option value="upcoming">Próximas</option>
            <option value="history">Histórico</option>
          </select>
          <select value={appointmentStatus} onChange={(event) => { setAppointmentStatus(event.target.value); setAppointmentPage(1); }}>
            <option value="open">Em aberto e em atendimento</option>
            <option value="all">Todos os status</option>
            <option value="scheduled">Agendadas</option>
            <option value="in_progress">Em atendimento</option>
            <option value="completed">Concluídas</option>
            <option value="cancelled">Canceladas</option>
          </select>
          <span className="filter-result-count">{filteredAppointments.length} resultado(s)</span>
        </div>

        {loading ? (
          <div className="spinner"></div>
        ) : filteredAppointments.length > 0 ? (
          <div className="card">
            <table className="appointments-table">
              <thead>
                <tr>
                  <th>Paciente</th>
                  <th>Médico</th>
                  <th>Data</th>
                  <th>Hora</th>
                  <th>Tipo</th>
                  <th>Status</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {visibleAppointments.map((appt) => (
                  <React.Fragment key={appt.id}>
                  <tr>
                    <td>{appt.patient_name}</td>
                    <td>{appt.doctor_name}</td>
                    <td>{new Date(appt.appointment_datetime).toLocaleDateString('pt-BR')}</td>
                    <td>{new Date(appt.appointment_datetime).toLocaleTimeString()}</td>
                    <td>{consultationTypeLabel(appt.consultation_type)}</td>
                    <td>
                      <span className={`status-badge status-${appt.status}`}>
                        {appointmentStatusLabel(appt.status)}
                      </span>
                    </td>
                    <td>
                      {['scheduled', 'confirmed'].includes(appt.status) ? (
                        <div className="form-actions">
                          <button type="button" className="btn btn-secondary" onClick={() => handleReceptionReschedule(appt)}>Alterar data</button>
                          <button type="button" className="btn btn-danger" onClick={() => handleReceptionCancel(appt)}>Cancelar</button>
                        </div>
                      ) : '—'}
                    </td>
                  </tr>
                  </React.Fragment>
                ))}
              </tbody>
            </table>
            {appointmentTotalPages > 1 && <div className="pagination-controls">
              <button type="button" className="btn btn-secondary" disabled={appointmentPage === 1} onClick={() => setAppointmentPage((page) => page - 1)}>Anterior</button>
              <span>Página {appointmentPage} de {appointmentTotalPages}</span>
              <button type="button" className="btn btn-secondary" disabled={appointmentPage === appointmentTotalPages} onClick={() => setAppointmentPage((page) => page + 1)}>Próxima</button>
            </div>}
          </div>
        ) : (
          <div className="card">
            <div className="empty-state">
              <p>Nenhum agendamento para hoje</p>
            </div>
          </div>
        )}
      </div></>}

      {activeView === 'dashboard' && <div className="dashboard-section reception-notifications">
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

export default ReceptionDashboard;
