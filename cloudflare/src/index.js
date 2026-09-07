const json = (data, status = 200, origin = '*') => new Response(JSON.stringify(data), {
  status,
  headers: { 'content-type': 'application/json; charset=utf-8', 'access-control-allow-origin': origin, 'access-control-allow-headers': 'Content-Type, Authorization', 'access-control-allow-methods': 'GET, POST, PUT, PATCH, OPTIONS' },
});
const error = (message, status = 400, origin = '*') => json({ detail: message }, status, origin);
const now = () => new Date().toISOString();
const body = async (request) => request.method === 'GET' || request.method === 'DELETE' ? {} : request.json();
const validateScheduleSlot = (value) => {
  const date = new Date(value);
  if (!value || Number.isNaN(date.getTime())) return 'Informe uma data e horário válidos.';
  if (date <= new Date()) return 'A consulta precisa ser agendada para o futuro.';
  const hour = date.getHours();
  const minutes = date.getMinutes();
  if (![0, 30].includes(minutes) || date.getSeconds() !== 0 || hour < 8 || hour > 22 || (hour === 22 && minutes !== 0)) {
    return 'Escolha um horário em intervalos de 30 minutos, entre 08:00 e 22:00.';
  }
  return null;
};
const userResponse = (row) => row && ({ id: row.id, email: row.email, full_name: row.full_name, phone: row.phone, cpf: row.cpf, role: row.role, status: row.status, created_at: row.created_at, updated_at: row.updated_at });
const empty = (status = 204, origin = '*') => new Response(null, { status, headers: { 'access-control-allow-origin': origin, 'access-control-allow-headers': 'Content-Type, Authorization', 'access-control-allow-methods': 'GET, POST, PUT, PATCH, OPTIONS' } });
const audit = (env, userId, action, entity, entityId = null, details = null) => env.DB.prepare('INSERT INTO audit_logs (user_id,action,entity,entity_id,details,created_at) VALUES (?,?,?,?,?,?)').bind(userId || null, action, entity, entityId, details ? JSON.stringify(details) : null, now()).run();

