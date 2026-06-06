import { Link } from 'react-router-dom';

function BookCard({ book, authorName }) {
  return (
    <Link to={`/books/${book.id}`} className="card book-card">
      <div className="book-card__cover">
        <span>{book.title?.charAt(0)?.toUpperCase() || '?'}</span>
      </div>
      <div className="book-card__body">
        <h3 className="book-card__title">{book.title}</h3>
        <p className="book-card__meta">
          {authorName ? authorName : `Автор #${book.author_id}`}
        </p>
        <p className="book-card__year">{book.pub_year} г.</p>
        {book.description && (
          <p className="book-card__desc">{book.description}</p>
        )}
      </div>
    </Link>
  );
}

export default BookCard;
