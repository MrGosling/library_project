import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';

import { AUTH_LOGOUT_EVENT, TOKEN_KEY } from '../api.js';
import * as authService from '../services/auth.js';

const AuthContext = createContext(null);

// Извлекаем ID пользователя из токена формата "token_{id}".
function parseUserId(token) {
  if (!token || !token.startsWith('token_')) return null;
  const id = Number.parseInt(token.replace('token_', ''), 10);
  return Number.isNaN(id) ? null : id;
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));

  const login = useCallback(async (credentials) => {
    const data = await authService.login(credentials);
    localStorage.setItem(TOKEN_KEY, data.access_token);
    setToken(data.access_token);
    return data;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
  }, []);

  // Сбрасываем состояние при принудительном выходе (401) и при изменении
  // токена в другой вкладке.
  useEffect(() => {
    const handleLogout = () => setToken(null);
    const handleStorage = (event) => {
      if (event.key === TOKEN_KEY) {
        setToken(event.newValue);
      }
    };
    window.addEventListener(AUTH_LOGOUT_EVENT, handleLogout);
    window.addEventListener('storage', handleStorage);
    return () => {
      window.removeEventListener(AUTH_LOGOUT_EVENT, handleLogout);
      window.removeEventListener('storage', handleStorage);
    };
  }, []);

  const value = useMemo(
    () => ({
      token,
      userId: parseUserId(token),
      isAuthenticated: Boolean(token),
      login,
      logout,
    }),
    [token, login, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth должен использоваться внутри AuthProvider');
  }
  return context;
}
