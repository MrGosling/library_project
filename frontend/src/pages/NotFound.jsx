import { Link } from 'react-router-dom';

function NotFound() {
  return (
    <div className="notfound">
      <h1>404</h1>
      <p>Страница не найдена.</p>
      <Link to="/" className="btn btn--primary">
        На главную
      </Link>
    </div>
  );
}

export default NotFound;
