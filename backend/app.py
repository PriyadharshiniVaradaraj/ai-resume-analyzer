import os
from flask import Flask, render_template, request

from resume_parser import extract_text_from_pdf
from skill_extractor import extract_skills
from resume_scorer import calculate_resume_score
from recommender import recommend_jobs
from skill_gap import find_skill_gap

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "../templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
    static_url_path="/static"
)

# Folder where uploaded resumes are stored
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------- HOME PAGE ----------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------- ANALYZE RESUME ----------------
@app.route("/analyze", methods=["POST"])
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


# ---------------- RUN APPLICATION ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)