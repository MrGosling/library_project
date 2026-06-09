import api from '../api.js';

// Список книг с фильтрами и пагинацией.
export async function getBooks(params = {}) {
  const { data } = await api.get('/books', { params });
  return data;
}

// Получить книгу по ID.
export async function getBook(id) {
  const { data } = await api.get(`/books/${id}`);
  return data;
}

// Создать книгу.
export async function createBook(payload) {
  const { data } = await api.post('/books', payload);
  return data;
}

// Удалить книгу.
export async function deleteBook(id) {
  await api.delete(`/books/${id}`);
}
