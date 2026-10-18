from datetime import datetime

from flask import Flask, abort, redirect, render_template, request, url_for
from jinja2 import TemplateNotFound
from werkzeug.exceptions import NotFound

# HTML lives in templates/. CSS/JS/images live in public/ because Vercel only serves
# static files from public/. Serving public/ at the site root makes local runs
# (python app.py) and Vercel use the same URLs, e.g. /styles/mainlogin.css
app = Flask(__name__, static_folder="public", static_url_path="")


@app.context_processor
def inject_globals():
    return {
        "current_year": datetime.now().year,
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


def login_view(template, id_field, id_message):
    """Shared sign-in handling for student / staff / admin pages."""
    errors = {}
    identifier = ""
    notice = None

    if request.method == "POST":
        identifier = request.form.get(id_field, "").strip()
        password = request.form.get("password", "")

        if not identifier:
            errors[id_field] = id_message
        if not password:
            errors["password"] = "Enter your password."

        if not errors:
            # TODO: check the ID and password against the database, then start a
            # session and redirect to the right dashboard.
            notice = "Sign-in is not connected yet. Your details were not saved."

    # The password is never sent back to the page.
    return render_template(template, errors=errors, notice=notice, **{id_field: identifier})


@app.route("/login/student", methods=["GET", "POST"])
def student_login():
    return login_view("login/student.html", "roll_number", "Enter your roll number.")


@app.route("/login/staff", methods=["GET", "POST"])
def staff_login():
    return login_view("login/staff.html", "staff_id", "Enter your staff ID.")


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


@app.route("/workers/about")
def worker_about():
    return page("workers/about.html")


@app.route("/workers/contact")
def worker_contact():
    return page("workers/contact.html")


# ---------- Student area: pages shown after a student signs in ----------
def get_current_student():
    """SAMPLE DATA. TODO: load the signed-in student from the database."""
    return {"name": "Student", "roll_number": "21B01A0001"}


@app.route("/students/home")
def student_home():
    return render_template("students/home.html", student=get_current_student())


# These pages are not built yet: they show the friendly 404 until their template exists.
@app.route("/students/profile")
def student_profile():
    return page("students/profile.html")


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
    )


@app.route("/students/feedback")
def student_feedback():
    return page("students/feedback.html")


@app.route("/students/suggestions")
def student_suggestions():
    return page("students/suggestions.html")


@app.route("/students/contact")
def student_contact():
    return page("students/contact.html")


@app.route("/students/about")
def student_about():
    return page("students/about.html")


@app.errorhandler(404)
def not_found(error):
    # Show a custom message only when we raised the 404 ourselves (page not built yet).
    message = error.description if error.description != NotFound.description else None
    path = request.path if len(request.path) <= 60 else request.path[:57] + "..."
    return render_template("404.html", message=message, path=path), 404


if __name__ == "__main__":
    app.run(debug=True)