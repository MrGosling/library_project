import { Link } from 'react-router-dom';

const features = [
  {
    icon: '🔎',
    title: 'Поиск книг',
    text: 'Ищите книги по названию, автору и категории.',
  },
  {
    icon: '📖',
    title: 'Страница книги',
    text: 'Описание, отзывы и рейтинг каждой книги.',
  },
  {
    icon: '⭐',
    title: 'Избранное',
    text: 'Добавляйте книги в избранное и отслеживайте прочитанное.',
  },
  {
    icon: '🤖',
    title: 'ИИ-рекомендации',
    text: 'Персональные рекомендации на основе прочитанного.',
  },
];

function Home() {
  return (
    <div className="home">
      <section className="hero">
        <h1 className="hero__title">Электронная библиотека</h1>
        <p className="hero__subtitle">
          Приложение для поиска, чтения и добавления книг с управлением
          избранным и личным кабинетом.
        </p>
        <div className="hero__actions">
          <Link to="/books" className="btn btn--primary btn--lg">
            Открыть каталог
          </Link>
          <Link to="/register" className="btn btn--ghost btn--lg">
            Регистрация
          </Link>
        </div>
      </section>

      <section className="features">
        {features.map((feature) => (
          <div key={feature.title} className="card feature">
            <div className="feature__icon">{feature.icon}</div>
            <h3 className="feature__title">{feature.title}</h3>
            <p className="feature__text">{feature.text}</p>
          </div>
        ))}
      </section>
    </div>
  );
}

export default Home;
