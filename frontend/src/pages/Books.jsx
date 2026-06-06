import { useCallback, useEffect, useMemo, useState } from 'react';

import BookCard from '../components/BookCard.jsx';
import Loader from '../components/Loader.jsx';
import Message from '../components/Message.jsx';
import { useAuth } from '../context/AuthContext.jsx';
import { getAuthors, getCategories } from '../services/catalog.js';
import { createBook, getBooks } from '../services/books.js';
import { getErrorMessage } from '../utils/error.js';

const PAGE_SIZE = 12;

function Books() {
  const { isAuthenticated } = useAuth();

  const [books, setBooks] = useState([]);
  const [authors, setAuthors] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Фильтры.
  const [search, setSearch] = useState('');
  const [authorId, setAuthorId] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [page, setPage] = useState(0);

  const authorsById = useMemo(() => {
    const map = {};
    authors.forEach((author) => {
      map[author.id] = author.full_name;
    });
    return map;
  }, [authors]);

  const loadBooks = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const params = {
        limit: PAGE_SIZE,
        offset: page * PAGE_SIZE,
      };
      if (search.trim()) params.search = search.trim();
      if (authorId) params.author_id = Number(authorId);
      if (categoryId) params.category_id = Number(categoryId);
      const data = await getBooks(params);
      setBooks(data);
    } catch (err) {
      setError(getErrorMessage(err, 'Не удалось загрузить книги'));
    } finally {
      setLoading(false);
    }
  }, [search, authorId, categoryId, page]);

  useEffect(() => {
    loadBooks();
  }, [loadBooks]);

  useEffect(() => {
    // Загружаем справочники для фильтров один раз.
    getAuthors({ limit: 100 })
      .then(setAuthors)
      .catch(() => setAuthors([]));
    getCategories()
      .then(setCategories)
      .catch(() => setCategories([]));
  }, []);

  const handleFilterSubmit = (event) => {
    event.preventDefault();
    setPage(0);
    loadBooks();
  };

  const resetFilters = () => {
    setSearch('');
    setAuthorId('');
    setCategoryId('');
    setPage(0);
  };

  return (
    <div className="books-page">
      <div className="page-head">
        <h1>Каталог книг</h1>
      </div>

      <form className="filters card" onSubmit={handleFilterSubmit}>
        <input
          className="filters__search"
          placeholder="Поиск по названию..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
        <select
          value={authorId}
          onChange={(event) => {
            setAuthorId(event.target.value);
            setPage(0);
          }}
        >
          <option value="">Все авторы</option>
          {authors.map((author) => (
            <option key={author.id} value={author.id}>
              {author.full_name}
            </option>
          ))}
        </select>
        <select
          value={categoryId}
          onChange={(event) => {
            setCategoryId(event.target.value);
            setPage(0);
          }}
        >
          <option value="">Все категории</option>
          {categories.map((category) => (
            <option key={category.id} value={category.id}>
              {category.name}
            </option>
          ))}
        </select>
        <button type="submit" className="btn btn--primary">
          Найти
        </button>
        <button type="button" className="btn btn--ghost" onClick={resetFilters}>
          Сбросить
        </button>
      </form>

      <Message type="error">{error}</Message>

      {isAuthenticated && (
        <AddBookForm authors={authors} onCreated={loadBooks} />
      )}

      {loading ? (
        <Loader />
      ) : books.length === 0 ? (
        <p className="empty">Книги не найдены.</p>
      ) : (
        <div className="grid">
          {books.map((book) => (
            <BookCard
              key={book.id}
              book={book}
              authorName={authorsById[book.author_id]}
            />
          ))}
        </div>
      )}

      <div className="pagination">
        <button
          type="button"
          className="btn btn--ghost"
          disabled={page === 0 || loading}
          onClick={() => setPage((prev) => Math.max(0, prev - 1))}
        >
          ← Назад
        </button>
        <span>Страница {page + 1}</span>
        <button
          type="button"
          className="btn btn--ghost"
          disabled={books.length < PAGE_SIZE || loading}
          onClick={() => setPage((prev) => prev + 1)}
        >
          Вперёд →
        </button>
      </div>
    </div>
  );
}

function AddBookForm({ authors, onCreated }) {
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    title: '',
    pub_year: '',
    author_id: '',
    description: '',
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
      await createBook({
        title: form.title,
        pub_year: Number(form.pub_year),
        author_id: Number(form.author_id),
        description: form.description || null,
      });
      setSuccess('Книга добавлена.');
      setForm({ title: '', pub_year: '', author_id: '', description: '' });
      onCreated();
    } catch (err) {
      setError(getErrorMessage(err, 'Не удалось добавить книгу'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="card add-book">
      <button
        type="button"
        className="add-book__toggle"
        onClick={() => setOpen((prev) => !prev)}
      >
        {open ? '− Скрыть форму' : '+ Добавить книгу'}
      </button>
      {open && (
        <form className="form" onSubmit={handleSubmit}>
          <Message type="error">{error}</Message>
          <Message type="success">{success}</Message>
          <div className="form__row">
            <label className="form__field">
              <span>Название</span>
              <input
                name="title"
                value={form.title}
                onChange={handleChange}
                required
              />
            </label>
            <label className="form__field">
              <span>Год издания</span>
              <input
                name="pub_year"
                type="number"
                value={form.pub_year}
                onChange={handleChange}
                required
              />
            </label>
          </div>
          <label className="form__field">
            <span>Автор</span>
            <select
              name="author_id"
              value={form.author_id}
              onChange={handleChange}
              required
            >
              <option value="">Выберите автора</option>
              {authors.map((author) => (
                <option key={author.id} value={author.id}>
                  {author.full_name}
                </option>
              ))}
            </select>
          </label>
          <label className="form__field">
            <span>Описание</span>
            <textarea
              name="description"
              rows={3}
              value={form.description}
              onChange={handleChange}
            />
          </label>
          <button
            type="submit"
            className="btn btn--primary"
            disabled={saving}
          >
            {saving ? 'Сохранение...' : 'Сохранить'}
          </button>
        </form>
      )}
    </div>
  );
}

export default Books;
