import sqlite3

# Початкові рецепти для найпершого запуску бази
INITIAL_RECIPES = [
    ("Борщ український", "Класичний червоний борщ з яловичиною. #обід #перші_страви"),
    ("Піца з ковбасою", "Домашня піца на тонкому тісті з сиром моцарела. #піца #випічка"),
    ("Салат Цезар", "Легкий салат з куркою та соусом цезар. #салат #обід"),
    ("Омлет із зеленню", "Ніжний та швидкий сніданок з яєць і зелені. #сніданок"),
    ("Сирники", "Пишні сирники до кави. #сніданок #десерти")
]

def get_connection():
    """Створення підключення до бази даних SQLite."""
    return sqlite3.connect("recipes.db")

def init_db():
    """
    Створення таблиці рецептів при старті.
    Наповнює базовими даними тільки якщо база порожня.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL
        )
    """)

    # Перевіряємо, чи є вже рецепти в базі
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
    """
    Розумний пошук рецептів:
    - Ігнорує решітки '#'
    - Шукає за коренем слова (знаходить "піца", "піци", "піцою")
    """
    if not query:
        return []

    # Прибираємо решітку, пробіли та переводимо в нижній регістр
    clean_query = query.replace("#", "").strip().lower()

    if not clean_query:
        return []

    # Обрізаємо закінчення для слів довжиною від 4 літер
    if len(clean_query) >= 4:
        search_term = clean_query[:-1]
    else:
        search_term = clean_query

    conn = get_connection()
    cursor = conn.cursor()

    # Пошук у назві та описі без урахування решітки '#'
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

def add_recipe(title: str, description: str):
    """Додавання нового рецепта."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO recipes (title, description) VALUES (?, ?)",
        (title, description)
    )

    conn.commit()
    conn.close()

def get_all_recipes():
    """Отримання всіх рецептів з бази."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM recipes")
    results = cursor.fetchall()

    conn.close()
    return results
