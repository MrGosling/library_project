import api from '../api.js';

// Список избранного.
export async function getFavorites() {
  const { data } = await api.get('/favorites/');
  return data;
}

// Добавить книгу в избранное.
export async function addFavorite(payload) {
  const { data } = await api.post('/favorites/', payload);
  return data;
}

// Удалить из избранного.
export async function removeFavorite(id) {
  await api.delete(`/favorites/${id}`);
}
