import os
import json
from datetime import datetime

import firebase_admin
import mysql.connector
from flask import Flask, abort, redirect, render_template, request, session, url_for
from firebase_admin import auth as firebase_auth, credentials
from jinja2 import TemplateNotFound
from werkzeug.exceptions import NotFound
from werkzeug.security import check_password_hash, generate_password_hash

# HTML lives in templates/. CSS/JS/images live in public/ because Vercel only serves
# static files from public/. Serving public/ at the site root makes local runs
# (python app.py) and Vercel use the same URLs, e.g. /styles/mainlogin.css
app = Flask(__name__, static_folder="public", static_url_path="")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")


def get_db_connection():
    """Create a MySQL connection using deployment environment variables."""
    required = ("MYSQL_HOST", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE")
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        raise RuntimeError(f"Missing database environment variables: {', '.join(missing)}")
    return mysql.connector.connect(
        host=os.environ["MYSQL_HOST"],
        port=int(os.environ.get("MYSQL_PORT", "3306")),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.environ["MYSQL_DATABASE"],
    )


def initialize_firebase():
    """Initialize Firebase Admin once when a service-account file is configured."""
    if firebase_admin._apps:
        return
    service_account_value = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
    if not service_account_value:
        app.logger.error("FIREBASE_SERVICE_ACCOUNT_JSON is not configured")
        return
    try:
        service_account = json.loads(service_account_value)
        credential = credentials.Certificate(service_account)
    except json.JSONDecodeError:
        credential = credentials.Certificate(service_account_value)
    firebase_admin.initialize_app(credential)


def verify_firebase_phone_token(id_token, mobile_number):
    """Verify Firebase's phone-auth token and match its phone number."""
    try:
        initialize_firebase()
        decoded = firebase_auth.verify_id_token(id_token)
        return decoded.get("phone_number") == mobile_number
    except Exception:
        app.logger.exception("Could not verify Firebase phone authentication")
        return False


def authenticate_user(role, identifier, password):
    """Return the matching user, or None when the credentials are invalid."""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, role, identifier, password_hash
            FROM users
            WHERE role = %s AND identifier = %s AND is_active = TRUE
            LIMIT 1
            """,
            (role, identifier),
        )
        user = cursor.fetchone()
        if user and check_password_hash(user["password_hash"], password):
            return user
    except (mysql.connector.Error, ValueError):
        app.logger.exception("Could not authenticate user against MySQL")
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()
    return None


def account_exists(role, identifier):
    """Return whether an account exists without checking its password."""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT 1 FROM users WHERE role = %s AND identifier = %s LIMIT 1",
            (role, identifier),
        )
        return cursor.fetchone() is not None
    except (mysql.connector.Error, ValueError):
        app.logger.exception("Could not check whether the user exists")
        return None
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def create_user(role, identifier, password, details):
    """Create an account and return its new ID."""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO users
                (role, identifier, password_hash, name, course, branch,
                 study_year, hostel_location, mobile_number, mobile_verified)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
            """,
            (
                role,
                identifier,
                generate_password_hash(password),
                details["name"],
                details.get("course"),
                details.get("branch"),
                details.get("study_year"),
                details.get("hostel_location"),
                details.get("mobile_number"),
            ),
        )
        connection.commit()
        return cursor.lastrowid
    except mysql.connector.Error:
        if connection is not None:
            connection.rollback()
        app.logger.exception("Could not create user account")
        return None
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


@app.context_processor
def inject_globals():
    return {
        "current_year": datetime.now().year,
        "firebase_config": {
            "apiKey": os.environ.get("FIREBASE_API_KEY", ""),
            "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN", ""),
            "projectId": os.environ.get("FIREBASE_PROJECT_ID", ""),
            "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET", ""),
            "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID", ""),
            "appId": os.environ.get("FIREBASE_APP_ID", ""),
        },
        # Number shown on the Requests tab of the worker menu.
        "pending_count": len(get_upcoming_requests()),
    }


def page(template_name):
    """Render a template; show a clean 404 if it has not been created yet."""
    try:
        return render_template(template_name)
    except TemplateNotFound:
        abort(404, description="This page is not ready yet.")


@app.route("/")
def index():
    return page("mainlogin.html")


