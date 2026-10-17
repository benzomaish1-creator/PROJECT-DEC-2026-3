from flask import *
import os  #to help us het path to save profile photo
import pymysql
import calendar
import io
from datetime import date as date_cls
from datetime import datetime, timedelta

# used for PDF report generation (patient/doctor "Download Report" feature)
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle  # NEW: used for the left-aligned DOCCONNECT PDF heading

app = Flask(__name__)
app.secret_key = "supersecretkey123"  # needed for session (login) to work

# setup file upload
app.config['UPLOAD_FOLDER'] = 'static/images'

# Maximum allowed length for any account password (login + confirm password)
MAX_PASSWORD_LENGTH = 6


def log_audit(connection, actor_type, actor_id, action, details=None):
    """Writes one row to the audit_log table. Used by the Admin section to
    monitor system activity and flag suspicious/bad behaviour (repeated
    failed logins, doctor removals, referrals, etc). Uses the
    connection/cursor already open in the calling route, same pattern as
    add_notification()."""
    audit_cursor = connection.cursor()
    audit_cursor.execute(
        "INSERT INTO audit_log (actor_type, actor_id, action, details, ip_address) "
        "VALUES (%s, %s, %s, %s, %s)",
        (actor_type, actor_id, action, details, request.remote_addr)
    )
    connection.commit()
    audit_cursor.close()


def add_notification(connection, patient_id, message):
    """Inserts an in-app notification row for a patient. Uses the
    connection/cursor already open in the calling route, so it doesn't
    open a new DB connection."""
    notif_cursor = connection.cursor()
    notif_cursor.execute(
        "INSERT INTO notifications (patient_id, message) VALUES (%s, %s)",
        (patient_id, message)
    )
    connection.commit()
    notif_cursor.close()


def format_time_hhmm(value):
    """PyMySQL returns SQL TIME columns as datetime.timedelta, not a time
    object - and str(timedelta) drops the leading zero on single-digit
    hours (e.g. '9:00:00' instead of '09:00:00'), which breaks matching
    against the frontend's 'HH:MM' slot strings. This normalizes either
    a timedelta or a time/datetime value into a clean 'HH:MM' string."""
    if isinstance(value, timedelta):
        total_minutes = int(value.total_seconds() // 60)
        hours = (total_minutes // 60) % 24
        minutes = total_minutes % 60
        return f"{hours:02d}:{minutes:02d}"
    return value.strftime('%H:%M')



# @app.route("/")
# def home():
#     return render_template("index.html")



# Define the Doctor Registration Route/Endpoint
@app.route('/doctor_registration', methods=['POST','GET'])
def doctor_registration():
    if request.method == 'POST':

        # Extract POST Data
        firstname = request.form['firstname']
        middlename = request.form['middlename']
        surname = request.form['surname']
        business_phone = request.form['business_phone']
        personal_phone = request.form['personal_phone']
        email = request.form['email']
        gender = request.form['gender']
        county = request.form['county']
        address = request.form['address']
        speciality = request.form['speciality']
        profile_description = request.form['profile_description']
        id_number = request.form['id_number']
        language = request.form['language']
        password = request.form['password']
        confirm_password = request.form.get('confirm_password', '')

        # ---- validate password / confirm password before doing anything else ----
        if password != confirm_password:
            return render_template(
                "doctor_registration.html",
                error="Password and Confirm Password do not match."
            )

        if len(password) == 0 or len(password) > MAX_PASSWORD_LENGTH:
            return render_template(
                "doctor_registration.html",
                error=f"Password must be between 1 and {MAX_PASSWORD_LENGTH} characters."
            )

        # Extract Image
        # we have used files because it is a photo
        photo = request.files['profile_photo']

        # Get image filename
        filename = photo.filename

        # Save image in Upload Folder
        # C/users/....static/
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(photo_path) # wesave the photo to static/images folder using its original name

        # So far we have doctors details
        
        # Connect to Database
        # connection variable holds the connection
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='medical_referral'
        )
        # We use the connection to create a cursor
        cursor = connection.cursor()

        # What is cursor? used to run/execute SQL in python
        # Insert Doctor Details
        cursor.execute("""
            INSERT INTO doctors
            (firstname, middlename, surname, business_phone,
             personal_phone, email, gender, county, address,
             speciality, profile_description, id_number,
             language, profile_photo, password)

            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            firstname,
            middlename,
            surname,
            business_phone,
            personal_phone,
            email,
            gender,
            county,
            address,
            speciality,
            profile_description,
            id_number,
            language,
            filename,
            password
        ))

        # Save changes
        connection.commit()

        log_audit(connection, 'doctor', cursor.lastrowid, 'doctor_registered',
                   f"New doctor registered: {firstname} {surname} ({email})")

        # Close connection
        cursor.close()
        connection.close()

        # Return success message
        return render_template( # show a message back to the form
            "doctor_registration.html",
            success="Doctor Registered successfully.Thank you."
        )
    
    else:# Show form first
        return render_template('doctor_registration.html')
    


# SHow specialists doctors
@app.route('/')
def specialists():

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='medical_referral'
    )

    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT * FROM doctors ORDER BY firstname ASC")

    doctors = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("index.html", doctors=doctors)



@app.route("/about")
def about():
    return render_template("about.html")



# One doctor route
# it looks a dictor by doctor id
@app.route('/doctor/<int:doctor_id>')
def doctor_details(doctor_id):

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='medical_referral'
    )

    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # Get only the selected doctor
    cursor.execute(
        "SELECT * FROM doctors WHERE doctor_id=%s",
        (doctor_id,)
    )

    doctor = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template("doctor_details.html", doctor=doctor)




# ================= PATIENT REGISTRATION =================
@app.route('/patient_registration', methods=['GET', 'POST'])
def patient_registration():
    if request.method == 'POST':

        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        phone = request.form['phone']
        county = request.form['county']
        address = request.form['address']
        dob = request.form['dob']
        password = request.form['password']
        confirm_password = request.form.get('confirm_password', '')

        # ---- validate password / confirm password before touching the DB ----
        if password != confirm_password:
            return render_template("patients.html", error="Password and Confirm Password do not match.")

        if len(password) == 0 or len(password) > MAX_PASSWORD_LENGTH:
            return render_template(
                "patients.html",
                error=f"Password must be between 1 and {MAX_PASSWORD_LENGTH} characters."
            )

        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='medical_referral'
        )
        cursor = connection.cursor()

        # check if email already registered
        cursor.execute("SELECT * FROM patients WHERE email=%s", (email,))
        existing = cursor.fetchone()

        if existing:
            cursor.close()
            connection.close()
            return render_template("patients.html", error="Email already registered.")

        cursor.execute("""
            INSERT INTO patients
            (firstname, lastname, email, phone, county, address, dob, password)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            firstname,
            lastname,
            email,
            phone,
            county,
            address,
            dob,
            password
        ))

        connection.commit()

        log_audit(connection, 'patient', cursor.lastrowid, 'patient_registered',
                   f"New patient registered: {firstname} {lastname} ({email})")

        cursor.close()
        connection.close()

        return render_template(
            "patients.html",
            success="Registration successful. Please login."
        )

    return render_template("patients.html")


# ================= PATIENT LOGIN =================
@app.route('/patient_login', methods=['GET', 'POST'])
def patient_login():
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='medical_referral'
        )
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        cursor.execute(
            "SELECT * FROM patients WHERE email=%s AND password=%s",
            (email, password)
        )
        patient = cursor.fetchone()

        if patient:
            cursor.close()
            connection.close()
            session['patient_id'] = patient['patient_id']
            session['patient_name'] = patient['firstname']
            return redirect(url_for('specialists'))
        else:
            # ---- log the failed attempt so Admin can spot suspicious/bad behaviour ----
            log_audit(connection, 'patient', None, 'failed_login',
                       f"Failed patient login attempt for email: {email}")
            cursor.close()
            connection.close()
            return render_template("patient_login.html", error="Invalid Email or password.")

    return render_template("patient_login.html")


@app.route('/patient_logout')
def patient_logout():
    session.pop('patient_id', None)
    session.pop('patient_name', None)
    return redirect(url_for('patient_login'))


# ================= M-PESA BOOKING FEE (NEW) =================
# The amount charged now comes from doctors.consultation_fee (set per doctor in
# the database). This value is only a fallback if a doctor has no fee saved.
CONSULTATION_FEE = 100