const bytesToBase64 = (bytes) => btoa(String.fromCharCode(...new Uint8Array(bytes))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
const base64ToBytes = (value) => Uint8Array.from(atob(value.replace(/-/g, '+').replace(/_/g, '/')), (char) => char.charCodeAt(0));
const encode = (value) => bytesToBase64(new TextEncoder().encode(JSON.stringify(value)));
const decode = (value) => JSON.parse(new TextDecoder().decode(base64ToBytes(value)));
const sign = async (value, secret) => bytesToBase64(await crypto.subtle.sign('HMAC', await crypto.subtle.importKey('raw', new TextEncoder().encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']), new TextEncoder().encode(value)));
const createToken = async (user, secret) => { const header = encode({ alg: 'HS256', typ: 'JWT' }); const payload = encode({ sub: String(user.id), role: user.role, exp: Math.floor(Date.now() / 1000) + 60 * 60 * 8 }); return `${header}.${payload}.${await sign(`${header}.${payload}`, secret)}`; };
const currentUser = async (request, env) => {
  const token = request.headers.get('authorization')?.replace(/^Bearer\s+/i, '');
  if (!token) return null;
  try { const [header, payload, signature] = token.split('.'); if (signature !== await sign(`${header}.${payload}`, env.SECRET_KEY)) return null; const data = decode(payload); if (data.exp < Date.now() / 1000) return null; return await env.DB.prepare('SELECT * FROM users WHERE id = ?').bind(Number(data.sub)).first(); } catch { return null; }
};
const hashPassword = async (password, salt = crypto.randomUUID()) => {
  const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(password), 'PBKDF2', false, ['deriveBits']);
  const bits = await crypto.subtle.deriveBits({ name: 'PBKDF2', salt: new TextEncoder().encode(salt), iterations: 100000, hash: 'SHA-256' }, key, 256);
  return `pbkdf2$100000$${salt}$${bytesToBase64(bits)}`;
};
const verifyPassword = async (password, stored) => { const [, iterations, salt, hash] = (stored || '').split('$'); return iterations && hash === (await hashPassword(password, salt)).split('$').pop(); };
const requireUser = async (request, env, roles = []) => { const user = await currentUser(request, env); return user && (!roles.length || roles.includes(user.role)) ? user : null; };
const detailedAppointments = async (env, where = '', params = []) => (await env.DB.prepare(`SELECT a.*, pu.full_name patient_name, du.full_name doctor_name, d.specialty doctor_specialty FROM appointments a JOIN patients p ON p.id=a.patient_id JOIN users pu ON pu.id=p.user_id JOIN doctors d ON d.id=a.doctor_id JOIN users du ON du.id=d.user_id ${where} ORDER BY a.appointment_datetime DESC`).bind(...params).all()).results;
const detailedPatients = async (env, where = '', params = []) => (await env.DB.prepare(`SELECT p.*, u.full_name, u.email, u.phone, u.cpf FROM patients p JOIN users u ON u.id=p.user_id ${where} ORDER BY u.full_name`).bind(...params).all()).results;
const detailedDoctors = async (env, where = '', params = []) => (await env.DB.prepare(`SELECT d.*, u.full_name, u.email, u.phone FROM doctors d JOIN users u ON u.id=d.user_id ${where} ORDER BY u.full_name`).bind(...params).all()).results;

export default {
  async fetch(request, env) {
    const configuredOrigins = (env.CORS_ORIGINS || '').split(',').map((value) => value.trim()).filter(Boolean);
    const requestOrigin = request.headers.get('Origin');
    const origin = requestOrigin && configuredOrigins.includes(requestOrigin) ? requestOrigin : (requestOrigin && configuredOrigins.length ? configuredOrigins[0] : '*');
    if (request.method === 'OPTIONS') return json({}, 200, origin);
    const url = new URL(request.url); const path = url.pathname.replace(/\/$/, '');
    try {
      if (path === '/health') return json({ status: 'healthy', app: env.APP_NAME || 'Clínica Médica API' }, 200, origin);
      if (path === '/api/auth/register' && request.method === 'POST') {
        const data = await body(request); if (!['doctor', 'reception'].includes(data.role)) return error('O cadastro público permite somente contas de médico ou recepção.', 422, origin);
        if (!data.full_name || !data.email || !data.cpf || !data.password) return error('Nome, email, CPF e senha são obrigatórios.', 422, origin);
        if (data.password.length < 8) return error('A senha deve ter no mínimo 8 caracteres.', 422, origin);
        if (!/^\S+@\S+\.\S+$/.test(data.email)) return error('Informe um email válido.', 422, origin);
        if (!/^\d{11}$/.test(String(data.cpf).replace(/\D/g, ''))) return error('Informe um CPF válido com 11 dígitos.', 422, origin);
        if (await env.DB.prepare('SELECT id FROM users WHERE email=?').bind(data.email).first()) return error('Este email já está cadastrado.', 409, origin);
        if (await env.DB.prepare('SELECT id FROM users WHERE cpf=?').bind(data.cpf).first()) return error('Este CPF já está cadastrado.', 409, origin);
        const stamp = now(); const password = await hashPassword(data.password); const result = await env.DB.prepare('INSERT INTO users (email,full_name,phone,cpf,hashed_password,role,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?, ?,?)').bind(data.email, data.full_name, data.phone || null, data.cpf, password, data.role || 'patient', 'active', stamp, stamp).run();
        await audit(env, result.meta.last_row_id, 'created', 'user', result.meta.last_row_id, { role: data.role });
        return json(userResponse(await env.DB.prepare('SELECT * FROM users WHERE id=?').bind(result.meta.last_row_id).first()), 201, origin);
      }
      if (path === '/api/auth/login' && request.method === 'POST') { const data = await body(request); const user = await env.DB.prepare('SELECT * FROM users WHERE email=?').bind(data.email).first(); if (!user || user.status !== 'active' || !(await verifyPassword(data.password, user.hashed_password))) return error('Email ou senha inválidos', 401, origin); return json({ access_token: await createToken(user, env.SECRET_KEY), token_type: 'bearer', user: userResponse(user) }, 200, origin); }
      const user = await currentUser(request, env); if (!user) return error('Não autenticado', 401, origin);
      if (path === '/api/auth/me') return json(userResponse(user), 200, origin);

      if (path === '/api/appointments' && request.method === 'GET') {
        const params = []; let where = ''; if (user.role === 'patient') { const patient = await env.DB.prepare('SELECT id FROM patients WHERE user_id=?').bind(user.id).first(); where = 'WHERE a.patient_id=?'; params.push(patient?.id || 0); } else if (user.role === 'doctor') { const doctor = await env.DB.prepare('SELECT id FROM doctors WHERE user_id=?').bind(user.id).first(); where = 'WHERE a.doctor_id=?'; params.push(doctor?.id || 0); } return json(await detailedAppointments(env, where, params), 200, origin);
      }
      if (path === '/api/appointments' && request.method === 'POST') {
        const data = await body(request);
        const scheduleError = validateScheduleSlot(data.appointment_datetime);
        if (scheduleError) return error(scheduleError, 422, origin);
        const requestedDate = new Date(data.appointment_datetime);
        const conflict = await env.DB.prepare("SELECT id FROM appointments WHERE doctor_id=? AND status NOT IN ('cancelled','completed') AND appointment_datetime > ? AND appointment_datetime < ? LIMIT 1")
          .bind(data.doctor_id, new Date(requestedDate.getTime() - 30 * 60 * 1000).toISOString(), new Date(requestedDate.getTime() + 30 * 60 * 1000).toISOString()).first();
        if (conflict) return error('Este horário já está ocupado para o médico.', 409, origin);
        const stamp = now();
        const result = await env.DB.prepare('INSERT INTO appointments (patient_id,doctor_id,room_id,appointment_datetime,duration_minutes,status,consultation_type,notes,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)').bind(data.patient_id, data.doctor_id, data.room_id || null, data.appointment_datetime, data.duration_minutes || 30, 'scheduled', data.consultation_type || 'follow_up', data.notes || null, stamp, stamp).run();
        return json((await detailedAppointments(env, 'WHERE a.id=?', [result.meta.last_row_id]))[0], 201, origin);
      }
      const appointmentMatch = path.match(/^\/api\/appointments\/(\d+)$/); const cancelMatch = path.match(/^\/api\/appointments\/(\d+)\/cancel$/);
      if (appointmentMatch && request.method === 'PUT') {
        const id = Number(appointmentMatch[1]); const data = await body(request);
        const appointment = await env.DB.prepare('SELECT a.*, p.user_id patient_user_id, d.user_id doctor_user_id FROM appointments a JOIN patients p ON p.id=a.patient_id JOIN doctors d ON d.id=a.doctor_id WHERE a.id=?').bind(id).first();
        if (!appointment) return error('Agendamento não encontrado', 404, origin);
        if (user.role === 'patient' || (user.role === 'doctor' && appointment.doctor_user_id !== user.id)) return error('Você não tem permissão para alterar este agendamento.', 403, origin);
        const fields = Object.entries(data).filter(([key]) => ['appointment_datetime','status','consultation_type','notes','cancel_reason','room_id'].includes(key));
        if (data.appointment_datetime) {
          const scheduleError = validateScheduleSlot(data.appointment_datetime);
          if (scheduleError) return error(scheduleError, 422, origin);
          const requestedDate = new Date(data.appointment_datetime);
          const conflict = await env.DB.prepare("SELECT id FROM appointments WHERE doctor_id=(SELECT doctor_id FROM appointments WHERE id=?) AND id<>? AND status NOT IN ('cancelled','completed') AND appointment_datetime > ? AND appointment_datetime < ? LIMIT 1")
            .bind(id, id, new Date(requestedDate.getTime() - 30 * 60 * 1000).toISOString(), new Date(requestedDate.getTime() + 30 * 60 * 1000).toISOString()).first();
          if (conflict) return error('Este horário já está ocupado para o médico.', 409, origin);
        }
        if (user.role === 'doctor' && data.status === 'in_progress') {
          const active = await env.DB.prepare('SELECT a.id FROM appointments a JOIN doctors d ON d.id=a.doctor_id WHERE d.user_id=? AND a.status=? AND a.id<>?').bind(user.id, 'in_progress', id).first();
          if (active) return error('Encerre o atendimento atual antes de chamar outro paciente.', 409, origin);
        }
        if (data.status && !['scheduled', 'in_progress', 'completed', 'cancelled'].includes(data.status)) return error('Status de consulta inválido.', 422, origin);
        if (data.status === 'completed' && user.role !== 'doctor') return error('Somente o médico pode concluir o atendimento.', 403, origin);
        if (fields.length) await env.DB.prepare(`UPDATE appointments SET ${fields.map(([key]) => `${key}=?`).join(',')}, updated_at=? WHERE id=?`).bind(...fields.map(([, value]) => value), now(), id).run();
        await audit(env, user.id, 'updated', 'appointment', id, { fields: fields.map(([key]) => key) });
        if (user.role === 'doctor' && data.status === 'in_progress') {
          const appointment = await env.DB.prepare('SELECT a.*, p.user_id patient_user_id, d.user_id doctor_user_id, pu.full_name patient_name FROM appointments a JOIN patients p ON p.id=a.patient_id JOIN doctors d ON d.id=a.doctor_id JOIN users pu ON pu.id=p.user_id WHERE a.id=?').bind(id).first();
          if (appointment) {
            const receptionUsers = (await env.DB.prepare("SELECT id FROM users WHERE role='reception'").all()).results;
            const message = `O médico está chamando o paciente ${appointment.patient_name} para entrar.`;
            await env.DB.batch(receptionUsers.map((recipient) => env.DB.prepare('INSERT INTO notifications (recipient_user_id,appointment_id,message,created_at) VALUES (?,?,?,?)').bind(recipient.id, id, message, now())));
          }
        }
        return json((await detailedAppointments(env, 'WHERE a.id=?', [id]))[0], 200, origin);
      }
      if (cancelMatch && request.method === 'POST') { const id = Number(cancelMatch[1]); const appointment = await env.DB.prepare('SELECT a.*, p.user_id patient_user_id, d.user_id doctor_user_id FROM appointments a JOIN patients p ON p.id=a.patient_id JOIN doctors d ON d.id=a.doctor_id WHERE a.id=?').bind(id).first(); if (!appointment) return error('Agendamento não encontrado',404,origin); if (!['scheduled', 'in_progress'].includes(appointment.status)) return error('Esta consulta não pode mais ser cancelada.', 409, origin); if ((user.role === 'patient' && appointment.patient_user_id !== user.id) || (user.role === 'doctor' && appointment.doctor_user_id !== user.id)) return error('Você não tem permissão para cancelar esta consulta.',403,origin); const reason = url.searchParams.get('reason') || null; await env.DB.prepare('UPDATE appointments SET status=?, cancel_reason=?, updated_at=? WHERE id=?').bind('cancelled', reason, now(), id).run(); await audit(env, user.id, 'cancelled', 'appointment', id, { reason }); const recipients = [appointment.patient_user_id, appointment.doctor_user_id, ...(await env.DB.prepare("SELECT id FROM users WHERE role='reception'").all()).results.map((row) => row.id)]; const message = `A consulta de ${new Date(appointment.appointment_datetime).toLocaleString('pt-BR')} foi cancelada.`; await env.DB.batch([...new Set(recipients)].map((recipient) => env.DB.prepare('INSERT INTO notifications (recipient_user_id,appointment_id,message,created_at) VALUES (?,?,?,?)').bind(recipient,id,message,now()))); return json((await detailedAppointments(env, 'WHERE a.id=?', [id]))[0], 200, origin); }

      if (appointmentMatch && request.method === 'DELETE') { if (!['reception', 'admin'].includes(user.role)) return error('Acesso negado', 403, origin); await env.DB.prepare('DELETE FROM appointments WHERE id=?').bind(Number(appointmentMatch[1])).run(); await audit(env, user.id, 'deleted', 'appointment', Number(appointmentMatch[1])); return empty(204, origin); }
      if (path === '/api/patients' && request.method === 'GET') { if (user.role === 'patient') { const patient = await env.DB.prepare('SELECT id FROM patients WHERE user_id=?').bind(user.id).first(); return json(await detailedPatients(env, 'WHERE p.id=?', [patient?.id || 0]), 200, origin); } return json(await detailedPatients(env), 200, origin); }
      if (path === '/api/patients' && request.method === 'POST') { if (!['reception', 'admin'].includes(user.role)) return error('Acesso negado', 403, origin); const data = await body(request); const stamp = now(); const result = await env.DB.prepare('INSERT INTO users (email,full_name,phone,cpf,hashed_password,role,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?)').bind(data.email,data.full_name,data.phone||null,data.cpf||null,await hashPassword(data.password || crypto.randomUUID()),'patient','active',stamp,stamp).run(); await env.DB.prepare('INSERT INTO patients (user_id,date_of_birth,gender,created_at,updated_at) VALUES (?,?,?,?,?)').bind(result.meta.last_row_id,data.date_of_birth||null,data.gender||null,stamp,stamp).run(); return json((await detailedPatients(env,'WHERE p.user_id=?',[result.meta.last_row_id]))[0],201,origin); }
      if (path === '/api/patients/register' && request.method === 'POST') { if (!['reception','admin'].includes(user.role)) return error('Acesso negado', 403, origin); const data = await body(request); const stamp = now(); const password = await hashPassword(data.password); const result = await env.DB.prepare('INSERT INTO users (email,full_name,phone,cpf,hashed_password,role,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?)').bind(data.email,data.full_name,data.phone||null,data.cpf,password,'patient','active',stamp,stamp).run(); await env.DB.prepare('INSERT INTO patients (user_id,date_of_birth,gender,created_at,updated_at) VALUES (?,?,?,?,?)').bind(result.meta.last_row_id,data.date_of_birth||null,data.gender||null,stamp,stamp).run(); return json((await detailedPatients(env,'WHERE p.user_id=?',[result.meta.last_row_id]))[0],201,origin); }
      const patientMatch = path.match(/^\/api\/patients\/(\d+)$/); if (patientMatch && request.method === 'PUT') { if (!['reception','admin'].includes(user.role)) return error('Acesso negado',403,origin); const data=await body(request); const fields=Object.entries(data).filter(([key])=>['date_of_birth','gender','address','city','state','zip_code','blood_type','allergies','medical_conditions','responsible_name','responsible_phone','responsible_cpf'].includes(key)); if(fields.length) await env.DB.prepare(`UPDATE patients SET ${fields.map(([key])=>`${key}=?`).join(',')},updated_at=? WHERE id=?`).bind(...fields.map(([,value])=>value),now(),Number(patientMatch[1])).run(); return json(await env.DB.prepare('SELECT * FROM patients WHERE id=?').bind(Number(patientMatch[1])).first(),200,origin); } if (patientMatch && request.method === 'DELETE') { if (!['reception','admin'].includes(user.role)) return error('Acesso negado',403,origin); await env.DB.prepare('DELETE FROM patients WHERE id=?').bind(Number(patientMatch[1])).run(); return json({},204,origin); }

      if (path === '/api/doctors' && request.method === 'GET') return json(await detailedDoctors(env),200,origin);
      if (path === '/api/doctors' && request.method === 'POST') { if (!['reception','admin'].includes(user.role)) return error('Acesso negado',403,origin); const data=await body(request); const stamp=now(); const result=await env.DB.prepare('INSERT INTO doctors (user_id,crm,specialty,bio,office_phone,vacation_start,vacation_end,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?)').bind(data.user_id,data.crm.toUpperCase(),data.specialty,data.bio||null,data.office_phone||null,data.vacation_start||null,data.vacation_end||null,stamp,stamp).run(); return json((await detailedDoctors(env,'WHERE d.id=?',[result.meta.last_row_id]))[0],201,origin); }
      if (path === '/api/doctors/users/unassigned' && request.method === 'GET') return json((await env.DB.prepare("SELECT u.* FROM users u LEFT JOIN doctors d ON d.user_id=u.id WHERE u.role='doctor' AND d.id IS NULL").all()).results.map(userResponse),200,origin);
      if (path === '/api/doctors/profile' && request.method === 'POST') { if(!['reception','admin'].includes(user.role)) return error('Acesso negado',403,origin); const data=await body(request); const stamp=now(); const result=await env.DB.prepare('INSERT INTO doctors (user_id,crm,specialty,bio,office_phone,vacation_start,vacation_end,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?)').bind(data.user_id,data.crm.toUpperCase(),data.specialty,data.bio||null,data.office_phone||null,data.vacation_start||null,data.vacation_end||null,stamp,stamp).run(); return json((await detailedDoctors(env,'WHERE d.id=?',[result.meta.last_row_id]))[0],201,origin); }

      if (path === '/api/medical-records' && request.method === 'GET') { if (!['doctor', 'patient'].includes(user.role)) return error('Acesso negado', 403, origin); let where='',params=[]; if(user.role==='patient'){const p=await env.DB.prepare('SELECT id FROM patients WHERE user_id=?').bind(user.id).first();where='WHERE m.patient_id=?';params=[p?.id||0];} if(user.role==='doctor'){const d=await env.DB.prepare('SELECT id FROM doctors WHERE user_id=?').bind(user.id).first();where='WHERE m.doctor_id=?';params=[d?.id||0];} const aid=url.searchParams.get('appointment_id');if(aid){where+=(where?' AND':'WHERE')+' m.appointment_id=?';params.push(Number(aid));} return json((await env.DB.prepare(`SELECT m.* FROM medical_records m ${where} ORDER BY m.created_at DESC`).bind(...params).all()).results,200,origin); }
      const recordMatch=path.match(/^\/api\/medical-records\/(\d+)$/); if((path==='/api/medical-records'||recordMatch)&&['POST','PUT'].includes(request.method)){if(user.role!=='doctor')return error('Somente o médico pode editar o laudo.',403,origin);const data=await body(request);const id=recordMatch?Number(recordMatch[1]):null;const stamp=now();if(id){const fields=Object.entries(data);await env.DB.prepare(`UPDATE medical_records SET ${fields.map(([key])=>`${key}=?`).join(',')},updated_at=? WHERE id=?`).bind(...fields.map(([,value])=>value),stamp,id).run();return json(await env.DB.prepare('SELECT * FROM medical_records WHERE id=?').bind(id).first(),200,origin);}const result=await env.DB.prepare('INSERT INTO medical_records (patient_id,doctor_id,appointment_id,chief_complaint,diagnosis,treatment_plan,prescription,medical_certificate,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)').bind(data.patient_id,data.doctor_id,data.appointment_id||null,data.chief_complaint,data.diagnosis,data.treatment_plan||null,data.prescription||null,data.medical_certificate||null,stamp,stamp).run();if(data.appointment_id)await env.DB.prepare('UPDATE appointments SET status="completed",updated_at=? WHERE id=?').bind(stamp,data.appointment_id).run();return json(await env.DB.prepare('SELECT * FROM medical_records WHERE id=?').bind(result.meta.last_row_id).first(),201,origin);}
      if(path==='/api/notifications'&&request.method==='GET')return json((await env.DB.prepare('SELECT * FROM notifications WHERE recipient_user_id=? ORDER BY created_at DESC,id DESC LIMIT 30').bind(user.id).all()).results,200,origin);
      const doctorUpdateMatch = path.match(/^\/api\/doctors\/(\d+)$/);
      if (doctorUpdateMatch && request.method === 'PUT') {
        if (!['doctor', 'reception', 'admin'].includes(user.role)) return error('Acesso negado', 403, origin);
        const data = await body(request); const fields = Object.entries(data).filter(([key]) => ['crm', 'specialty', 'bio', 'office_phone', 'vacation_start', 'vacation_end'].includes(key));
        if (fields.length) await env.DB.prepare(`UPDATE doctors SET ${fields.map(([key]) => `${key}=?`).join(',')}, updated_at=? WHERE id=?`).bind(...fields.map(([, value]) => value), now(), Number(doctorUpdateMatch[1])).run();
        return json((await detailedDoctors(env, 'WHERE d.id=?', [Number(doctorUpdateMatch[1])]))[0], 200, origin);
      }
      if (doctorUpdateMatch && request.method === 'DELETE') { if (!['reception', 'admin'].includes(user.role)) return error('Acesso negado', 403, origin); await env.DB.prepare('DELETE FROM doctors WHERE id=?').bind(Number(doctorUpdateMatch[1])).run(); return json({}, 204, origin); }
      const userMatch = path.match(/^\/api\/users\/(\d+)(\/password)?$/);
      if (userMatch && request.method === 'PUT') {
        const targetId = Number(userMatch[1]); const data = await body(request);
        if (userMatch[2]) { if (!['reception', 'admin'].includes(user.role)) return error('Acesso negado', 403, origin); await env.DB.prepare('UPDATE users SET hashed_password=?, updated_at=? WHERE id=?').bind(await hashPassword(data.password), now(), targetId).run(); }
        else { if (user.id !== targetId && !['reception', 'admin'].includes(user.role)) return error('Acesso negado', 403, origin); const fields = Object.entries(data).filter(([key]) => ['email', 'full_name', 'phone', 'cpf', 'status'].includes(key)); if (fields.length) await env.DB.prepare(`UPDATE users SET ${fields.map(([key]) => `${key}=?`).join(',')}, updated_at=? WHERE id=?`).bind(...fields.map(([, value]) => value), now(), targetId).run(); }
        return json(userResponse(await env.DB.prepare('SELECT * FROM users WHERE id=?').bind(targetId).first()), 200, origin);
      }
      const patientDetailMatch = path.match(/^\/api\/patients\/(\d+)$/);
      if (patientDetailMatch && request.method === 'GET') {
        const patient = await detailedPatients(env, 'WHERE p.id=?', [Number(patientDetailMatch[1])]);
        return patient[0] ? json(patient[0], 200, origin) : error('Paciente não encontrado', 404, origin);
      }
      if (appointmentMatch && request.method === 'GET') {
        const appointments = await detailedAppointments(env, 'WHERE a.id=?', [Number(appointmentMatch[1])]);
        return appointments[0] ? json(appointments[0], 200, origin) : error('Agendamento não encontrado', 404, origin);
      }
      if (doctorUpdateMatch && request.method === 'GET') {
        const doctors = await detailedDoctors(env, 'WHERE d.id=?', [Number(doctorUpdateMatch[1])]);
        return doctors[0] ? json(doctors[0], 200, origin) : error('Médico não encontrado', 404, origin);
      }
      return error('Rota não encontrada',404,origin);
    } catch (exception) { return error(exception.message || 'Erro interno do servidor',500,origin); }
  },
};
