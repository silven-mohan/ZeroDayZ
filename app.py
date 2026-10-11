from datetime import datetime

from flask import Flask, abort, render_template, request
from jinja2 import TemplateNotFound
from werkzeug.exceptions import NotFound

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


@app.errorhandler(404)
def not_found(error):
    # Show a custom message only when we raised the 404 ourselves (page not built yet).
    message = error.description if error.description != NotFound.description else None
    path = request.path if len(request.path) <= 60 else request.path[:57] + "..."
    return render_template("404.html", message=message, path=path), 404


if __name__ == "__main__":
    app.run(debug=True)