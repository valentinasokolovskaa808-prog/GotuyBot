import sqlite3

# сюди вставити ВСІ ваші початкові рецепти
INITIAL_RECIPES = [
    # ваш повний список рецептів...
]

def get_connection():
    return sqlite3.connect("recipes.db")

def init_db():
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

# Функції для кнопок меню
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

def add_recipe(title: str, description: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO recipes (title, description) VALUES (?, ?)",
        (title, description)
    )
    conn.commit()
    conn.close()

def get_all_recipes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recipes")
    results = cursor.fetchall()
    conn.close()
    return results
