from flask import Flask, render_template, request, redirect, session, flash, url_for
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from admin_routes import admin_bp   # ✅ Import admin blueprint

app = Flask(__name__)
app.secret_key = "secret123"
print("Flask app initialized")

# ✅ Register the admin blueprint
app.register_blueprint(admin_bp)

# ------------------- DATABASE CONNECTION -------------------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shreya@2005",
        database="ArtGallery"
    )

# ------------------- HOME PAGE -------------------
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

# ------------------- ARTWORK DETAILS -------------------
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

# ------------------- SIGNUP -------------------
@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_pw = generate_password_hash(password)  # Secure password

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

# ------------------- LOGIN -------------------
from werkzeug.security import check_password_hash

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user:
            stored_password = user["password"]

            # ✅ If password is hashed → check hash, else compare plain text
            try:
                password_matches = check_password_hash(stored_password, password)
            except ValueError:
                password_matches = stored_password == password

            if password_matches:
                session["user_id"] = user["user_id"]
                session["role"] = user["role"]
                flash("Login successful!", "success")

                # ✅ Redirect admin to dashboard
                if user["role"] == "admin":
                    return redirect(url_for("admin.dashboard"))
                else:
                    return redirect(url_for("home"))
            else:
                flash("Invalid password!", "danger")
        else:
            flash("User not found!", "danger")

    return render_template("login.html")



# ------------------- PLACE AN ORDER -------------------
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

# ------------------- LOGOUT -------------------
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("role", None)  # ✅ Clear role from session
    flash("Logged out successfully", "info")
    return redirect("/")

# ------------------- DUMMY ARTWORKS PAGE -------------------
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
        },
                {
            "title": "The Hay Wain",
            "artist": "John Constable",
            "price": 180,
            "image": "haywain.jpg"
        },
        {
            "title": "Liberty Leading the People",
            "artist": "Eugène Delacroix",
            "price": 400,
            "image": "liberty.jpg"
        },
        {
            "title": "Napoleon Crossing the Alps",
            "artist": "Jacques-Louis David",
            "price": 350,
            "image": "napolean.jpg"
        },
        {
            "title": "Water Lilies",
            "artist": "Claude Monet",
            "price": 280,
            "image": "waterlily.jpg"
        }
    ]
    return render_template("artworks.html", artworks=artworks)

# ------------------- VIEW ALL ORDERS -------------------
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

# ------------------- MY ORDERS -------------------
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

# ------------------- RUN APP -------------------
if __name__ == "__main__":
    app.run(debug=True)
