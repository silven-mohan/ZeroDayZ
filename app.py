from datetime import datetime

from flask import Flask, abort, render_template
from jinja2 import TemplateNotFound

# Flask defaults: HTML in templates/, CSS/JS/images in static/
app = Flask(__name__)


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