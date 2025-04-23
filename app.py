from flask import Flask, render_template, request, redirect, session, flash
from flask_session import Session
import redis
import hashlib
from db import get_users, get_orders, get_products, add_user, add_product, get_registered_users

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Redis клиент для сессий
session_redis = redis.StrictRedis(host='localhost', port=6379, db=0)
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = session_redis
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'flask_session:'
Session(app)

# Отдельный Redis клиент для кеша
raw_redis = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

@app.route("/")
def index():
    return render_template("index.html", logged_in=('username' in session))

@app.route("/users")
def users():
    visit_count_users = raw_redis.incr("visit_count_users")
    data = get_users()
    return render_template("users.html", users=data, visit_count_users=visit_count_users)

@app.route("/orders")
def orders():
    data = get_orders()
    return render_template("orders.html", orders=data)

@app.route('/products')
def products():
    visit_count_products = raw_redis.incr("visit_count_products")
    products = get_products()
    return render_template('product.html', products=products, visit_count_products=visit_count_products)

@app.route("/add_user", methods=["GET", "POST"])
def add_user_route():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        password = request.form["password"]
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
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    users = get_registered_users()
    if any(user[0] == username for user in users):
        flash("Пользователь уже существует")
        return redirect('/')

    # Добавляем в Reg_users
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Reg_users (username, password_hash)
        VALUES (%s, %s);
    """, (username, password_hash))
    conn.commit()
    cur.close()
    conn.close()

    session['username'] = username
    return redirect("/")

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    users = get_registered_users()
    user = next((user for user in users if user[0] == username), None)

    if user and user[1] == password_hash:
        session['username'] = username
        return redirect("/")

    flash("Неверный логин или пароль")
    return redirect("/")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)
