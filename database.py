import sqlite3

# Початкові рецепти для ініціалізації бази
INITIAL_RECIPES = [
    ("Борщ український", "Класичний червоний борщ з яловичиною. #обід #перші_страви"),
    ("Піца з ковбасою", "Домашня піца на тонкому тісті з сиром моцарела. #піца #випічка"),
    ("Салат Цезар", "Легкий салат з куркою та соусом цезар. #салат #обід"),
    ("Омлет із зеленню", "Ніжний та швидкий сніданок з яєць і зелені. #сніданок"),
    ("Сирники", "Пишні сирники до кави. #сніданок #десерти"),
    ("Запечена курка", "Соковита курка в духовці з овочами. #вечеря #курка")
]

def get_connection():
    """Створення підключення до бази даних."""
    return sqlite3.connect("recipes.db")

def init_db():
    """Створення та первинне наповнення бази даних."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM recipes")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany(
            "INSERT INTO recipes (title, description) VALUES (?, ?)",
            INITIAL_RECIPES
        )

    conn.commit()
    conn.close()

def search_recipes(query: str):
    """Пошук рецептів з урахуванням відмінків та без '#'."""
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
        SELECT * FROM recipes 
        WHERE LOWER(REPLACE(title, '#', '')) LIKE ? 
           OR LOWER(REPLACE(description, '#', '')) LIKE ?
    """

    param = f"%{search_term}%"
    cursor.execute(sql_query, (param, param))

    results = cursor.fetchall()
    conn.close()

    return results

# --- ФУНКЦІЇ ДЛЯ КНОПОК КАТЕГОРІЙ ---

def get_breakfast_recipes():
    """Отримання рецептів для сніданку."""
    return search_recipes("сніданок")

def get_lunch_recipes():
    """Отримання рецептів для обіду."""
    return search_recipes("обід")

def get_dinner_recipes():
    """Отримання рецептів для вечері."""
    return search_recipes("вечеря")

def get_baking_recipes():
    """Отримання рецептів випічки."""
    return search_recipes("випічка")

def get_dessert_recipes():
    """Отримання рецептів десертів."""
    return search_recipes("десерти")

def get_video_recipes():
    """Отримання відеорецептів."""
    return search_recipes("відео")

def add_recipe(title: str, description: str):
    """Додавання рецепта."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO recipes (title, description) VALUES (?, ?)",
        (title, description)
    )
    conn.commit()
    conn.close()

def get_all_recipes():
    """Отримання всіх рецептів."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recipes")
    results = cursor.fetchall()
    conn.close()
    return results
