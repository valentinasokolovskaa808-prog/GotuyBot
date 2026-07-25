import sqlite3

def init_db():
    """Створює таблицю рецептів та наповнює її посиланнями на Telegram-канал"""
    conn = sqlite3.connect("recipes.db")
    cursor = conn.cursor()
    
    # Видаляємо стару таблицю, щоб повністю оновити базу даних
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
    
    sample_recipes = [
        ("Салат із крабовими паличками, сиром та помідорами", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2000"),
        ("Маковий лимонний торт", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1999"),
        ("Дуууууже смачні курячі котлети", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1998"),
        ("Салат «Буніто»", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1997"),
        ("Кекси з бананом та яблуком", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1996"),
        ("Картопляні кульки з сиром", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1995"),
        ("Дієтична куряча ковбаса з грибами", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1994"),
        ("Запечені овочі з картоплею та мʼясом", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1992"),
        ("Домашня пахлава", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1991"),
        ("Домашній сулугуні", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1990"),
        ("Повітряний бісквіт до чаю", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1987"),
        ("Салат із консервованим горошком", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1986"),
        ("Млинці в «горошок»", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1985"),
        ("Оселедцевий паштет", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1984"),
        ("Соковите м'ясо по-французьки", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1983"),
        ("Хліб Фокачча", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1982"),
        ("Рулет з варенням", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1981"),
        ("Густий капусняк з ребрами", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1980"),
        ("Вівсяний домашній кекс", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1979"),
        ("Найсмачніший банановий млинець на сніданок", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1978"),
        ("Найпростіший Квас", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1976"),
        ("Кекси до чаю", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1975"),
        ("Курка з овочами в соусі", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1974"),
        ("Пиріг із плавленими сирками та цибулею", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1973"),
        ("Човники з листкового тіста", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1972"),
        ("М'ясний пиріг із картоплею", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1970"),
        ("Салат із тунцем", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1969"),
        ("Сальтисон. Дуже смачний рецепт", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1968"),
        ("Святковий салат", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1966"),
        ("Торт «Пеньок»", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1965"),
        ("Запечена курка з овочами та сиром", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1964"),
        ("Закуска з перців", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1963"),
        ("Деруни", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1962"),
        ("Оладки", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1961"),
        ("Печиво «Хвилинка»", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1960"),
        ("Домашня буженина з курячого філе", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1959"),
        ("Піца з кабачка", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1958"),
        ("Салат з копченим сиром", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1957"),
        ("Свинина під шубою", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1956")
    ]
    
    cursor.executemany(
        "INSERT INTO recipes (title, ingredients, instructions, video_url) VALUES (?, ?, ?, ?)", 
        sample_recipes
    )
    
    conn.commit()
    conn.close()

def search_recipes(query: str):
    """Гнучкий точний пошук без обмежень кирилиці в SQLite"""
    conn = sqlite3.connect("recipes.db")
    cursor = conn.cursor()
    
    cursor.execute('SELECT title, ingredients, instructions, video_url FROM recipes')
    all_recipes = cursor.fetchall()
    conn.close()
    
    query_clean = query.strip().lower()
    results = []
    
    for title, ingredients, instructions, video_url in all_recipes:
        if query_clean in title.lower() or query_clean in ingredients.lower():
            results.append((title, ingredients, instructions, video_url))
            
    return results
