export const appointmentStatusLabels = {
  scheduled: 'Agendada',
  // A clínica não usa uma etapa separada de confirmação.
  confirmed: 'Agendada',
  in_progress: 'Em atendimento',
  completed: 'Concluída',
  cancelled: 'Cancelada',
  no_show: 'Não compareceu',
};

export const consultationTypeLabels = {
  first_visit: 'Primeira consulta',
  follow_up: 'Retorno',
  emergency: 'Emergência',
  procedure: 'Procedimento',
};

export const appointmentStatusLabel = (value) => appointmentStatusLabels[value] || value;
export const consultationTypeLabel = (value) => consultationTypeLabels[value] || value;
