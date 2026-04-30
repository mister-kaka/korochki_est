import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user'
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    course_name TEXT NOT NULL,
    start_date TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Новая',
    feedback TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

cursor.execute("SELECT * FROM users WHERE login = 'Admin'")
if not cursor.fetchone():
    cursor.execute('''
    INSERT INTO users (login, password, full_name, phone, email, role)
    VALUES ('Admin', 'KorokNET', 'Администратор', '8(000)000-00-00', 'admin@korochki.ru', 'admin')
    ''')

conn.commit()
conn.close()
print("База данных создана!")