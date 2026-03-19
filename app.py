from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret'

# Create DB
def init_db():
    conn = sqlite3.connect('database.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS orders (username TEXT, food TEXT, price INT)')
    conn.close()

init_db()

# Home → Login
@app.route('/')
def home():
    return render_template('login.html')

# Signup
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        conn = sqlite3.connect('database.db')
        conn.execute("INSERT INTO users VALUES (?,?)",(u,p))
        conn.commit()
        conn.close()

        return redirect('/')
    return render_template('signup.html')

# Login
@app.route('/login', methods=['POST'])
def login():
    u = request.form['username']
    p = request.form['password']

    conn = sqlite3.connect('database.db')
    data = conn.execute("SELECT * FROM users WHERE username=? AND password=?",(u,p)).fetchone()
    conn.close()

    if data:
        session['user'] = u
        return redirect('/menu')
    else:
        return "Invalid Login"

# Menu
@app.route('/menu')
def menu():
    if 'user' not in session:
        return redirect('/')
    return render_template('menu.html')

# Add to cart
@app.route('/add', methods=['POST'])
def add():
    food = request.form['food']
    price = int(request.form['price'])

    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append((food, price))
    session.modified = True

    return redirect('/menu')

# View Cart
@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    total = sum([item[1] for item in cart])
    return render_template('cart.html', cart=cart, total=total)

# Place Order
@app.route('/place')
def place():
    user = session.get('user')
    cart = session.get('cart', [])

    conn = sqlite3.connect('database.db')
    for item in cart:
        conn.execute("INSERT INTO orders VALUES (?,?,?)",(user,item[0],item[1]))
    conn.commit()
    conn.close()

    session['cart'] = []
    return render_template('success.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0,0,0,0',port=10000)