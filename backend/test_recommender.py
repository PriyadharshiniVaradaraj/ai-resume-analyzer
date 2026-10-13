import os
from resume_parser import extract_text_from_pdf
from skill_extractor import extract_skills
from recommender import recommend_jobs

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
possible_paths = [
    os.path.join(BASE_DIR, "../uploads/resume.pdf"),
    os.path.join(BASE_DIR, "../uploads/uploaded_resume.pdf"),
    os.path.join(BASE_DIR, "uploads/25MCA043  Resume.pdf"),
]
pdf_path = next((p for p in possible_paths if os.path.exists(p)), None)

if pdf_path:
    # Extract resume text & skills
    resume_text = extract_text_from_pdf(pdf_path)
    resume_skills = extract_skills(resume_text)

    # Get recommendations
    recommendations = recommend_jobs(
        resume_skills=resume_skills,
        experience=1
    )

    print("\n========== JOB RECOMMENDATIONS ==========\n")

    # Display top 5 jobs
    for job in recommendations[:5]:
        print("Job:", job["job_title"])
        print("Company:", job["company"])
        print("Location:", job["location"])
        print("Match:", job["match_score"], "%")
        print("Salary:", job["salary"])
        print("Matched Skills:", job["matched_skills"])
        print("-----------------------------------")
else:
    print("No test PDF found!")