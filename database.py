import sqlite3

# Початковий список рецептів (якщо база створюється з нуля)
INITIAL_RECIPES = [
    ("Борщ український", "Класичний червоний борщ з яловичиною.", "обід"),
    ("Піца з ковбасою", "Домашня піца на тонкому тісті.", "випічка"),
    ("Салат Цезар", "Легкий салат з куркою.", "обід"),
    ("Омлет із зеленню", "Ніжний та швидкий сніданок.", "сніданок"),
    ("Сирники", "Пишні сирники до кави.", "десерти"),
]


def get_connection():
    """Підключення до бази даних SQLite."""
    return sqlite3.connect("recipes.db")


def init_db():
    """Ініціалізація бази даних з 4 колонками."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT DEFAULT ''
        )
    """
    )

    cursor.execute("SELECT COUNT(*) FROM recipes")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany(
            "INSERT INTO recipes (title, description, category) VALUES (?, ?, ?)",
            INITIAL_RECIPES,
        )

    conn.commit()
    conn.close()


def search_recipes(query: str):
    """
    Розумний пошук рецептів:
    - Прибирає '#' з пошукового запиту та з текстів у базі
    - Відрізає закінчення слів від 4 літер для урахування відмінків
    - Повертає 4 колонки: id, title, description, category
    """
    if not query:
        return []

    clean_query = query.replace("#", "").strip().lower()

    if not clean_query:
        return []

    if len(clean_query) >= 4:
        search_term = clean_query[:-1]
    else:
        search_term = clean_query

    conn = get_connection()
    cursor = conn.cursor()

    sql_query = """
        SELECT id, title, description, category FROM recipes 
        WHERE LOWER(REPLACE(title, '#', '')) LIKE ? 
           OR LOWER(REPLACE(description, '#', '')) LIKE ?
           OR LOWER(REPLACE(category, '#', '')) LIKE ?
    """

    param = f"%{search_term}%"
    cursor.execute(sql_query, (param, param, param))

    results = cursor.fetchall()
    conn.close()

    return results


# --- ФУНКЦІЇ ДЛЯ КНОПОК МЕНЮ ---


def get_breakfast_recipes():
    return search_recipes("сніданок")


def get_lunch_recipes():
    return search_recipes("обід")


def get_dinner_recipes():
    return search_recipes("вечеря")


def get_baking_recipes():
    return search_recipes("випічка")


def get_dessert_recipes():
    return search_recipes("десерт")


def get_video_recipes():
    return search_recipes("відео")


def add_recipe(title: str, description: str, category: str = ""):
    """Додавання нового рецепта."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO recipes (title, description, category) VALUES (?, ?, ?)",
        (title, description, category),
    )
    conn.commit()
    conn.close()


def get_all_recipes():
    """Отримання всіх рецептів з бази."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, category FROM recipes")
    results = cursor.fetchall()
    conn.close()
    return results
