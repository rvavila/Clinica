import {
  appointmentStatusLabel,
  consultationTypeLabel,
} from './appointmentLabels';

describe('rótulos de agendamento', () => {
  test('converte status conhecidos para português', () => {
    expect(appointmentStatusLabel('scheduled')).toBe('Agendada');
    expect(appointmentStatusLabel('in_progress')).toBe('Em atendimento');
  });

  test('mantém valores desconhecidos para facilitar compatibilidade', () => {
    expect(appointmentStatusLabel('future_status')).toBe('future_status');
  });

  test('converte tipos de consulta conhecidos', () => {
    expect(consultationTypeLabel('first_visit')).toBe('Primeira consulta');
    expect(consultationTypeLabel('emergency')).toBe('Emergência');
  });
});
