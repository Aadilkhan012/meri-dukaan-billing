from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('billing.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS items
                 (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sales
                 (id INTEGER PRIMARY KEY, item_name TEXT, qty INTEGER, total REAL)''')
    c.execute("SELECT COUNT(*) FROM items")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO items VALUES (1, 'Samosa', 25, 100)")
        c.execute("INSERT INTO items VALUES (2, 'Chai', 20, 200)")
        c.execute("INSERT INTO items VALUES (3, 'Cold Drink', 30, 50)")
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = sqlite3.connect('billing.db')
    c = conn.cursor()
    c.execute("SELECT * FROM items")
    items = c.fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/sell', methods=['POST'])
def sell():
    item_id = request.form['item_id']
    qty = int(request.form['qty'])
    conn = sqlite3.connect('billing.db')
    c = conn.cursor()
    c.execute("SELECT name, price, stock FROM items WHERE id=?", (item_id,))
    item = c.fetchone()
    if item and item[2] >= qty:
        total = item[1] * qty
        c.execute("INSERT INTO sales (item_name, qty, total) VALUES (?,?,?)", (item[0], qty, total))
        c.execute("UPDATE items SET stock = stock - ? WHERE id=?", (qty, item_id))
        conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