# ================= BOOK APPOINTMENT =================
@app.route('/book/<int:doctor_id>', methods=['GET', 'POST'])
def book_appointment(doctor_id):

    # make sure patient is logged in
    if 'patient_id' not in session:
        return redirect(url_for('patient_login'))

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT * FROM doctors WHERE doctor_id=%s", (doctor_id,))
    doctor = cursor.fetchone()

    # NEW: this doctor's consultation fee (whole shillings) - shown in the M-PESA dialog and charged
    if doctor:
        doctor['consultation_fee'] = int(doctor.get('consultation_fee') or CONSULTATION_FEE)

    if request.method == 'POST':

        reason = request.form['reason']
        appointment_date = request.form['appointment_date']
        appointment_time = request.form['appointment_time']
        patient_id = session['patient_id']

        # ---- check the chosen date/time is at least 1 hour from now ----
        try:
            chosen_datetime = datetime.strptime(
                appointment_date + " " + appointment_time, "%Y-%m-%d %H:%M"
            )
        except ValueError:
            cursor.close()
            connection.close()
            return render_template(
                "book_appointment.html",
                doctor=doctor,
                error="Invalid date or time selected."
            )

        earliest_allowed = datetime.now() + timedelta(hours=1)

        if chosen_datetime < earliest_allowed:
            cursor.close()
            connection.close()
            return render_template(
                "book_appointment.html",
                doctor=doctor,
                error="That time has already passed or is too soon. Please book at least 1 hour ahead."
            )

        # ---- check if this doctor already has a booking at this exact date/time ----
        cursor.execute("""
            SELECT appointment_id FROM appointments
            WHERE doctor_id=%s AND appointment_date=%s AND appointment_time=%s AND status NOT IN ('Declined', 'Completed', 'Cancelled')
        """, (doctor_id, appointment_date, appointment_time))
        clash = cursor.fetchone()

        if clash:
            cursor.close()
            connection.close()
            return render_template(
                "book_appointment.html",
                doctor=doctor,
                error="That time slot is already booked for this doctor. Please choose another time."
            )

        # ---- check if this patient already has an appointment with this same doctor ----
        cursor.execute("""
            SELECT appointment_id FROM appointments
            WHERE patient_id=%s AND doctor_id=%s AND status NOT IN ('Cancelled', 'Declined', 'Completed')
        """, (patient_id, doctor_id))
        already_with_doctor = cursor.fetchone()

        if already_with_doctor:
            cursor.close()
            connection.close()
            return render_template(
                "book_appointment.html",
                doctor=doctor,
                error="You already have an appointment with this doctor. Please check My Appointments."
            )

        # ---- check if this patient already has an appointment with ANY doctor at this exact date/time ----
        cursor.execute("""
            SELECT appointment_id FROM appointments
            WHERE patient_id=%s AND appointment_date=%s AND appointment_time=%s AND status NOT IN ('Cancelled', 'Declined', 'Completed')
        """, (patient_id, appointment_date, appointment_time))
        already_at_time = cursor.fetchone()

        if already_at_time:
            cursor.close()
            connection.close()
            return render_template(
                "book_appointment.html",
                doctor=doctor,
                error="You already have another appointment booked at this same date and time."
            )

        # ---- NEW: send the M-PESA prompt to the number typed in the dialog ----
        import mpesa
        mpesa_phone = request.form.get('mpesa_phone', '').strip().replace(' ', '').replace('+', '')
        if not (mpesa_phone.isdigit() and len(mpesa_phone) == 12 and mpesa_phone.startswith(('2547', '2541'))):
            cursor.close()
            connection.close()
            return render_template(
                "book_appointment.html",
                doctor=doctor,
                error="Enter a valid M-Pesa number in the format 2547XXXXXXXX."
            )

        payment_result = mpesa.make_payment(mpesa_phone, doctor['consultation_fee'])
        if not payment_result["success"]:
            cursor.close()
            connection.close()
            return render_template(
                "book_appointment.html",
                doctor=doctor,
                error="M-Pesa payment failed: " + payment_result["message"] + " Your booking was not made."
            )

        try:
            cursor.execute("""
                INSERT INTO appointments (patient_id, doctor_id, reason, appointment_date, appointment_time)
                VALUES (%s, %s, %s, %s, %s)
            """, (patient_id, doctor_id, reason, appointment_date, appointment_time))
            connection.commit()
            new_appointment_id = cursor.lastrowid
        except (pymysql.err.IntegrityError, pymysql.err.OperationalError):
            # another patient grabbed this exact slot a split-second earlier
            # (the DB's trg_appt_no_double_book trigger is what catches this)
            cursor.close()
            connection.close()
            return render_template(
                "book_appointment.html",
                doctor=doctor,
                error="That time slot was just booked by someone else. Please choose another time."
            )

        # NEW: remember which number paid, so the doctor can match it to the M-PESA message
        cursor.execute(
            "UPDATE appointments SET payment_phone=%s WHERE appointment_id=%s",
            (mpesa_phone, new_appointment_id)
        )
        connection.commit()

        add_notification(
            connection,
            patient_id,
            f"Your appointment with Dr. {doctor['firstname']} {doctor['surname']} "
            f"on {appointment_date} at {appointment_time} has been booked and is Pending confirmation."
        )

        log_audit(connection, 'patient', patient_id, 'appointment_booked',
                   f"Appointment #{new_appointment_id} booked with Dr. {doctor['firstname']} {doctor['surname']} on {appointment_date} at {appointment_time}.")

        cursor.close()
        connection.close()
        # (old) import mpesa
        # (old) mpesa.mpesa_payment()   <- sent a prompt to a hard-coded number; replaced by mpesa.make_payment() above

        # remember what was paid so the success page can show it
        session['last_mpesa_phone'] = mpesa_phone
        session['last_mpesa_amount'] = doctor['consultation_fee']

        # (old) return render_template("book_appointment.html", doctor=doctor, success="Appointment booked successfully.")
        # NEW: show the "Complete Payment in your phone" dialog; its Continue button opens the success page
        return render_template(
            "book_appointment.html",
            doctor=doctor,
            payment_prompt=True,
            new_appointment_id=new_appointment_id
        )
  

    cursor.close()
    connection.close()

    return render_template("book_appointment.html", doctor=doctor)


# ================= BOOKING SUCCESS (NEW) =================
@app.route('/booking_success/<int:appointment_id>')
def booking_success(appointment_id):

    if 'patient_id' not in session:
        return redirect(url_for('patient_login'))

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT a.appointment_id, a.reason, a.appointment_date, a.appointment_time, a.status,
               d.firstname, d.surname, d.speciality
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE a.appointment_id=%s AND a.patient_id=%s
    """, (appointment_id, session['patient_id']))
    appointment = cursor.fetchone()

    cursor.close()
    connection.close()

    if not appointment:
        return redirect(url_for('my_appointments'))

    appointment['appointment_time'] = format_time_hhmm(appointment['appointment_time'])

    return render_template(
        "booking_success.html",
        appointment=appointment,
        amount=session.get('last_mpesa_amount', CONSULTATION_FEE),
        phone=session.get('last_mpesa_phone', '')
    )


# ================= DOCTOR CONFIRMS PAYMENT RECEIVED (NEW) =================
@app.route('/confirm_payment/<int:appointment_id>', methods=['POST'])
def confirm_payment(appointment_id):

    if 'doctor_id' not in session:
        return redirect(url_for('doctor_login'))

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # only the doctor this booking belongs to can confirm its payment
    cursor.execute("""
        SELECT a.appointment_id, a.patient_id, a.appointment_date, a.appointment_time, a.payment_status,
               d.firstname, d.surname, d.consultation_fee
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE a.appointment_id=%s AND a.doctor_id=%s
    """, (appointment_id, session['doctor_id']))
    appt = cursor.fetchone()

    if not appt:
        cursor.close()
        connection.close()
        flash("Booking not found.")
        return redirect(url_for('doctor_dashboard'))

    if appt['payment_status'] == 'Paid':
        cursor.close()
        connection.close()
        flash("Payment for this booking is already confirmed.")
        return redirect(url_for('doctor_dashboard'))

    fee = int(appt['consultation_fee'] or CONSULTATION_FEE)

    cursor.execute(
        "UPDATE appointments SET payment_status='Paid', amount_paid=%s WHERE appointment_id=%s",
        (fee, appointment_id)
    )
    connection.commit()

    add_notification(
        connection,
        appt['patient_id'],
        f"Dr. {appt['firstname']} {appt['surname']} has confirmed receipt of your payment of KES {fee} "
        f"for your appointment on {appt['appointment_date']} at {format_time_hhmm(appt['appointment_time'])}."
    )

    log_audit(connection, 'doctor', session['doctor_id'], 'payment_confirmed',
              f"Payment of KES {fee} confirmed for appointment #{appointment_id}.")

    cursor.close()
    connection.close()

    flash(f"Payment of KES {fee} confirmed for booking #{appointment_id}.")
    return redirect(url_for('doctor_dashboard'))


# ================= GET BOOKED SLOTS (for a doctor on a given date) =================
@app.route('/get_booked_slots/<int:doctor_id>')
def get_booked_slots(doctor_id):

    date = request.args.get('date')

    if not date:
        return jsonify([])

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT appointment_time FROM appointments
        WHERE doctor_id=%s AND appointment_date=%s AND status NOT IN ('Declined', 'Completed', 'Cancelled')
    """, (doctor_id, date))

    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    # convert time values to plain "HH:MM" strings so JS can read them
    booked_times = [format_time_hhmm(row['appointment_time']) for row in rows]

    return jsonify(booked_times)


# ================= GET MONTH BOOKING COUNTS (for calendar view) =================
@app.route('/get_month_bookings/<int:doctor_id>')
def get_month_bookings(doctor_id):

    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)

    if not year or not month:
        return jsonify({})

    first_day = date_cls(year, month, 1)
    last_day = date_cls(year, month, calendar.monthrange(year, month)[1])

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT appointment_date, COUNT(*) as booked_count
        FROM appointments
        WHERE doctor_id=%s AND appointment_date BETWEEN %s AND %s AND status NOT IN ('Declined', 'Completed', 'Cancelled')
        GROUP BY appointment_date
    """, (doctor_id, first_day, last_day))

    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    # e.g. {"2026-07-20": 5, "2026-07-21": 12}
    counts = {str(row['appointment_date']): row['booked_count'] for row in rows}

    return jsonify(counts)


# ================= PATIENT: VIEW MY APPOINTMENTS =================
@app.route('/my_appointments')
def my_appointments():

    if 'patient_id' not in session:
        return redirect(url_for('patient_login'))

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT a.*, d.firstname, d.surname, d.speciality
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE a.patient_id = %s
        ORDER BY a.appointment_date DESC
    """, (session['patient_id'],))

    appointments = cursor.fetchall()
    rowcount = cursor.rowcount

    # ---- get this patient's notifications (newest first) ----
    cursor.execute("""
        SELECT * FROM notifications
        WHERE patient_id = %s
        ORDER BY created_at DESC
    """, (session['patient_id'],))
    notifications = cursor.fetchall()

    # mark them as read now that the patient has seen this page
    cursor.execute(
        "UPDATE notifications SET is_read=1 WHERE patient_id=%s AND is_read=0",
        (session['patient_id'],)
    )
    connection.commit()

    # ---- referrals made about this patient (the referral platform) ----
    cursor.execute("""
        SELECT r.*, d1.firstname AS from_first, d1.surname AS from_last,
               d2.firstname AS to_first, d2.surname AS to_last, d2.doctor_id AS to_doctor_id,
               ra.appointment_date AS scheduled_date, ra.appointment_time AS scheduled_time
        FROM referrals r
        JOIN doctors d1 ON r.referring_doctor_id = d1.doctor_id
        JOIN doctors d2 ON r.referred_to_doctor_id = d2.doctor_id
        LEFT JOIN appointments ra ON r.resulting_appointment_id = ra.appointment_id
        WHERE r.patient_id = %s
        ORDER BY r.created_at DESC
    """, (session['patient_id'],))
    referrals = cursor.fetchall()

    if rowcount==0:
        print("x")
        cursor.close()
        connection.close()
        return render_template(
            "my_appointments.html",
            message="You don't have any appointments,Please make an appointment",
            notifications=notifications,
            referrals=referrals
        )
    else:
        print("y")
        cursor.close()
        connection.close()

        return render_template("my_appointments.html", appointments=appointments, notifications=notifications, referrals=referrals)


# ================= DOCTOR LOGIN =================
@app.route('/doctor_login', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='medical_referral'
        )
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        cursor.execute(
            "SELECT * FROM doctors WHERE email=%s AND password=%s",
            (email, password)
        )
        doctor = cursor.fetchone()

        if doctor:
            cursor.close()
            connection.close()
            session['doctor_id'] = doctor['doctor_id']
            session['doctor_name'] = doctor['firstname']
            return redirect(url_for('doctor_dashboard'))
        else:
            # ---- log the failed attempt so Admin can spot suspicious/bad behaviour ----
            log_audit(connection, 'doctor', None, 'failed_login',
                       f"Failed doctor login attempt for email: {email}")
            cursor.close()
            connection.close()
            return render_template("doctor_login.html", error="Invalid email or password.")

    return render_template("doctor_login.html")


