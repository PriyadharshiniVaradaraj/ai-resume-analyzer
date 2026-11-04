import os
import sys
from datetime import timedelta
from urllib.parse import quote_plus
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"), override=True)

# Ensure backend modules are importable from any working directory
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from resume_parser import extract_text_from_pdf
from skill_extractor import extract_skills
from resume_scorer import calculate_resume_score
from recommender import recommend_jobs
from skill_gap import find_skill_gap
from auth import auth, login_manager, init_auth_table
from history import init_history_table, save_history, get_history, get_one
from applications import init_applications_table, add_application, get_applications

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "../templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
    static_url_path="/static"
)

# Secret key for sessions & CSRF protection (uses env variable if set, otherwise fallback for local dev)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "resume-analyzer-secret-key-12345")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=bool(os.environ.get("RENDER"))
)

login_manager.init_app(app)
csrf = CSRFProtect(app)
app.register_blueprint(auth)
print("ADMIN_EMAIL loaded:", bool(os.environ.get("ADMIN_EMAIL")), "| ADMIN_PASSWORD loaded:", bool(os.environ.get("ADMIN_PASSWORD")))
init_auth_table()
init_history_table()
init_applications_table()

# Folder where uploaded resumes are stored
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------- HOME PAGE ----------------
@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    return render_template("index.html")


# ---------------- ANALYZE RESUME ----------------
@app.route("/analyze", methods=["POST"])
@login_required
def analyze():
    # Check whether file was uploaded
    if "resume" not in request.files:
        return "No resume file uploaded.", 400

    file = request.files["resume"]

    # Check filename
    if file.filename == "":
        return "Please select a resume.", 400

    # Save uploaded resume
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Extract text from PDF
    try:
        resume_text = extract_text_from_pdf(file_path)
    except Exception as e:
        return f"Error reading resume: {e}", 500

    # Extract skills
    skills = extract_skills(resume_text)

    # Check profile attributes for scoring
    text_lower = resume_text.lower()
    education = any(
        word in text_lower
        for word in ["b.tech", "b.e", "bachelor", "m.tech", "m.e", "master", "degree", "bca", "mca", "bs", "ms"]
    )
    experience = any(
        word in text_lower
        for word in ["experience", "internship", "worked", "developer", "engineer", "analyst"]
    )
    projects = any(
        word in text_lower
        for word in ["project", "projects", "developed", "built"]
    )
    certifications = any(
        word in text_lower
        for word in ["certification", "certificate", "certified"]
    )

    # Calculate overall resume score
    score = calculate_resume_score(
        skills,
        education,
        experience,
        projects,
        certifications
    )

    # Recommend matching jobs
    exp_years = 1 if experience else 0
    jobs = recommend_jobs(
        resume_skills=skills,
        experience=exp_years
    )

    # Calculate skill gaps compared to popular tech stack
    target_job_skills = ["python", "sql", "machine learning", "aws", "docker", "git", "react", "html", "css", "java"]
    matching_skills, missing_skills = find_skill_gap(skills, target_job_skills)
    gaps = {"matching": matching_skills, "missing": missing_skills}

    # Save analysis record to history for the current user
    if current_user.is_authenticated:
        save_history(current_user.id, file.filename, score, skills, gaps, jobs)

    # Send extracted information to results page
    return render_template(
        "results.html",
        filename=file.filename,
        resume_text=resume_text[:500],
        score=score,
        skills=skills,
        jobs=jobs,
        education=education,
        experience=experience,
        projects=projects,
        certifications=certifications,
        matching_skills=matching_skills,
        missing_skills=missing_skills
    )


# ---------------- HISTORY ROUTES ----------------
@app.route("/history")
@login_required
def history():
    return render_template("history.html", records=get_history(current_user.id))


@app.route("/history/<int:record_id>")
@login_required
def history_detail(record_id):
    record = get_one(current_user.id, record_id)
    if record is None:
        abort(404)
    return render_template("history_detail.html", r=record)


# ---------------- APPLICATION TRACKING ROUTES ----------------
@app.route("/apply", methods=["POST"])
@login_required
def apply_job():
    title = request.form.get("job_title", "").strip()
    company = request.form.get("company", "").strip()
    url = request.form.get("apply_url", "").strip()
    if not title:
        abort(400)
    if not url.lower().startswith(("http://", "https://")):
        # no direct link in the data: open a job search for this role instead
        url = "https://www.linkedin.com/jobs/search/?keywords=" + quote_plus(f"{title} {company}")
    add_application(current_user.id, title, company, url)
    return redirect(url)


@app.route("/applications")
@login_required
def applications():
    return render_template("applications.html", apps=get_applications(current_user.id))


# ---------------- RUN APPLICATION ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
