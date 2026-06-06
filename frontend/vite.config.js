import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  // Цель проксирования /api на бэкенд.
  // Локально (vite вне Docker): http://localhost:8000.
  // В Docker-контейнере: http://backend:8000 (через VITE_PROXY_TARGET).
  const proxyTarget = env.VITE_PROXY_TARGET || 'http://localhost:8000';

  return {
    plugins: [react()],
    server: {
      host: true,
      port: 5173,
      proxy: {
        '/api': {
          target: proxyTarget,
          changeOrigin: true,
        },
      },
      // Корректная работа HMR при запуске в контейнере Docker.
      watch: {
        usePolling: true,
      },
    },
  };
});
