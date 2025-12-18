import sqlite3
import os

# Проверим, существует ли файл базы данных
db_path = 'test.db'
if os.path.exists(db_path):
    print(f"Файл базы данных {db_path} существует")
    
    # Подключимся к базе данных и проверим роли
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Проверим, есть ли таблица roles
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='roles';")
    tables = cursor.fetchall()
    if tables:
        print("Таблица roles существует")
        
        # Получим все роли
        cursor.execute("SELECT * FROM roles;")
        roles = cursor.fetchall()
        print("Роли в базе данных:")
        for role in roles:
            print(f"  ID: {role[0]}, Name: {role[1]}, Level: {role[2]}")
    else:
        print("Таблица roles не существует")
    
    # Проверим структуру таблицы roles
    try:
        cursor.execute("PRAGMA table_info(roles);")
        columns = cursor.fetchall()
        print("Структура таблицы roles:")
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}, Default: {col[4]}")
    except:
        print("Не удалось получить структуру таблицы roles")
    
    conn.close()
else:
    print(f"Файл базы данных {db_path} не существует")