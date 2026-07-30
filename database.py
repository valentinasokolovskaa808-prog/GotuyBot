import sqlite3

# Початкові рецепти (4 поля під ваш bot.py)
INITIAL_RECIPES = [
    (
        "Борщ український",
        "Яловичина, буряк, капуста, картопля, квасоля",
        "Класичний червоний борщ з яловичиною. #обід #перші_страви",
        "https://t.me/gotuy_prosti_recepty"
    ),
    (
        "Салат Цезар",
        "Куряче філе, салат айсберг, сухарики, соус цезар",
        "Легкий салат з куркою. #обід #салат #вечеря",
        "https://t.me/gotuy_prosti_recepty"
    ),
    (
        "Піца з ковбасою",
        "Тісто, ковбаса, моцарела, томатний соус",
        "Домашня піца на тонкому тісті. #випічка #піца",
        "https://t.me/gotuy_prosti_recepty"
    ),
    (
        "Сирники",
        "Домашній сир, яйця, борошно, цукор",
        "Ніжні та пишні сирники до сніданку. #сніданок #десерти",
        "https://t.me/gotuy_prosti_recepty"
    )
]

def get_connection():
    """Підключення до бази даних SQLite."""
    return sqlite3.connect("recipes.db")

def init_db():
    """Створення та первинне наповнення бази даних."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            ingredients TEXT DEFAULT '',
            description TEXT NOT NULL,
            link TEXT DEFAULT ''
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM recipes")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany(
            "INSERT INTO recipes (title, ingredients, description, link) VALUES (?, ?, ?, ?)",
            INITIAL_RECIPES
        )

    conn.commit()
    conn.close()

def search_recipes(query: str):
    """
    Пошук рецептів (повертає точно 4 значення для bot.py: title, ingredients, description, link):
    - Ігнорує '#'
    - Враховує відмінки (відрізає остання літеру для слів від 4 символів)
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

    # Повертаємо 4 поля, як очікує bot.py у рядку 121
    sql_query = """
        SELECT title, ingredients, description, link FROM recipes 
        WHERE LOWER(REPLACE(title, '#', '')) LIKE ? 
           OR LOWER(REPLACE(ingredients, '#', '')) LIKE ?
           OR LOWER(REPLACE(description, '#', '')) LIKE ?
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

def add_recipe(title: str, ingredients: str, description: str, link: str = ""):
    """Додавання нового рецепта."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO recipes (title, ingredients, description, link) VALUES (?, ?, ?, ?)",
        (title, ingredients, description, link)
    )
    conn.commit()
    conn.close()

def get_all_recipes():
    """Отримання всіх рецептів (4 поля)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, ingredients, description, link FROM recipes")
    results = cursor.fetchall()
    conn.close()
    return results
