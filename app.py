from flask import Flask, render_template, request, redirect, session, flash
from flask_session import Session
import redis
from db import get_users, get_orders, get_products, add_user, add_product

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Redis клиент для сессий без decode_responses
session_redis = redis.StrictRedis(host='localhost', port=6379, db=0)
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = session_redis
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'flask_session:'
Session(app)

# Отдельный Redis клиент, если нужен напрямую
raw_redis = redis.StrictRedis(host='localhost', port=6379, db=0)

@app.route("/")
def index():
    return render_template("index.html", logged_in=('username' in session))

@app.route("/users")
def users():
    data = get_users()
    return render_template("users.html", users=data)

@app.route("/orders")
def orders():
    data = get_orders()
    return render_template("orders.html", orders=data)

@app.route('/products')
def products():
    products = get_products()
    return render_template('product.html', products=products)

@app.route("/add_user", methods=["GET", "POST"])
def add_user_route():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        password = request.form["password"]
        # Добавляем пользователя с паролем в открытом виде
        add_user(first_name, last_name, email, password)
        return redirect("/users")
    return render_template("add_user.html")

@app.route("/add_product", methods=["GET", "POST"])
def add_product_route():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        price = request.form["price"]
        stock_quantity = request.form["stock_quantity"]
        add_product(name, description, price, stock_quantity)
        return redirect("/products")
    return render_template("add_product.html")

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    # Получаем пользователей из базы
    users = get_users()

    # Проверяем, есть ли такой пользователь
    if any(user[1] == username for user in users):  # user[1] это username
        flash("Пользователь уже существует")
        return redirect('/')

    # Добавляем нового пользователя в базу с паролем в открытом виде
    add_user(username, password)
    session['username'] = username
    return redirect("/")

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Получаем пользователей из базы
    users = get_users()

    user = next((user for user in users if user[1] == username), None)  # user[1] это username

    if user and user[2] == password:  # user[2] это пароль в открытом виде
        session['username'] = username
        return redirect("/")  # Перенаправляем на главную страницу

    flash("Неверный логин или пароль")
    return redirect("/")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)
@app.route("/users")
def users():
    # Увеличиваем счётчик посещений страницы пользователей
    visit_count_users = raw_redis.incr("visit_count_users")
    data = get_users()
    return render_template("users.html", users=data, visit_count_users=visit_count_users)


@app.route('/products')
def products():
    # Увеличиваем счётчик посещений страницы продуктов
    visit_count_products = raw_redis.incr("visit_count_products")
    products = get_products()
    return render_template('product.html', products=products, visit_count_products=visit_count_products)