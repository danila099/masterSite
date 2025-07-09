from tomllib import TOMLDecodeError
from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

def init_db():
    with sqlite3.connect('users.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS masters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                bio TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                master_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                image_url TEXT,
                price TEXT,
                FOREIGN KEY (master_id) REFERENCES masters (id) ON DELETE CASCADE
            )
        ''')
        
        # Добавляем начальных мастеров, если таблица пуста
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM masters')
        if cur.fetchone()[0] == 0:
            # Добавляем начальных мастеров
            initial_masters = [
                ('Вадик', 'Мастер по компьютерам с опытом более 5 лет.'),
                ('Данила', 'Компьютерный мастер, специализация — обслуживание и апгрейд.')
            ]
            cur.executemany('INSERT INTO masters (name, bio) VALUES (?, ?)', initial_masters)
            conn.commit()
            
            # Добавляем начальные услуги
            initial_services = [
                (1, 'Переустановка ОС', 'Быстрая и качественная переустановка Windows с активацией. Стоимость: 1000 рублей.', 'https://avatars.mds.yandex.net/i?id=ba857f95c9df1640149912ffea97d0bf_l-5236381-images-thumbs&n=13', '1000 рублей'),
                (1, 'Подключение и настройка драйверов', 'Установка и обновление драйверов для всех устройств. Стоимость: 500 рублей.', 'https://avatars.mds.yandex.net/i?id=303c22b68e4481228ca04c5f907fb9047310a7ad-10753427-images-thumbs&n=13', '500 рублей'),
                (1, 'Сборка компьютера', 'Профессиональная сборка и тестирование ПК под ваши задачи. Стоимость: от 1000 рублей.', 'https://avatars.mds.yandex.net/i?id=4d93010131159e8caa75ae1994ab970aa2f42b27-4576399-images-thumbs&n=13', 'от 1000 рублей'),
                (2, 'Чистка и обслуживание ПК', 'Профилактическая чистка от пыли, замена термопасты. Стоимость: 600 рублей.', 'https://sun9-55.userapi.com/impf/NahC2NYkmfXA10zWh-g6ApbBIdaqZCdiPvFZ5g/XrUnk7v6b-0.jpg?size=1920x768&quality=95&crop=0,51,1120,447&sign=b45e612243bbc16fe62f80f7729302cb&type=cover_group', '600 рублей'),
                (2, 'Апгрейд комплектующих', 'Установка SSD, увеличение оперативной памяти, замена видеокарты. Стоимость: от 1000 рублей.', 'https://pixel-l.ru/uploads/category/48/menu_pk.png', 'от 1000 рублей'),
                (2, 'Настройка интернета и Wi-Fi', 'Подключение и настройка домашней сети, устранение проблем с интернетом. Стоимость: 800 рублей.', 'https://avatars.dzeninfra.ru/get-zen_doc/1886085/pub_5fc5368946df8177e2749185_5fc5373f37dee85d8574cf9f/scale_1200', '800 рублей')
            ]
            cur.executemany('INSERT INTO services (master_id, title, description, image_url, price) VALUES (?, ?, ?, ?, ?)', initial_services)
            conn.commit()

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Замените на сложный ключ в реальном проекте
init_db()

# Функция для проверки администратора
def is_admin(username):
    return username == 'admin'  # Простая проверка - пользователь с именем 'admin' является администратором

# Функции для работы с мастерами в БД
def get_all_masters():
    with sqlite3.connect('users.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT id, name, bio FROM masters ORDER BY id')
        masters = []
        for row in cur.fetchall():
            masters.append({
                'id': row[0],
                'name': row[1],
                'bio': row[2]
            })
        return masters

def get_master_by_id(master_id):
    with sqlite3.connect('users.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT id, name, bio FROM masters WHERE id = ?', (master_id,))
        row = cur.fetchone()
        if row:
            master = {
                'id': row[0],
                'name': row[1],
                'bio': row[2]
            }
            # Добавляем услуги мастера
            master['works'] = get_services_by_master_id(master_id)
            return master
        return None

def add_master(name, bio):
    with sqlite3.connect('users.db') as conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO masters (name, bio) VALUES (?, ?)', (name, bio))
        conn.commit()
        return cur.lastrowid

def delete_master_from_db(master_id):
    with sqlite3.connect('users.db') as conn:
        cur = conn.cursor()
        cur.execute('DELETE FROM masters WHERE id = ?', (master_id,))
        conn.commit()
        return cur.rowcount > 0

def get_services_by_master_id(master_id):
    with sqlite3.connect('users.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT id, title, description, image_url, price FROM services WHERE master_id = ?', (master_id,))
        services = []
        for row in cur.fetchall():
            services.append({
                'id': row[0],
                'title': row[1],
                'desc': row[2],
                'image': row[3],
                'price': row[4]
            })
        return services

def add_service(master_id, title, description, image_url, price):
    with sqlite3.connect('users.db') as conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO services (master_id, title, description, image_url, price) VALUES (?, ?, ?, ?, ?)', 
                   (master_id, title, description, image_url, price))
        conn.commit()
        return cur.lastrowid
 


# --- FLASK ROUTES ---
# Главная страница: список мастеров
@app.route('/')
def index():
    masters = get_all_masters()
    return render_template('index.html', masters=masters, username=session.get('username'))

# Страница о нас
@app.route('/about')
def about():
    return render_template('about.html', username=session.get('username'))

# Страница контактов
@app.route('/contacts')
def contacts():
    return render_template('contacts.html', username=session.get('username'))

# Страница мастера: его услуги
@app.route('/master/<int:master_id>')
def master_page(master_id):
    master = get_master_by_id(master_id)
    if not master:
        return render_template('404.html', username=session.get('username')), 404
    
    return render_template('master.html', master=master, username=session.get('username'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('profile'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('users.db') as conn:
            cur = conn.cursor()
            cur.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
            row = cur.fetchone()
            if not row or not check_password_hash(row[0], password):
                return render_template('login.html', error='Неверный логин или пароль')
        session['username'] = username
        return redirect(url_for('index'))
    return render_template('login.html', username=session.get('username'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            return render_template('register.html', error='Пароли не совпадают', username=session.get('username'))
        if 'username'  in session:
            return redirect(url_for('profile'))
        with sqlite3.connect('users.db') as conn:
            cur = conn.cursor()
            cur.execute('SELECT id FROM users WHERE username = ?', (username,))
            if cur.fetchone():
                return render_template('register.html', error='Пользователь уже существует', username=session.get('username'))
            cur.execute(
                'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            conn.commit()
        return render_template('login.html', message='Регистрация успешна! Войдите.', username=session.get('username'))
    return render_template('register.html', username=session.get('username'))

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html', username=session['username'])

@app.route('/createmaster', methods=['GET', 'POST'])
def createmaster():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        
        # Создаем мастера
        master_id = add_master(name, description)
        
        # Добавляем услуги мастера
        service_titles = request.form.getlist('service_titles[]')
        service_descriptions = request.form.getlist('service_descriptions[]')
        service_images = request.form.getlist('service_images[]')
        service_prices = request.form.getlist('service_prices[]')
        
        for i in range(len(service_titles)):
            if service_titles[i].strip():  # Проверяем, что название не пустое
                add_service(master_id, service_titles[i], service_descriptions[i], service_images[i], service_prices[i])
        
        return redirect(url_for('index'))
    return render_template('createmaster.html', username=session.get('username'))

@app.route('/delete_master/<int:master_id>', methods=['POST'])
def delete_master(master_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if not is_admin(session['username']):
        return redirect(url_for('index'))
    
    # Удаляем мастера из БД
    delete_master_from_db(master_id)
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
