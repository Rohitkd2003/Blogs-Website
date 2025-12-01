from flask import Flask, render_template, request, redirect, session
from db import get_connection

app = Flask(__name__)
app.secret_key = "mysecret"

# ---------------- HOME -------------------
@app.route("/")
def home():
    return render_template("index.html") 


# ---------------- REGISTER -------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO users (name,email,password) VALUES (%s,%s,%s)",
                  (name, email, password))
        conn.commit()
        return redirect("/login")

    return render_template("register.html")


# ---------------- LOGIN -------------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()
        c = conn.cursor(dictionary=True)
        c.execute("SELECT * FROM users WHERE email=%s AND password=%s",
                  (email, password))
        user = c.fetchone()

        if user:
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect("/dashboard")
        else:
            return "Invalid Credentials!"

    return render_template("login.html")


# ---------------- DASHBOARD -------------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    c = conn.cursor(dictionary=True)
    c.execute("SELECT * FROM blogs WHERE user_id=%s ORDER BY id DESC",
              (session["user_id"],))
    blogs = c.fetchall()

    return render_template("dashboard.html", blogs=blogs, name=session["user_name"])


# ---------------- ADD BLOG -------------------
@app.route("/add", methods=["GET","POST"])
def add_blog():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO blogs (user_id,title,content) VALUES (%s,%s,%s)",
                  (session["user_id"], title, content))
        conn.commit()
        return redirect("/dashboard")

    return render_template("add_blog.html")


# ---------------- EDIT BLOG -------------------
@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit_blog(id):
    conn = get_connection()
    c = conn.cursor(dictionary=True)

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        c.execute("UPDATE blogs SET title=%s, content=%s WHERE id=%s",
                  (title, content, id))
        conn.commit()
        return redirect("/dashboard")

    c.execute("SELECT * FROM blogs WHERE id=%s", (id,))
    blog = c.fetchone()
    return render_template("edit_blog.html", blog=blog)


# ---------------- DELETE BLOG -------------------
@app.route("/delete/<int:id>")
def delete_blog(id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM blogs WHERE id=%s", (id,))
    conn.commit()
    return redirect("/dashboard")


# ---------------- BLOG DETAIL -------------------
@app.route("/blog/<int:id>")
def blog_detail(id):
    conn = get_connection()
    c = conn.cursor(dictionary=True)

    c.execute("""
        SELECT blogs.*, users.name 
        FROM blogs INNER JOIN users ON users.id = blogs.user_id
        WHERE blogs.id=%s
    """, (id,))
    blog = c.fetchone()

    return render_template("blog_detail.html", blog=blog)


# ---------------- LOGOUT -------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
