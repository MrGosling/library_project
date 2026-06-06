import axios from 'axios';

// Базовый URL API. В production (nginx) и в dev (vite proxy) используется
// относительный путь '/api/v1', который проксируется на бэкенд.
// Можно переопределить через переменную окружения VITE_API_URL.
const baseURL = import.meta.env.VITE_API_URL || '/api/v1';

const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const TOKEN_KEY = 'library_token';

// Событие, которое генерируется при принудительном выходе (например, при 401),
// чтобы AuthContext мог синхронизировать своё состояние с localStorage.
export const AUTH_LOGOUT_EVENT = 'auth:logout';

// Интерцептор запросов: добавляем токен авторизации, если он есть.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Интерцептор ответов: при 401 очищаем токен.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem(TOKEN_KEY);
      // Уведомляем AuthContext, чтобы он сбросил состояние авторизации.
      window.dispatchEvent(new Event(AUTH_LOGOUT_EVENT));
    }
    return Promise.reject(error);
  }
);

export default api;