def login_view(template, role, id_field, id_message, destination):
    """Shared sign-in handling for student / staff / admin pages."""
    errors = {}
    identifier = ""
    notice = None

    if request.method == "POST":
        identifier = request.form.get(id_field, "").strip().upper()
        password = request.form.get("password", "")

        if not identifier:
            errors[id_field] = id_message
        if not password:
            errors["password"] = "Enter your password."

        if not errors:
            user = authenticate_user(role, identifier, password)
            if user is None:
                if account_exists(role, identifier) is False:
                    return redirect(url_for("create_account", role=role, identifier=identifier))
                errors["form"] = "The ID or password is incorrect."
            else:
                session.clear()
                session["user_id"] = user["id"]
                session["role"] = user["role"]
                session["identifier"] = user["identifier"]
                return redirect(url_for(destination))

    # The password is never sent back to the page.
    return render_template(template, errors=errors, notice=notice, **{id_field: identifier})


@app.route("/login/student", methods=["GET", "POST"])
def student_login():
    return login_view(
        "login/student.html", "student", "roll_number",
        "Enter your roll number.", "student_home",
    )


@app.route("/login/staff", methods=["GET", "POST"])
def staff_login():
    return login_view(
        "login/staff.html", "staff", "staff_id",
        "Enter your staff ID.", "worker_requests",
    )


@app.route("/account/create/<role>", methods=["GET", "POST"])
def create_account(role):
    """Collect details and create a student or staff account."""
    if role not in {"student", "staff"}:
        abort(404)

    id_field = "roll_number" if role == "student" else "staff_id"
    identifier = request.args.get("identifier", "").strip().upper()
    if request.method == "POST":
        identifier = request.form.get(id_field, "").strip().upper()
    values = {
        id_field: identifier,
        "name": request.form.get("name", "").strip(),
    }
    if role == "student":
        values.update({
            "course": request.form.get("course", "").strip(),
            "branch": request.form.get("branch", "").strip(),
            "study_year": request.form.get("study_year", "").strip(),
            "hostel_location": request.form.get("hostel_location", "").strip(),
            "mobile_number": request.form.get("mobile_number", "").strip(),
        })
    errors = {}

    if request.method == "POST":
        password = request.form.get("password", "")
        if not identifier:
            errors[id_field] = "Enter your identifier."
        if len(values["name"]) < 2:
            errors["name"] = "Enter your full name."
        if not password:
            errors["password"] = "Create a password."
        elif len(password) < 8:
            errors["password"] = "Use at least 8 characters."
        if role == "student":
            if not values["course"]:
                errors["course"] = "Choose your course."
            if not values["branch"]:
                errors["branch"] = "Enter your branch."
            if values["study_year"] not in {"1", "2", "3", "4", "5", "6"}:
                errors["study_year"] = "Choose your current year."
            if not values["hostel_location"]:
                errors["hostel_location"] = "Enter your hostel location."
            mobile_digits = "".join(character for character in values["mobile_number"] if character.isdigit())
            if len(mobile_digits) != 10:
                errors["mobile_number"] = "Enter a 10-digit mobile number."
            else:
                values["mobile_number"] = "+91" + mobile_digits
                if not verify_firebase_phone_token(
                    request.form.get("firebase_id_token", ""), values["mobile_number"]
                ):
                    errors["mobile_number"] = "Verify your mobile number with Firebase."
        if not errors:
            user_id = create_user(role, identifier, password, values)
            if user_id is None:
                errors["form"] = "That account could not be created. It may already exist."
            else:
                session.clear()
                session["user_id"] = user_id
                session["role"] = role
                session["identifier"] = identifier
                return redirect(url_for("student_home" if role == "student" else "worker_requests"))

    return render_template(
        "login/create_account.html",
        role=role,
        id_field=id_field,
        values=values,
        errors=errors,
        otp_sent=False,
    )




@app.route("/login/admin")
def admin_login():
    return page("login/admin.html")


@app.route("/login/forgot")
def forgot_password():
    return page("login/forgot.html")


# ---------- Worker (staff) area: pages shown after a worker signs in ----------
def get_current_worker():
    """SAMPLE DATA. TODO: load the signed-in worker and their request counts from
    the database once sign-in and sessions exist."""
    name = "Swejo"
    worker = {
        "name": name,
        "initials": "".join(part[0] for part in name.split()[:2]).upper(),
        "role": "Hostel staff",
        "staff_id": "ST-0001",
        "description": "Looks after electrical and plumbing complaints in the hostel.",
        "photo": None,  # URL of an uploaded photo; None shows the initials instead
    }
    stats = {"completed": 72, "ongoing": 2, "rejected": 12}
    stats["total"] = sum(stats.values())
    return worker, stats


@app.route("/workers/profile")
def worker_profile():
    worker, stats = get_current_worker()
    return render_template("workers/profile.html", worker=worker, stats=stats)


