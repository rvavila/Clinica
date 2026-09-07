import hashlib
import json
import secrets
import sqlite3
from datetime import datetime, timedelta
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HOST = "127.0.0.1"
PORT = 8000
DATABASE = Path(__file__).with_name("clinica_local.db")
TOKENS = {}


def password_hash(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def database():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def setup_database():
    connection = database()
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            birth_date TEXT NOT NULL,
            responsible TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialty TEXT NOT NULL,
            crm TEXT NOT NULL UNIQUE,
            phone TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            room_number TEXT NOT NULL UNIQUE,
            equipment TEXT DEFAULT '',
            active INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient TEXT NOT NULL,
            doctor TEXT NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Agendada'
        );
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            appointment_id INTEGER,
            created_at TEXT NOT NULL,
            is_read INTEGER NOT NULL DEFAULT 0,
            recipient_role TEXT NOT NULL DEFAULT 'recepcao'
        );
        """
    )
    # Compatibilidade com bancos locais criados antes dos avisos por perfil.
    notification_columns = {
        row[1] for row in connection.execute("PRAGMA table_info(notifications)")
    }
    if "recipient_role" not in notification_columns:
        connection.execute(
            "ALTER TABLE notifications ADD COLUMN recipient_role TEXT NOT NULL DEFAULT 'recepcao'"
        )
    # Corrige avisos antigos, criados antes de existir destinatário por perfil.
    connection.execute(
        """
        INSERT INTO notifications(message, appointment_id, created_at, is_read, recipient_role)
        SELECT n.message, n.appointment_id, n.created_at, n.is_read, 'medico'
        FROM notifications n
        JOIN appointments a ON a.id = n.appointment_id
        JOIN users u ON u.name = a.doctor AND u.role = 'medico'
        WHERE n.recipient_role = 'recepcao'
          AND NOT EXISTS (
              SELECT 1 FROM notifications existing
              WHERE existing.appointment_id = n.appointment_id
                AND existing.created_at = n.created_at
                AND existing.recipient_role = 'medico'
          )
        """
    )
    users = [
        ("Dr. Carlos Silva", "medico@clinica.local", "medico123", "medico"),
        ("Ana Recepcao", "recepcao@clinica.local", "recepcao123", "recepcao"),
        ("Maria Paciente", "paciente@clinica.local", "paciente123", "paciente"),
    ]
    for name, email, password, role in users:
        connection.execute(
            "INSERT OR IGNORE INTO users(name,email,password,role) VALUES(?,?,?,?)",
            (name, email, password_hash(password), role),
        )
    if connection.execute("SELECT COUNT(*) FROM patients").fetchone()[0] == 0:
        connection.execute(
            "INSERT INTO patients(name,phone,birth_date,responsible) VALUES(?,?,?,?)",
            ("Maria Paciente", "11999990000", "2010-05-20", "Joao Paciente"),
        )
    connection.execute(
        "INSERT OR IGNORE INTO doctors(name,specialty,crm,phone) VALUES(?,?,?,?)",
        ("Dr. Carlos Silva", "Pediatria", "CRM-12345", "1133334444"),
    )
    connection.execute(
        "INSERT OR IGNORE INTO rooms(name,room_number,equipment) VALUES(?,?,?)",
        ("Consultorio Pediatrico", "01", "Maca infantil, balanca"),
    )
    if connection.execute("SELECT COUNT(*) FROM appointments").fetchone()[0] == 0:
        connection.execute(
            "INSERT INTO appointments(patient,doctor,appointment_date,appointment_time) VALUES(?,?,?,?)",
            ("Maria Paciente", "Dr. Carlos Silva", datetime.now().strftime("%Y-%m-%d"), "14:00"),
        )
    connection.commit()
    connection.close()


def rows_to_dict(rows):
    return [dict(row) for row in rows]


def page():
    return r"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Clinica Local</title>
  <style>
    *{box-sizing:border-box}body{margin:0;background:#f4f7f6;color:#20312e;font:16px system-ui,sans-serif}
    header{background:#173f3a;color:white;padding:22px 7%;display:flex;justify-content:space-between;align-items:center}
    main{max-width:1100px;margin:35px auto;padding:0 20px}.panel{background:white;border:1px solid #d8e2df;border-radius:10px;padding:24px;margin-bottom:20px;box-shadow:0 4px 16px #183b3210}
    h1,h2{margin-top:0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}.metric{background:#e2f1ed;border-left:4px solid #25806f;padding:18px;border-radius:8px}.metric strong{display:block;font-size:28px;margin-top:5px}
    input,button{font:inherit;padding:11px 13px;border-radius:6px;border:1px solid #b8cbc6}input{width:100%;margin:5px 0 12px}button{background:#237969;color:white;border:0;cursor:pointer}button.secondary{background:#71817e}button:hover{filter:brightness(.92)}
    form{max-width:420px}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:12px 8px;border-bottom:1px solid #e2e9e7}th{color:#48635d}.muted{color:#637873}.error{color:#a63232;margin-top:12px}.hidden{display:none}.login{max-width:460px;margin:80px auto}
  </style>
</head>
<body>
  <header><strong>Clinica Local</strong><span id="user"></span><button id="logout" class="secondary hidden">Sair</button></header>
  <main>
    <section id="login" class="panel login"><h1>Acesso ao sistema</h1><p class="muted">Modo local sem instalacao de pacotes.</p>
      <form id="loginForm"><label>E-mail<input id="email" type="email" required value="recepcao@clinica.local"></label><label>Senha<input id="password" type="password" required value="recepcao123"></label><button>Entrar</button><div id="loginError" class="error"></div></form>
      <p class="muted">Teste: recepcao@clinica.local / recepcao123</p>
    </section>
    <section id="dashboard" class="hidden"><div class="panel"><h1 id="welcome"></h1><p id="role" class="muted"></p></div>
      <div id="metrics" class="grid"></div><div class="panel"><h2>Agendamentos</h2><div id="appointments"></div></div>
      <div id="patientsPanel" class="panel"><h2>Pacientes</h2><div id="patients"></div></div>
    </section>
  </main>
  <script>
    const state={token:null,user:null};
    const $=id=>document.getElementById(id);
    async function api(url, options={}) { const response=await fetch(url,{...options,headers:{'Content-Type':'application/json','Authorization':state.token||'',...(options.headers||{})}}); const data=await response.json(); if(!response.ok) throw Error(data.detail||'Erro na requisicao'); return data; }
    function table(items, columns){ if(!items.length)return '<p class="muted">Nenhum registro encontrado.</p>'; return '<table><thead><tr>'+columns.map(c=>'<th>'+c.label+'</th>').join('')+'</tr></thead><tbody>'+items.map(item=>'<tr>'+columns.map(c=>'<td>'+String(item[c.key]??'')+'</td>').join('')+'</tr>').join('')+'</tbody></table>'; }
    async function load(){ const data=await api('/api/dashboard'); $('welcome').textContent='Ola, '+data.user.name; $('role').textContent='Perfil: '+data.user.role; $('user').textContent=data.user.name; $('metrics').innerHTML='<div class="metric">Agendamentos<strong>'+data.appointments.length+'</strong></div><div class="metric">Pacientes<strong>'+data.patients.length+'</strong></div><div class="metric">Acesso<strong>'+data.user.role+'</strong></div>'; $('appointments').innerHTML=table(data.appointments,[{key:'appointment_date',label:'Data'},{key:'appointment_time',label:'Hora'},{key:'patient',label:'Paciente'},{key:'doctor',label:'Medico'},{key:'status',label:'Status'}]); $('patients').innerHTML=table(data.patients,[{key:'name',label:'Nome'},{key:'phone',label:'Telefone'},{key:'birth_date',label:'Nascimento'},{key:'responsible',label:'Responsavel'}]); }
    $('loginForm').onsubmit=async event=>{event.preventDefault();$('loginError').textContent='';try{const data=await api('/api/login',{method:'POST',body:JSON.stringify({email:$('email').value,password:$('password').value})});state.token=data.token;state.user=data.user;$('login').classList.add('hidden');$('dashboard').classList.remove('hidden');$('logout').classList.remove('hidden');await load()}catch(error){$('loginError').textContent=error.message}};
    $('logout').onclick=()=>{state.token=null;state.user=null;$('dashboard').classList.add('hidden');$('login').classList.remove('hidden');$('logout').classList.add('hidden');$('user').textContent=''};
  </script>
</body></html>"""

