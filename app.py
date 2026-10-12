from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "hospital_project_secret"

DATABASE = "hospital.db"


# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            address TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            available_time TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'Booked',
            FOREIGN KEY(patient_id) REFERENCES patients(id),
            FOREIGN KEY(doctor_id) REFERENCES doctors(id)
        )
    """)

    # Add sample doctors
    cursor.execute("SELECT COUNT(*) FROM doctors")

    if cursor.fetchone()[0] == 0:

        doctors = [
            (
                "Dr. Priya Sharma",
                "Cardiologist",
                "9876543210",
                "priya@hospital.com",
                "10:00 AM - 2:00 PM"
            ),
            (
                "Dr. Rahul Reddy",
                "General Physician",
                "9876543211",
                "rahul@hospital.com",
                "9:00 AM - 1:00 PM"
            ),
            (
                "Dr. Ananya Rao",
                "Dermatologist",
                "9876543212",
                "ananya@hospital.com",
                "11:00 AM - 4:00 PM"
            )
        ]

        cursor.executemany("""
            INSERT INTO doctors
            (name, specialization, phone, email, available_time)
            VALUES (?, ?, ?, ?, ?)
        """, doctors)

    conn.commit()
    conn.close()


# ---------------- HOME ----------------

@app.route("/")
def index():

    conn = get_db()

    patient_count = conn.execute(
        "SELECT COUNT(*) FROM patients"
    ).fetchone()[0]

    doctor_count = conn.execute(
        "SELECT COUNT(*) FROM doctors"
    ).fetchone()[0]

    appointment_count = conn.execute(
        "SELECT COUNT(*) FROM appointments WHERE status='Booked'"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        patient_count=patient_count,
        doctor_count=doctor_count,
        appointment_count=appointment_count
    )


# ---------------- PATIENTS ----------------

@app.route("/patients")
def patients():

    conn = get_db()

    patients = conn.execute("""
        SELECT *
        FROM patients
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "patients.html",
        patients=patients
    )


@app.route("/register-patient", methods=["POST"])
def register_patient():

    name = request.form.get("name", "").strip()
    age = request.form.get("age", "").strip()
    gender = request.form.get("gender", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    address = request.form.get("address", "").strip()

    if not name or not age or not gender or not phone:

        flash(
            "Please fill all required fields.",
            "danger"
        )

        return redirect(url_for("patients"))

    try:
        age = int(age)

        if age <= 0 or age > 120:
            raise ValueError

    except ValueError:

        flash(
            "Please enter a valid age.",
            "danger"
        )

        return redirect(url_for("patients"))

    conn = get_db()

    conn.execute("""
        INSERT INTO patients
        (name, age, gender, phone, email, address)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        name,
        age,
        gender,
        phone,
        email,
        address
    ))

    conn.commit()
    conn.close()

    flash(
        "Patient registered successfully!",
        "success"
    )

    return redirect(url_for("patients"))


# ---------------- DOCTORS ----------------

@app.route("/doctors")
def doctors():

    conn = get_db()

    doctors = conn.execute("""
        SELECT *
        FROM doctors
        ORDER BY name
    """).fetchall()

    conn.close()

    return render_template(
        "doctors.html",
        doctors=doctors
    )


@app.route("/add-doctor", methods=["POST"])
def add_doctor():

    name = request.form.get("name", "").strip()
    specialization = request.form.get(
        "specialization", ""
    ).strip()

    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()

    available_time = request.form.get(
        "available_time", ""
    ).strip()

    if not name or not specialization:

        flash(
            "Doctor name and specialization are required.",
            "danger"
        )

        return redirect(url_for("doctors"))

    conn = get_db()

    conn.execute("""
        INSERT INTO doctors
        (name, specialization, phone, email, available_time)
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        specialization,
        phone,
        email,
        available_time
    ))

    conn.commit()
    conn.close()

    flash(
        "Doctor added successfully!",
        "success"
    )

    return redirect(url_for("doctors"))


# ---------------- BOOK APPOINTMENT ----------------

