import sqlite3

def init_db():
    """Створює таблицю рецептів та наповнює її даними з усіма категоріями"""
    conn = sqlite3.connect("recipes.db")
    cursor = conn.cursor()
    
    cursor.execute('DROP TABLE IF EXISTS recipes')
    
    cursor.execute('''
        CREATE TABLE recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            video_url TEXT,
            is_breakfast INTEGER DEFAULT 0,
            is_lunch INTEGER DEFAULT 0,
            is_dinner INTEGER DEFAULT 0,
            is_baking INTEGER DEFAULT 0,
            is_desserts INTEGER DEFAULT 0
        )
    ''')
    
    # Формат: (title, ingredients, instructions, video_url, is_breakfast, is_lunch, is_dinner, is_baking, is_desserts)
    sample_recipes = [
        ("Салат із крабовими паличками, сиром та помідорами", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2000", 0, 1, 1, 0, 0),
        ("Маковий лимонний торт", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1999", 0, 0, 0, 1, 1),
        ("Дуууууже смачні курячі котлети", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1998", 0, 1, 1, 0, 0),
        ("Салат «Буніто»", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1997", 0, 1, 1, 0, 0),
        ("Кекси з бананом та яблуком", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1996", 1, 0, 0, 1, 1),
        ("Картопляні кульки з сиром", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1995", 0, 1, 1, 0, 0),
        ("Дієтична куряча ковбаса з грибами", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1994", 1, 1, 0, 0, 0),
        ("Запечені овочі з картоплею та мʼясом", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1992", 0, 1, 1, 0, 0),
        ("Домашня пахлава", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1991", 0, 0, 0, 1, 1),
        ("Домашній сулугуні", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1990", 1, 0, 0, 0, 0),
        ("Повітряний бісквіт до чаю", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1987", 0, 0, 0, 1, 1),
        ("Салат із консервованим горошком", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1986", 0, 1, 1, 0, 0),
        ("Млинці в «горошок»", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1985", 1, 0, 0, 1, 0),
        ("Оселедцевий паштет", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1984", 1, 0, 0, 0, 0),
        ("Соковите м'ясо по-французьки", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1983", 0, 1, 1, 0, 0),
        ("Хліб Фокачча", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1982", 0, 0, 0, 1, 0),
        ("Рулет з варенням", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1981", 0, 0, 0, 1, 1),
        ("Густий капусняк з ребрами", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1980", 0, 1, 0, 0, 0),
        ("Вівсяний домашній кекс", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1979", 1, 0, 0, 1, 1),
        ("Найсмачніший банановий млинець на сніданок", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1978", 1, 0, 0, 1, 0),
        ("Найпростіший Квас", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1976", 0, 0, 0, 0, 0),
        ("Кекси до чаю", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1975", 1, 0, 0, 1, 1),
        ("Курка з овочами в соусі", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1974", 0, 1, 1, 0, 0),
        ("Пиріг із плавленими сирками та цибулею", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1973", 0, 1, 1, 1, 0),
        ("Човники з листкового тіста", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1972", 0, 1, 1, 1, 0),
        ("М'ясний пиріг із картоплею", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1970", 0, 1, 1, 1, 0),
        ("Салат із тунцем", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1969", 0, 1, 1, 0, 0),
        ("Сальтисон. Дуже смачний рецепт", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1968", 0, 1, 0, 0, 0),
        ("Святковий салат", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1966", 0, 1, 1, 0, 0),
        ("Торт «Пеньок»", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1965", 0, 0, 0, 1, 1),
        ("Запечена курка з овочами та сиром", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1964", 0, 1, 1, 0, 0),
        ("Закуска з перців", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1963", 0, 1, 1, 0, 0),
        ("Деруни", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1962", 1, 1, 0, 0, 0),
        ("Оладки", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1961", 1, 0, 0, 1, 0),
        ("Печиво «Хвилинка»", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1960", 1, 0, 0, 1, 1),
        ("Домашня буженина з курячого філе", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1959", 0, 1, 1, 0, 0),
        ("Піца з кабачка", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1958", 0, 1, 1, 1, 0),
        ("Салат з копченим сиром", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1957", 0, 1, 1, 0, 0),
        ("Свинина під шубою", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1956", 0, 1, 1, 0, 0)
    ]
    
    cursor.executemany(
        "INSERT INTO recipes (title, ingredients, instructions, video_url, is_breakfast, is_lunch, is_dinner, is_baking, is_desserts) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
        sample_recipes
    )
    
    conn.commit()
    conn.close()

def search_recipes(query: str):
    """Шукає рецепти за ключовим словом"""
    conn = sqlite3.connect("recipes.db")
    cursor = conn.cursor()
    cursor.execute('SELECT title, ingredients, instructions, video_url FROM recipes')
    all_recipes = cursor.fetchall()
    conn.close()
    
    query_clean = query.strip().lower().replace("#", "")
    results = []
    
    for title, ingredients, instructions, video_url in all_recipes:
        if query_clean in title.lower() or query_clean in ingredients.lower():
            results.append((title, ingredients, instructions, video_url))
            
    return results

def get_breakfast_recipes():
    conn = sqlite3.connect("recipes.db")
    cursor = conn.cursor()
    cursor.execute('SELECT title, ingredients, instructions, video_url FROM recipes WHERE is_breakfast = 1')
    results = cursor.fetchall()
    conn.close()
    return results

def get_lunch_recipes():
    conn = sqlite3.connect("recipes.db")
    cursor = conn.cursor()
    cursor.execute('SELECT title, ingredients, instructions, video_url FROM recipes WHERE is_lunch = 1')
    results = cursor.fetchall()
    conn.close()
    return results

def get_dinner_recipes():
    conn = sqlite3.connect("recipes.db")
    cursor = conn.cursor()
    cursor.execute('SELECT title, ingredients, instructions, video_url FROM recipes WHERE is_dinner = 1')
    results = cursor.fetchall()
    conn.close()
    return results

def get_baking_recipes():
    """Повертає всі рецепти випічки"""
    conn = sqlite3.connect("recipes.db")
    cursor = conn.cursor()
    cursor.execute('SELECT title, ingredients, instructions, video_url FROM recipes WHERE is_baking = 1')
    results = cursor.fetchall()
    conn.close()
    return results

def get_dessert_recipes():
    """Повертає всі рецепти десертів"""
    conn = sqlite3.connect("recipes.db")
    cursor = conn.cursor()
    cursor.execute('SELECT title, ingredients, instructions, video_url FROM recipes WHERE is_desserts = 1')
    results = cursor.fetchall()
    conn.close()
    return results