def get_upcoming_requests():
    """SAMPLE DATA. TODO: load the new requests assigned to the signed-in worker."""
    return [
        {
            "id": 1,
            "location": "Hostel Block-I, Ground Floor, Room No. 26",
            "description": (
                "From the last three days we are having voltage fluctuations, please "
                "take our request into consideration and resolve it as soon as possible."
            ),
        }
    ]


def get_past_requests():
    """SAMPLE DATA. TODO: load the worker's earlier requests.
    status is one of: completed, ongoing, rejected, cancelled"""
    return [
        {"title": "Light issues", "status": "completed"},
        {"title": "Plug point issue", "status": "completed"},
        {"title": "Fan issue", "status": "completed"},
        {"title": "Low voltage issue", "status": "ongoing"},
        {"title": "Light replacement", "status": "ongoing"},
        {"title": "Fan issues", "status": "rejected"},
        {"title": "Light issues", "status": "cancelled"},
    ]


ACTION_NOTICES = {
    "accept": "You chose to accept this request. It was not saved yet, because requests are not connected to the database.",
    "decline": "You chose to decline this request. It was not saved yet, because requests are not connected to the database.",
}


@app.route("/workers/requests")
def worker_requests():
    # `done` is only ever one of the two known actions, never printed as typed.
    notice = ACTION_NOTICES.get(request.args.get("done", ""))
    return render_template(
        "workers/requests.html",
        upcoming=get_upcoming_requests(),
        past=get_past_requests(),
        notice=notice,
    )


@app.route("/workers/requests/<int:request_id>/<action>", methods=["POST"])
def worker_request_action(request_id, action):
    if action not in ACTION_NOTICES:
        abort(404)
    # TODO: save the worker's choice for this request in the database.
    # Redirect so that refreshing the page does not send the choice again.
    return redirect(url_for("worker_requests", done=action), code=303)


