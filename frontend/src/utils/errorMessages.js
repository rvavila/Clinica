export const getApiErrorMessage = (error, fallback = 'Não foi possível concluir a operação.') => {
  const detail = error?.response?.data?.detail;

  if (Array.isArray(detail)) {
    return detail.map((item) => {
      const location = item.loc?.[item.loc.length - 1] || 'campo';
      return `${location}: ${item.msg}`;
    }).join(' | ');
  }

  if (typeof detail === 'string' && detail.trim()) return detail;
  if (error?.request && !error?.response) return 'Não foi possível conectar ao servidor. Tente novamente em alguns instantes.';
  return fallback;
};
