import sqlite3

DATABASE_NAME = "recipes.db"

def get_connection():
    return sqlite3.connect(DATABASE_NAME)

def init_db():
    """Створює таблицю рецептів та безпечно додає початкові рецепти, не видаляючи нові."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
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
    
    sample_recipes = [
        # --- Нові рецепти (2009 - 2029) ---
        ("Бананові панкейки (млинці)", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2029", 1, 0, 0, 1, 1),
        ("Булочки з вареним згущеним молоком", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2028", 0, 0, 0, 1, 1),
        ("Салат із баклажанів з волоськими горіхами та сметаною", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2026", 0, 1, 1, 0, 0),
        ("Салат із простих інгредієнтів", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2025", 0, 1, 1, 0, 0),
        ("Вершкова паста з куркою та грибами", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2024", 0, 1, 1, 0, 0),
        ("Печеня з курки", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2023", 0, 1, 1, 0, 0),
        ("Морозиво за 5 хвилин", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2022", 0, 0, 0, 0, 1),
        ("Хрустка картопля фрі в аерогрилі", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2021", 0, 1, 1, 0, 0),
        ("Тушкована свинина з картоплею та горошком", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2020", 0, 1, 1, 0, 0),
        ("Сніданок з тунцем", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2019", 1, 0, 0, 0, 0),
        ("ГРЕЦЬКА МУСАКА — НЕЙМОВІРНА СМАКОТА З БАКЛАЖАНАМИ", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2018", 0, 1, 1, 0, 0),
        ("Желе \"Схід сонця\"", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2017", 0, 0, 0, 0, 1),
        ("Миттєва піца на лаваші", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2016", 1, 1, 1, 1, 0),
        ("Хрумкі малосольні кабачки з м’ятою", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2015", 0, 1, 1, 0, 0),
        ("Налисники по Одесі", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2014", 1, 0, 0, 1, 1),
        ("ПИРІГ З ВИШНЕЮ", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2012", 0, 0, 0, 1, 1),
        ("Часниковий хліб із сиром", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2011", 1, 1, 0, 1, 0),
        ("Картопля по-домашньому", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2010", 0, 1, 1, 0, 0),
        ("Швидка намазка з тунця", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2009", 1, 1, 0, 0, 0),

        # --- Попередній список рецептів ---
        ("Соковиті січені рибні котлети", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2007", 0, 1, 1, 0, 0),
        ("Трубочки із сиром", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2006", 1, 0, 0, 1, 0),
        ("Вергуни", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2005", 0, 0, 0, 1, 1),
        ("Пікантні мариновані помідори", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2004", 0, 1, 1, 0, 0),
        ("Швидкі коржі", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2003", 1, 0, 0, 1, 0),
        ("Хрусткий мигдаль у меді та кунжуті", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2002", 0, 0, 0, 0, 1),
        ("Індичка з овочами в горщиках", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2001", 0, 1, 1, 0, 0),
        ("Салат із крабовими паличками, сиром та помідорами", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/2000", 0, 1, 1, 0, 0),
        ("Маковий лимонний торт", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1999", 0, 0, 0, 1, 1),
        ("Дуууууже смачні курячі котлети", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1998", 0, 1, 1, 0, 0),
        ("Салат «Буніто»", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1997", 0, 1, 1, 0, 0),
        ("Кекси з бананом та яблуком", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1996", 1, 0, 0, 1, 1),
        ("Картопляні кульки з сиром", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1995", 0, 1, 1, 0, 0),
        ("Дієтична куряча ковбаса з грибами", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1994", 0, 1, 1, 0, 0),
        ("Ситний сніданок або перекус", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1993", 1, 0, 0, 0, 0),
        ("Запечені овочі з картоплею та мʼясом", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1992", 0, 1, 1, 0, 0),
        ("Домашня пахлава", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1991", 0, 0, 0, 1, 1),
        ("Домашній сир", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1990", 1, 0, 0, 0, 0),
        ("Трендовий закритий бургер", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1989", 0, 1, 1, 0, 0),
        ("Пиріжки з картоплею та сосискою", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1988", 1, 1, 0, 1, 0),
        ("Повітряний бісквіт до чаю", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1987", 0, 0, 0, 1, 1),
        ("Салат із консервованим горошком", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1986", 0, 1, 1, 0, 0),
        ("Млинці в «горошок»", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1985", 1, 0, 0, 1, 1),
        ("Оселедцевий паштет", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1984", 1, 1, 0, 0, 0),
        ("Соковите м'ясо по-французьки", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1983", 0, 1, 1, 0, 0),
        ("Хліб Фокачча", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1982", 0, 0, 0, 1, 0),
        ("Рулет з варенням", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1981", 0, 0, 0, 1, 1),
        ("Густий капусняк з ребрами", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1980", 0, 1, 1, 0, 0),
        ("Вівсяний домашній кекс", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1979", 1, 0, 0, 1, 1),
        ("Найсмачніший банановий млинець на сніданок", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1978", 1, 0, 0, 0, 1),
        ("Смачна ідея для бургерів", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1977", 0, 1, 1, 0, 0),
        ("Найпростіший Квас", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1976", 0, 0, 0, 0, 1),
        ("Кекси до чаю", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1975", 0, 0, 0, 1, 1),
        ("Курка з овочами в соусі", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1974", 0, 1, 1, 0, 0),
        ("Пиріг із плавленими сирками та цибулею", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1973", 0, 1, 1, 1, 0),
        ("Човники з листкового тіста", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1972", 1, 1, 1, 1, 0),
        ("Закусковий перчик", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1971", 0, 1, 1, 0, 0),
        ("М'ясний пиріг із картоплею", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1970", 0, 1, 1, 1, 0),
        ("Салат із тунцем", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1969", 0, 1, 1, 0, 0),
        ("Сальтисон. Дуже смачний рецепт", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1968", 0, 1, 1, 0, 0),
        ("Святковий салат", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1966", 0, 1, 1, 0, 0),
        ("Торт «Пеньок»", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1965", 0, 0, 0, 1, 1),
        ("Запечена курка з овочами та сиром", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1964", 0, 1, 1, 0, 0),
        ("Закуска з перців", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1963", 0, 1, 1, 0, 0),
        ("Неззвичайні деруни", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1962", 1, 1, 1, 0, 0),
        ("Оладки", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1961", 1, 0, 0, 1, 0),
        ("Найпростіше печиво «Хвилинка»", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1960", 0, 0, 0, 1, 1),
        ("Домашня буженина з курячого філе", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1959", 0, 1, 1, 0, 0),
        ("Пiцa з кабачка", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1958", 1, 1, 1, 0, 0),
        ("Салат з копченим сиром", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1957", 0, 1, 1, 0, 0),
        ("Свинина під шубою", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1956", 0, 1, 1, 0, 0),
        ("Медове печиво", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1955", 0, 0, 0, 1, 1),
        ("Сніданок у стилі мексиканської кесадільї", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1954", 1, 0, 0, 0, 0),
        ("Салат з курячою печінкою та корейською морквою", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1953", 0, 1, 1, 0, 0),
        ("Шоколадний торт або торт «три склянки»", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1952", 0, 0, 0, 1, 1),
        ("Фінський млинець", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1951", 1, 0, 0, 1, 0),
        ("Оселедець «Закусковий»", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1950", 0, 1, 1, 0, 0),
        ("Смачний, ніжний курячий шніцель", "Рецепт та деталі у відео", "Дивіться відеорецепт у каналі", "https://t.me/gotuy_prosti_recepty/1949", 0, 1, 1, 0, 0)
    ]

    # Перевіряємо та додаємо лише ті рецепти, яких ще немає у базі за назвою
    for r in sample_recipes:
        cursor.execute("SELECT COUNT(*) FROM recipes WHERE title = ?", (r[0],))
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO recipes (title, ingredients, instructions, video_url, is_breakfast, is_lunch, is_dinner, is_baking, is_desserts)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', r)
    
    conn.commit()
    conn.close()

def add_recipe(title, ingredients, instructions, video_url, category="baking"):
    """Додає новий рецепт у базу даних із визначеною категорією."""
    conn = get_connection()
    cursor = conn.cursor()
    
    is_breakfast = 1 if category == "breakfast" else 0
    is_lunch = 1 if category == "lunch" else 0
    is_dinner = 1 if category == "dinner" else 0
    is_baking = 1 if category == "baking" else 0
    is_desserts = 1 if category == "desserts" else 0

    cursor.execute('''
        INSERT INTO recipes (title, ingredients, instructions, video_url, is_breakfast, is_lunch, is_dinner, is_baking, is_desserts)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title.strip(), ingredients.strip(), instructions.strip(), video_url.strip(), is_breakfast, is_lunch, is_dinner, is_baking, is_desserts))
    
    conn.commit()
    conn.close()

def get_breakfast_recipes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, ingredients, instructions, video_url FROM recipes WHERE is_breakfast = 1")
    recipes = cursor.fetchall()
    conn.close()
    return recipes

def get_lunch_recipes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, ingredients, instructions, video_url FROM recipes WHERE is_lunch = 1")
    recipes = cursor.fetchall()
    conn.close()
    return recipes

def get_dinner_recipes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, ingredients, instructions, video_url FROM recipes WHERE is_dinner = 1")
    recipes = cursor.fetchall()
    conn.close()
    return recipes

def get_baking_recipes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, ingredients, instructions, video_url FROM recipes WHERE is_baking = 1")
    recipes = cursor.fetchall()
    conn.close()
    return recipes

def get_dessert_recipes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, ingredients, instructions, video_url FROM recipes WHERE is_desserts = 1")
    recipes = cursor.fetchall()
    conn.close()
    return recipes

def get_video_recipes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, ingredients, instructions, video_url FROM recipes WHERE video_url IS NOT NULL AND video_url != ''")
    recipes = cursor.fetchall()
    conn.close()
    return recipes

def search_recipes(query):
    """Шукає рецепти з врахуванням хештегів та слів."""
    if not query:
        return []

    clean_query = query.replace("#", "").strip().lower()

    if not clean_query:
        return []

    if len(clean_query) > 5:
        search_term = clean_query[:-2]
    elif len(clean_query) == 5:
        search_term = clean_query[:-1]
    else:
        search_term = clean_query

    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT title, ingredients, instructions, video_url FROM recipes")
    all_recipes = cursor.fetchall()
    conn.close()
    
    matched_recipes = []
    for recipe in all_recipes:
        title = (recipe[0] or "").lower()
        ingredients = (recipe[1] or "").lower()
        
        if search_term in title or search_term in ingredients:
            matched_recipes.append(recipe)
            
    return matched_recipes