@app.route('/doctor_logout')
def doctor_logout():
    session.pop('doctor_id', None)
    session.pop('doctor_name', None)
    return redirect(url_for('doctor_login'))


# ================= DOCTOR DASHBOARD (view patients who booked) =================
@app.route('/doctor_dashboard')
def doctor_dashboard():

    if 'doctor_id' not in session:
        return redirect(url_for('doctor_login'))

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # ---- the logged-in doctor's own profile (for the personalized header/photo) ----
    cursor.execute(
        "SELECT firstname, surname, speciality, profile_photo FROM doctors WHERE doctor_id=%s",
        (session['doctor_id'],)
    )
    my_profile = cursor.fetchone()

    cursor.execute("""
        SELECT a.*, p.firstname,p.lastname, p.email, p.county AS patient_county,
               rd.firstname AS referred_to_first, rd.surname AS referred_to_last
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        LEFT JOIN referrals r ON r.appointment_id = a.appointment_id
        LEFT JOIN doctors rd ON r.referred_to_doctor_id = rd.doctor_id
        WHERE a.doctor_id = %s
        ORDER BY a.appointment_date DESC
    """, (session['doctor_id'],))

    appointments = cursor.fetchall()

    rowcount = cursor.rowcount

    # ---- other doctors, for the "Refer to Another Doctor" dropdown ----
    cursor.execute(
        "SELECT doctor_id, firstname, surname, speciality FROM doctors WHERE doctor_id != %s ORDER BY firstname ASC",
        (session['doctor_id'],)
    )
    other_doctors = cursor.fetchall()

    # ---- incoming referrals sent TO this doctor (hide ones already scheduled -
    #      those now show up as normal appointments in "Patients Booked with" below) ----
    cursor.execute("""
        SELECT r.*, p.firstname AS pat_first, p.lastname AS pat_last, p.phone AS pat_phone,
               d.firstname AS from_first, d.surname AS from_last,
               ra.appointment_date AS scheduled_date, ra.appointment_time AS scheduled_time
        FROM referrals r
        JOIN patients p ON r.patient_id = p.patient_id
        JOIN doctors d ON r.referring_doctor_id = d.doctor_id
        LEFT JOIN appointments ra ON r.resulting_appointment_id = ra.appointment_id
        WHERE r.referred_to_doctor_id = %s AND r.resulting_appointment_id IS NULL
        ORDER BY r.created_at DESC
    """, (session['doctor_id'],))
    incoming_referrals = cursor.fetchall()

    # ---- patients THIS doctor has already referred (a doctor can only refer
    #      a given patient once; a different doctor who received that
    #      referral can still refer the same patient onward) ----
    cursor.execute(
        "SELECT DISTINCT patient_id FROM referrals WHERE referring_doctor_id=%s",
        (session['doctor_id'],)
    )
    already_referred_patient_ids = {row['patient_id'] for row in cursor.fetchall()}

    cursor.close()
    connection.close()

    if rowcount == 0:
        return render_template(
            "doctor_dashboard.html",
            message="You don't have any Bookings!",
            other_doctors=other_doctors,
            incoming_referrals=incoming_referrals,
            my_profile=my_profile,
            already_referred_patient_ids=already_referred_patient_ids
        )
    else:
        return render_template(
            "doctor_dashboard.html",
            appointments=appointments,
            other_doctors=other_doctors,
            incoming_referrals=incoming_referrals,
            my_profile=my_profile,
            already_referred_patient_ids=already_referred_patient_ids
        )



# ================= DOCTOR: UPDATE APPOINTMENT STATUS =================
@app.route('/update_status/<int:appointment_id>/<string:status>', methods=['POST'])
def update_status(appointment_id, status):

    if 'doctor_id' not in session:
        return redirect(url_for('doctor_login'))

    reason = request.form.get('reason', '').strip()

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='medical_referral'
    )
    cursor = connection.cursor()

    # NEW: a booking can only be Approved (Confirmed) or Completed after the doctor
    # has confirmed the M-PESA payment (Declined etc. are still allowed any time)
    if status in ('Confirmed', 'Completed'):
        cursor.execute(
            "SELECT payment_status FROM appointments WHERE appointment_id=%s AND doctor_id=%s",
            (appointment_id, session['doctor_id'])
        )
        pay_row = cursor.fetchone()
        if not pay_row or pay_row[0] != 'Paid':
            cursor.close()
            connection.close()
            flash("Confirm the M-PESA payment first - then you can approve this booking and mark it completed.")
            return redirect(url_for('doctor_dashboard'))

    if reason:
        cursor.execute(
            "UPDATE appointments SET status=%s, feedback=%s WHERE appointment_id=%s",
            (status, reason, appointment_id)
        )
    else:
        cursor.execute(
            "UPDATE appointments SET status=%s WHERE appointment_id=%s",
            (status, appointment_id)
        )

    connection.commit()

    # ---- get patient + doctor info so we can notify the patient ----
    info_cursor = connection.cursor(pymysql.cursors.DictCursor)
    info_cursor.execute("""
        SELECT a.patient_id, p.firstname AS patient_first,
               d.firstname AS doc_first, d.surname AS doc_last,
               a.appointment_date, a.appointment_time
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE a.appointment_id = %s
    """, (appointment_id,))
    info = info_cursor.fetchone()
    info_cursor.close()

    if info:
        message = (
            f"Your appointment with Dr. {info['doc_first']} {info['doc_last']} "
            f"on {info['appointment_date']} at {format_time_hhmm(info['appointment_time'])} is now: {status}."
        )
        if reason:
            message += f" Reason: {reason}"

        add_notification(connection, info['patient_id'], message)

    log_audit(connection, 'doctor', session['doctor_id'], f'appointment_{status.lower()}',
               f"Appointment #{appointment_id} set to {status}." + (f" Reason: {reason}" if reason else ""))

    cursor.close()
    connection.close()

    return redirect(url_for('doctor_dashboard'))


    return redirect(url_for('doctor_dashboard'))



# ================= DOCTOR: RESCHEDULE APPOINTMENT =================
@app.route('/reschedule_appointment/<int:appointment_id>', methods=['POST'])
def reschedule_appointment(appointment_id):

    if 'doctor_id' not in session:
        return redirect(url_for('doctor_login'))

    new_date = request.form['new_date']
    new_time = request.form['new_time']
    reason = request.form.get('reason', '').strip()

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # make sure this appointment belongs to the logged-in doctor, and get old date/time + patient info
    cursor.execute("""
        SELECT a.patient_id, a.doctor_id, a.appointment_date, a.appointment_time,
               d.firstname AS doc_first, d.surname AS doc_last
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE a.appointment_id = %s
    """, (appointment_id,))
    appt = cursor.fetchone()

    if not appt or appt['doctor_id'] != session['doctor_id']:
        cursor.close()
        connection.close()
        return redirect(url_for('doctor_dashboard'))

    # NEW: the new date/time cannot be in the past (must be at least 1 hour from now)
    try:
        chosen_datetime = datetime.strptime(new_date + " " + new_time, "%Y-%m-%d %H:%M")
    except ValueError:
        cursor.close()
        connection.close()
        flash("Invalid date or time selected.")
        return redirect(url_for('doctor_dashboard'))

    if chosen_datetime < datetime.now() + timedelta(hours=1):
        cursor.close()
        connection.close()
        flash("That time has already passed or is too soon. Please choose a date and time at least 1 hour ahead.")
        return redirect(url_for('doctor_dashboard'))

    # make sure the doctor isn't already booked elsewhere at the new date/time
    cursor.execute("""
        SELECT appointment_id FROM appointments
        WHERE doctor_id=%s AND appointment_date=%s AND appointment_time=%s
              AND appointment_id != %s AND status NOT IN ('Declined', 'Completed', 'Cancelled')
    """, (session['doctor_id'], new_date, new_time, appointment_id))
    clash = cursor.fetchone()

    if clash:
        cursor.close()
        connection.close()
        flash("You already have another appointment at that new date/time. Please pick a different slot.")
        return redirect(url_for('doctor_dashboard'))

    try:
        if reason:
            cursor.execute("""
                UPDATE appointments
                SET appointment_date=%s, appointment_time=%s, status='Rescheduled', feedback=%s
                WHERE appointment_id=%s
            """, (new_date, new_time, reason, appointment_id))
        else:
            cursor.execute("""
                UPDATE appointments
                SET appointment_date=%s, appointment_time=%s, status='Rescheduled'
                WHERE appointment_id=%s
            """, (new_date, new_time, appointment_id))

        connection.commit()

    except (pymysql.err.IntegrityError, pymysql.err.OperationalError):
        cursor.close()
        connection.close()
        flash("That new date/time was just taken by another appointment. Please pick a different slot.")
        return redirect(url_for('doctor_dashboard'))

    reschedule_message = (
        f"Dr. {appt['doc_first']} {appt['doc_last']} rescheduled your appointment "
        f"from {appt['appointment_date']} {format_time_hhmm(appt['appointment_time'])} to {new_date} {new_time}."
    )
    if reason:
        reschedule_message += f" Reason: {reason}"

    add_notification(connection, appt['patient_id'], reschedule_message)

    log_audit(connection, 'doctor', session['doctor_id'], 'appointment_rescheduled',
               f"Appointment #{appointment_id} rescheduled to {new_date} {new_time}.")

    cursor.close()
    connection.close()

    return redirect(url_for('doctor_dashboard'))


def get_effective_feedback(cursor, appointment_id, raw_feedback):
    """Works out what should actually be shown as 'Doctor's Feedback' for a
    completed appointment:
      1. If a follow-up was booked off this appointment -> its date/time
      2. Else if this appointment led to a referral -> who it went to
      3. Else -> whatever note the doctor added when marking it Completed
    """
    cursor.execute(
        "SELECT appointment_date, appointment_time FROM appointments WHERE follow_up_of_appointment_id=%s LIMIT 1",
        (appointment_id,)
    )
    followup = cursor.fetchone()
    if followup:
        return f"Follow-up scheduled on {followup['appointment_date']} at {format_time_hhmm(followup['appointment_time'])}"

    cursor.execute("""
        SELECT r.reason, d.firstname, d.surname
        FROM referrals r JOIN doctors d ON r.referred_to_doctor_id = d.doctor_id
        WHERE r.appointment_id=%s LIMIT 1
    """, (appointment_id,))
    referral = cursor.fetchone()
    if referral:
        return f"Referred to Dr. {referral['firstname']} {referral['surname']} - {referral['reason']}"

    return raw_feedback


def _appointment_datetime(appointment_date, appointment_time):
    """Combines a DB DATE + TIME value into one datetime, so we can check
    how far away an appointment is (used for the patient's 6-hour cutoff)."""
    return datetime.strptime(f"{appointment_date} {format_time_hhmm(appointment_time)}", "%Y-%m-%d %H:%M")


# ================= PATIENT: RESCHEDULE OWN APPOINTMENT =================
@app.route('/patient/reschedule/<int:appointment_id>', methods=['POST'])
def patient_reschedule_appointment(appointment_id):

    if 'patient_id' not in session:
        return redirect(url_for('patient_login'))

    new_date = request.form['new_date']
    new_time = request.form['new_time']
    reason = request.form.get('reason', '').strip()

    if not reason:
        flash("Please give a reason for rescheduling.")
        return redirect(url_for('my_appointments'))

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT patient_id, doctor_id, appointment_date, appointment_time, status
        FROM appointments WHERE appointment_id=%s
    """, (appointment_id,))
    appt = cursor.fetchone()

    if not appt or appt['patient_id'] != session['patient_id']:
        cursor.close()
        connection.close()
        return redirect(url_for('my_appointments'))

    if appt['status'] in ('Declined', 'Completed', 'Cancelled'):
        cursor.close()
        connection.close()
        flash("This appointment can no longer be rescheduled.")
        return redirect(url_for('my_appointments'))

    # ---- must be at least 6 hours before the CURRENTLY booked date/time ----
    current_appointment_dt = _appointment_datetime(appt['appointment_date'], appt['appointment_time'])
    if datetime.now() > current_appointment_dt - timedelta(hours=6):
        cursor.close()
        connection.close()
        flash("Appointments can only be rescheduled at least 6 hours before the booked time.")
        return redirect(url_for('my_appointments'))

    # ---- the new slot must also be at least 1 hour from now ----
    try:
        chosen_datetime = datetime.strptime(new_date + " " + new_time, "%Y-%m-%d %H:%M")
    except ValueError:
        cursor.close()
        connection.close()
        flash("Invalid date or time selected.")
        return redirect(url_for('my_appointments'))

    if chosen_datetime < datetime.now() + timedelta(hours=1):
        cursor.close()
        connection.close()
        flash("That time has already passed or is too soon. Please choose a time at least 1 hour ahead.")
        return redirect(url_for('my_appointments'))

    # ---- make sure the doctor isn't already booked at the new date/time ----
    cursor.execute("""
        SELECT appointment_id FROM appointments
        WHERE doctor_id=%s AND appointment_date=%s AND appointment_time=%s
              AND appointment_id != %s AND status NOT IN ('Declined', 'Completed', 'Cancelled')
    """, (appt['doctor_id'], new_date, new_time, appointment_id))
    clash = cursor.fetchone()

    if clash:
        cursor.close()
        connection.close()
        flash("The doctor already has another appointment at that new date/time. Please pick a different slot.")
        return redirect(url_for('my_appointments'))

    try:
        cursor.execute("""
            UPDATE appointments
            SET appointment_date=%s, appointment_time=%s, status='Rescheduled'
            WHERE appointment_id=%s
        """, (new_date, new_time, appointment_id))
        connection.commit()
    except (pymysql.err.IntegrityError, pymysql.err.OperationalError):
        cursor.close()
        connection.close()
        flash("That new date/time was just taken by another appointment. Please pick a different slot.")
        return redirect(url_for('my_appointments'))

    log_audit(connection, 'patient', session['patient_id'], 'patient_rescheduled_appointment',
               f"Appointment #{appointment_id} rescheduled by patient to {new_date} {new_time}. Reason: {reason}")

    cursor.close()
    connection.close()

    flash("Your appointment has been rescheduled and sent back to the doctor for confirmation.")
    return redirect(url_for('my_appointments'))


# ================= PATIENT: CANCEL OWN APPOINTMENT =================
@app.route('/patient/cancel/<int:appointment_id>', methods=['POST'])
def patient_cancel_appointment(appointment_id):

    if 'patient_id' not in session:
        return redirect(url_for('patient_login'))

    reason = request.form.get('reason', '').strip()

    if not reason:
        flash("Please give a reason for cancelling.")
        return redirect(url_for('my_appointments'))

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT patient_id, doctor_id, appointment_date, appointment_time, status
        FROM appointments WHERE appointment_id=%s
    """, (appointment_id,))
    appt = cursor.fetchone()

    if not appt or appt['patient_id'] != session['patient_id']:
        cursor.close()
        connection.close()
        return redirect(url_for('my_appointments'))

    if appt['status'] in ('Declined', 'Completed', 'Cancelled'):
        cursor.close()
        connection.close()
        flash("This appointment can no longer be cancelled.")
        return redirect(url_for('my_appointments'))

    # ---- must be at least 6 hours before the booked date/time ----
    current_appointment_dt = _appointment_datetime(appt['appointment_date'], appt['appointment_time'])
    if datetime.now() > current_appointment_dt - timedelta(hours=6):
        cursor.close()
        connection.close()
        flash("Appointments can only be cancelled at least 6 hours before the booked time.")
        return redirect(url_for('my_appointments'))

    cursor.execute("""
        UPDATE appointments SET status='Cancelled', feedback=%s WHERE appointment_id=%s
    """, (f"Cancelled by patient. Reason: {reason}", appointment_id))
    connection.commit()

    log_audit(connection, 'patient', session['patient_id'], 'patient_cancelled_appointment',
               f"Appointment #{appointment_id} cancelled by patient. Reason: {reason}")

    cursor.close()
    connection.close()

    flash("Your appointment has been cancelled.")
    return redirect(url_for('my_appointments'))


# ================= PATIENT: DELETE NOTIFICATION =================
@app.route('/delete_notification/<int:notification_id>')
def delete_notification(notification_id):

    if 'patient_id' not in session:
        return redirect(url_for('patient_login'))

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='medical_referral'
    )
    cursor = connection.cursor()

    # only delete it if it actually belongs to this patient
    cursor.execute(
        "DELETE FROM notifications WHERE notification_id=%s AND patient_id=%s",
        (notification_id, session['patient_id'])
    )

    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for('my_appointments'))


# ================= DOCTOR: BOOK FOLLOW-UP APPOINTMENT =================
@app.route('/book_followup/<int:appointment_id>', methods=['POST'])
def book_followup(appointment_id):

    if 'doctor_id' not in session:
        return redirect(url_for('doctor_login'))

    followup_date = request.form['followup_date']
    followup_time = request.form['followup_time']
    followup_reason = request.form.get('followup_reason') or 'Follow-up appointment'

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # make sure this completed appointment belongs to the logged-in doctor
    cursor.execute("""
        SELECT a.patient_id, a.doctor_id, d.firstname AS doc_first, d.surname AS doc_last
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE a.appointment_id = %s AND a.status = 'Completed'
    """, (appointment_id,))
    appt = cursor.fetchone()

    if not appt or appt['doctor_id'] != session['doctor_id']:
        cursor.close()
        connection.close()
        return redirect(url_for('doctor_dashboard'))

    # NEW: the follow-up date/time cannot be in the past (must be at least 1 hour from now)
    try:
        chosen_datetime = datetime.strptime(followup_date + " " + followup_time, "%Y-%m-%d %H:%M")
    except ValueError:
        cursor.close()
        connection.close()
        flash("Invalid date or time selected.")
        return redirect(url_for('doctor_dashboard'))

    if chosen_datetime < datetime.now() + timedelta(hours=1):
        cursor.close()
        connection.close()
        flash("That time has already passed or is too soon. Please choose a follow-up date and time at least 1 hour ahead.")
        return redirect(url_for('doctor_dashboard'))

    # make sure the doctor isn't already booked at that date/time
    cursor.execute("""
        SELECT appointment_id FROM appointments
        WHERE doctor_id=%s AND appointment_date=%s AND appointment_time=%s AND status NOT IN ('Declined', 'Completed', 'Cancelled')
    """, (appt['doctor_id'], followup_date, followup_time))
    clash = cursor.fetchone()

    if clash:
        cursor.close()
        connection.close()
        flash("You already have another appointment at that date/time. Please pick a different slot.")
        return redirect(url_for('doctor_dashboard'))

    try:
        cursor.execute("""
            INSERT INTO appointments (patient_id, doctor_id, reason, appointment_date, appointment_time, follow_up_of_appointment_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (appt['patient_id'], appt['doctor_id'], followup_reason, followup_date, followup_time, appointment_id))

        connection.commit()

    except (pymysql.err.IntegrityError, pymysql.err.OperationalError):
        cursor.close()
        connection.close()
        flash("That date/time was just taken by another appointment. Please pick a different slot.")
        return redirect(url_for('doctor_dashboard'))

    add_notification(
        connection,
        appt['patient_id'],
        f"Dr. {appt['doc_first']} {appt['doc_last']} has set up a follow-up appointment for you "
        f"on {followup_date} at {followup_time}."
    )

    cursor.close()
    connection.close()

    return redirect(url_for('doctor_dashboard'))


# =====================================================================
# ============================ ADMIN SECTION =========================
# =====================================================================

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='medical_referral'
        )
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        cursor.execute(
            "SELECT * FROM admins WHERE email=%s AND password=%s",
            (email, password)
        )
        admin = cursor.fetchone()

        if admin:
            session['admin_id'] = admin['admin_id']
            session['admin_name'] = admin['username']
            log_audit(connection, 'admin', admin['admin_id'], 'admin_login', f"Admin '{admin['username']}' logged in.")
            cursor.close()
            connection.close()
            return redirect(url_for('admin_dashboard'))
        else:
            log_audit(connection, 'admin', None, 'failed_login', f"Failed admin login attempt for email: {email}")
            cursor.close()
            connection.close()
            return render_template("admin_login.html", error="Invalid email or password.")

    return render_template("admin_login.html")


@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    return redirect(url_for('admin_login'))


# ================= ADMIN DASHBOARD =================
@app.route('/admin_dashboard')
def admin_dashboard():

    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # ---- headline numbers ----
    cursor.execute("SELECT COUNT(*) AS c FROM doctors")
    doctor_count = cursor.fetchone()['c']

    cursor.execute("SELECT COUNT(*) AS c FROM patients")
    patient_count = cursor.fetchone()['c']

    cursor.execute("SELECT COUNT(*) AS c FROM appointments")
    appointment_count = cursor.fetchone()['c']

    cursor.execute("SELECT COUNT(*) AS c FROM referrals")
    referral_count = cursor.fetchone()['c']

    # ---- doctor list, so admin can remove a doctor ----
    cursor.execute("SELECT doctor_id, firstname, surname, email, speciality, county FROM doctors ORDER BY firstname ASC")
    doctors = cursor.fetchall()

    # ---- recent activity across the whole system ----
    cursor.execute("SELECT * FROM audit_log ORDER BY created_at DESC LIMIT 100")
    logs = cursor.fetchall()

    # ---- flag "bad behaviour": emails with 3+ failed logins in the log window we just pulled ----
    failed_attempts = {}
    for row in logs:
        if row['action'] == 'failed_login' and row['details']:
            key = row['details'].split(':')[-1].strip()
            failed_attempts[key] = failed_attempts.get(key, 0) + 1
    suspicious_emails = [email for email, count in failed_attempts.items() if count >= 3]

    cursor.close()
    connection.close()

    return render_template(
        "admin_dashboard.html",
        doctor_count=doctor_count,
        patient_count=patient_count,
        appointment_count=appointment_count,
        referral_count=referral_count,
        doctors=doctors,
        logs=logs,
        suspicious_emails=suspicious_emails
    )


# ================= ADMIN: DOCTORS LIST =================
@app.route('/admin/doctors')
def admin_doctors():

    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    connection = pymysql.connect(
        host='localhost', user='root', password='', database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT doctor_id, firstname, surname, email, speciality, county, business_phone
        FROM doctors ORDER BY firstname ASC
    """)
    doctors = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("admin_doctors.html", doctors=doctors)


