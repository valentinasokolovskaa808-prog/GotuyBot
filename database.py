import sqlite3

DATABASE_NAME = "recipes.db"

def get_connection():
    return sqlite3.connect(DATABASE_NAME)

def init_db():
    """Створює таблицю рецептів, якщо її ще немає (без видалення існуючих даних)."""
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
    ''', (title, ingredients, instructions, video_url, is_breakfast, is_lunch, is_dinner, is_baking, is_desserts))
    
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
    """Шукає рецепти за назвою або інгредієнтами незалежно від регістру літер."""
    conn = get_connection()
    cursor = conn.cursor()
    search_query = f"%{query.strip().lower()}%"
    
    cursor.execute('''
        SELECT title, ingredients, instructions, video_url 
        FROM recipes 
        WHERE LOWER(title) LIKE ? OR LOWER(ingredients) LIKE ?
    ''', (search_query, search_query))
    
    recipes = cursor.fetchall()
    conn.close()
    return recipes
