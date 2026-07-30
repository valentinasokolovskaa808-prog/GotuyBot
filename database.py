import sqlite3

# Початковий список рецептів для першої ініціалізації бази
INITIAL_RECIPES = [
    ("Борщ український", "Класичний червоний борщ з яловичиною та квасолею. #борщ #перші_страви"),
    ("Піца з ковбасою", "Домашня піца на тонкому тісті з сиром моцарела та соусом. #піца #випічка"),
    ("Салат Цезар", "Легкий салат з куркою, сухариками та соусом цезар. #салат #курка"),
    ("Вареники з картоплею", "Традиційні українські вареники з цибулевою зажаркою. #вареники #другі_страви"),
    ("Сирники", "Ніжні сирники із домашнього сиру до сніданку. #сніданок #сирники"),
]

def get_connection():
    """Підключення до бази даних."""
    return sqlite3.connect("recipes.db")

def init_db():
    """
    Ініціалізація бази даних. Створює таблицю, якщо її немає,
    та наповнює базовими рецептами при першому запуску.
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

    # Перевіряємо, чи база порожня
    cursor.execute("SELECT COUNT(*) FROM recipes")
    count = cursor.fetchone()[0]

    # Наповнюємо лише якщо база нова
    if count == 0:
        cursor.executemany(
            "INSERT INTO recipes (title, description) VALUES (?, ?)",
            INITIAL_RECIPES
        )

    conn.commit()
    conn.close()

def search_recipes(query: str):
    """
    Розумний пошук рецептів за назвою та описом.
    - Ігнорує решітки '#' у запиті та в базі.
    - Враховує відмінки (шукає за коренем слова).
    """
    if not query:
        return []

    # 1. Прибираємо решітку, зайві пробіли та зводимо до нижнього регістру
    clean_query = query.replace("#", "").strip().lower()

    if not clean_query:
        return []

    # 2. Відрізаємо остання літеру для слів від 4 символів (наприклад, "піца" -> "піц"),
    # щоб шукати і "піца", і "піци", і "піцою"
    if len(clean_query) >= 4:
        search_term = clean_query[:-1]
    else:
        search_term = clean_query

    conn = get_connection()
    cursor = conn.cursor()

    # 3. Пошук у назві та описі з очищенням текстів від '#'
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
    """Додавання нового рецепта в базу."""
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
