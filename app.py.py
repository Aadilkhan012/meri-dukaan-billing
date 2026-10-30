from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('billing.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS items 
                 (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sales 
                 (id INTEGER PRIMARY KEY, item_name TEXT, qty INTEGER, total REAL, date TEXT)''')
    c.execute("SELECT COUNT(*) FROM items")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO items VALUES (1,'Samosa',15,100)")
        c.execute("INSERT INTO items VALUES (2,'Chai',10,200)")
        c.execute("INSERT INTO items VALUES (3,'Cold Drink',20,50)")
    conn.commit()
    conn.close()

@app.route('/')
def home():
    conn = sqlite3.connect('billing.db')
    c = conn.cursor()
    c.execute("SELECT * FROM items")
    items = c.fetchall()
    c.execute("SELECT SUM(total) FROM sales WHERE date=date('now')")
    today_sale = c.fetchone()[0] or 0
    conn.close()
    return render_template('index.html', items=items, today_sale=today_sale)

@app.route('/bill', methods=['POST'])
def make_bill():
    item_id = request.form['item_id']
    qty = int(request.form['qty'])
    
    conn = sqlite3.connect('billing.db')
    c = conn.cursor()
    c.execute("SELECT name, price, stock FROM items WHERE id=?", (item_id,))
    name, price, stock = c.fetchone()
    
    if stock >= qty:
        total = price * qty
        c.execute("UPDATE items SET stock=stock-? WHERE id=?", (qty, item_id))
        c.execute("INSERT INTO sales (item_name, qty, total, date) VALUES (?,?,?,date('now'))", (name, qty, total))
        conn.commit()
        conn.close()
        return render_template('bill.html', name=name, qty=qty, price=price, total=total)
    else:
        conn.close()
        return "Stock khatam hai bhai!"

if __name__ == '__main__':
    init_db()
    app.run(debug=True)