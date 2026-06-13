import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { vi } from 'vitest';

import { AuthContext } from '../context/AuthContext.jsx';
import Login from '../pages/Login.jsx';

test('на странице есть поля логин и пароль', () => {
  const authValue = {
    token: null,
    isAuthenticated: false,
    userId: null,
    login: vi.fn(),
    logout: vi.fn(),
  };

  render(
    <MemoryRouter initialEntries={['/login']}>
      <AuthContext.Provider value={authValue}>
        <Routes>
          <Route path="/login" element={<Login />} />
        </Routes>
      </AuthContext.Provider>
    </MemoryRouter>
  );

  expect(screen.getByLabelText(/логин/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/пароль/i)).toBeInTheDocument();
});

test('при отправке формы вызывается login', async () => {
  const loginFn = vi.fn().mockResolvedValue({});

  const authValue = {
    token: null,
    isAuthenticated: false,
    userId: null,
    login: loginFn,
    logout: vi.fn(),
  };

  render(
    <MemoryRouter initialEntries={['/login']}>
      <AuthContext.Provider value={authValue}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/books" element={<div>Каталог</div>} />
        </Routes>
      </AuthContext.Provider>
    </MemoryRouter>
  );

  await userEvent.type(screen.getByLabelText(/логин/i), 'testuser');
  await userEvent.type(screen.getByLabelText(/пароль/i), 'testpass');
  await userEvent.click(screen.getByRole('button', { name: /войти/i }));

  expect(loginFn).toHaveBeenCalledWith({ username: 'testuser', password: 'testpass' });
});

test('при неверном логине показывается ошибка', async () => {
  const loginFn = vi.fn().mockRejectedValue(new Error('Неверный логин или пароль'));

  const authValue = {
    token: null,
    isAuthenticated: false,
    userId: null,
    login: loginFn,
    logout: vi.fn(),
  };

  render(
    <MemoryRouter initialEntries={['/login']}>
      <AuthContext.Provider value={authValue}>
        <Routes>
          <Route path="/login" element={<Login />} />
        </Routes>
      </AuthContext.Provider>
    </MemoryRouter>
  );

  await userEvent.type(screen.getByLabelText(/логин/i), 'wrong');
  await userEvent.type(screen.getByLabelText(/пароль/i), 'wrong');
  await userEvent.click(screen.getByRole('button', { name: /войти/i }));

  expect(await screen.findByText(/неверный логин или пароль/i)).toBeInTheDocument();
});
