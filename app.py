import hashlib
import os
from pathlib import Path

from flask import Flask, flash, redirect, render_template, render_template_string, request, session, url_for


app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", "local-lab-secret-change-me"),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Strict",
)

OPERATORS = {
    "iskender": {
        "password": hashlib.sha256("kontrtim34".encode()).hexdigest(),
        "clearance": "ULTRA SECRET",
        "name": "ISKENDER",
        "department": "KOMUTA MERKEZI",
        "id": "ADM-001",
    }
}

PERSONNEL = [
    {"id": "PER-001", "name": "Ahmet YILMAZ", "department": "SIBER OPERASYONLAR", "clearance": "SECRET", "location": "ANKARA"},
    {"id": "PER-002", "name": "Ayse KARA", "department": "KONTRASPIYONAJ", "clearance": "TOP SECRET", "location": "ISTANBUL"},
    {"id": "PER-003", "name": "Mehmet DEMIR", "department": "SAHA OPERASYONLARI", "clearance": "SECRET", "location": "IZMIR"},
    {"id": "PER-004", "name": "Fatma CELIK", "department": "ANALIZ BIRIMI", "clearance": "CONFIDENTIAL", "location": "ANKARA"},
    {"id": "PER-005", "name": "Ali OZTURK", "department": "TEKNIK ISTIHBARAT", "clearance": "TOP SECRET", "location": "ANKARA"},
    {"id": "PER-006", "name": "Zeynep ARSLAN", "department": "KOORDINASYON", "clearance": "SECRET", "location": "BURSA"},
]


def read_flag():
    flag_path = Path(os.environ.get("FLAG_PATH", "/app/flag.txt"))
    try:
        return flag_path.read_text(encoding="utf-8").strip()
    except OSError:
        return "LAB{LOCAL_DEVELOPMENT_FLAG}"


@app.context_processor
def lab_context():
    # Deliberately exposed to the vulnerable Jinja context for the exercise.
    return {"lab_flag": read_flag()}


@app.route("/")
def index():
    return redirect(url_for("dashboard" if "operator" in session else "login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password_hash = hashlib.sha256(request.form.get("password", "").encode()).hexdigest()
        operator = OPERATORS.get(username)

        if operator and operator["password"] == password_hash:
            session.update(operator=username, **{key: operator[key] for key in ("clearance", "name", "department", "id")})
            return redirect(url_for("dashboard"))

        flash("ERISIM REDDEDILDI - Gecersiz kimlik dogrulama", "error")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "operator" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")


@app.route("/personnel", methods=["GET", "POST"])
def personnel_search():
    if "operator" not in session:
        return redirect(url_for("login"))

    search_term = ""
    template_output = None
    template_error = None
    found_personnel = []

    if request.method == "POST":
        search_term = request.form.get("search_term", "").strip()
        if len(search_term) < 2:
            template_error = "En az 2 karakter girmelisiniz."
        else:
            found_personnel = [
                person
                for person in PERSONNEL
                if search_term.lower() in person["name"].lower()
                or search_term.lower() in person["department"].lower()
            ]
            try:
                # INTENTIONALLY VULNERABLE: this is the single SSTI sink in the lab.
                template_output = render_template_string(search_term)
            except Exception as exc:
                template_error = f"Template hatasi: {exc}"

    return render_template(
        "personnel.html",
        found_personnel=found_personnel,
        search_term=search_term,
        template_error=template_error,
        template_output=template_output,
    )


@app.route("/operations")
def operations():
    if "operator" not in session:
        return redirect(url_for("login"))
    return render_template("operations.html")


@app.route("/reports")
def reports():
    if "operator" not in session:
        return redirect(url_for("login"))
    return render_template("reports.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000)
