from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.core.db import AsyncSessionLocal
from backend.models.author import Author
from backend.models.category import Category
from backend.models.genre import Genre
from backend.models.book import Book


async def create_initial_authors() -> None:
    authors_data = [
        {
            'full_name': 'Лев Толстой',
            'birth_year': 1828,
            'bio': 'Один из величайших писателей-романистов мира.',
        },
        {
            'full_name': 'Федор Достоевский',
            'birth_year': 1821,
            'bio': 'Классик русской литературы и один из лучших романистов мирового значения.',
        },
        {
            'full_name': 'Александр Пушкин',
            'birth_year': 1799,
            'bio': 'Великий русский поэт, драматург и прозаик.',
        },
        {
            'full_name': 'Михаил Булгаков',
            'birth_year': 1891,
            'bio': 'Русский писатель советского периода, драматург, филолог.',
        },
        {
            'full_name': 'Антон Чехов',
            'birth_year': 1860,
            'bio': 'Выдающийся русский писатель, драматург, классик мировой литературы.',
        },
        {
            'full_name': 'Джордж Оруэлл',
            'birth_year': 1903,
            'bio': 'Британский писатель и публицист, автор антиутопий.',
        },
        {
            'full_name': 'Эрнест Хемингуэй',
            'birth_year': 1899,
            'bio': 'Американский писатель, журналист, лауреат Нобелевской премии.',
        },
        {
            'full_name': 'Габриэль Гарсиа Маркес',
            'birth_year': 1927,
            'bio': 'Колумбийский писатель-прозаик, журналист, издатель и политический деятель.',
        },
        {
            'full_name': 'Франц Кафка',
            'birth_year': 1883,
            'bio': 'Один из крупнейших немецкоязычных писателей XX века.',
        },
        {
            'full_name': 'Рэй Брэдбери',
            'birth_year': 1920,
            'bio': 'Американский писатель, известный по роману «451 градус по Фаренгейту».',
        },
    ]

    async with AsyncSessionLocal() as session:
        for author_info in authors_data:
            result = await session.execute(
                select(Author).where(
                    Author.full_name == author_info['full_name']
                )
            )
            if not result.scalars().first():
                session.add(Author(**author_info))
        await session.commit()


async def create_initial_categories() -> None:
    categories_data = [
        {
            'name': 'Художественная литература',
            'description': 'Литературный род, использующий в качестве единственного материала слова языка.',
        },
        {
            'name': 'Научно-популярная',
            'description': 'Произведения о науке, научных достижениях и об учёных.',
        },
        {
            'name': 'Классика',
            'description': 'Произведения, считающиеся образцовыми для той или иной эпохи.',
        },
        {
            'name': 'Современная проза',
            'description': 'Литературные произведения, созданные в наши дни.',
        },
    ]

    async with AsyncSessionLocal() as session:
        for cat_info in categories_data:
            result = await session.execute(
                select(Category).where(Category.name == cat_info['name'])
            )
            if not result.scalars().first():
                session.add(Category(**cat_info))
        await session.commit()


async def create_initial_genres() -> None:
    genres_data = [
        {'name': 'Роман'},
        {'name': 'Драма'},
        {'name': 'Антиутопия'},
        {'name': 'Фантастика'},
        {'name': 'Детектив'},
    ]

    async with AsyncSessionLocal() as session:
        for genre_info in genres_data:
            result = await session.execute(
                select(Genre).where(Genre.name == genre_info['name'])
            )
            if not result.scalars().first():
                session.add(Genre(**genre_info))
        await session.commit()


