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


@app.route("/students/complaints/new")
def student_new_complaint():
    return page("students/new_complaint.html")


@app.route("/students/complaints")
def student_complaints():
    return page("students/complaints.html")


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