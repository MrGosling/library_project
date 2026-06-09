import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom';

import { useAuth } from '../context/AuthContext.jsx';

function Layout() {
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="app">
      <header className="header">
        <div className="container header__inner">
          <Link to="/" className="logo">
            <span className="logo__icon">📚</span>
            <span>Электронная библиотека</span>
          </Link>
          <nav className="nav">
            <NavLink to="/" end className="nav__link">
              Главная
            </NavLink>
            <NavLink to="/books" className="nav__link">
              Каталог
            </NavLink>
            {isAuthenticated && (
              <>
                <NavLink to="/favorites" className="nav__link">
                  Избранное
                </NavLink>
                <NavLink to="/profile" className="nav__link">
                  Профиль
                </NavLink>
              </>
            )}
            {isAuthenticated ? (
              <button
                type="button"
                className="btn btn--ghost"
                onClick={handleLogout}
              >
                Выйти
              </button>
            ) : (
              <NavLink to="/login" className="btn btn--primary">
                Войти
              </NavLink>
            )}
          </nav>
        </div>
      </header>

      <main className="main container">
        <Outlet />
      </main>

      <footer className="footer">
        <div className="container">
          <p>Электронная библиотека — поиск, чтение и добавление книг.</p>
        </div>
      </footer>
    </div>
  );
}

export default Layout;
