import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';

import Loader from '../components/Loader.jsx';
import Message from '../components/Message.jsx';
import { useAuth } from '../context/AuthContext.jsx';
import { deleteBook, getBook } from '../services/books.js';
import { getAuthor } from '../services/catalog.js';
import { addFavorite } from '../services/favorites.js';
import { createReview, getReviews } from '../services/reviews.js';
import { getErrorMessage } from '../utils/error.js';

function BookDetail() {
  const { id } = useParams();
  const bookId = Number(id);
  const navigate = useNavigate();
  const { isAuthenticated, userId } = useAuth();

  const [book, setBook] = useState(null);
  const [author, setAuthor] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  const loadReviews = useCallback(async () => {
    try {
      const all = await getReviews();
      setReviews(all.filter((review) => review.book_id === bookId));
    } catch {
      setReviews([]);
    }
  }, [bookId]);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError('');
    getBook(bookId)
      .then(async (data) => {
        if (!active) return;
        setBook(data);
        if (data.author_id) {
          try {
            const authorData = await getAuthor(data.author_id);
            if (active) setAuthor(authorData);
          } catch {
            /* автор может быть недоступен */
          }
        }
      })
      .catch((err) => {
        if (active) setError(getErrorMessage(err, 'Книга не найдена'));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    loadReviews();
    return () => {
      active = false;
    };
  }, [bookId, loadReviews]);

  const averageRating = useMemo(() => {
    if (reviews.length === 0) return null;
    const sum = reviews.reduce((acc, review) => acc + review.rating, 0);
    return (sum / reviews.length).toFixed(1);
  }, [reviews]);

  const handleAddFavorite = async () => {
    setNotice('');
    setError('');
    try {
      await addFavorite({ user_id: userId, book_id: bookId, is_read: false });
      setNotice('Книга добавлена в избранное.');
    } catch (err) {
      setError(getErrorMessage(err, 'Не удалось добавить в избранное'));
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Удалить книгу?')) return;
    try {
      await deleteBook(bookId);
      navigate('/books');
    } catch (err) {
      setError(getErrorMessage(err, 'Не удалось удалить книгу'));
    }
  };

  if (loading) return <Loader />;
  if (error && !book) {
    return (
      <div>
        <Message type="error">{error}</Message>
        <Link to="/books" className="btn btn--ghost">
          ← К каталогу
        </Link>
      </div>
    );
  }
  if (!book) return null;

  return (
    <div className="book-detail">
      <Link to="/books" className="back-link">
        ← К каталогу
      </Link>

      <div className="book-detail__head card">
        <div className="book-detail__cover">
          {book.title?.charAt(0)?.toUpperCase()}
        </div>
        <div className="book-detail__info">
          <h1>{book.title}</h1>
          <p className="book-detail__author">
            {author ? (
              <>Автор: {author.full_name}</>
            ) : (
              <>Автор #{book.author_id}</>
            )}
          </p>
          <p className="book-detail__year">Год издания: {book.pub_year}</p>
          <p className="book-detail__rating">
            Рейтинг:{' '}
            {averageRating ? `${averageRating} / 5` : 'нет оценок'}
            {reviews.length > 0 && ` (${reviews.length})`}
          </p>
          {book.description && (
            <p className="book-detail__desc">{book.description}</p>
          )}
          <Message type="success">{notice}</Message>
          <Message type="error">{error}</Message>
          <div className="book-detail__actions">
            {isAuthenticated && (
              <button
                type="button"
                className="btn btn--primary"
                onClick={handleAddFavorite}
              >
                ⭐ В избранное
              </button>
            )}
            {isAuthenticated && (
              <button
                type="button"
                className="btn btn--danger"
                onClick={handleDelete}
              >
                Удалить
              </button>
            )}
          </div>
        </div>
      </div>

      <section className="reviews">
        <h2>Отзывы</h2>
        {reviews.length === 0 ? (
          <p className="empty">Пока нет отзывов.</p>
        ) : (
          <ul className="reviews__list">
            {reviews.map((review) => (
              <li key={review.id} className="card review">
                <div className="review__rating">★ {review.rating}/5</div>
                {review.text && <p>{review.text}</p>}
              </li>
            ))}
          </ul>
        )}

        {isAuthenticated && (
          <ReviewForm
            bookId={bookId}
            userId={userId}
            onCreated={loadReviews}
          />
        )}
      </section>
    </div>
  );
}

function ReviewForm({ bookId, userId, onCreated }) {
  const [rating, setRating] = useState(5);
  const [text, setText] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSaving(true);
    try {
      await createReview({
        rating: Number(rating),
        text: text || null,
        book_id: bookId,
        user_id: userId,
      });
      setText('');
      setRating(5);
      onCreated();
    } catch (err) {
      setError(getErrorMessage(err, 'Не удалось отправить отзыв'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <form className="card form review-form" onSubmit={handleSubmit}>
      <h3>Оставить отзыв</h3>
      <Message type="error">{error}</Message>
      <label className="form__field">
        <span>Оценка</span>
        <select value={rating} onChange={(e) => setRating(e.target.value)}>
          {[5, 4, 3, 2, 1].map((value) => (
            <option key={value} value={value}>
              {value}
            </option>
          ))}
        </select>
      </label>
      <label className="form__field">
        <span>Комментарий</span>
        <textarea
          rows={3}
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
      </label>
      <button type="submit" className="btn btn--primary" disabled={saving}>
        {saving ? 'Отправка...' : 'Отправить'}
      </button>
    </form>
  );
}

export default BookDetail;