# ---------- Student area: pages shown after a student signs in ----------
def get_current_student():
    """Load the signed-in student's identity from the database."""
    if session.get("role") != "student" or not session.get("user_id"):
        return None

    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
                 SELECT identifier, name, course, branch, study_year,
                     hostel_location, mobile_number
            FROM users
            WHERE id = %s AND role = 'student' AND is_active = TRUE
            LIMIT 1
            """,
            (session["user_id"],),
        )
        user = cursor.fetchone()
    except (mysql.connector.Error, ValueError):
        app.logger.exception("Could not load the signed-in student")
        return None
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()

    if user is None:
        return None

    name = user["name"]
    return {
        "name": name,
        "initials": "".join(part[0] for part in name.split()[:2]).upper(),
        "roll_number": user["identifier"],
        "course": user["course"] or "Not provided",
        "branch": user["branch"] or "Not provided",
        "year": f"Year {user['study_year']}" if user["study_year"] else "Not provided",
        "block": user["hostel_location"] or "Not provided",
        "room": "",
        "mobile": user["mobile_number"] or "Not provided",
        "photo": None,  # URL of an uploaded photo; None shows the initials instead
    }


@app.route("/students/home")
def student_home():
    student = get_current_student()
    if student is None:
        return redirect(url_for("student_login"))
    return render_template("students/home.html", student=student)


# These pages are not built yet: they show the friendly 404 until their template exists.
@app.route("/students/profile")
def student_profile():
    student = get_current_student()
    if student is None:
        return redirect(url_for("student_login"))
    return render_template("students/profile.html", student=student)


# What each category covers (shown on the registered complaints page).
CATEGORY_HINTS = {
    "Plumbing": "Leaks, taps, toilets, water supply, drainage",
    "Electrical": "Fans, tube lights, power issues, switches, AC, heater",
    "Maintenance": "Room cleaning, windows, doors, furniture",
    "Other": "Pest control, food, regular check-ups",
}
COMPLAINT_CATEGORIES = list(CATEGORY_HINTS)
MAX_PHOTO_BYTES = 5 * 1024 * 1024
# First bytes of real JPEG / PNG / WebP files (the file name alone is not trusted).
PHOTO_SIGNATURES = (b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"RIFF")


def check_photo(photo):
    """Return an error message for a bad photo, or None when it is fine or absent."""
    if photo is None or not photo.filename:
        return None
    head = photo.stream.read(12)
    photo.stream.seek(0, 2)
    size = photo.stream.tell()
    photo.stream.seek(0)
    if not head.startswith(PHOTO_SIGNATURES) or (head.startswith(b"RIFF") and head[8:12] != b"WEBP"):
        return "Choose a JPG, PNG or WebP photo."
    if size > MAX_PHOTO_BYTES:
        return "That photo is larger than 5 MB. Choose a smaller one."
    return None


@app.route("/students/complaints/new", methods=["GET", "POST"])
def student_new_complaint():
    student = get_current_student()
    if student is None:
        return redirect(url_for("student_login"))
    errors = {}
    values = {"mobile": "", "location": "", "category": "", "description": ""}

    if request.method == "POST":
        for key in values:
            values[key] = request.form.get(key, "").strip()
        mobile_digits = "".join(ch for ch in values["mobile"] if ch.isdigit())
        if mobile_digits.startswith("91") and len(mobile_digits) == 12:
            mobile_digits = mobile_digits[2:]

        if len(mobile_digits) != 10:
            errors["mobile"] = "Enter a 10-digit mobile number."
        if not values["location"]:
            errors["location"] = "Enter the block, floor and room."
        if values["category"] not in COMPLAINT_CATEGORIES:
            errors["category"] = "Choose a category."
        if len(values["description"]) < 10:
            errors["description"] = "Describe the problem in at least 10 characters."
        elif len(values["description"]) > 500:
            errors["description"] = "Keep the description under 500 characters."
        photo_error = check_photo(request.files.get("photo"))
        if photo_error:
            errors["photo"] = photo_error

        if not errors:
            # TODO: save the complaint (and the photo) for student["roll_number"].
            # Redirect so that refreshing the page does not send it again.
            return redirect(url_for("student_new_complaint", sent=1), code=303)

    return render_template(
        "students/new_complaint.html",
        student=student,
        errors=errors,
        values=values,
        categories=COMPLAINT_CATEGORIES,
        sent=request.args.get("sent") == "1",
    )


STATUS_LABELS = {
    "pending": "Waiting",
    "ongoing": "In progress",
    "completed": "Fixed",
    "rejected": "Not accepted",
}


def get_student_complaints():
    """SAMPLE DATA. TODO: load this student's complaints from the database.
    status is one of: pending, ongoing, completed, rejected"""
    return [
        {"ref": "#1004", "category": "Electrical", "location": "Room No. 228",
         "description": "Lights not working.", "date": "15 Oct 2026", "status": "pending"},
        {"ref": "#1003", "category": "Other", "location": "Room No. 26",
         "description": "Broken door.", "date": "12 Oct 2026", "status": "ongoing"},
        {"ref": "#1002", "category": "Plumbing", "location": "Washroom",
         "description": "No water from the tap.", "date": "9 Oct 2026", "status": "completed"},
        {"ref": "#1001", "category": "Plumbing", "location": "Washroom",
         "description": "Water leakage from the tap.", "date": "2 Oct 2026", "status": "completed"},
    ]


@app.route("/students/complaints")
def student_complaints():
    student = get_current_student()
    if student is None:
        return redirect(url_for("student_login"))
    everything = get_student_complaints()
    # `category` is only used when it is one of the known names.
    selected = request.args.get("category", "")
    if selected not in COMPLAINT_CATEGORIES:
        selected = ""
    categories = [
        {"name": name, "hint": hint, "count": sum(1 for c in everything if c["category"] == name)}
        for name, hint in CATEGORY_HINTS.items()
    ]
    shown = [c for c in everything if not selected or c["category"] == selected]
    return render_template(
        "students/complaints.html",
        categories=categories,
        complaints=shown,
        selected=selected,
        status_labels=STATUS_LABELS,
        student=student,
    )


@app.route("/students/feedback", methods=["GET", "POST"])
def student_feedback():
    student = get_current_student()
    if student is None:
        return redirect(url_for("student_login"))
    # Feedback can only be given on complaints that were fixed.
    eligible = [c for c in get_student_complaints() if c["status"] == "completed"]
    errors = {}
    values = {"complaint": "", "rating": "", "solved": "", "comment": ""}

    if request.method == "POST":
        for key in values:
            values[key] = request.form.get(key, "").strip()
        if values["complaint"] not in {c["ref"] for c in eligible}:
            errors["complaint"] = "Choose the complaint this is about."
        if values["rating"] not in {"1", "2", "3", "4", "5"}:
            errors["rating"] = "Choose a star rating."
        if values["solved"] not in {"yes", "no"}:
            errors["solved"] = "Say whether the problem is solved."
        if len(values["comment"]) > 500:
            errors["comment"] = "Keep your comments under 500 characters."
        if not errors:
            # TODO: save the feedback for this student and complaint.
            return redirect(url_for("student_feedback", sent=1), code=303)

    return render_template(
        "students/feedback.html",
        eligible=eligible, errors=errors, values=values,
        sent=request.args.get("sent") == "1",
        student=student,
    )


SUGGESTION_TOPICS = ["Hostel facilities", "Safety", "Cleanliness", "Rules and timings", "Other"]


@app.route("/students/suggestions", methods=["GET", "POST"])
def student_suggestions():
    student = get_current_student()
    if student is None:
        return redirect(url_for("student_login"))
    errors = {}
    values = {"topic": "", "title": "", "suggestion": "", "anonymous": ""}

    if request.method == "POST":
        for key in values:
            values[key] = request.form.get(key, "").strip()
        if values["topic"] not in SUGGESTION_TOPICS:
            errors["topic"] = "Choose a topic."
        if not 3 <= len(values["title"]) <= 80:
            errors["title"] = "Give your suggestion a short title (3 to 80 characters)."
        if len(values["suggestion"]) < 10:
            errors["suggestion"] = "Write your suggestion in at least 10 characters."
        elif len(values["suggestion"]) > 500:
            errors["suggestion"] = "Keep your suggestion under 500 characters."
        if not errors:
            # TODO: save the suggestion (leave the student out when values["anonymous"] is set).
            return redirect(url_for("student_suggestions", sent=1), code=303)

    return render_template(
        "students/suggestions.html",
        topics=SUGGESTION_TOPICS, errors=errors, values=values,
        sent=request.args.get("sent") == "1",
        student=student,
    )


# ---------- About and Contact: one page each, shared by students and workers ----------
# The pages live in templates/shared/. Only the surrounding layout (header buttons, menu)
# and one call-to-action change with the role.
def shared_layout(role):
    """Return the layout, menu highlight and call-to-action for a signed-in role."""
    if role == "worker":
        return {
            "role": "worker",
            "layout": "workers/base_workers.html",
            "cta": {
                "text": "Waiting on a request? Open your requests to accept or decline new ones.",
                "label": "Open requests",
                "url": url_for("worker_requests"),
            },
            "contact_url": url_for("worker_contact"),
        }
    return {
        "role": "student",
        "layout": "students/base_students.html",
        "cta": {
            "text": "Something broken in your room or block? A registered complaint is the quickest way to get it fixed and to follow its progress.",
            "label": "Register a complaint",
            "url": url_for("student_new_complaint"),
        },
        "contact_url": url_for("student_contact"),
    }


def get_hostel_contacts():
    """SAMPLE DATA: replace these placeholder numbers and addresses with the real ones."""
    contacts = [
        {"role": "Hostel warden", "note": "Rooms, rules and anything serious.", "icon": "phone",
         "phone": "98765 00001", "email": "warden@example.com", "urgent": False},
        {"role": "Hostel office", "note": "Complaint follow-ups and paperwork.", "icon": "mail",
         "phone": "98765 00002", "email": "office@example.com", "urgent": False},
        {"role": "Security and emergencies", "note": "Open all day and night.", "icon": "alert",
         "phone": "98765 00003", "email": None, "urgent": True},
    ]
    hours = [("Monday to Saturday", "9:00 am to 5:00 pm"), ("Sunday", "Closed (security only)")]
    return contacts, hours


def get_developer_contact():
    """SAMPLE DATA: the person who looks after the ZeroDayZ website itself."""
    return {
        "name": "ZeroDayZ developer",
        "note": "Found a bug, cannot sign in, or see wrong information on this website? Write to the developer. For problems with a room or facility, use a complaint instead.",
        "email": "developer@example.com",
        "phone": None,
    }


def about_page(role):
    if role == "student" and get_current_student() is None:
        return redirect(url_for("student_login"))
    return render_template("about.html", active="about", **shared_layout(role))


def contact_page(role):
    if role == "student" and get_current_student() is None:
        return redirect(url_for("student_login"))
    contacts, hours = get_hostel_contacts()
    return render_template(
        "contact.html",
        active="contact", contacts=contacts, hours=hours,
        developer=get_developer_contact(), **shared_layout(role),
    )


@app.route("/students/about")
def student_about():
    return about_page("student")


@app.route("/students/contact")
def student_contact():
    return contact_page("student")


@app.route("/workers/about")
def worker_about():
    return about_page("worker")


@app.route("/workers/contact")
def worker_contact():
    return contact_page("worker")


@app.errorhandler(404)
def not_found(error):
    # Show a custom message only when we raised the 404 ourselves (page not built yet).
    message = error.description if error.description != NotFound.description else None
    path = request.path if len(request.path) <= 60 else request.path[:57] + "..."
    return render_template("404.html", message=message, path=path), 404


if __name__ == "__main__":
    app.run(debug=True)