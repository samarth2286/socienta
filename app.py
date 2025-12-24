from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "socienta_secret_key"

def get_user(username, password):
    conn = sqlite3.connect("database/socienta.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, username, role FROM users WHERE username=? AND password=?",
        (username, password)
    )
    user = cursor.fetchone()

    conn.close()
    return user

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = get_user(username, password)

        if user:
            session["user_id"] = user[0]
            session["username"] = user[1]
            session["role"] = user[2]
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        username=session["username"],
        role=session["role"]
    )

@app.route("/add-resident", methods=["GET", "POST"])
def add_resident():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/login")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            conn = sqlite3.connect("database/socienta.db")
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, password, "resident")
            )

            conn.commit()
            conn.close()

            return render_template(
                "add_resident.html",
                message="Resident added successfully"
            )

        except sqlite3.IntegrityError:
            return render_template(
                "add_resident.html",
                error="Username already exists"
            )

    return render_template("add_resident.html")
@app.route("/raise-complaint", methods=["GET", "POST"])
def raise_complaint():
    if "user_id" not in session or session.get("role") != "resident":
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]

        conn = sqlite3.connect("database/socienta.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO complaints (user_id, title, description) VALUES (?, ?, ?)",
            (session["user_id"], title, description)
        )

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("raise_complaint.html")

@app.route("/view-complaints")
def view_complaints():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/login")

    conn = sqlite3.connect("database/socienta.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT users.username, complaints.title, complaints.description, complaints.status, complaints.id
        FROM complaints
        JOIN users ON complaints.user_id = users.id
    """)

    complaints = cursor.fetchall()
    conn.close()

    return render_template(
        "view_complaints.html",
        complaints=complaints
    )
@app.route("/update-complaint-status", methods=["POST"])
def update_complaint_status():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/login")

    complaint_id = request.form["complaint_id"]
    status = request.form["status"]

    conn = sqlite3.connect("database/socienta.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE complaints SET status=? WHERE id=?",
        (status, complaint_id)
    )

    conn.commit()
    conn.close()

    return redirect("/view-complaints")
@app.route("/add-visitor", methods=["GET", "POST"])
def add_visitor():
    if "user_id" not in session or session.get("role") != "resident":
        return redirect("/login")

    if request.method == "POST":
        visitor_name = request.form["visitor_name"]
        purpose = request.form["purpose"]
        visit_date = request.form["visit_date"]

        conn = sqlite3.connect("database/socienta.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO visitors (user_id, visitor_name, purpose, visit_date) VALUES (?, ?, ?, ?)",
            (session["user_id"], visitor_name, purpose, visit_date)
        )

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("add_visitor.html")
@app.route("/view-visitors")
def view_visitors():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/login")

    conn = sqlite3.connect("database/socienta.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT users.username,
               visitors.visitor_name,
               visitors.purpose,
               visitors.visit_date,
               visitors.status,
               visitors.id
        FROM visitors
        JOIN users ON visitors.user_id = users.id
    """)

    visitors = cursor.fetchall()
    conn.close()

    return render_template(
        "view_visitors.html",
        visitors=visitors
    )
@app.route("/update-visitor-status", methods=["POST"])
def update_visitor_status():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/login")

    visitor_id = request.form["visitor_id"]
    status = request.form["status"]

    conn = sqlite3.connect("database/socienta.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE visitors SET status=? WHERE id=?",
        (status, visitor_id)
    )

    conn.commit()
    conn.close()

    return redirect("/view-visitors")
@app.route("/my-visitors")
def my_visitors():
    if "user_id" not in session or session.get("role") != "resident":
        return redirect("/login")

    conn = sqlite3.connect("database/socienta.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT visitor_name, purpose, visit_date, status
        FROM visitors
        WHERE user_id = ?
    """, (session["user_id"],))

    visitors = cursor.fetchall()
    conn.close()

    return render_template(
        "my_visitors.html",
        visitors=visitors
    )
@app.route("/set-payment", methods=["GET", "POST"])
def set_payment():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/login")

    conn = sqlite3.connect("database/socienta.db")
    cursor = conn.cursor()

    # Get all residents
    cursor.execute("SELECT id, username FROM users WHERE role='resident'")
    users = cursor.fetchall()

    if request.method == "POST":
        user_id = request.form["user_id"]
        month = request.form["month"]
        amount = request.form["amount"]

        cursor.execute(
            "INSERT INTO payments (user_id, month, amount) VALUES (?, ?, ?)",
            (user_id, month, amount)
        )
        conn.commit()

        return redirect("/dashboard")

    conn.close()
    return render_template("set_payment.html", users=users)
@app.route("/my-payments")
def my_payments():
    if "user_id" not in session or session.get("role") != "resident":
        return redirect("/login")

    conn = sqlite3.connect("database/socienta.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT month, amount, status, id
        FROM payments
        WHERE user_id = ?
    """, (session["user_id"],))

    payments = cursor.fetchall()
    conn.close()

    return render_template(
        "my_payments.html",
        payments=payments
    )
@app.route("/pay-maintenance", methods=["POST"])
def pay_maintenance():
    if "user_id" not in session or session.get("role") != "resident":
        return redirect("/login")

    payment_id = request.form["payment_id"]

    conn = sqlite3.connect("database/socienta.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE payments SET status='Paid' WHERE id=?",
        (payment_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/my-payments")
@app.route("/maintenance-report")
def maintenance_report():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/login")

    month = request.args.get("month")
    records = []

    if month:
        conn = sqlite3.connect("database/socienta.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT users.username,
                   payments.month,
                   payments.amount,
                   payments.status
            FROM payments
            JOIN users ON payments.user_id = users.id
            WHERE payments.month = ?
        """, (month,))

        records = cursor.fetchall()
        conn.close()

    return render_template(
        "maintenance_report.html",
        records=records
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)