@app.route("/appointment")
def appointment():

    conn = get_db()

    patients = conn.execute("""
        SELECT *
        FROM patients
        ORDER BY name
    """).fetchall()

    doctors = conn.execute("""
        SELECT *
        FROM doctors
        ORDER BY name
    """).fetchall()

    conn.close()

    return render_template(
        "appointment.html",
        patients=patients,
        doctors=doctors
    )


@app.route("/book-appointment", methods=["POST"])
def book_appointment():

    patient_id = request.form.get("patient_id")
    doctor_id = request.form.get("doctor_id")
    appointment_date = request.form.get("appointment_date")
    appointment_time = request.form.get("appointment_time")
    reason = request.form.get("reason", "").strip()

    if not patient_id or not doctor_id:

        flash(
            "Please select a patient and doctor.",
            "danger"
        )

        return redirect(url_for("appointment"))

    if not appointment_date or not appointment_time:

        flash(
            "Please select date and time.",
            "danger"
        )

        return redirect(url_for("appointment"))

    try:

        selected_date = datetime.strptime(
            appointment_date,
            "%Y-%m-%d"
        ).date()

        if selected_date < datetime.now().date():

            flash(
                "Appointment date cannot be in the past.",
                "danger"
            )

            return redirect(url_for("appointment"))

    except ValueError:

        flash(
            "Invalid appointment date.",
            "danger"
        )

        return redirect(url_for("appointment"))

    conn = get_db()

    # Check duplicate booking

    existing = conn.execute("""
        SELECT id
        FROM appointments
        WHERE doctor_id = ?
        AND appointment_date = ?
        AND appointment_time = ?
        AND status = 'Booked'
    """, (
        doctor_id,
        appointment_date,
        appointment_time
    )).fetchone()

    if existing:

        conn.close()

        flash(
            "Doctor is already booked at this time.",
            "danger"
        )

        return redirect(url_for("appointment"))

    conn.execute("""
        INSERT INTO appointments
        (
            patient_id,
            doctor_id,
            appointment_date,
            appointment_time,
            reason,
            status
        )
        VALUES (?, ?, ?, ?, ?, 'Booked')
    """, (
        patient_id,
        doctor_id,
        appointment_date,
        appointment_time,
        reason
    ))

    conn.commit()
    conn.close()

    flash(
        "Appointment booked successfully!",
        "success"
    )

    return redirect(url_for("appointments"))


# ---------------- APPOINTMENTS ----------------

@app.route("/appointments")
def appointments():

    conn = get_db()

    appointments = conn.execute("""
        SELECT
            a.id,
            p.name AS patient_name,
            d.name AS doctor_name,
            d.specialization,
            a.appointment_date,
            a.appointment_time,
            a.reason,
            a.status

        FROM appointments a

        JOIN patients p
        ON a.patient_id = p.id

        JOIN doctors d
        ON a.doctor_id = d.id

        ORDER BY
            a.appointment_date,
            a.appointment_time
    """).fetchall()

    conn.close()

    return render_template(
        "appointments.html",
        appointments=appointments
    )


# ---------------- CANCEL ----------------

@app.route(
    "/cancel/<int:appointment_id>",
    methods=["POST"]
)
def cancel_appointment(appointment_id):

    conn = get_db()

    conn.execute("""
        UPDATE appointments
        SET status = 'Cancelled'
        WHERE id = ?
    """, (
        appointment_id,
    ))

    conn.commit()
    conn.close()

    flash(
        "Appointment cancelled successfully.",
        "success"
    )

    return redirect(url_for("appointments"))


# ---------------- SEARCH ----------------

@app.route("/search")
def search():

    query = request.args.get(
        "query",
        ""
    ).strip()

    patients = []

    if query:

        conn = get_db()

        patients = conn.execute("""
            SELECT *
            FROM patients
            WHERE name LIKE ?
            OR phone LIKE ?
            OR email LIKE ?
            ORDER BY name
        """, (
            "%" + query + "%",
            "%" + query + "%",
            "%" + query + "%"
        )).fetchall()

        conn.close()

    return render_template(
        "search.html",
        patients=patients,
        query=query
    )


# ---------------- START APPLICATION ----------------

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )