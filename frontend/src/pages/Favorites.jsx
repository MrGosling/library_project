import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import Loader from '../components/Loader.jsx';
import Message from '../components/Message.jsx';
import { useAuth } from '../context/AuthContext.jsx';
import { getBook } from '../services/books.js';
import { getFavorites, removeFavorite } from '../services/favorites.js';
import { getErrorMessage } from '../utils/error.js';

function Favorites() {
  const { userId } = useAuth();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const favorites = await getFavorites();
      const mine = favorites.filter((fav) => fav.user_id === userId);
      // Подгружаем данные книг для каждого избранного.
      const withBooks = await Promise.all(
        mine.map(async (fav) => {
          try {
            const book = await getBook(fav.book_id);
            return { ...fav, book };
          } catch {
            return { ...fav, book: null };
          }
        })
      );
      setItems(withBooks);
    } catch (err) {
      setError(getErrorMessage(err, 'Не удалось загрузить избранное'));
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    load();
  }, [load]);

  const handleRemove = async (id) => {
    try {
      await removeFavorite(id);
      setItems((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      setError(getErrorMessage(err, 'Не удалось удалить из избранного'));
    }
  };

  if (loading) return <Loader />;

  return (
    <div className="favorites-page">
      <div className="page-head">
        <h1>Избранное</h1>
      </div>
      <Message type="error">{error}</Message>
      {items.length === 0 ? (
        <p className="empty">
          В избранном пока ничего нет.{' '}
          <Link to="/books">Перейти в каталог</Link>
        </p>
      ) : (
        <ul className="favorites__list">
          {items.map((item) => (
            <li key={item.id} className="card favorite-row">
              <div>
                <h3>
                  {item.book ? (
                    <Link to={`/books/${item.book.id}`}>
                      {item.book.title}
                    </Link>
                  ) : (
                    `Книга #${item.book_id}`
                  )}
                </h3>
                <span
                  className={`badge ${item.is_read ? 'badge--read' : ''}`}
                >
                  {item.is_read ? 'Прочитано' : 'Не прочитано'}
                </span>
              </div>
              <button
                type="button"
                className="btn btn--danger"
                onClick={() => handleRemove(item.id)}
              >
                Удалить
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default Favorites;
