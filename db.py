import sqlite3

def connect_to_database():
    conn = sqlite3.connect('ohhwow.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE,
                        password TEXT
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER,
                        amount INTEGER,
                        description TEXT,
                        category TEXT,
                        date TEXT,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS spending_targets (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER,
                        target_amount INTEGER,
                        time_period TEXT,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                    )''')
    conn.commit()
    
    return conn, cursor

