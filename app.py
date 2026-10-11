from datetime import datetime

from flask import Flask, abort, render_template
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


@app.route("/login/student")
def student_login():
    return page("login/student.html")


@app.route("/login/staff")
def staff_login():
    return page("login/staff.html")


@app.route("/login/admin")
def admin_login():
    return page("login/admin.html")


if __name__ == "__main__":
    app.run(debug=True)