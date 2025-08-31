from flask import Flask, render_template, request, redirect, session, flash, url_for
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"
print("Flask app initialized")

# Database connection helper
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Yuvika@2005",
        database="ArtGallery"
    )

@app.route("/")
def home():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.artwork_id, a.title, a.price, a.year, ar.name AS artist 
        FROM Artworks a 
        JOIN Artists ar ON a.artist_id = ar.artist_id
    """)
    artworks = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("index.html", artworks=artworks)

@app.route("/artwork/<int:artwork_id>")
def artwork_detail(artwork_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.*, ar.name AS artist 
        FROM Artworks a 
        JOIN Artists ar ON a.artist_id = ar.artist_id 
        WHERE a.artwork_id=%s
    """, (artwork_id,))
    artwork = cursor.fetchone()
    cursor.close()
    db.close()
    return render_template("artwork.html", artwork=artwork)

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_pw = generate_password_hash(password)  # secure password storage

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "INSERT INTO Users (name, email, password) VALUES (%s, %s, %s)", 
            (name, email, hashed_pw)
        )
        db.commit()
        cursor.close()
        db.close()

        flash("Signup successful, please login!", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["user_id"]
            flash("Login successful!", "success")
            return redirect("/")
        else:
            flash("Invalid credentials", "danger")
    return render_template("login.html")

@app.route("/order/<int:artwork_id>", methods=["GET", "POST"])
def orders(artwork_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        user_id = session["user_id"]
        cursor.execute("""
            INSERT INTO Orders (user_id, artwork_id, order_date, status) 
            VALUES (%s, %s, CURDATE(), 'Pending')
        """, (user_id, artwork_id))
        db.commit()
        cursor.close()
        db.close()
        flash("Order placed successfully!", "success")
        return redirect("/")

    cursor.execute("SELECT * FROM Artworks WHERE artwork_id=%s", (artwork_id,))
    artwork = cursor.fetchone()
    cursor.close()
    db.close()

    return render_template("order.html", artwork=artwork)

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out successfully", "info")
    return redirect("/")

@app.route("/artworks")
def artworks():
    artworks = [
        {
            "title": "Starry Night",
            "artist": "Vincent van Gogh",
            "price": 200,
            "image": "starrynight.jpg"
        },
        {
            "title": "Mona Lisa",
            "artist": "Leonardo da Vinci",
            "price": 500,
            "image": "monalisa.jpg"
        },
        {
            "title": "The Persistence of Memory",
            "artist": "Salvador Dalí",
            "price": 300,
            "image": "persistence.jpg"
        },
        {
            "title": "The Scream",
            "artist": "Edvard Munch",
            "price": 250,
            "image": "scream.jpg"
        }
    ]
    return render_template("artworks.html", artworks=artworks)


@app.route("/orders")
def orders_page():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT o.order_id, o.order_date, o.status, a.title AS artwork 
        FROM Orders o 
        JOIN Artworks a ON o.artwork_id = a.artwork_id
        WHERE o.user_id=%s
    """, (session["user_id"],))
    orders = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("orders.html", orders=orders)

@app.route("/my-orders")
def my_orders():
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT o.order_id, o.order_date, o.status, a.title, a.price
        FROM Orders o
        JOIN Artworks a ON o.artwork_id = a.artwork_id
        WHERE o.user_id = %s
    """, (session["user_id"],))
    orders = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template("my_orders.html", orders=orders)


    
if __name__ == "__main__":
    app.run(debug=True)
