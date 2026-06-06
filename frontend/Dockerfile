# --- Этап сборки ---
FROM node:20-alpine AS build

WORKDIR /app

# Устанавливаем зависимости (кэшируется, пока не меняется package.json).
COPY package*.json ./
RUN npm install

# Копируем исходники и собираем production-бандл.
COPY . .
RUN npm run build

# --- Этап раздачи статики через nginx ---
FROM nginx:1.27-alpine

# Конфигурация nginx с проксированием API на бэкенд.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Копируем собранную статику.
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
