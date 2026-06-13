import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import BookCard from '../components/BookCard.jsx';

const book = { id: 1, title: 'Мастер и Маргарита', pub_year: 1967, author_id: 2 };

test('показывает название книги', () => {
  render(
    <MemoryRouter>
      <BookCard book={book} authorName="Михаил Булгаков" />
    </MemoryRouter>
  );
  expect(screen.getByText('Мастер и Маргарита')).toBeInTheDocument();
});

test('показывает имя автора', () => {
  render(
    <MemoryRouter>
      <BookCard book={book} authorName="Михаил Булгаков" />
    </MemoryRouter>
  );
  expect(screen.getByText('Михаил Булгаков')).toBeInTheDocument();
});

test('если автор не передан показывает Автор #id', () => {
  render(
    <MemoryRouter>
      <BookCard book={book} />
    </MemoryRouter>
  );
  expect(screen.getByText('Автор #2')).toBeInTheDocument();
});

test('ссылка ведёт на страницу книги', () => {
  render(
    <MemoryRouter>
      <BookCard book={book} authorName="Михаил Булгаков" />
    </MemoryRouter>
  );
  expect(screen.getByRole('link')).toHaveAttribute('href', '/books/1');
});
