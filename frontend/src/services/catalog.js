import api from '../api.js';

// Авторы.
export async function getAuthors(params = {}) {
  const { data } = await api.get('/authors', { params });
  return data;
}

export async function getAuthor(id) {
  const { data } = await api.get(`/authors/${id}`);
  return data;
}

export async function createAuthor(payload) {
  const { data } = await api.post('/authors', payload);
  return data;
}

// Категории.
export async function getCategories() {
  const { data } = await api.get('/categories/');
  return data;
}

// Жанры.
export async function getGenres() {
  const { data } = await api.get('/genres/');
  return data;
}
