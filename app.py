from datetime import datetime

from flask import Flask, abort, render_template, request
from jinja2 import TemplateNotFound

# HTML lives in templates/. CSS/JS/images live in public/ because Vercel only serves
# static files from public/. Serving public/ at the site root makes local runs
# (python app.py) and Vercel use the same URLs, e.g. /styles/mainlogin.css
app = Flask(__name__, static_folder="public", static_url_path="")


@app.context_processor
def inject_globals():
    return {"current_year": datetime.now().year}


def page(template_name):
    """Render a template; show a clean 404 if it has not been created yet."""
    try:
        return render_template(template_name)
    except TemplateNotFound:
        abort(404, description="This page is not ready yet.")


@app.route("/")
def index():
    return page("mainlogin.html")


@app.route("/login/student", methods=["GET", "POST"])
def student_login():
    errors = {}
    roll_number = ""
    notice = None

    if request.method == "POST":
        roll_number = request.form.get("roll_number", "").strip()
        password = request.form.get("password", "")

        if not roll_number:
            errors["roll_number"] = "Enter your roll number."
        if not password:
            errors["password"] = "Enter your password."

        if not errors:
            # TODO: check the roll number and password against the student database,
            # then start a session and redirect to the student dashboard.
            notice = "Student sign-in is not connected yet. Your details were not saved."

    # The password is never sent back to the page.
    return render_template(
        "login/student.html", errors=errors, roll_number=roll_number, notice=notice
    )


@app.route("/login/student/forgot")
def forgot_password():
    return page("login/forgot.html")


@app.route("/login/staff")
def staff_login():
    return page("login/staff.html")


@app.route("/login/admin")
def admin_login():
    return page("login/admin.html")


if __name__ == "__main__":
    app.run(debug=True)