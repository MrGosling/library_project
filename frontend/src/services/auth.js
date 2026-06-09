import api from '../api.js';

// Регистрация нового пользователя.
export async function register(payload) {
  const { data } = await api.post('/users/register', payload);
  return data;
}

// Вход пользователя. Возвращает { access_token, token_type }.
export async function login(credentials) {
  const { data } = await api.post('/users/login', credentials);
  return data;
}

// Смена пароля.
export async function changePassword(payload) {
  const { data } = await api.post('/users/change-password', payload);
  return data;
}

// Обновление токена.
export async function refreshToken(token) {
  const { data } = await api.post('/users/refresh-token', { token });
  return data;
}
