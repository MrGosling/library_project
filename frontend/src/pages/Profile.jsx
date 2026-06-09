import { useEffect, useState } from 'react';

import Message from '../components/Message.jsx';
import { useAuth } from '../context/AuthContext.jsx';
import { getFavorites } from '../services/favorites.js';
import { changePassword } from '../services/auth.js';
import { getErrorMessage } from '../utils/error.js';

function Profile() {
  const { userId } = useAuth();
  const [stats, setStats] = useState({ total: 0, read: 0 });

  useEffect(() => {
    getFavorites()
      .then((favorites) => {
        const mine = favorites.filter((fav) => fav.user_id === userId);
        setStats({
          total: mine.length,
          read: mine.filter((fav) => fav.is_read).length,
        });
      })
      .catch(() => setStats({ total: 0, read: 0 }));
  }, [userId]);

  return (
    <div className="profile-page">
      <div className="page-head">
        <h1>Личный кабинет</h1>
      </div>

      <div className="profile__stats">
        <div className="card stat">
          <span className="stat__value">{stats.total}</span>
          <span className="stat__label">В избранном</span>
        </div>
        <div className="card stat">
          <span className="stat__value">{stats.read}</span>
          <span className="stat__label">Прочитано</span>
        </div>
        <div className="card stat">
          <span className="stat__value">#{userId ?? '—'}</span>
          <span className="stat__label">ID пользователя</span>
        </div>
      </div>

      <ChangePasswordForm />
    </div>
  );
}

function ChangePasswordForm() {
  const [form, setForm] = useState({
    username: '',
    old_password: '',
    new_password: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [saving, setSaving] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSuccess('');
    setSaving(true);
    try {
      await changePassword(form);
      setSuccess('Пароль успешно изменён.');
      setForm({ username: '', old_password: '', new_password: '' });
    } catch (err) {
      setError(getErrorMessage(err, 'Не удалось сменить пароль'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <form className="card form" onSubmit={handleSubmit}>
      <h2>Смена пароля</h2>
      <Message type="error">{error}</Message>
      <Message type="success">{success}</Message>
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
        <span>Текущий пароль</span>
        <input
          name="old_password"
          type="password"
          value={form.old_password}
          onChange={handleChange}
          required
        />
      </label>
      <label className="form__field">
        <span>Новый пароль</span>
        <input
          name="new_password"
          type="password"
          value={form.new_password}
          onChange={handleChange}
          required
        />
      </label>
      <button type="submit" className="btn btn--primary" disabled={saving}>
        {saving ? 'Сохранение...' : 'Сменить пароль'}
      </button>
    </form>
  );
}

export default Profile;
