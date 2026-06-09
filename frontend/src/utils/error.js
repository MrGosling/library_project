export function getErrorMessage(error, fallback = 'Произошла ошибка') {
  const detail = error?.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail) && detail.length > 0) {
    return detail.map((item) => item.msg || JSON.stringify(item)).join('; ');
  }
  if (error?.message) return error.message;
  return fallback;
}
