from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ---------------- DATABASE SETUP ----------------

def init_db():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS salary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            month TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# ---------------- LOGIN ----------------

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/start', methods=['POST'])
def start():
    session['name'] = request.form['name']
    session['job'] = request.form['job']
    return redirect('/')

# ---------------- HOME PAGE ----------------

@app.route('/')
def index():

    if 'name' not in session:
        return redirect('/login')

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    # All expenses
    cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
    expenses = cursor.fetchall()

    # Category totals
    cursor.execute("""
        SELECT category, SUM(amount)
        FROM expenses
        GROUP BY category
    """)
    totals = cursor.fetchall()

    # Current month
    current_month = datetime.now().strftime("%Y-%m")

    # Monthly expense
    cursor.execute("""
        SELECT SUM(amount)
        FROM expenses
        WHERE strftime('%Y-%m', date) = ?
    """, (current_month,))

    monthly_expense = cursor.fetchone()[0] or 0

    # Salary
    cursor.execute("""
        SELECT amount
        FROM salary
        WHERE month = ?
    """, (current_month,))

    result = cursor.fetchone()
    monthly_salary = result[0] if result else 0

    # Balance
    balance = monthly_salary - monthly_expense

    conn.close()

    return render_template(
        'index.html',
        expenses=expenses,
        totals=totals,
        monthly_salary=monthly_salary,
        monthly_expense=monthly_expense,
        balance=balance
    )

# ---------------- ADD EXPENSE ----------------

@app.route('/add', methods=['POST'])
def add():

    amount = request.form['amount']
    category = request.form['category']
    date = request.form['date']

    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO expenses (amount, category, date) VALUES (?, ?, ?)",
        (amount, category, date)
    )

    conn.commit()
    conn.close()

    return redirect('/')

# ---------------- SET SALARY ----------------

@app.route('/set-salary', methods=['POST'])
def set_salary():

    salary = request.form['salary']
    current_month = datetime.now().strftime("%Y-%m")

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM salary WHERE month = ?",
        (current_month,)
    )

    cursor.execute(
        "INSERT INTO salary (amount, month) VALUES (?, ?)",
        (salary, current_month)
    )

    conn.commit()
    conn.close()

    return redirect('/')

# ---------------- CLEAR SALARY ----------------

@app.route('/clear-salary', methods=['POST'])
def clear_salary():

    current_month = datetime.now().strftime("%Y-%m")

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM salary WHERE month = ?",
        (current_month,)
    )

    conn.commit()
    conn.close()

    return redirect('/')

# ---------------- CLEAR ALL EXPENSES ----------------

@app.route('/clear', methods=['POST'])
def clear():

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM expenses")

    conn.commit()
    conn.close()

    return redirect('/')

# ---------------- LOGOUT ----------------

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect('/login')

# ---------------- RUN APP ----------------

if __name__ == '__main__':
    app.run(debug=True)
