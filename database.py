import sqlite3


def get_connection():
    """Створення підключення до бази даних."""
    return sqlite3.connect("recipes.db")


def search_recipes(query: str):
    """
    Пошук рецептів за назвою та описом.
    Очищає запит від символу '#', пробілів і враховує відмінки.
    """
    if not query:
        return []

    # 1. Очищаємо запит від решітки та зайвих пробілів
    clean_query = query.replace("#", "").strip().lower()

    if not clean_query:
        return []

    # 2. Обрізаємо закінчення для слів довжиною від 4 символів,
    # щоб шукати за коренем (наприклад, "піца" -> "піц", знайде і "піци", і "піцою")
    if len(clean_query) >= 4:
        search_term = clean_query[:-1]
    else:
        search_term = clean_query

    conn = get_connection()
    cursor = conn.cursor()

    # 3. Шукаємо в назві (title) та описі (description),
    # прибираючи '#' з тексту бази під час порівняння та зводячи до нижнього регістру
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
