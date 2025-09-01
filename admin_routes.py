from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shreya@2005",
        database="ArtGallery"
    )

# Admin Access Check
def admin_required(func):
    def wrapper(*args, **kwargs):
        if "user_id" not in session or session.get("role") != "admin":
            flash("Access denied! Admins only.", "danger")
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# ------------------- ADMIN DASHBOARD -------------------
@admin_bp.route("/")
@admin_required
def dashboard():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM Users")
    users = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) AS total FROM Artists")
    artists = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) AS total FROM Artworks")
    artworks = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) AS total FROM Orders")
    orders = cursor.fetchone()["total"]

    cursor.close()
    db.close()
    return render_template("admin/dashboard.html",
                           users=users, artists=artists, artworks=artworks, orders=orders)

# ------------------- MANAGE USERS -------------------
@admin_bp.route("/users", methods=["GET", "POST"])
@admin_required
def manage_users():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # ADD USER
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        role = request.form["role"]
        cursor.execute("INSERT INTO Users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                       (name, email, "default123", role))
        db.commit()
        flash("User added successfully!", "success")
        return redirect(url_for("admin.manage_users"))

    cursor.execute("SELECT * FROM Users")
    users = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("admin/manage_users.html", users=users)

# DELETE USER
@admin_bp.route("/users/delete/<int:user_id>")
@admin_required
def delete_user(user_id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Users WHERE user_id=%s", (user_id,))
    db.commit()
    cursor.close()
    db.close()
    flash("User deleted successfully!", "info")
    return redirect(url_for("admin.manage_users"))

# ------------------- MANAGE ARTISTS -------------------
@admin_bp.route("/artists", methods=["GET", "POST"])
@admin_required
def manage_artists():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        name = request.form["name"]
        bio = request.form["bio"]
        country = request.form["country"]
        cursor.execute("INSERT INTO Artists (name, bio, country) VALUES (%s, %s, %s)",
                       (name, bio, country))
        db.commit()
        flash("Artist added successfully!", "success")
        return redirect(url_for("admin.manage_artists"))

    cursor.execute("SELECT * FROM Artists")
    artists = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("admin/manage_artists.html", artists=artists)

# DELETE ARTIST
@admin_bp.route("/artists/delete/<int:artist_id>")
@admin_required
def delete_artist(artist_id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Artists WHERE artist_id=%s", (artist_id,))
    db.commit()
    cursor.close()
    db.close()
    flash("Artist deleted successfully!", "info")
    return redirect(url_for("admin.manage_artists"))

# ------------------- MANAGE ARTWORKS -------------------
@admin_bp.route("/artworks", methods=["GET", "POST"])
@admin_required
def manage_artworks():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        title = request.form["title"]
        artist_id = request.form["artist_id"]
        price = request.form["price"]
        year = request.form["year"]
        description = request.form["description"]
        cursor.execute("INSERT INTO Artworks (title, artist_id, price, year, description) VALUES (%s, %s, %s, %s, %s)",
                       (title, artist_id, price, year, description))
        db.commit()
        flash("Artwork added successfully!", "success")
        return redirect(url_for("admin.manage_artworks"))

    cursor.execute("SELECT * FROM Artworks")
    artworks = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("admin/manage_artworks.html", artworks=artworks)

# DELETE ARTWORK
@admin_bp.route("/artworks/delete/<int:artwork_id>")
@admin_required
def delete_artwork(artwork_id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Artworks WHERE artwork_id=%s", (artwork_id,))
    db.commit()
    cursor.close()
    db.close()
    flash("Artwork deleted successfully!", "info")
    return redirect(url_for("admin.manage_artworks"))

# ------------------- MANAGE ORDERS -------------------
@admin_bp.route("/orders", methods=["GET", "POST"])
@admin_required
def manage_orders():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # UPDATE ORDER STATUS
    if request.method == "POST":
        order_id = request.form["order_id"]
        status = request.form["status"]
        cursor.execute("UPDATE Orders SET status=%s WHERE order_id=%s",
                       (status, order_id))
        db.commit()
        flash("Order status updated!", "success")
        return redirect(url_for("admin.manage_orders"))

    cursor.execute("""
        SELECT o.order_id, u.name AS user, a.title AS artwork, o.status, o.order_date
        FROM Orders o
        JOIN Users u ON o.user_id = u.user_id
        JOIN Artworks a ON o.artwork_id = a.artwork_id
    """)
    orders = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("admin/manage_orders.html", orders=orders)
