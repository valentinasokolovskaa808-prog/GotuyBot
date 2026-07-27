import sqlite3

DATABASE_NAME = "recipes.db"

def get_connection():
    return sqlite3.connect(DATABASE_NAME)

def init_db():
    """Створює таблицю рецептів, якщо її ще немає."""
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
    
    conn.commit()
    conn.close()

def add_recipe(title, ingredients, instructions, video_url, is_breakfast=0, is_lunch=0, is_dinner=0, is_baking=0, is_desserts=0):
    """Додає новий рецепт у базу даних."""
    conn = get_connection()
    cursor = conn.cursor()
    
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
    """Шукає рецепти за допомогою Python (100% працює з кирилицею та українськими літерами)."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT title, ingredients, instructions, video_url FROM recipes")
    all_recipes = cursor.fetchall()
    conn.close()
    
    search_query = query.strip().lower()
    matched_recipes = []
    
    for recipe in all_recipes:
        title = recipe[0] or ""
        ingredients = recipe[1] or ""
        
        # Перевіряємо входження слова у назву або інгредієнти
        if search_query in title.lower() or search_query in ingredients.lower():
            matched_recipes.append(recipe)
            
    return matched_recipes