# ================= ADMIN: DOCTORS LIST (PDF DOWNLOAD) =================
@app.route('/admin/doctors/pdf')
def admin_doctors_pdf():

    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    connection = pymysql.connect(
        host='localhost', user='root', password='', database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT doctor_id, firstname, surname, email, speciality, county, business_phone
        FROM doctors ORDER BY firstname ASC
    """)
    rows = cursor.fetchall()

    headers = ["ID", "Name", "Speciality", "County", "Email", "Phone"]
    data_rows = [
        [r['doctor_id'], f"Dr. {r['firstname']} {r['surname']}", r['speciality'], r['county'], r['email'], r['business_phone']]
        for r in rows
    ]

    # ---- NEW: classify the doctors by speciality (same speciality together, A-Z) ----
    grouped = {}
    for r in rows:
        key = (r['speciality'] or '').strip() or 'Not specified'
        grouped.setdefault(key, []).append(
            [r['doctor_id'], f"Dr. {r['firstname']} {r['surname']}", r['county'], r['email'], r['business_phone']]
        )
    grouped_rows = sorted(grouped.items(), key=lambda item: item[0].lower())

    buffer = _build_grouped_table_report_pdf(
        "All Doctors Report (Classified by Speciality)",
        f"Total doctors in system: {len(rows)} | Specialities: {len(grouped_rows)}",
        ["ID", "Name", "County", "Email", "Phone"],
        grouped_rows,
        col_widths=[20 * mm, 70 * mm, 50 * mm, 80 * mm, 40 * mm]
    )

    # ---- ORIGINAL (unclassified) report, kept for reference ----
    # buffer = _build_table_report_pdf(
    #     "All Doctors Report",
    #     f"Total doctors in system: {len(rows)}",
    #     headers,
    #     data_rows,
    #     wide=True,
    #     col_widths=[15 * mm, 55 * mm, 45 * mm, 40 * mm, 60 * mm, 30 * mm]
    # )

    log_audit(connection, 'admin', session['admin_id'], 'admin_generated_doctors_report',
               "All-doctors report generated.")

    cursor.close()
    connection.close()

    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name="all_doctors_report.pdf"
    )


# ================= ADMIN: PATIENTS LIST =================
@app.route('/admin/patients')
def admin_patients():

    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    connection = pymysql.connect(
        host='localhost', user='root', password='', database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT patient_id, firstname, lastname, email, phone, county, dob
        FROM patients ORDER BY firstname ASC
    """)
    patients = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("admin_patients.html", patients=patients)


# ================= ADMIN: REFERRALS LIST =================
@app.route('/admin/referrals')
def admin_referrals():

    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    connection = pymysql.connect(
        host='localhost', user='root', password='', database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT r.*, p.firstname AS pat_first, p.lastname AS pat_last,
               d1.firstname AS from_first, d1.surname AS from_last,
               d2.firstname AS to_first, d2.surname AS to_last,
               ra.appointment_date AS scheduled_date, ra.appointment_time AS scheduled_time
        FROM referrals r
        JOIN patients p ON r.patient_id = p.patient_id
        JOIN doctors d1 ON r.referring_doctor_id = d1.doctor_id
        JOIN doctors d2 ON r.referred_to_doctor_id = d2.doctor_id
        LEFT JOIN appointments ra ON r.resulting_appointment_id = ra.appointment_id
        ORDER BY r.created_at DESC
    """)
    referrals = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("admin_referrals.html", referrals=referrals)


# ================= ADMIN: REFERRALS LIST (PDF DOWNLOAD) =================
@app.route('/admin/referrals/pdf')
def admin_referrals_pdf():

    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    connection = pymysql.connect(
        host='localhost', user='root', password='', database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT r.*, p.firstname AS pat_first, p.lastname AS pat_last,
               d1.firstname AS from_first, d1.surname AS from_last,
               d2.firstname AS to_first, d2.surname AS to_last
        FROM referrals r
        JOIN patients p ON r.patient_id = p.patient_id
        JOIN doctors d1 ON r.referring_doctor_id = d1.doctor_id
        JOIN doctors d2 ON r.referred_to_doctor_id = d2.doctor_id
        ORDER BY r.created_at DESC
    """)
    rows = cursor.fetchall()

    headers = ["ID", "Patient", "Referred By", "Referred To", "Reason", "Status", "Created"]
    data_rows = [
        [
            r['referral_id'],
            f"{r['pat_first']} {r['pat_last']}",
            f"Dr. {r['from_first']} {r['from_last']}",
            f"Dr. {r['to_first']} {r['to_last']}",
            r['reason'],
            r['status'],
            r['created_at'],
        ]
        for r in rows
    ]

    buffer = _build_table_report_pdf(
        "All Referrals Report",
        f"Total referrals in system: {len(rows)}",
        headers,
        data_rows,
        wide=True,
        col_widths=[12 * mm, 35 * mm, 40 * mm, 40 * mm, 80 * mm, 25 * mm, 35 * mm]
    )

    log_audit(connection, 'admin', session['admin_id'], 'admin_generated_referrals_report',
               "All-referrals report generated.")

    cursor.close()
    connection.close()

    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name="all_referrals_report.pdf"
    )


# ================= ADMIN: REMOVE A DOCTOR =================
@app.route('/admin/remove_doctor/<int:doctor_id>', methods=['POST'])
def admin_remove_doctor(doctor_id):

    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT firstname, surname, email FROM doctors WHERE doctor_id=%s", (doctor_id,))
    doctor = cursor.fetchone()

    if doctor:
        # ON DELETE CASCADE on appointments/referrals takes care of related rows
        cursor.execute("DELETE FROM doctors WHERE doctor_id=%s", (doctor_id,))
        connection.commit()

        log_audit(
            connection, 'admin', session['admin_id'], 'doctor_removed',
            f"Admin '{session.get('admin_name')}' removed Dr. {doctor['firstname']} {doctor['surname']} ({doctor['email']})."
        )

    cursor.close()
    connection.close()

    flash("Doctor removed from the system.")
    return redirect(url_for('admin_dashboard'))


