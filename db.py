import sqlite3

def create_news_table():
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sent_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            date DATE
        )
    ''')

    conn.commit()
    conn.close()

def create_sports_table():
    conn = sqlite3.connect('sports.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sent_sports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            date DATE
        )
    ''')

    conn.commit()
    conn.close()

def create_eco_table():
    conn = sqlite3.connect('eco.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sent_eco (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            date DATE
        )
    ''')

    conn.commit()
    conn.close()

def create_politica_table():
    conn = sqlite3.connect('politica.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sent_politica (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            date DATE
        )
    ''')

    conn.commit()
    conn.close()

def create_folha_table():
    conn = sqlite3.connect('folha.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sent_folha (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            date DATE
        )
    ''')

    conn.commit()
    conn.close()

def create_ab_table():
    conn = sqlite3.connect('ab.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sent_ab (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            date DATE
        )
    ''')

    conn.commit()
    conn.close()

create_news_table()
create_sports_table()
create_eco_table()
create_politica_table()
create_folha_table()
create_ab_table()