from flask import Flask, render_template, request, redirect, session, flash
from flask_session import Session
import redis
from db import (
    get_users, get_orders, get_products,
    add_user, add_product,
    get_registered_users, add_registered_user,
    update_user,  # функция обновления пользователя
    r  # redis клиент
)
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Настройка Redis для сессий
session_redis = redis.StrictRedis(host='localhost', port=6379, db=1)
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = session_redis
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'flask_session:'
Session(app)

# Прямой клиент Redis для кэширования данных
raw_redis = r

@app.route("/")
def index():
    return render_template("index.html", logged_in=('username' in session))

@app.route("/users")
def users():
    visit_count_users = raw_redis.incr("visit_count_users")
    search_query = request.args.get('search')

    all_users = get_users()

    if search_query:
        filtered_users = [
            user for user in all_users
            if search_query.lower() in user['first_name'].lower() or search_query.lower() in user['last_name'].lower()
        ]
    else:
        filtered_users = all_users

    no_users_found = (len(filtered_users) == 0)

    return render_template(
        "users.html",
        users=filtered_users,
        visit_count_users=visit_count_users,
        search_query=search_query,
        no_users_found=no_users_found
    )

@app.route("/clear_users_cache")
def clear_users_cache():
    raw_redis.delete("users")
    flash("Кэш пользователей очищен!")
    return redirect("/users")

@app.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    all_users = get_users()
    user = next((u for u in all_users if u['user_id'] == user_id), None)

    if not user:
        flash("Пользователь не найден")
        return redirect("/users")

    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]

        update_user(user_id, first_name, last_name, email)
        raw_redis.delete("users")  # очищаем кэш
        flash("Пользователь успешно обновлён!")
        return redirect("/users")

    return render_template("edit_user.html", user=user)

@app.route("/orders")
def orders():
    data = get_orders()
    return render_template("orders.html", orders=data)

@app.route("/products")
def products():
    visit_count_products = raw_redis.incr("visit_count_products")
    search_query = request.args.get('search')

    all_products = get_products()

    if search_query:
        filtered_products = [p for p in all_products if search_query.lower() in p[1].lower()]
    else:
        filtered_products = all_products

    return render_template(
        "product.html",
        products=filtered_products,
        visit_count_products=visit_count_products,
        search_query=search_query
    )

@app.route("/add_user", methods=["GET", "POST"])
def add_user_route():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        phone_number = request.form.get("phone_number")
        password = request.form["password"]

        if not phone_number:
            phone_number = None

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        add_user(first_name, last_name, email, phone_number, password_hash)

        raw_redis.delete("users")  # чистим кэш
        flash("Пользователь успешно добавлен!")
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
        flash("Товар успешно добавлен!")
        return redirect("/products")

    return render_template("add_product.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = get_registered_users()
        if any(user[0] == username for user in users):
            flash("Пользователь уже существует!")
            return redirect("/register")

        add_registered_user(username, password)
        session["username"] = username
        flash("Регистрация прошла успешно!")
        return redirect("/")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = get_registered_users()
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        user = next((u for u in users if u[0] == username and u[1] == password_hash), None)

        if user:
            session["username"] = username
            flash("Успешный вход!")
            return redirect("/")
        else:
            flash("Неверный логин или пароль!")
            return redirect("/login")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Вы вышли из системы!")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
