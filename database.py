import sqlite3

def init_db():
    """Створює таблицю рецептів та наповнює її посиланнями на відеорецепти"""
    conn = sqlite3.connect("recipes.db")
    cursor = conn.cursor()
    
    # Видаляємо стару таблицю, щоб оновити дані при запуску
    cursor.execute('DROP TABLE IF EXISTS recipes')
    
    cursor.execute('''
        CREATE TABLE recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            video_url TEXT
        )
    ''')
    
    # Список рецептів із посиланнями на ваші відеорецепти
    # Формат: ("Назва", "Короткі інгредієнти", "Опис або примітка", "Посилання на відео")
    sample_recipes = [
        ("Борщ український", "М'ясо, картопля, капуста, буряк, зажарка", "Класичний справжній український борщ.", "https://facebook.com"),
        ("Омлет класичний", "Яйця, молоко, сіль, масло", "Ніжний та пишний сніданок за 5 хвилин.", "https://instagram.com"),
        ("Салат Цезар", "Куряче філе, салат, сухарики, пармезан, соус", "Смачний ресторанний салат удома.", "https://facebook.com"),
        ("Котлети з курячого філе", "Куряче філе, цибуля, яйце, спеції", "Соковиті рублені курячі котлетки.", "https://facebook.com"),
        ("Соковиті чебуреки", "Тісто, м'ясний фарш, цибуля, спеції", "Хрусткі чебуреки з м'ясною начинкою.", "https://facebook.com"),
        ("Хрусткі деруни", "Картопля, цибуля, яйце, борошно", "Золотисті картопляні деруни зі сметаною.", "https://facebook.com"),
        ("Сирна запіканка", "Кисломолочний сир, яйця, манка, цукор", "Ніжна запіканка як у дитинстві.", "https://facebook.com"),
        ("Запечений кабачок із сиром сулугуні", "Кабачок, сир сулугуні, часник, зелень", "Проста та швидка літня закуска.", "https://facebook.com"),
        ("Соковитий бургер", "Булка, фарш, сир, помідори, соус", "Домашній мега-бургер краще ніж у ресторані.", "https://facebook.com")
    ]
    
    cursor.executemany(
        "INSERT INTO recipes (title, ingredients, instructions, video_url) VALUES (?, ?, ?, ?)", 
        sample_recipes
    )
    
    conn.commit()
    conn.close()

def search_recipes(query: str):
    """Шукає рецепти за ключовим словом у назві або інгредієнтах"""
    conn = sqlite3.connect("recipes.db")
    cursor = conn.cursor()
    
    search_pattern = f"%{query.lower()}%"
    cursor.execute('''
        SELECT title, ingredients, instructions, video_url 
        FROM recipes 
        WHERE LOWER(title) LIKE ? OR LOWER(ingredients) LIKE ?
    ''', (search_pattern, search_pattern))
    
    results = cursor.fetchall()
    conn.close()
    return results
