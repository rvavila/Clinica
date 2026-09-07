import { getApiErrorMessage } from './errorMessages';

describe('mensagens de erro da API', () => {
  test('prioriza o detalhe retornado pelo servidor', () => {
    expect(getApiErrorMessage({ response: { data: { detail: 'Este CPF já está cadastrado.' } } }))
      .toBe('Este CPF já está cadastrado.');
  });

  test('informa campos de erros de validação', () => {
    expect(getApiErrorMessage({ response: { data: { detail: [{ loc: ['body', 'email'], msg: 'email inválido' }] } } }))
      .toBe('email: email inválido');
  });

  test('identifica falha de conexão', () => {
    expect(getApiErrorMessage({ request: {}, response: undefined }))
      .toContain('conectar ao servidor');
  });
});
