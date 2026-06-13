import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { vi } from 'vitest';

import { AuthContext } from '../context/AuthContext.jsx';
import ProtectedRoute from '../components/ProtectedRoute.jsx';

test('авторизованный пользователь видит страницу', () => {
  const authValue = {
    token: 'token_1',
    isAuthenticated: true,
    userId: 1,
    login: vi.fn(),
    logout: vi.fn(),
  };

  render(
    <MemoryRouter initialEntries={['/profile']}>
      <AuthContext.Provider value={authValue}>
        <Routes>
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <div>Личный кабинет</div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthContext.Provider>
    </MemoryRouter>
  );

  expect(screen.getByText('Личный кабинет')).toBeInTheDocument();
});

test('неавторизованный пользователь перенаправляется на логин', () => {
  const authValue = {
    token: null,
    isAuthenticated: false,
    userId: null,
    login: vi.fn(),
    logout: vi.fn(),
  };

  render(
    <MemoryRouter initialEntries={['/profile']}>
      <AuthContext.Provider value={authValue}>
        <Routes>
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <div>Личный кабинет</div>
              </ProtectedRoute>
            }
          />
          <Route path="/login" element={<div>Страница входа</div>} />
        </Routes>
      </AuthContext.Provider>
    </MemoryRouter>
  );

  expect(screen.getByText('Страница входа')).toBeInTheDocument();
  expect(screen.queryByText('Личный кабинет')).not.toBeInTheDocument();
});
