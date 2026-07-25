import sqlite3

def init_db():
    """Створює таблицю рецептів та наповнює її посиланнями на Telegram-канал"""
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
    
    # Список ваших рецептів з реальними посиланнями на Telegram-канал
    sample_recipes = [
        ("Рецепт 2000", "Інгредієнти за посиланням", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2000"),
        ("Рецепт 1997", "Інгредієнти за посиланням", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1997"),
        ("Рецепт 1994", "Інгредієнти за посиланням", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1994"),
        ("Рецепт 1992", "Інгредієнти за посиланням", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1992"),
        ("Рецепт 1991", "Інгредієнти за посиланням", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1991"),
        ("Рецепт 1987", "Інгредієнти за посиланням", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1987"),
        ("Рецепт 1986", "Інгредієнти за посиланням", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1986"),
        ("Рецепт 1984", "Інгредієнти за посиланням", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1984"),
        ("Рецепт 1983", "Інгредієнти за посиланням", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1983"),
        ("Рецепт 1981", "Інгредієнти за посиланням", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1981"),
        ("Рецепт 1980", "Інгредієнти за посиланням", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1980"),
        ("Рецепт 1979", "Інгредієнти за посиланням", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1979"),
        ("Рецепт 1978", "Інгредієнти за посиланням", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1978"),
        ("Рецепт 1976", "Інгредієнти за посиланням", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1976"),
        ("Рецепт 1975", "Інгредієнти за посиланням", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1975"),
        ("Рецепт 1974", "Інгредієнти за посиланням", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1974"),
        ("Рецепт 1973", "Інгредієнти за посиланням", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1973"),
        ("Рецепт 1972", "Інгредієнти за посиланням", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1972"),
        ("Рецепт 1971", "Інгредієнти за посиланням", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1971"),
        ("Рецепт 1970", "Інгредієнти за посиланням", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1970"),
        ("Рецепт 1969", "Інгредієнти за посиланням", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1969"),
        ("Рецепт 1968", "Інгредієнти за посиланням", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1968"),
        ("Рецепт 1966", "Інгредієнти за посиланням", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1966"),
        ("Рецепт 1965", "Інгредієнти за посиланням", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1965")
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
