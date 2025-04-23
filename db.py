import psycopg2
import hashlib
import redis

def get_connection():
    return psycopg2.connect(
        dbname="Taradb",
        user="postgres",
        password="123",
        host="localhost",
        port="5432"
    )

# Redis клиент
r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# Получение зарегистрированных пользователей (для логина)
def get_registered_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT username, password_hash FROM Reg_users;")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users

# Получение пользователей из таблицы Users (отображение)
def get_users():
    cached = r.get("users")
    if cached:
        return eval(cached)  # Желательно заменить на json.loads в будущем

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id, first_name, last_name, email FROM Users;")
    users = cur.fetchall()
    cur.close()
    conn.close()

    r.setex("users", 3600, str(users))
    return users

# Получение заказов
def get_orders():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT o.order_id, u.first_name, u.last_name, o.order_date, o.status
        FROM Orders o
        JOIN Users u ON o.user_id = u.user_id;
    """)
    orders = cur.fetchall()
    cur.close()
    conn.close()
    return orders

# Получение продуктов
def get_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT product_id, name, price, stock_quantity FROM Products;")
    products = cur.fetchall()
    cur.close()
    conn.close()
    return products

# Регистрация пользователя в Reg_users
def add_registered_user(username, password):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Reg_users (username, password_hash)
        VALUES (%s, %s);
    """, (username, password_hash))
    conn.commit()
    cur.close()
    conn.close()

# Добавление в таблицу Users (отдельные данные)
def add_user(first_name, last_name, email, password=""):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Users (first_name, last_name, email)
        VALUES (%s, %s, %s);
    """, (first_name, last_name, email))
    conn.commit()
    cur.close()
    conn.close()

# Добавление продукта
def add_product(name, description, price, stock_quantity):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Products (name, description, price, stock_quantity)
        VALUES (%s, %s, %s, %s);
    """, (name, description, price, stock_quantity))
    conn.commit()
    cur.close()
    conn.close()
