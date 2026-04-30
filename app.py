from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'supersecretkey123'

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def validate_login(login):
    return bool(re.match(r'^[a-zA-Z0-9]{6,}$', login))

def validate_password(password):
    return len(password) >= 8

def validate_full_name(name):
    return bool(re.match(r'^[а-яА-ЯёЁ\s]+$', name))

def validate_phone(phone):
    return bool(re.match(r'^8\(\d{3}\)\d{3}-\d{2}-\d{2}$', phone))

def validate_email(email):
    return bool(re.match(r'^[^@]+@[^@]+\.[^@]+$', email))

# ---- Маршруты (страницы) ----

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('applications'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        full_name = request.form['full_name']
        phone = request.form['phone']
        email = request.form['email']

        if not validate_login(login):
            error = 'Логин: только латиница и цифры, минимум 6 символов'
        elif not validate_password(password):
            error = 'Пароль: минимум 8 символов'
        elif not validate_full_name(full_name):
            error = 'ФИО: только кириллица и пробелы'
        elif not validate_phone(phone):
            error = 'Телефон: формат 8(XXX)XXX-XX-XX'
        elif not validate_email(email):
            error = 'Email: неверный формат'
        else:
            try:
                db = get_db()
                db.execute(
                    'INSERT INTO users (login, password, full_name, phone, email) VALUES (?, ?, ?, ?, ?)',
                    (login, password, full_name, phone, email)
                )
                db.commit()
                db.close()
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                error = 'Пользователь с таким логином уже существует'
    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']

        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE login = ? AND password = ?',
            (login, password)
        ).fetchone()
        db.close()

        if user:
            session['user_id'] = user['id']
            session['login'] = user['login']
            session['role'] = user['role']
            if user['role'] == 'admin':
                return redirect(url_for('admin_panel'))
            return redirect(url_for('applications'))
        else:
            error = 'Неверный логин или пароль'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/applications', methods=['GET', 'POST'])
def applications():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()

    if request.method == 'POST' and 'feedback' in request.form:
        app_id = request.form['app_id']
        feedback = request.form['feedback']
        db.execute('UPDATE applications SET feedback = ? WHERE id = ? AND user_id = ?',
                   (feedback, app_id, session['user_id']))
        db.commit()

    apps = db.execute(
        'SELECT * FROM applications WHERE user_id = ? ORDER BY id DESC',
        (session['user_id'],)
    ).fetchall()
    db.close()
    return render_template('applications.html', apps=apps)

@app.route('/create_application', methods=['GET', 'POST'])
def create_application():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        course_name = request.form['course_name']
        start_date = request.form['start_date']
        payment_method = request.form['payment_method']

        db = get_db()
        db.execute(
            'INSERT INTO applications (user_id, course_name, start_date, payment_method) VALUES (?, ?, ?, ?)',
            (session['user_id'], course_name, start_date, payment_method)
        )
        db.commit()
        db.close()
        return redirect(url_for('applications'))

    return render_template('create_application.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    db = get_db()

    if request.method == 'POST':
        app_id = request.form['app_id']
        new_status = request.form['status']
        db.execute('UPDATE applications SET status = ? WHERE id = ?', (new_status, app_id))
        db.commit()

    apps = db.execute('''
        SELECT a.*, u.full_name, u.email, u.phone
        FROM applications a
        JOIN users u ON a.user_id = u.id
        ORDER BY a.id DESC
    ''').fetchall()
    db.close()
    return render_template('admin.html', apps=apps)

if __name__ == '__main__':
    app.run(debug=True, port=5000)