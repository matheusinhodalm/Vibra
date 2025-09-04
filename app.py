# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, abort
import sqlite3
import datetime as dt
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Cria app apontando para as pastas locais de templates/ e static/
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config.from_object('config')

# --- Garantir pasta do banco e inicializar mesmo sob Gunicorn/Render ---
# Se DATABASE apontar para um caminho com diretório, cria o diretório.
db_path = app.config.get("DATABASE")
db_dir = os.path.dirname(db_path) if db_path else ""
if db_dir:
    os.makedirs(db_dir, exist_ok=True)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        is_admin INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    ''')
    # Seed admin (Matheus Pereira Silva)
    cur = db.execute("SELECT id FROM users WHERE email=?", ("admin@vibra.com",))
    if cur.fetchone() is None:
        db.execute(
            "INSERT INTO users (email, name, password_hash, is_admin, created_at) VALUES (?, ?, ?, 1, ?)",
            ("admin@vibra.com", "Matheus Pereira Silva", generate_password_hash("vibra123"), dt.datetime.utcnow().isoformat())
        )
        db.commit()
    # Seed demo user
    cur = db.execute("SELECT id FROM users WHERE email=?", ("demo@vibra.com",))
    if cur.fetchone() is None:
        db.execute(
            "INSERT INTO users (email, name, password_hash, is_admin, created_at) VALUES (?, ?, ?, 0, ?)",
            ("demo@vibra.com", "Usuário Demo", generate_password_hash("vibra123"), dt.datetime.utcnow().isoformat())
        )
        db.commit()
    # Seed sample post
    cur = db.execute("SELECT COUNT(*) c FROM posts")
    if cur.fetchone()["c"] == 0:
        db.execute(
            "INSERT INTO posts (user_id, content, created_at) VALUES ((SELECT id FROM users WHERE email='admin@vibra.com'), ?, ?)",
            ("Bem-vindo(a) à VIBRA! Este é um post de teste.", dt.datetime.utcnow().isoformat())
        )
        db.commit()

# Inicializa o DB ao importar o app (funciona com gunicorn no Render)
with app.app_context():
    try:
        init_db()
    except Exception as e:
        # Log no stdout para aparecer nos logs do Render
        print("Falha ao inicializar DB:", e)

def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    db = get_db()
    return db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()

def login_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user():
            return redirect(url_for('login', next=request.path))
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user or not user["is_admin"]:
            abort(403)
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def index():
    return redirect(url_for("feed") if current_user() else url_for("login"))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            flash("Login realizado!", "success")
            return redirect(request.args.get("next") or url_for("feed"))
        flash("Credenciais inválidas.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Sessão encerrada.", "info")
    return redirect(url_for("login"))

@app.route("/feed", methods=["GET","POST"])
@login_required
def feed():
    db = get_db()
    user = current_user()
    if request.method == "POST":
        content = request.form.get("content","").strip()
        if content:
            db.execute(
                "INSERT INTO posts (user_id, content, created_at) VALUES (?, ?, ?)",
                (user["id"], content, dt.datetime.utcnow().isoformat())
            )
            db.commit()
            flash("Publicado!", "success")
        else:
            flash("Escreva algo para publicar.", "warning")
        return redirect(url_for("feed"))
    posts = db.execute(
        "SELECT p.*, u.name AS author FROM posts p JOIN users u ON u.id=p.user_id ORDER BY p.created_at DESC"
    ).fetchall()
    return render_template("feed.html", user=user, posts=posts)

@app.route("/admin")
@admin_required
def admin():
    db = get_db()
    stats = {
        "users": db.execute("SELECT COUNT(*) c FROM users").fetchone()["c"],
        "posts": db.execute("SELECT COUNT(*) c FROM posts").fetchone()["c"]
    }
    return render_template("admin.html", user=current_user(), stats=stats)

@app.route("/admin/users", methods=["GET","POST"])
@admin_required
def admin_users():
    db = get_db()
    if request.method == "POST":
        name = request.form.get("name","").strip()
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        is_admin = 1 if request.form.get("is_admin") == "on" else 0
        if name and email and len(password) >= 6:
            try:
                db.execute(
                    "INSERT INTO users (name, email, password_hash, is_admin, created_at) VALUES (?, ?, ?, ?, ?)",
                    (name, email, generate_password_hash(password), is_admin, dt.datetime.utcnow().isoformat())
                )
                db.commit()
                flash("Usuário criado.", "success")
            except sqlite3.IntegrityError:
                flash("E-mail já cadastrado.", "danger")
        else:
            flash("Preencha todos os campos (senha 6+).", "warning")
        return redirect(url_for("admin_users"))
    users = db.execute(
        "SELECT id, name, email, is_admin, created_at FROM users ORDER BY id"
    ).fetchall()
    return render_template("admin_users.html", users=users, user=current_user())

@app.errorhandler(403)
def forbidden(e):
    return render_template("base.html", content="Acesso negado.", title="403"), 403

# Execução local (não é usado no Render, mas mantém para testes locais)
if __name__ == "__main__":
    app.secret_key = app.config["SECRET_KEY"]
    app.run(debug=True, host="0.0.0.0", port=5000)
