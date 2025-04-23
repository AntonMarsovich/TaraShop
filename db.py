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

# Функция для получения списка пользователей с кэшированием через Redis
def get_users():
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    cached = r.get("users")
    if cached:
        return eval(cached)

    # Если нет в кэше, запрашиваем из PostgreSQL
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT username, password_hash FROM Reg_users;")  # Теперь из таблицы Reg_users
    users = cur.fetchall()
    cur.close()
    conn.close()

    # Кэшируем пользователей на 1 час
    r.setex("users", 3600, str(users))
    return users

# Функция для получения всех заказов
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

# Функция для получения всех продуктов
def get_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT product_id, name, price, stock_quantity FROM Products;")
    products = cur.fetchall()
    cur.close()
    conn.close()
    return products

# Функция для добавления пользователя (с логином и хешированием пароля)
def add_user(username, password):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Reg_users (username, password_hash)  -- Добавляем в таблицу Reg_users
        VALUES (%s, %s);
    """, (username, password_hash))
    conn.commit()
    cur.close()
    conn.close()

# Функция для добавления товара
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
