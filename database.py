import sqlite3

def get_connection():
    """Підключення до бази даних."""
    return sqlite3.connect("recipes.db")

def init_db():
    """Створення таблиці рецептів з 4 колонками (id, title, description, category)."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT DEFAULT ''
        )
    """)

    conn.commit()
    conn.close()

def search_recipes(query: str):
    """
    Пошук рецептів (повертає 4 поля, щоб bot.py не видавав ValueError):
    - Ігнорує решітки '#'
    - Враховує відмінки
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

    # Пошук повертає 4 колонки: id, title, description, category
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
    """Додавання рецепта з 4 параметрами."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO recipes (title, description, category) VALUES (?, ?, ?)",
        (title, description, category)
    )
    conn.commit()
    conn.close()

def get_all_recipes():
    """Отримання всіх рецептів (4 колонки)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, category FROM recipes")
    results = cursor.fetchall()
    conn.close()
    return results
