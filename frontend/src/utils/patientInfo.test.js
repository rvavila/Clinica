import { ageLabel, calculateAge } from './patientInfo';

describe('informações do paciente', () => {
  const referenceDate = new Date(2026, 8, 7);

  test('calcula a idade considerando o aniversário', () => {
    expect(calculateAge('2000-09-06', referenceDate)).toBe(26);
    expect(calculateAge('2000-09-08', referenceDate)).toBe(25);
  });

  test('informa quando a data de nascimento não existe', () => {
    expect(ageLabel('', referenceDate)).toBe('Idade não informada');
  });
});
