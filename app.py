from flask import Flask, render_template
from db import get_users, get_orders, get_products  # Убедись, что добавил get_products в db.py

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
    products = get_products()  # Получаем данные о продуктах из базы данных
    return render_template('product.html', products=products)

if __name__ == '__main__':
    app.run(debug=True)
