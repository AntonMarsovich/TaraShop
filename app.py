from flask import Flask, render_template, request, redirect
from db import get_users, get_orders, get_products, add_user, add_product  # импорт нужных функций

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

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

# Роут для добавления пользователя
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

# Роут для добавления продукта
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

if __name__ == '__main__':
    app.run(debug=True)
