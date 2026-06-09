// Регистрация Service Worker. Работает только в production-сборке,
// чтобы не мешать горячей перезагрузке в режиме разработки.
export function registerServiceWorker() {
  if (!('serviceWorker' in navigator)) return;
  if (!import.meta.env.PROD) return;

  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/service-worker.js')
      .catch((error) => {
        // eslint-disable-next-line no-console
        console.error('Ошибка регистрации Service Worker:', error);
      });
  });
}