async def create_initial_books() -> None:
    async with AsyncSessionLocal() as session:
        # Получаем авторов, жанры и категории для связей
        authors_result = await session.execute(select(Author))
        authors = {a.full_name: a for a in authors_result.scalars().all()}

        genres_result = await session.execute(select(Genre))
        genres = {g.name: g for g in genres_result.scalars().all()}

        categories_result = await session.execute(select(Category))
        categories = {c.name: c for c in categories_result.scalars().all()}

        books_data = [
            {
                'title': 'Война и мир',
                'pub_year': 1869,
                'author_name': 'Лев Толстой',
                'description': 'Роман-эпопея Льва Николаевича Толстого.',
                'genre_names': ['Роман'],
                'category_names': ['Классика', 'Художественная литература'],
            },
            {
                'title': 'Преступление и наказание',
                'pub_year': 1866,
                'author_name': 'Федор Достоевский',
                'description': 'Роман Фёдора Михайловича Достоевского.',
                'genre_names': ['Роман', 'Драма'],
                'category_names': ['Классика', 'Художественная литература'],
            },
            {
                'title': 'Евгений Онегин',
                'pub_year': 1833,
                'author_name': 'Александр Пушкин',
                'description': 'Роман в стихах Александра Сергеевича Пушкина.',
                'genre_names': ['Роман'],
                'category_names': ['Классика'],
            },
            {
                'title': 'Мастер и Маргарита',
                'pub_year': 1967,
                'author_name': 'Михаил Булгаков',
                'description': 'Роман Михаила Афанасьевича Булгакова.',
                'genre_names': ['Роман', 'Фантастика'],
                'category_names': ['Классика', 'Художественная литература'],
            },
            {
                'title': 'Палата №6',
                'pub_year': 1892,
                'author_name': 'Антон Чехов',
                'description': 'Повесть Антона Павловича Чехова.',
                'genre_names': ['Драма'],
                'category_names': ['Классика'],
            },
            {
                'title': '1984',
                'pub_year': 1949,
                'author_name': 'Джордж Оруэлл',
                'description': 'Роман-антиутопия Джорджа Оруэлла.',
                'genre_names': ['Роман', 'Антиутопия'],
                'category_names': ['Художественная литература'],
            },
            {
                'title': 'Старик и море',
                'pub_year': 1952,
                'author_name': 'Эрнест Хемингуэй',
                'description': 'Повесть Эрнеста Хемингуэя.',
                'genre_names': ['Драма'],
                'category_names': ['Художественная литература'],
            },
            {
                'title': 'Сто лет одиночества',
                'pub_year': 1967,
                'author_name': 'Габриэль Гарсиа Маркес',
                'description': 'Роман Габриэля Гарсиа Маркеса.',
                'genre_names': ['Роман'],
                'category_names': ['Художественная литература'],
            },
            {
                'title': 'Процесс',
                'pub_year': 1925,
                'author_name': 'Франц Кафка',
                'description': 'Роман Франца Кафки.',
                'genre_names': ['Роман', 'Драма'],
                'category_names': ['Классика'],
            },
            {
                'title': '451 градус по Фаренгейту',
                'pub_year': 1953,
                'author_name': 'Рэй Брэдбери',
                'description': 'Научно-фантастический роман-антиутопия Рэя Брэдбери.',
                'genre_names': ['Роман', 'Фантастика', 'Антиутопия'],
                'category_names': ['Художественная литература'],
            },
        ]

        for book_info in books_data:
            # Ищем книгу, включая загрузку текущих жанров и категорий
            result = await session.execute(
                select(Book)
                .where(Book.title == book_info['title'])
                .options(
                    selectinload(Book.genres), selectinload(Book.categories)
                )
            )
            book = result.scalars().first()

            author_name = book_info.pop('author_name')
            genre_names = book_info.pop('genre_names')
            category_names = book_info.pop('category_names')

            if not book:
                author = authors.get(author_name)
                if author:
                    book = Book(**book_info, author_id=author.id)
                    session.add(book)

            if book:
                # Обновляем жанры, если их нет
                current_genre_names = {g.name for g in book.genres}
                for g_name in genre_names:
                    if g_name in genres and g_name not in current_genre_names:
                        book.genres.append(genres[g_name])

                # Обновляем категории, если их нет
                current_cat_names = {c.name for c in book.categories}
                for c_name in category_names:
                    if (
                        c_name in categories
                        and c_name not in current_cat_names
                    ):
                        book.categories.append(categories[c_name])

        await session.commit()


async def create_initial_data() -> None:
    await create_initial_authors()
    await create_initial_categories()
    await create_initial_genres()
    await create_initial_books()
