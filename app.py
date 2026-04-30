from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'supersecretkey123'

# ---- База данных ----

def query(sql, params=(), fetchall=False, fetchone=False, commit=False):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.execute(sql, params)
    if commit:
        conn.commit()
    result = cur.fetchall() if fetchall else cur.fetchone() if fetchone else None
    conn.close()
    return result

# ---- Валидация ----

def validate(data):
    errors = []
    if not re.match(r'^[a-zA-Z0-9]{6,}$', data.get('login', '')):
        errors.append('Логин: только латиница и цифры, минимум 6 символов')
    if len(data.get('password', '')) < 8:
        errors.append('Пароль: минимум 8 символов')
    if not re.match(r'^[а-яА-ЯёЁ\s]+$', data.get('full_name', '')):
        errors.append('ФИО: только кириллица и пробелы')
    if not re.match(r'^8\(\d{3}\)\d{3}-\d{2}-\d{2}$', data.get('phone', '')):
        errors.append('Телефон: формат 8(XXX)XXX-XX-XX')
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', data.get('email', '')):
        errors.append('Email: неверный формат')
    return errors[0] if errors else None

# ---- Маршруты ----

@app.route('/')
def index():
    return redirect(url_for('applications') if 'user_id' in session else url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        error = validate(request.form)
        if not error:
            try:
                query('INSERT INTO users (login, password, full_name, phone, email) VALUES (?, ?, ?, ?, ?)',
                      (request.form['login'], request.form['password'], request.form['full_name'],
                       request.form['phone'], request.form['email']), commit=True)
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                error = 'Пользователь с таким логином уже существует'
    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = query('SELECT * FROM users WHERE login = ? AND password = ?',
                     (request.form['login'], request.form['password']), fetchone=True)
        if user:
            session.update({'user_id': user['id'], 'login': user['login'], 'role': user['role']})
            return redirect(url_for('admin_panel' if user['role'] == 'admin' else 'applications'))
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

    if request.method == 'POST' and 'feedback' in request.form:
        query('UPDATE applications SET feedback = ? WHERE id = ? AND user_id = ?',
              (request.form['feedback'], request.form['app_id'], session['user_id']), commit=True)

    apps = query('SELECT * FROM applications WHERE user_id = ? ORDER BY id DESC',
                 (session['user_id'],), fetchall=True)
    return render_template('applications.html', apps=apps)

@app.route('/create_application', methods=['GET', 'POST'])
def create_application():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        query('INSERT INTO applications (user_id, course_name, start_date, payment_method) VALUES (?, ?, ?, ?)',
              (session['user_id'], request.form['course_name'], request.form['start_date'], request.form['payment_method']), commit=True)
        return redirect(url_for('applications'))
    return render_template('create_application.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        query('UPDATE applications SET status = ? WHERE id = ?',
              (request.form['status'], request.form['app_id']), commit=True)
    apps = query('''SELECT a.*, u.full_name, u.email, u.phone
                    FROM applications a JOIN users u ON a.user_id = u.id
                    ORDER BY a.id DESC''', fetchall=True)
    return render_template('admin.html', apps=apps)

if __name__ == '__main__':
    app.run(debug=True, port=5000)