def page_v2():
    return r"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Clinica Local</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@700;800&display=swap');
:root{--ink:#172a35;--muted:#71808a;--line:#e5ebe9;--brand:#0d776b;--brand-dark:#07564f;--mint:#e8f5f1;--orange:#d98245}*{box-sizing:border-box}body{margin:0;background:#f7f9f8;color:var(--ink);font:14px 'DM Sans',sans-serif}header{height:74px;background:#fff;border-bottom:1px solid var(--line);padding:0 34px;display:flex;align-items:center;gap:18px;margin-left:238px}header strong{font:800 21px Manrope,sans-serif;color:var(--brand-dark);margin-right:auto}main{max-width:1420px;margin:0 auto;padding:32px 38px 50px 276px}.sidebar{position:fixed;left:0;top:0;bottom:0;width:238px;background:var(--brand-dark);padding:28px 16px;color:#d8efea;z-index:3}.brand{font:800 21px Manrope,sans-serif;color:#fff;padding:0 14px 34px}.brand span{color:#8fd6c5}.side-label{font-size:10px;text-transform:uppercase;letter-spacing:1.4px;color:#8bbab1;padding:0 14px;margin:18px 0 8px}.nav{display:flex;align-items:center;gap:11px;width:100%;background:transparent;color:#c4dfda;text-align:left;margin:3px 0;padding:12px 14px;border:0}.nav:hover,.nav.active{background:#146f64;color:#fff}.nav-icon{width:20px;text-align:center;font-size:16px}.panel{background:#fff;border:1px solid var(--line);border-radius:14px;padding:24px;margin-bottom:20px;box-shadow:0 8px 24px #193e3510}.hero{display:flex;justify-content:space-between;align-items:end;margin-bottom:26px}.hero h1{font:800 30px Manrope,sans-serif;margin:0 0 7px}.hero p{color:var(--muted);margin:0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:16px;margin-bottom:24px}.metric{background:#fff;border:1px solid var(--line);border-radius:14px;padding:19px;position:relative}.metric:before{content:'';display:block;width:34px;height:4px;background:var(--brand);border-radius:5px;margin-bottom:18px}.metric b{display:block;font:800 29px Manrope,sans-serif;margin-top:7px}.metric span{color:var(--muted);font-size:12px}.tabs{display:flex;gap:5px;flex-wrap:wrap;border-bottom:1px solid var(--line);margin-bottom:20px}.tabs button{background:transparent;color:var(--muted);border-radius:0;padding:12px 16px;border-bottom:2px solid transparent}.tabs button.active{background:transparent;color:var(--brand-dark);border-bottom-color:var(--brand)}.view{display:none}.view.active{display:block}form{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:14px;align-items:end}label{display:block;color:#52636a;font-size:13px;font-weight:600}input,select,button{font:inherit;padding:11px 13px;border-radius:8px;border:1px solid #d5e1df}input,select{width:100%;margin-top:6px;background:#fbfcfc}input:focus,select:focus{outline:2px solid #a8d9ce;border-color:var(--brand)}button{background:var(--brand);color:white;border:0;cursor:pointer;font-weight:600}button:hover{filter:brightness(.94)}.secondary{background:#edf2f1;color:#355b55}.danger{background:#b95252}.muted{color:var(--muted)}.error{color:#a63232;margin-top:10px}table{width:100%;border-collapse:collapse;overflow:auto}th,td{text-align:left;padding:13px 9px;border-bottom:1px solid var(--line)}th{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.5px}.login{max-width:450px;margin:70px auto}.hidden{display:none}.section-title{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px}.section-title h2{margin:0;font:700 19px Manrope,sans-serif}.section-title p{margin:5px 0 0;color:var(--muted)}@media(max-width:800px){.sidebar{width:68px;padding:20px 8px}.brand{font-size:0;text-align:center;padding:0 0 30px}.brand span{font-size:20px}.side-label,.nav-text{display:none}.nav{justify-content:center;padding:13px 8px}.nav-icon{font-size:18px}header{margin-left:68px;padding:0 18px}main{padding:24px 16px 40px 84px}.hero h1{font-size:24px}.panel{padding:18px}}@media(max-width:520px){header strong{font-size:17px}main{padding:20px 10px 30px 78px}.hero{display:block}.hero h1{font-size:21px}.grid{gap:10px}.metric{padding:14px}}
</style></head>
<body><aside class="sidebar"><div class="brand">Clinica <span>+</span></div><div class="side-label">Menu principal</div><button class="nav active" data-view="agenda"><span class="nav-icon">⌂</span><span class="nav-text">Agenda</span></button><button class="nav" data-view="patients" id="patientsNav"><span class="nav-icon">♙</span><span class="nav-text">Pacientes</span></button><button class="nav" data-view="doctors" id="doctorsNav"><span class="nav-icon">✚</span><span class="nav-text">Equipe medica</span></button><button class="nav" data-view="rooms" id="roomsNav"><span class="nav-icon">▦</span><span class="nav-text">Salas</span></button><div class="side-label">Sistema</div><button class="nav" id="logoutSide"><span class="nav-icon">↪</span><span class="nav-text">Sair</span></button></aside><header><strong id="topTitle">Visao geral</strong><span id="user"></span><button id="logout" class="secondary hidden">Sair</button></header><main>
<section id="login" class="panel login"><h1>Acesso ao sistema</h1><p class="muted">Sistema local em Python puro com banco SQLite.</p><form id="loginForm"><label>E-mail<input id="email" type="email" required value="recepcao@clinica.local"></label><label>Senha<input id="password" type="password" required value="recepcao123"></label><button>Entrar</button></form><div id="loginError" class="error"></div><p class="muted">Recepcao: recepcao@clinica.local / recepcao123</p></section>
<section id="dashboard" class="hidden"><div class="hero"><div><h1 id="welcome"></h1><p id="role" class="muted"></p></div><div class="muted" id="todayLabel"></div></div><div id="metrics" class="grid"></div>
<section id="agenda" class="view active"><div class="panel" id="appointmentFormPanel"><div class="section-title"><div><h2>Novo agendamento</h2><p>A recepcao realiza os agendamentos para todos.</p></div></div><form id="appointmentForm"><label>Paciente<select id="appointmentPatient" required></select></label><label>Medico<select id="appointmentDoctor" required></select></label><label>Sala<select id="appointmentRoom" required></select></label><label>Data<input id="appointmentDate" type="date" required></label><label>Hora<input id="appointmentTime" type="time" required></label><button>+ Agendar consulta</button></form><div id="appointmentMessage" class="error"></div></div><div class="panel"><div class="section-title"><div><h2 id="appointmentsTitle">Agendamentos</h2><p>Consulte e acompanhe os horarios da clinica.</p></div><input id="appointmentSearch" placeholder="Buscar paciente ou medico" style="max-width:260px"></div><div id="appointments"></div></div></section>
<section id="patients" class="view"><div class="panel" id="patientFormPanel"><div class="section-title"><div><h2>Novo paciente</h2><p>Cadastre dados básicos e responsável.</p></div></div><form id="patientForm"><label>Nome<input id="patientName" required></label><label>Telefone<input id="patientPhone" required></label><label>Nascimento<input id="patientBirth" type="date" required></label><label>Responsavel<input id="patientResponsible"></label><button>Cadastrar paciente</button></form><div id="patientMessage" class="error"></div></div><div class="panel"><div class="section-title"><div><h2>Pacientes cadastrados</h2><p>Consulte rapidamente os registros.</p></div><input id="patientSearch" placeholder="Buscar por nome ou telefone" style="max-width:260px"></div><div id="patientsTable"></div></div></section>
<section id="doctors" class="view"><div class="panel" id="doctorFormPanel"><div class="section-title"><div><h2>Novo medico</h2><p>Adicione profissionais à equipe da clínica.</p></div></div><form id="doctorForm"><label>Nome<input id="doctorName" required></label><label>Especialidade<input id="doctorSpecialty" required value="Pediatria"></label><label>CRM<input id="doctorCrm" required></label><label>Telefone<input id="doctorPhone"></label><button>Cadastrar medico</button></form><div id="doctorMessage" class="error"></div></div><div class="panel"><div class="section-title"><div><h2>Equipe medica</h2><p>Profissionais ativos no atendimento.</p></div></div><div id="doctorsTable"></div></div></section>
<section id="rooms" class="view"><div class="panel" id="roomFormPanel"><div class="section-title"><div><h2>Nova sala</h2><p>Organize os espaços e equipamentos.</p></div></div><form id="roomForm"><label>Nome<input id="roomName" required></label><label>Numero<input id="roomNumber" required></label><label>Equipamentos<input id="roomEquipment"></label><button>Cadastrar sala</button></form><div id="roomMessage" class="error"></div></div><div class="panel"><div class="section-title"><div><h2>Salas</h2><p>Ambientes disponíveis para agendamento.</p></div></div><div id="roomsTable"></div></div></section>
<section id="notificationsPanel" class="panel hidden"><h2>Avisos de cancelamento</h2><div id="notifications"></div></section>
</section></main>
<script>
const state={token:null,user:null,data:null};const $=id=>document.getElementById(id);const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
async function api(url,options={}){const response=await fetch(url,{...options,headers:{'Content-Type':'application/json','Authorization':state.token||'',...(options.headers||{})}});const data=await response.json();if(!response.ok)throw Error(data.detail||'Erro na requisicao');return data}
function table(items,columns,actions=''){if(!items.length)return '<p class="muted">Nenhum registro encontrado.</p>';return '<table><thead><tr>'+columns.map(c=>'<th>'+c.label+'</th>').join('')+(actions?'<th>Acoes</th>':'')+'</tr></thead><tbody>'+items.map(item=>'<tr>'+columns.map(c=>'<td>'+esc(item[c.key])+'</td>').join('')+(actions?'<td>'+actions(item)+'</td>':'')+'</tr>').join('')+'</tbody></table>'}
function fill(id,items,label,key='name'){ $(id).innerHTML='<option value="">Selecione</option>'+items.map(item=>'<option value="'+esc(item[label])+'">'+esc(item[label])+'</option>').join('') }
function render(data){state.data=data;const role=data.user.role;$('welcome').textContent=role==='paciente'?'Meus horarios':'Ola, '+data.user.name;$('role').textContent=role==='paciente'?'Paciente: consulte e cancele seus proprios horarios':role==='medico'?'Visao medica: seus pacientes e sua agenda':'Recepcao: controle de agenda, cadastros e avisos';$('user').textContent=data.user.name;$('todayLabel').textContent=new Date().toLocaleDateString('pt-BR',{weekday:'long',day:'2-digit',month:'long'});$('metrics').innerHTML='<div class="metric"><span>Agendamentos</span><b>'+data.appointments.length+'</b></div><div class="metric"><span>Pacientes</span><b>'+data.patients.length+'</b></div>'+(['recepcao','medico'].includes(role)?'<div class="metric"><span>Avisos pendentes</span><b>'+data.notifications.length+'</b></div>':'');$('appointmentFormPanel').classList.toggle('hidden',role!=='recepcao');$('patientFormPanel').classList.toggle('hidden',role!=='recepcao');$('doctorFormPanel').classList.toggle('hidden',role!=='recepcao');$('roomFormPanel').classList.toggle('hidden',role!=='recepcao');$('patientsNav').classList.toggle('hidden',role==='paciente');$('doctorsNav').classList.toggle('hidden',role==='paciente');$('roomsNav').classList.toggle('hidden',role!=='recepcao');$('notificationsPanel').classList.toggle('hidden',!['recepcao','medico'].includes(role));$('appointmentsTitle').textContent=role==='paciente'?'Meus horarios marcados':role==='medico'?'Consultas de hoje':'Agenda completa';if(['recepcao','medico'].includes(role))$('notifications').innerHTML=data.notifications.length?data.notifications.map(n=>'<p><strong>Novo aviso:</strong> '+esc(n.message)+' <span class="muted">('+esc(n.created_at)+')</span></p>').join(''):'<p class="muted">Nenhum aviso novo.</p>';fill('appointmentPatient',data.patients,'name');fill('appointmentDoctor',data.doctors,'name');fill('appointmentRoom',data.rooms,'room_number');drawTables()}
function drawTables(){const d=state.data;const search=($('appointmentSearch').value||'').toLowerCase();const canCancel=['paciente','recepcao','medico'].includes(state.user.role);$('appointments').innerHTML=table(d.appointments.filter(x=>(x.patient+' '+x.doctor).toLowerCase().includes(search)),[{key:'appointment_date',label:'Data'},{key:'appointment_time',label:'Hora'},{key:'patient',label:'Paciente'},{key:'doctor',label:'Medico'},{key:'status',label:'Status'}],x=>canCancel&&x.status==='Agendada'?'<button class="danger" onclick="cancelAppointment('+x.id+')">Cancelar consulta</button>':'');const ps=($('patientSearch').value||'').toLowerCase();$('patientsTable').innerHTML=table(d.patients.filter(x=>(x.name+' '+x.phone).toLowerCase().includes(ps)),[{key:'name',label:'Nome'},{key:'phone',label:'Telefone'},{key:'birth_date',label:'Nascimento'},{key:'responsible',label:'Responsavel'}]);$('doctorsTable').innerHTML=table(d.doctors,[{key:'name',label:'Nome'},{key:'specialty',label:'Especialidade'},{key:'crm',label:'CRM'},{key:'phone',label:'Telefone'}]);$('roomsTable').innerHTML=table(d.rooms,[{key:'name',label:'Nome'},{key:'room_number',label:'Numero'},{key:'equipment',label:'Equipamentos'}])}
    async function refresh(){render(await api('/api/dashboard'))}async function action(form,url,message){const fields={patientForm:{patientName:'name',patientPhone:'phone',patientBirth:'birth_date',patientResponsible:'responsible'},doctorForm:{doctorName:'name',doctorSpecialty:'specialty',doctorCrm:'crm',doctorPhone:'phone'},roomForm:{roomName:'name',roomNumber:'room_number',roomEquipment:'equipment'},appointmentForm:{appointmentPatient:'patient',appointmentDoctor:'doctor',appointmentRoom:'room_number',appointmentDate:'appointment_date',appointmentTime:'appointment_time'}};$(message).textContent='';try{const payload={};Object.entries(fields[form]||{}).forEach(([id,key])=>payload[key]=$(id).value);await api(url,{method:'POST',body:JSON.stringify(payload)});$(form).reset();await refresh()}catch(e){$(message).textContent=e.message}}
$('loginForm').onsubmit=async e=>{e.preventDefault();$('loginError').textContent='';try{const d=await api('/api/login',{method:'POST',body:JSON.stringify({email:$('email').value,password:$('password').value})});state.token=d.token;state.user=d.user;$('login').classList.add('hidden');$('dashboard').classList.remove('hidden');$('logout').classList.remove('hidden');await refresh()}catch(x){$('loginError').textContent=x.message}};
$('patientForm').onsubmit=e=>{e.preventDefault();action('patientForm','/api/patients','patientMessage')};$('doctorForm').onsubmit=e=>{e.preventDefault();action('doctorForm','/api/doctors','doctorMessage')};$('roomForm').onsubmit=e=>{e.preventDefault();action('roomForm','/api/rooms','roomMessage')};$('appointmentForm').onsubmit=e=>{e.preventDefault();action('appointmentForm','/api/appointments','appointmentMessage')};$('appointmentSearch').oninput=drawTables;$('patientSearch').oninput=drawTables;
async function cancelAppointment(id){if(!confirm('Deseja cancelar este horario?'))return;try{const result=await api('/api/appointments/'+id+'/cancel',{method:'POST',body:JSON.stringify({})});alert(result.message);await refresh()}catch(error){alert(error.message)}};document.querySelectorAll('.nav[data-view]').forEach(button=>button.onclick=()=>{document.querySelectorAll('.nav[data-view],.view').forEach(x=>x.classList.remove('active'));button.classList.add('active');$(button.dataset.view).classList.add('active');$('topTitle').textContent=button.querySelector('.nav-text').textContent});$('logout').onclick=()=>location.reload();$('logoutSide').onclick=()=>location.reload();
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def send_json(self, payload, status=HTTPStatus.OK):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length) or b"{}")

    def do_PATCH(self):
        path = urlparse(self.path).path
        if not path.startswith("/api/appointments/"):
            self.send_json({"detail": "Rota nao encontrada"}, HTTPStatus.NOT_FOUND)
            return
        user = self.current_user()
        if not user:
            self.send_json({"detail": "Nao autenticado"}, HTTPStatus.UNAUTHORIZED)
            return
        appointment_id = path.rsplit("/", 1)[-1]
        connection = database()
        appointment = connection.execute("SELECT * FROM appointments WHERE id=?", (appointment_id,)).fetchone()
        if not appointment:
            connection.close()
            self.send_json({"detail": "Agendamento nao encontrado"}, HTTPStatus.NOT_FOUND)
            return
        if user["role"] == "paciente" and appointment["patient"] != user["name"]:
            connection.close()
            self.send_json({"detail": "Voce so pode cancelar seus proprios horarios"}, HTTPStatus.FORBIDDEN)
            return
        if user["role"] == "medico" and appointment["doctor"] != user["name"]:
            connection.close()
            self.send_json({"detail": "Voce so pode cancelar consultas da sua agenda"}, HTTPStatus.FORBIDDEN)
            return
        data = self.read_json()
        status = data.get("status", "Cancelada")
        if status == "Cancelada" and appointment["status"] != "Agendada":
            connection.close()
            self.send_json({"detail": "Somente consultas agendadas podem ser canceladas"}, HTTPStatus.CONFLICT)
            return
        if status == "Cancelada" and user["role"] == "paciente":
            appointment_at = datetime.fromisoformat(
                f"{appointment['appointment_date']}T{appointment['appointment_time']}"
            )
            if appointment_at - datetime.now() < timedelta(hours=24):
                connection.close()
                self.send_json(
                    {"detail": "O cancelamento pelo paciente so e permitido com no minimo 24 horas de antecedencia."},
                    HTTPStatus.UNPROCESSABLE_ENTITY,
                )
                return
        connection.execute("UPDATE appointments SET status=? WHERE id=?", (status, appointment_id))
        if user["role"] == "paciente":
            message = f"Cancelada pelo usuario: {user['name']} cancelou o horario de {appointment['appointment_date']} as {appointment['appointment_time']}."
            connection.executemany(
                "INSERT INTO notifications(message,appointment_id,created_at,recipient_role) VALUES(?,?,?,?)",
                [
                    (message, appointment_id, datetime.now().isoformat(timespec="seconds"), "medico"),
                    (message, appointment_id, datetime.now().isoformat(timespec="seconds"), "recepcao"),
                    ],
                )
        elif user["role"] == "medico":
            message = f"Cancelada pela clinica: o medico cancelou a consulta de {appointment['patient']} em {appointment['appointment_date']} as {appointment['appointment_time']}."
            connection.executemany(
                "INSERT INTO notifications(message,appointment_id,created_at,recipient_role) VALUES(?,?,?,?)",
                [
                    (message, appointment_id, datetime.now().isoformat(timespec="seconds"), "recepcao"),
                    (message, appointment_id, datetime.now().isoformat(timespec="seconds"), "paciente"),
                ],
            )
        connection.commit()
        connection.close()
        self.send_json({"message": "Agendamento cancelado. A recepcao foi avisada." if user["role"] == "paciente" else "Agendamento atualizado"})

    def current_user(self):
        return TOKENS.get(self.headers.get("Authorization", ""))

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            body = page_v2().encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/health":
            self.send_json({"status": "healthy", "mode": "python-standalone"})
            return
        if path == "/api/dashboard":
            user = self.current_user()
            if not user:
                self.send_json({"detail": "Nao autenticado"}, HTTPStatus.UNAUTHORIZED)
                return
            connection = database()
            appointments = rows_to_dict(connection.execute("SELECT * FROM appointments ORDER BY appointment_date, appointment_time"))
            patients = rows_to_dict(connection.execute("SELECT * FROM patients ORDER BY name"))
            doctors = rows_to_dict(connection.execute("SELECT * FROM doctors ORDER BY name"))
            rooms = rows_to_dict(connection.execute("SELECT * FROM rooms WHERE active=1 ORDER BY room_number"))
            notifications = rows_to_dict(connection.execute(
                "SELECT * FROM notifications WHERE recipient_role=? ORDER BY id DESC LIMIT 30",
                (user["role"],),
            )) if user["role"] in {"recepcao", "medico"} else []
            connection.close()
            if user["role"] == "paciente":
                appointments = [item for item in appointments if item["patient"] == user["name"]]
                patients = [item for item in patients if item["name"] == user["name"]]
            elif user["role"] == "medico":
                appointments = [item for item in appointments if item["doctor"] == user["name"]]
                patient_names = {item["patient"] for item in appointments}
                patients = [item for item in patients if item["name"] in patient_names]
            self.send_json({"user": user, "appointments": appointments, "patients": patients, "doctors": doctors, "rooms": rooms, "notifications": notifications})
            return
        self.send_json({"detail": "Rota nao encontrada"}, HTTPStatus.NOT_FOUND)

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/login":
            data = self.read_json()
            connection = database()
            user = connection.execute("SELECT id,name,email,role FROM users WHERE email=? AND password=?", (data.get("email", ""), password_hash(data.get("password", "")))).fetchone()
            connection.close()
            if not user:
                self.send_json({"detail": "E-mail ou senha invalidos"}, HTTPStatus.UNAUTHORIZED)
                return
            public_user = dict(user)
            token = secrets.token_urlsafe(24)
            TOKENS[token] = public_user
            self.send_json({"token": token, "user": public_user})
            return
        user = self.current_user()
        if not user:
            self.send_json({"detail": "Nao autenticado"}, HTTPStatus.UNAUTHORIZED)
            return
        path_parts = [part for part in path.split("/") if part]
        if len(path_parts) == 4 and path_parts[:2] == ["api", "appointments"] and path_parts[-1] == "cancel":
            appointment_id = path_parts[2]
            connection = database()
            appointment = connection.execute("SELECT * FROM appointments WHERE id=?", (appointment_id,)).fetchone()
            if not appointment:
                connection.close()
                self.send_json({"detail": "Agendamento nao encontrado"}, HTTPStatus.NOT_FOUND)
                return
            if user["role"] == "paciente" and appointment["patient"] != user["name"]:
                connection.close()
                self.send_json({"detail": "Voce so pode cancelar seus proprios horarios"}, HTTPStatus.FORBIDDEN)
                return
            if user["role"] == "medico" and appointment["doctor"] != user["name"]:
                connection.close()
                self.send_json({"detail": "Voce so pode cancelar consultas da sua agenda"}, HTTPStatus.FORBIDDEN)
                return
            if appointment["status"] != "Agendada":
                connection.close()
                self.send_json({"detail": "Somente consultas agendadas podem ser canceladas"}, HTTPStatus.CONFLICT)
                return
            if user["role"] == "paciente":
                appointment_at = datetime.fromisoformat(
                    f"{appointment['appointment_date']}T{appointment['appointment_time']}"
                )
                if appointment_at - datetime.now() < timedelta(hours=24):
                    connection.close()
                    self.send_json(
                        {"detail": "O cancelamento pelo paciente so e permitido com no minimo 24 horas de antecedencia."},
                        HTTPStatus.UNPROCESSABLE_ENTITY,
                    )
                    return
            connection.execute("UPDATE appointments SET status='Cancelada' WHERE id=?", (appointment_id,))
            if user["role"] == "paciente":
                message = f"Cancelada pelo usuario: {user['name']} cancelou o horario de {appointment['appointment_date']} as {appointment['appointment_time']}."
                connection.executemany(
                    "INSERT INTO notifications(message,appointment_id,created_at,recipient_role) VALUES(?,?,?,?)",
                    [
                        (message, appointment_id, datetime.now().isoformat(timespec="seconds"), "medico"),
                        (message, appointment_id, datetime.now().isoformat(timespec="seconds"), "recepcao"),
                    ],
                )
            elif user["role"] == "medico":
                message = f"Cancelada pela clinica: o medico cancelou a consulta de {appointment['patient']} em {appointment['appointment_date']} as {appointment['appointment_time']}."
                connection.executemany(
                    "INSERT INTO notifications(message,appointment_id,created_at,recipient_role) VALUES(?,?,?,?)",
                    [
                        (message, appointment_id, datetime.now().isoformat(timespec="seconds"), "recepcao"),
                        (message, appointment_id, datetime.now().isoformat(timespec="seconds"), "paciente"),
                    ],
                )
            connection.commit()
            connection.close()
            self.send_json({"message": "Agendamento cancelado. A recepcao foi avisada." if user["role"] == "paciente" else "Agendamento cancelado."})
            return
        data = self.read_json()
        connection = database()
        try:
            if path == "/api/patients":
                if user["role"] == "paciente":
                    raise ValueError("Paciente nao pode cadastrar outro paciente")
                if not data.get("name") or not data.get("phone") or not data.get("birth_date"):
                    raise ValueError("Nome, telefone e nascimento sao obrigatorios")
                connection.execute("INSERT INTO patients(name,phone,birth_date,responsible) VALUES(?,?,?,?)", (data["name"], data["phone"], data["birth_date"], data.get("responsible", "")))
            elif path == "/api/doctors":
                if user["role"] == "paciente":
                    raise ValueError("Paciente nao pode cadastrar medico")
                connection.execute("INSERT INTO doctors(name,specialty,crm,phone) VALUES(?,?,?,?)", (data["name"], data["specialty"], data["crm"], data.get("phone", "")))
            elif path == "/api/rooms":
                if user["role"] == "paciente":
                    raise ValueError("Paciente nao pode cadastrar sala")
                connection.execute("INSERT INTO rooms(name,room_number,equipment) VALUES(?,?,?)", (data["name"], data["room_number"], data.get("equipment", "")))
            elif path == "/api/appointments":
                if user["role"] != "recepcao":
                    raise ValueError("Somente a recepcao pode criar agendamentos")
                connection.execute("INSERT INTO appointments(patient,doctor,appointment_date,appointment_time,status) VALUES(?,?,?,?,?)", (data["patient"], data["doctor"], data["appointment_date"], data["appointment_time"], "Agendada"))
            else:
                self.send_json({"detail": "Rota nao encontrada"}, HTTPStatus.NOT_FOUND)
                return
            connection.commit()
            self.send_json({"message": "Registro salvo com sucesso"}, HTTPStatus.CREATED)
        except sqlite3.IntegrityError as error:
            self.send_json({"detail": "Registro duplicado ou invalido: " + str(error)}, HTTPStatus.BAD_REQUEST)
        except (KeyError, ValueError) as error:
            self.send_json({"detail": str(error)}, HTTPStatus.BAD_REQUEST)
        finally:
            connection.close()
        return
        if path != "/api/login":
            self.send_json({"detail": "Rota nao encontrada"}, HTTPStatus.NOT_FOUND)
            return
        data = self.read_json()
        connection = database()
        user = connection.execute("SELECT id,name,email,role FROM users WHERE email=? AND password=?", (data.get("email", ""), password_hash(data.get("password", "")))).fetchone()
        connection.close()
        if not user:
            self.send_json({"detail": "E-mail ou senha invalidos"}, HTTPStatus.UNAUTHORIZED)
            return
        public_user = dict(user)
        token = secrets.token_urlsafe(24)
        TOKENS[token] = public_user
        self.send_json({"token": token, "user": public_user})


if __name__ == "__main__":
    setup_database()
    print(f"Clinica local: http://localhost:{PORT}")
    print("Usuarios de teste: recepcao@clinica.local / recepcao123")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
