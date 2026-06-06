import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import Message from '../components/Message.jsx';
import { register } from '../services/auth.js';
import { getErrorMessage } from '../utils/error.js';

function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register({
        username: form.username,
        email: form.email,
        first_name: form.first_name || null,
        last_name: form.last_name || null,
        password: form.password,
      });
      navigate('/login', {
        state: { registered: true },
        replace: true,
      });
    } catch (err) {
      setError(getErrorMessage(err, 'Не удалось зарегистрироваться'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth">
      <div className="card auth__card">
        <h1 className="auth__title">Регистрация</h1>
        <Message type="error">{error}</Message>
        <form onSubmit={handleSubmit} className="form">
          <label className="form__field">
            <span>Логин</span>
            <input
              name="username"
              value={form.username}
              onChange={handleChange}
              required
            />
          </label>
          <label className="form__field">
            <span>Email</span>
            <input
              name="email"
              type="email"
              value={form.email}
              onChange={handleChange}
              required
            />
          </label>
          <div className="form__row">
            <label className="form__field">
              <span>Имя</span>
              <input
                name="first_name"
                value={form.first_name}
                onChange={handleChange}
              />
            </label>
            <label className="form__field">
              <span>Фамилия</span>
              <input
                name="last_name"
                value={form.last_name}
                onChange={handleChange}
              />
            </label>
          </div>
          <label className="form__field">
            <span>Пароль</span>
            <input
              name="password"
              type="password"
              value={form.password}
              onChange={handleChange}
              autoComplete="new-password"
              required
            />
          </label>
          <button
            type="submit"
            className="btn btn--primary btn--block"
            disabled={loading}
          >
            {loading ? 'Регистрация...' : 'Зарегистрироваться'}
          </button>
        </form>
        <p className="auth__hint">
          Уже есть аккаунт? <Link to="/login">Войти</Link>
        </p>
      </div>
    </div>
  );
}

export default Register;
