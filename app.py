
from flask import Flask, request, redirect, session, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

def connect():
    return sqlite3.connect("accounts.db")

def page(content):
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>lnstagram</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                background: #fafafa;
                font-family: Arial;
                text-align: center;
                margin: 0;
            }
            .box {
                background: white;
                max-width: 330px;
                margin: 65px auto;
                padding: 25px;
                border: 1px solid #ddd;
                border-radius: 12px;
            }
            h1 { color: #833ab4; font-size: 38px; }
            input {
                width: 90%;
                padding: 13px;
                margin: 8px;
                border: 1px solid #ddd;
                border-radius: 6px;
                box-sizing: border-box;
            }
            button {
                width: 90%;
                padding: 13px;
                background: #833ab4;
                color: white;
                border: none;
                border-radius: 6px;
                margin: 10px;
            }
            a { color: #833ab4; }
            .notice { color: #833ab4; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>lnstagram</h1>
            <p class="notice">MY SOCIAL WEBSITE</p>
            {{ content|safe }}
        </div>
    </body>
    </html>
    """, content=content)

@app.route("/")
def home():
    return redirect("/dashboard" if "user" in session else "/register")

@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        if len(username) < 3 or len(password) < 8:
            message = "Username needs 3 characters and password 8."
        else:
            db = connect()
            try:
                db.execute(
                    "INSERT INTO users VALUES (?, ?)",
                    (username, generate_password_hash(password))
                )
                db.commit()
                return redirect("/login")
            except sqlite3.IntegrityError:
                message = "Username already exists."
            finally:
                db.close()

    return page(f"""
        <h3>Create an account</h3>
        <p>{message}</p>
        <form method="POST">
            <input name="username" placeholder="Username" required>
            <input name="password" type="password"
                   placeholder="Create password" required>
            <button>Create account</button>
        </form>
        <p>Already registered? <a href="/login">Login</a></p>
    """)

@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        db = connect()
        user = db.execute(
            "SELECT username, password FROM users WHERE username=?",
            (request.form["username"].strip(),)
        ).fetchone()
        db.close()

        if user and check_password_hash(user[1], request.form["password"]):
            session["user"] = user[0]
            return redirect("/dashboard")

        message = "Incorrect username or password."

    return page(f"""
        <h3>Login</h3>
        <p>{message}</p>
        <form method="POST">
            <input name="username" placeholder="Username" required>
            <input name="password" type="password"
                   placeholder="Password" required>
            <button>Login</button>
        </form>
        <p>New here? <a href="/register">Create account</a></p>
    """)

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    return page(f"""
        <h2>Welcome, {session["user"]}!</h2>
        <p>Your account is working.</p>
        <a href="/logout">Logout</a>
    """)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

with connect() as db:
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)

