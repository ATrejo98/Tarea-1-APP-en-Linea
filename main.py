from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "miclaveultrasecreta"

# Inicializar la base de datos
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()


@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE user_id=?", (session["user_id"],))
    tasks = c.fetchall()
    conn.close()
    return render_template("index.html", tasks=tasks)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session["user_id"] = user[0]
            return redirect(url_for("home"))
        else:
            return "Usuario o contraseña incorrecta"
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        except:
            return "El usuario ya existe"
        conn.close()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/add", methods=["POST"])
def add_task():
    title = request.form["title"]
    description = request.form["description"]
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO tasks (user_id, title, description) VALUES (?, ?, ?)",
              (session["user_id"], title, description))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))

@app.route("/delete/<int:id>")
def delete_task(id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id=? AND user_id=?", (id, session["user_id"]))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_task(id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        c.execute("UPDATE tasks SET title=?, description=? WHERE id=? AND user_id=?",
                  (title, description, id, session["user_id"]))
        conn.commit()
        conn.close()
        return redirect(url_for("home"))

    c.execute("SELECT * FROM tasks WHERE id=? AND user_id=?", (id, session["user_id"]))
    task = c.fetchone()
    conn.close()
    return render_template("edit.html", task=task)


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=3000)
