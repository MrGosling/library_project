import api from '../api.js';

// Список отзывов.
export async function getReviews() {
  const { data } = await api.get('/reviews/');
  return data;
}

// Создать отзыв.
export async function createReview(payload) {
  const { data } = await api.post('/reviews/', payload);
  return data;
}