# ================= ADMIN: DELETE A PATIENT =================
@app.route('/admin/delete_patient/<int:patient_id>', methods=['POST'])
def admin_delete_patient(patient_id):

    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    connection = pymysql.connect(
        host='localhost', user='root', password='', database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT firstname, lastname, email FROM patients WHERE patient_id=%s", (patient_id,))
    patient = cursor.fetchone()

    if patient:
        # ON DELETE CASCADE on appointments/referrals/notifications takes care of related rows
        cursor.execute("DELETE FROM patients WHERE patient_id=%s", (patient_id,))
        connection.commit()

        log_audit(
            connection, 'admin', session['admin_id'], 'patient_removed',
            f"Admin '{session.get('admin_name')}' removed patient {patient['firstname']} {patient['lastname']} ({patient['email']})."
        )

    cursor.close()
    connection.close()

    flash("Patient removed from the system.")
    return redirect(url_for('admin_patients'))


# ================= ADMIN: DELETE AN APPOINTMENT =================
@app.route('/admin/delete_appointment/<int:appointment_id>', methods=['POST'])
def admin_delete_appointment(appointment_id):

    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    connection = pymysql.connect(
        host='localhost', user='root', password='', database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT appointment_id FROM appointments WHERE appointment_id=%s", (appointment_id,))
    appt = cursor.fetchone()

    if appt:
        # referrals.appointment_id is ON DELETE SET NULL, so referral history is preserved
        cursor.execute("DELETE FROM appointments WHERE appointment_id=%s", (appointment_id,))
        connection.commit()

        log_audit(
            connection, 'admin', session['admin_id'], 'appointment_removed',
            f"Admin '{session.get('admin_name')}' removed appointment #{appointment_id}."
        )

    cursor.close()
    connection.close()

    flash("Appointment removed from the system.")
    return redirect(request.referrer or url_for('admin_appointments_report'))


# ================= ADMIN: DELETE A REFERRAL =================
@app.route('/admin/delete_referral/<int:referral_id>', methods=['POST'])
def admin_delete_referral(referral_id):

    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    connection = pymysql.connect(
        host='localhost', user='root', password='', database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT referral_id FROM referrals WHERE referral_id=%s", (referral_id,))
    referral = cursor.fetchone()

    if referral:
        cursor.execute("DELETE FROM referrals WHERE referral_id=%s", (referral_id,))
        connection.commit()

        log_audit(
            connection, 'admin', session['admin_id'], 'referral_removed',
            f"Admin '{session.get('admin_name')}' removed referral #{referral_id}."
        )

    cursor.close()
    connection.close()

    flash("Referral removed from the system.")
    return redirect(url_for('admin_referrals'))


# ================= ADMIN: APPOINTMENTS REPORT (DATE RANGE, TABLE VIEW) =================
@app.route('/admin/appointments_report')
def admin_appointments_report():

    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    patient_id = request.args.get('patient_id', '')

    report_rows = []
    patients = []
    if start_date and end_date:
        connection = pymysql.connect(
            host='localhost', user='root', password='', database='medical_referral'
        )
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        query = """
            SELECT a.appointment_id, p.firstname AS pat_first, p.lastname AS pat_last,
                   d.firstname AS doc_first, d.surname AS doc_last,
                   a.appointment_date, a.appointment_time, a.status, a.reason
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.appointment_date BETWEEN %s AND %s
        """
        params = [start_date, end_date]

        if patient_id:
            query += " AND a.patient_id = %s"
            params.append(patient_id)

        query += " ORDER BY a.appointment_date ASC, a.appointment_time ASC"

        cursor.execute(query, params)
        report_rows = cursor.fetchall()

        cursor.close()
        connection.close()

    # ---- patient list for the "specific patient" dropdown ----
    connection = pymysql.connect(
        host='localhost', user='root', password='', database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT patient_id, firstname, lastname FROM patients ORDER BY firstname ASC")
    patients = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template(
        "admin_appointments_report.html",
        report_rows=report_rows,
        start_date=start_date,
        end_date=end_date,
        patient_id=patient_id,
        patients=patients
    )


# ================= ADMIN: APPOINTMENTS REPORT (PDF DOWNLOAD) =================
@app.route('/admin/appointments_report/pdf')
def admin_appointments_report_pdf():

    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    patient_id = request.args.get('patient_id', '')

    connection = pymysql.connect(
        host='localhost', user='root', password='', database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    query = """
        SELECT a.appointment_id, p.firstname AS pat_first, p.lastname AS pat_last,
               d.firstname AS doc_first, d.surname AS doc_last,
               a.appointment_date, a.appointment_time, a.status, a.reason
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE a.appointment_date BETWEEN %s AND %s
    """
    params = [start_date, end_date]

    if patient_id:
        query += " AND a.patient_id = %s"
        params.append(patient_id)

    query += " ORDER BY a.appointment_date ASC, a.appointment_time ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    headers = ["ID", "Patient", "Doctor", "Date", "Time", "Status", "Reason for Consultation"]
    data_rows = [
        [
            r['appointment_id'],
            f"{r['pat_first']} {r['pat_last']}",
            f"Dr. {r['doc_first']} {r['doc_last']}",
            r['appointment_date'],
            format_time_hhmm(r['appointment_time']),
            r['status'],
            r['reason'],
        ]
        for r in rows
    ]

    subtitle = f"Date range: {start_date} to {end_date}"
    if patient_id and rows:
        subtitle = f"Patient: {rows[0]['pat_first']} {rows[0]['pat_last']} | " + subtitle
    download_name_suffix = f"patient_{patient_id}_" if patient_id else ""

    buffer = _build_table_report_pdf(
        "Appointments Report",
        subtitle,
        headers,
        data_rows,
        wide=True,
        col_widths=[15 * mm, 35 * mm, 40 * mm, 22 * mm, 18 * mm, 25 * mm, 90 * mm]
    )

    log_audit(connection, 'admin', session['admin_id'], 'admin_generated_appointments_report',
               f"Appointments report generated for {start_date} to {end_date}."
               + (f" (patient #{patient_id})" if patient_id else ""))

    cursor.close()
    connection.close()

    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"appointments_report_{download_name_suffix}{start_date}_to_{end_date}.pdf"
    )


# ================= ADMIN: SINGLE APPOINTMENT REPORT (INDIVIDUAL PDF) =================
@app.route('/admin/report/<int:appointment_id>')
def admin_appointment_report_pdf(appointment_id):

    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    connection = pymysql.connect(
        host='localhost', user='root', password='', database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT a.*, d.firstname AS doc_first, d.surname AS doc_last, d.speciality,
               p.firstname AS pat_first, p.lastname AS pat_last, p.email AS pat_email, p.county AS pat_county
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        JOIN patients p ON a.patient_id = p.patient_id
        WHERE a.appointment_id=%s
    """, (appointment_id,))
    a = cursor.fetchone()

    if not a:
        cursor.close()
        connection.close()
        flash("Appointment not found.")
        return redirect(url_for('admin_appointments_report'))

    if a['status'] == 'Completed':
        effective_feedback = get_effective_feedback(cursor, appointment_id, a['feedback'])
    else:
        effective_feedback = a['feedback'] or '-'

    # ---- was this booking referred on to another doctor? ----
    cursor.execute("""
        SELECT d.firstname, d.surname, r.reason, r.status
        FROM referrals r JOIN doctors d ON r.referred_to_doctor_id = d.doctor_id
        WHERE r.appointment_id=%s LIMIT 1
    """, (appointment_id,))
    referral_info = cursor.fetchone()

    rows = [
        ("Appointment ID", a['appointment_id']),
        ("Patient", f"{a['pat_first']} {a['pat_last']}"),
        ("Patient Email", a['pat_email']),
        ("Patient County", a['pat_county']),
        ("Doctor", f"Dr. {a['doc_first']} {a['doc_last']}"),
        ("Speciality", a['speciality']),
        ("Reason for Visit", a['reason']),
        ("Date", a['appointment_date']),
        ("Time", format_time_hhmm(a['appointment_time'])),
        ("Status", a['status']),
        ("Feedback / Notes", effective_feedback),
    ]

    if referral_info:
        rows.append((
            "Referred To",
            f"Dr. {referral_info['firstname']} {referral_info['surname']} "
            f"({referral_info['status']}) - {referral_info['reason']}"
        ))

    buffer = _build_appointment_report_pdf("Admin Appointment Report", rows)

    log_audit(connection, 'admin', session['admin_id'], 'admin_generated_appointment_report',
               f"Individual appointment report generated for appointment #{appointment_id}.")

    cursor.close()
    connection.close()

    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"appointment_report_{appointment_id}.pdf"
    )


# ================= ADMIN: ALL PATIENTS REPORT (PDF DOWNLOAD) =================
@app.route('/admin/patients_report/pdf')
def admin_patients_report_pdf():

    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    connection = pymysql.connect(
        host='localhost', user='root', password='', database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT patient_id, firstname, lastname, email, phone, county, dob
        FROM patients ORDER BY firstname ASC
    """)
    rows = cursor.fetchall()

    headers = ["ID", "Name", "Email", "Phone", "County", "Date of Birth"]
    data_rows = [
        [r['patient_id'], f"{r['firstname']} {r['lastname']}", r['email'], r['phone'], r['county'], r['dob']]
        for r in rows
    ]

    buffer = _build_table_report_pdf(
        "All Patients Report",
        f"Total patients in system: {len(rows)}",
        headers,
        data_rows,
        wide=True,
        col_widths=[15 * mm, 50 * mm, 60 * mm, 35 * mm, 40 * mm, 35 * mm]
    )

    log_audit(connection, 'admin', session['admin_id'], 'admin_generated_patients_report',
               "All-patients report generated.")

    cursor.close()
    connection.close()

    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name="all_patients_report.pdf"
    )


# =====================================================================
# ========================= REFERRAL PLATFORM ========================
# =====================================================================

# ================= DOCTOR: REFER A PATIENT TO ANOTHER DOCTOR =================
@app.route('/refer_patient/<int:appointment_id>', methods=['POST'])
def refer_patient(appointment_id):

    if 'doctor_id' not in session:
        return redirect(url_for('doctor_login'))

    referred_to_doctor_id = request.form['referred_to_doctor_id']
    reason = request.form['referral_reason']

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # make sure this appointment (and patient) belongs to the referring doctor
    cursor.execute("""
        SELECT a.patient_id, a.doctor_id, a.status, d.firstname AS doc_first, d.surname AS doc_last
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE a.appointment_id = %s
    """, (appointment_id,))
    appt = cursor.fetchone()

    if not appt or appt['doctor_id'] != session['doctor_id']:
        cursor.close()
        connection.close()
        return redirect(url_for('doctor_dashboard'))

    if appt['status'] != 'Completed':
        cursor.close()
        connection.close()
        flash("Please mark this appointment as Completed before referring the patient.")
        return redirect(url_for('doctor_dashboard'))

    if int(referred_to_doctor_id) == session['doctor_id']:
        cursor.close()
        connection.close()
        flash("You cannot refer a patient to yourself.")
        return redirect(url_for('doctor_dashboard'))

    # ---- THIS doctor must not have already referred this same patient before
    #      (a different doctor - e.g. one who received the patient via a
    #      referral - is still allowed to refer them onward) ----
    cursor.execute(
        "SELECT referral_id FROM referrals WHERE patient_id=%s AND referring_doctor_id=%s",
        (appt['patient_id'], session['doctor_id'])
    )
    already_referred = cursor.fetchone()

    if already_referred:
        cursor.close()
        connection.close()
        flash("You have already referred this patient.")
        return redirect(url_for('doctor_dashboard'))

    cursor.execute("SELECT firstname, surname FROM doctors WHERE doctor_id=%s", (referred_to_doctor_id,))
    target_doctor = cursor.fetchone()

    cursor.execute("""
        INSERT INTO referrals (patient_id, referring_doctor_id, referred_to_doctor_id, appointment_id, reason)
        VALUES (%s, %s, %s, %s, %s)
    """, (appt['patient_id'], session['doctor_id'], referred_to_doctor_id, appointment_id, reason))

    connection.commit()

    add_notification(
        connection, appt['patient_id'],
        f"Dr. {appt['doc_first']} {appt['doc_last']} has referred you to "
        f"Dr. {target_doctor['firstname']} {target_doctor['surname']}. Reason: {reason}. "
        f"Please book an appointment with Dr. {target_doctor['firstname']} {target_doctor['surname']} to continue your consultation."
    )

    log_audit(connection, 'doctor', session['doctor_id'], 'referral_created',
               f"Referred patient #{appt['patient_id']} to doctor #{referred_to_doctor_id}. Reason: {reason}")

    cursor.close()
    connection.close()

    flash("Referral sent successfully.")
    return redirect(url_for('doctor_dashboard'))


# ================= DOCTOR: ACCEPT / DECLINE AN INCOMING REFERRAL =================
@app.route('/referral/<int:referral_id>/<string:decision>', methods=['POST'])
def respond_to_referral(referral_id, decision):

    if 'doctor_id' not in session:
        return redirect(url_for('doctor_login'))

    if decision not in ('Accepted', 'Declined'):
        return redirect(url_for('doctor_dashboard'))

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT r.patient_id, r.referred_to_doctor_id, d.firstname AS ref_first, d.surname AS ref_last
        FROM referrals r
        JOIN doctors d ON r.referring_doctor_id = d.doctor_id
        WHERE r.referral_id = %s
    """, (referral_id,))
    referral = cursor.fetchone()

    if not referral or referral['referred_to_doctor_id'] != session['doctor_id']:
        cursor.close()
        connection.close()
        return redirect(url_for('doctor_dashboard'))

    cursor.execute("UPDATE referrals SET status=%s WHERE referral_id=%s", (decision, referral_id))
    connection.commit()

    doctor_name = session.get('doctor_name', 'the specialist')

    if decision == 'Accepted':
        message = (
            f"Dr. {doctor_name} has accepted the referral from Dr. {referral['ref_first']} {referral['ref_last']}. "
            f"You have been referred to Dr. {doctor_name}. They will schedule your appointment shortly."
        )
    else:
        message = (
            f"Dr. {doctor_name} was unable to accept the referral from Dr. {referral['ref_first']} {referral['ref_last']}. "
            f"Please book a fresh appointment with another doctor."
        )

    add_notification(connection, referral['patient_id'], message)

    log_audit(connection, 'doctor', session['doctor_id'], 'referral_' + decision.lower(),
               f"Referral #{referral_id} {decision.lower()}.")

    cursor.close()
    connection.close()

    return redirect(url_for('doctor_dashboard'))


    cursor.close()
    connection.close()

    return redirect(url_for('doctor_dashboard'))


# ================= DOCTOR: SCHEDULE THE REFERRED PATIENT'S APPOINTMENT =================
@app.route('/referral/<int:referral_id>/schedule', methods=['POST'])
def schedule_referral_appointment(referral_id):

    if 'doctor_id' not in session:
        return redirect(url_for('doctor_login'))

    appointment_date = request.form.get('appointment_date', '').strip()
    appointment_time = request.form.get('appointment_time', '').strip()
    note = request.form.get('note', '').strip()

    if not appointment_date or not appointment_time:
        flash("Please choose a date and time for the referred patient.")
        return redirect(url_for('doctor_dashboard'))

    connection = pymysql.connect(
        host='localhost', user='root', password='', database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT r.*, p.firstname AS pat_first, p.lastname AS pat_last
        FROM referrals r JOIN patients p ON r.patient_id = p.patient_id
        WHERE r.referral_id=%s
    """, (referral_id,))
    referral = cursor.fetchone()

    if not referral or referral['referred_to_doctor_id'] != session['doctor_id']:
        cursor.close()
        connection.close()
        return redirect(url_for('doctor_dashboard'))

    if referral['status'] != 'Accepted':
        cursor.close()
        connection.close()
        flash("You can only schedule a referral you've accepted.")
        return redirect(url_for('doctor_dashboard'))

    if referral['resulting_appointment_id']:
        cursor.close()
        connection.close()
        flash("An appointment has already been scheduled for this referral.")
        return redirect(url_for('doctor_dashboard'))

    # ---- must be at least 1 hour from now ----
    try:
        chosen_datetime = datetime.strptime(appointment_date + " " + appointment_time, "%Y-%m-%d %H:%M")
    except ValueError:
        cursor.close()
        connection.close()
        flash("Invalid date or time selected.")
        return redirect(url_for('doctor_dashboard'))

    if chosen_datetime < datetime.now() + timedelta(hours=1):
        cursor.close()
        connection.close()
        flash("Please choose a date/time at least 1 hour from now.")
        return redirect(url_for('doctor_dashboard'))

    # ---- make sure this doctor isn't already booked at that date/time ----
    cursor.execute("""
        SELECT appointment_id FROM appointments
        WHERE doctor_id=%s AND appointment_date=%s AND appointment_time=%s AND status NOT IN ('Declined', 'Completed', 'Cancelled')
    """, (session['doctor_id'], appointment_date, appointment_time))
    clash = cursor.fetchone()

    if clash:
        cursor.close()
        connection.close()
        flash("You already have another appointment at that date/time. Please pick a different slot.")
        return redirect(url_for('doctor_dashboard'))

    reason_text = note if note else f"Referral consultation - {referral['reason']}"

    try:
        cursor.execute("""
            INSERT INTO appointments (patient_id, doctor_id, reason, appointment_date, appointment_time, status)
            VALUES (%s, %s, %s, %s, %s, 'Confirmed')
        """, (referral['patient_id'], session['doctor_id'], reason_text, appointment_date, appointment_time))
        connection.commit()
        new_appointment_id = cursor.lastrowid
    except (pymysql.err.IntegrityError, pymysql.err.OperationalError):
        cursor.close()
        connection.close()
        flash("That date/time was just taken by another appointment. Please pick a different slot.")
        return redirect(url_for('doctor_dashboard'))

    cursor.execute(
        "UPDATE referrals SET resulting_appointment_id=%s WHERE referral_id=%s",
        (new_appointment_id, referral_id)
    )
    connection.commit()

    doctor_name = session.get('doctor_name', 'the specialist')
    add_notification(
        connection, referral['patient_id'],
        f"Dr. {doctor_name} has scheduled your referred appointment for {appointment_date} at {appointment_time}."
    )

    log_audit(connection, 'doctor', session['doctor_id'], 'referral_scheduled',
               f"Referral #{referral_id} scheduled as appointment #{new_appointment_id} on {appointment_date} at {appointment_time}.")

    cursor.close()
    connection.close()

    flash("Appointment scheduled for the referred patient.")
    return redirect(url_for('doctor_dashboard'))


# =====================================================================
# ===================== DOWNLOADABLE PDF REPORTS =====================
# =====================================================================

def _build_table_report_pdf(title, subtitle, headers, data_rows, wide=False, col_widths=None):
    """Builds a multi-row, multi-page PDF table (used by the Admin section's
    Appointments and Patients reports, and the Doctor's full patient-records
    report) and returns it as a BytesIO buffer. Pass wide=True for reports
    with many columns to render in landscape orientation."""
    buffer = io.BytesIO()
    pagesize = landscape(A4) if wide else A4
    doc = SimpleDocTemplate(buffer, pagesize=pagesize, topMargin=15 * mm, bottomMargin=15 * mm,
                             leftMargin=12 * mm, rightMargin=12 * mm)
    styles = getSampleStyleSheet()
    cell_style = styles['Normal']
    cell_style.fontSize = 8
    cell_style.leading = 10

    elements = [
        # ORIGINAL heading (kept for reference):
        # Paragraph("Medical Specialist Consultation and Referral System", styles['Title']),
        # NEW: DOCCONNECT heading, aligned to the top-left of the page
        Paragraph("DOCCONNECT", ParagraphStyle('DocConnectHeading', parent=styles['Title'], alignment=0)),
        Paragraph(title, styles['Heading2']),
    ]
    if subtitle:
        elements.append(Paragraph(subtitle, styles['Normal']))
    elements.append(Spacer(1, 8 * mm))

    # ---- wrap long text cells (feedback, reasons) in Paragraphs so they don't overflow the page ----
    def _cell(value):
        text = str(value) if value not in (None, '') else '-'
        return Paragraph(text, cell_style) if wide else text

    table_data = [list(headers)] + [[_cell(cell) for cell in row] for row in data_rows]

    table = Table(table_data, repeatRows=1, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#146C6A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5FAF9')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(table)

    elements.append(Spacer(1, 10 * mm))
    elements.append(Paragraph(f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    elements.append(Paragraph(f"Total records: {len(data_rows)}", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def _build_grouped_table_report_pdf(title, subtitle, headers, grouped_rows, col_widths=None, group_label="Speciality"):
    """NEW: Builds a landscape PDF where the records are classified into sections,
    one section per group (e.g. one per medical speciality). `grouped_rows` is a
    list of (group_name, data_rows) tuples, already in the order they should
    appear. Each section gets its own heading, record count and table, and the
    report ends with a summary of how many records each group has.
    Returns a BytesIO buffer, ready for send_file()."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=15 * mm, bottomMargin=15 * mm,
                             leftMargin=12 * mm, rightMargin=12 * mm)
    styles = getSampleStyleSheet()
    cell_style = styles['Normal']
    cell_style.fontSize = 8
    cell_style.leading = 10

    elements = [
        # ORIGINAL heading (kept for reference):
        # Paragraph("Medical Specialist Consultation and Referral System", styles['Title']),
        # NEW: DOCCONNECT heading, aligned to the top-left of the page
        Paragraph("DOCCONNECT", ParagraphStyle('DocConnectHeading', parent=styles['Title'], alignment=0)),
        Paragraph(title, styles['Heading2']),
    ]
    if subtitle:
        elements.append(Paragraph(subtitle, styles['Normal']))
    elements.append(Spacer(1, 6 * mm))

    total_records = 0
    for group_name, data_rows in grouped_rows:
        total_records += len(data_rows)

        # ---- section heading: "Speciality: Cardiology (3 doctors)" ----
        elements.append(Paragraph(
            f"{group_label}: {group_name or 'Not specified'} ({len(data_rows)})",
            styles['Heading3']
        ))

        table_data = [list(headers)] + [
            [Paragraph(str(cell) if cell not in (None, '') else '-', cell_style) for cell in row]
            for row in data_rows
        ]
        table = Table(table_data, repeatRows=1, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#146C6A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5FAF9')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 6 * mm))

    # ---- summary: how many records per group ----
    elements.append(Paragraph("Summary", styles['Heading3']))
    summary_data = [[group_label, "Total"]] + [
        [g or 'Not specified', len(rows_)] for g, rows_ in grouped_rows
    ]
    summary_table = Table(summary_data, colWidths=[80 * mm, 25 * mm], hAlign='LEFT')
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#146C6A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
    ]))
    elements.append(summary_table)

    elements.append(Spacer(1, 8 * mm))
    elements.append(Paragraph(f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    elements.append(Paragraph(f"Total records: {total_records}", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def _build_appointment_report_pdf(title, rows):
    """Builds a simple one-page PDF summary from a list of (label, value)
    rows and returns it as a BytesIO buffer, ready for send_file()."""
    buffer = io.BytesIO()
    doc = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    doc.setFont("Helvetica-Bold", 16)
    # ORIGINAL heading (kept for reference):
    # doc.drawString(20 * mm, height - 25 * mm, "Medical Specialist Consultation and Referral System")
    # NEW: DOCCONNECT heading, top-left
    doc.drawString(20 * mm, height - 25 * mm, "DOCCONNECT")

    doc.setFont("Helvetica-Bold", 13)
    doc.drawString(20 * mm, height - 35 * mm, title)

    doc.line(20 * mm, height - 38 * mm, width - 20 * mm, height - 38 * mm)

    y = height - 50 * mm
    doc.setFont("Helvetica", 11)
    for label, value in rows:
        doc.setFont("Helvetica-Bold", 11)
        doc.drawString(20 * mm, y, f"{label}:")
        doc.setFont("Helvetica", 11)
        doc.drawString(65 * mm, y, str(value) if value not in (None, '') else '-')
        y -= 9 * mm

    doc.setFont("Helvetica-Oblique", 9)
    doc.drawString(20 * mm, 15 * mm, f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    doc.showPage()
    doc.save()
    buffer.seek(0)
    return buffer


# ================= PATIENT: DOWNLOAD APPOINTMENT REPORT =================
@app.route('/patient/report/<int:appointment_id>')
def patient_appointment_report(appointment_id):

    if 'patient_id' not in session:
        return redirect(url_for('patient_login'))

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT a.*, d.firstname AS doc_first, d.surname AS doc_last, d.speciality,
               p.firstname AS pat_first, p.lastname AS pat_last
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        JOIN patients p ON a.patient_id = p.patient_id
        WHERE a.appointment_id=%s AND a.patient_id=%s
    """, (appointment_id, session['patient_id']))
    a = cursor.fetchone()

    if not a:
        cursor.close()
        connection.close()
        return redirect(url_for('my_appointments'))

    if a['status'] != 'Completed':
        cursor.close()
        connection.close()
        flash("Your report will be available once the doctor marks your appointment as Completed.")
        return redirect(url_for('my_appointments'))

    # ---- work out what to actually show as "Doctor's Feedback" ----
    effective_feedback = get_effective_feedback(cursor, appointment_id, a['feedback'])

    cursor.close()
    connection.close()

    rows = [
        ("Patient", f"{a['pat_first']} {a['pat_last']}"),
        ("Doctor", f"Dr. {a['doc_first']} {a['doc_last']}"),
        ("Speciality", a['speciality']),
        ("Reason for Visit", a['reason']),
        ("Date", a['appointment_date']),
        ("Time", format_time_hhmm(a['appointment_time'])),
        ("Status", a['status']),
        ("Doctor's Feedback", effective_feedback),
    ]

    buffer = _build_appointment_report_pdf("Patient Appointment Report", rows)

    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"appointment_report_{appointment_id}.pdf"
    )


# ================= PATIENT: TREATMENT REPORTS (DATE RANGE, TABLE VIEW) =================
@app.route('/patient/appointments_report')
def patient_appointments_report():

    if 'patient_id' not in session:
        return redirect(url_for('patient_login'))

    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    report_rows = []
    if start_date and end_date:
        connection = pymysql.connect(
            host='localhost', user='root', password='', database='medical_referral'
        )
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # ---- only Completed appointments count as a "treatment report" ----
        cursor.execute("""
            SELECT a.appointment_id, d.firstname AS doc_first, d.surname AS doc_last,
                   d.speciality, a.appointment_date, a.appointment_time, a.status
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.patient_id = %s AND a.status = 'Completed'
                  AND a.appointment_date BETWEEN %s AND %s
            ORDER BY a.appointment_date ASC, a.appointment_time ASC
        """, (session['patient_id'], start_date, end_date))
        report_rows = cursor.fetchall()

        cursor.close()
        connection.close()

    return render_template(
        "patient_appointments_report.html",
        report_rows=report_rows,
        start_date=start_date,
        end_date=end_date
    )


# ================= PATIENT: ALL TREATMENTS IN RANGE (ONE COMBINED PDF) =================
@app.route('/patient/appointments_report/pdf')
def patient_appointments_report_pdf():

    if 'patient_id' not in session:
        return redirect(url_for('patient_login'))

    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    connection = pymysql.connect(
        host='localhost', user='root', password='', database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT a.appointment_id, d.firstname AS doc_first, d.surname AS doc_last,
               d.speciality, a.appointment_date, a.appointment_time, a.status
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE a.patient_id = %s AND a.status = 'Completed'
              AND a.appointment_date BETWEEN %s AND %s
        ORDER BY a.appointment_date ASC, a.appointment_time ASC
    """, (session['patient_id'], start_date, end_date))
    rows = cursor.fetchall()

    headers = ["ID", "Doctor", "Speciality", "Date", "Time", "Status"]
    data_rows = [
        [
            r['appointment_id'],
            f"Dr. {r['doc_first']} {r['doc_last']}",
            r['speciality'],
            r['appointment_date'],
            format_time_hhmm(r['appointment_time']),
            r['status'],
        ]
        for r in rows
    ]

    buffer = _build_table_report_pdf(
        "My Treatment Reports",
        f"Patient: {session.get('patient_name', '')} | Date range: {start_date} to {end_date}",
        headers,
        data_rows
    )

    cursor.close()
    connection.close()

    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"treatment_reports_{start_date}_to_{end_date}.pdf"
    )


# ================= DOCTOR: DOWNLOAD APPOINTMENT REPORT =================
@app.route('/doctor/report/<int:appointment_id>')
def doctor_appointment_report(appointment_id):

    if 'doctor_id' not in session:
        return redirect(url_for('doctor_login'))

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT a.*, d.firstname AS doc_first, d.surname AS doc_last, d.speciality,
               p.firstname AS pat_first, p.lastname AS pat_last, p.email AS pat_email, p.county AS pat_county
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        JOIN patients p ON a.patient_id = p.patient_id
        WHERE a.appointment_id=%s AND a.doctor_id=%s
    """, (appointment_id, session['doctor_id']))
    a = cursor.fetchone()

    if not a:
        cursor.close()
        connection.close()
        return redirect(url_for('doctor_dashboard'))

    # ---- work out what to actually show as "Doctor's Feedback" / notes.
    #      Reports can now be downloaded for any status (approved/confirmed,
    #      declined, completed, referred, etc), not just Completed ones. ----
    if a['status'] == 'Completed':
        effective_feedback = get_effective_feedback(cursor, appointment_id, a['feedback'])
    else:
        effective_feedback = a['feedback'] or '-'

    # ---- was this booking referred on to another doctor? ----
    cursor.execute("""
        SELECT d.firstname, d.surname, r.reason, r.status
        FROM referrals r JOIN doctors d ON r.referred_to_doctor_id = d.doctor_id
        WHERE r.appointment_id=%s LIMIT 1
    """, (appointment_id,))
    referral_info = cursor.fetchone()

    cursor.close()
    connection.close()

    rows = [
        ("Patient", f"{a['pat_first']} {a['pat_last']}"),
        ("Patient Email", a['pat_email']),
        ("Patient County", a['pat_county']),
        ("Doctor", f"Dr. {a['doc_first']} {a['doc_last']}"),
        ("Speciality", a['speciality']),
        ("Reason for Visit", a['reason']),
        ("Date", a['appointment_date']),
        ("Time", format_time_hhmm(a['appointment_time'])),
        ("Status", a['status']),
        ("Feedback / Notes", effective_feedback),
    ]

    if referral_info:
        rows.append((
            "Referred To",
            f"Dr. {referral_info['firstname']} {referral_info['surname']} "
            f"({referral_info['status']}) - {referral_info['reason']}"
        ))

    buffer = _build_appointment_report_pdf("Doctor Appointment Report", rows)

    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"appointment_report_{appointment_id}.pdf"
    )


# ================= DOCTOR: BOOKINGS REPORT (DATE RANGE, TABLE VIEW) =================
@app.route('/doctor/appointments_report')
def doctor_appointments_report():

    if 'doctor_id' not in session:
        return redirect(url_for('doctor_login'))

    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    status_filter = request.args.get('status', '')

    report_rows = []
    if start_date and end_date:
        connection = pymysql.connect(
            host='localhost', user='root', password='', database='medical_referral'
        )
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        query = """
            SELECT a.appointment_id, p.firstname AS pat_first, p.lastname AS pat_last,
                   a.appointment_date, a.appointment_time, a.status,
                   rd.firstname AS referred_to_first, rd.surname AS referred_to_last,
                   r.status AS referral_status
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            LEFT JOIN referrals r ON r.appointment_id = a.appointment_id
            LEFT JOIN doctors rd ON r.referred_to_doctor_id = rd.doctor_id
            WHERE a.doctor_id = %s AND a.appointment_date BETWEEN %s AND %s
        """
        params = [session['doctor_id'], start_date, end_date]

        # ---- "Referred" is a virtual status: it means this booking has a
        #      referral attached to it, on top of whatever its real status is ----
        if status_filter == 'Referred':
            query += " AND r.referral_id IS NOT NULL"
        elif status_filter:
            query += " AND a.status = %s"
            params.append(status_filter)

        query += " ORDER BY a.appointment_date ASC, a.appointment_time ASC"

        cursor.execute(query, params)
        report_rows = cursor.fetchall()

        cursor.close()
        connection.close()

    return render_template(
        "doctor_appointments_report.html",
        report_rows=report_rows,
        start_date=start_date,
        end_date=end_date,
        status_filter=status_filter
    )


# ================= DOCTOR: ALL BOOKINGS IN RANGE (ONE COMBINED PDF) =================
@app.route('/doctor/appointments_report/pdf')
def doctor_appointments_report_pdf():

    if 'doctor_id' not in session:
        return redirect(url_for('doctor_login'))

    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    status_filter = request.args.get('status', '')

    connection = pymysql.connect(
        host='localhost', user='root', password='', database='medical_referral'
    )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # ---- the doctor's own details (speciality is the same for every row here) ----
    cursor.execute("SELECT firstname, surname, speciality FROM doctors WHERE doctor_id=%s", (session['doctor_id'],))
    doc_info = cursor.fetchone()

    query = """
        SELECT a.appointment_id, p.firstname AS pat_first, p.lastname AS pat_last,
               p.phone AS pat_phone, p.county AS pat_county,
               a.reason, a.feedback, a.appointment_date, a.appointment_time, a.status,
               rd.firstname AS referred_to_first, rd.surname AS referred_to_last,
               r.status AS referral_status
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        LEFT JOIN referrals r ON r.appointment_id = a.appointment_id
        LEFT JOIN doctors rd ON r.referred_to_doctor_id = rd.doctor_id
        WHERE a.doctor_id = %s AND a.appointment_date BETWEEN %s AND %s
    """
    params = [session['doctor_id'], start_date, end_date]

    if status_filter == 'Referred':
        query += " AND r.referral_id IS NOT NULL"
    elif status_filter:
        query += " AND a.status = %s"
        params.append(status_filter)

    query += " ORDER BY a.appointment_date ASC, a.appointment_time ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    headers = ["Patient", "Phone", "Residence", "Reason for Consultation",
               "Date", "Time", "Status", "Doctor's Feedback", "Referred To"]
    # widths in mm, tuned to fit a landscape A4 page (~273mm usable width)
    col_widths = [w * mm for w in (30, 25, 25, 45, 20, 15, 20, 60, 33)]

    data_rows = []
    for r in rows:
        if r['status'] == 'Completed':
            feedback = get_effective_feedback(cursor, r['appointment_id'], r['feedback'])
        else:
            feedback = r['feedback'] or '-'

        referred_to = (
            f"Dr. {r['referred_to_first']} {r['referred_to_last']} ({r['referral_status']})"
            if r['referred_to_first'] else '-'
        )

        data_rows.append([
            f"{r['pat_first']} {r['pat_last']}",
            r['pat_phone'],
            r['pat_county'],
            r['reason'],
            r['appointment_date'],
            format_time_hhmm(r['appointment_time']),
            r['status'],
            feedback,
            referred_to,
        ])

    doctor_name = f"Dr. {doc_info['firstname']} {doc_info['surname']}" if doc_info else ""
    speciality = doc_info['speciality'] if doc_info else ""
    subtitle = f"Doctor: {doctor_name} | Speciality: {speciality} | Date range: {start_date} to {end_date}"
    if status_filter:
        subtitle += f" | Status: {status_filter}"

    buffer = _build_table_report_pdf(
        "Bookings Report", subtitle, headers, data_rows, wide=True, col_widths=col_widths
    )

    cursor.close()
    connection.close()

    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"bookings_report_{start_date}_to_{end_date}.pdf"
    )


app.run(debug=True)