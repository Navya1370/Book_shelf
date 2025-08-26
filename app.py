from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Change this
app.permanent_session_lifetime = timedelta(minutes=30)

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",       # default XAMPP user
    password="",       # default XAMPP password is empty
    database="bookshelf"
)

cursor = db.cursor(dictionary=True)

@app.route('/')
def home():
    if 'username' in session:
        cursor.execute("SELECT * FROM books")
        books = cursor.fetchall()
        print("Books fetched:", books)  # Debugging
        return render_template("home.html", username=session['username'], books=books)
    else:
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            hashed_password = generate_password_hash(password)
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            db.commit()
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            return f"Error: {err}"

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session.permanent = True
            session['username'] = username
            return redirect(url_for("home"))
        else:
            return "Invalid credentials"

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
