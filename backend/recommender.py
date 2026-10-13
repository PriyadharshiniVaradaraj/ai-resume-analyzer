import os
import pandas as pd


def recommend_jobs(
    resume_skills,
    experience=0,
    preferred_location=None,
    expected_salary=None
):
    # Handle case where text or a CSV path is passed instead of skills list
    if isinstance(resume_skills, str):
        if os.path.exists(resume_skills) and resume_skills.endswith(".csv"):
            resume_skills = []
        else:
            from skill_extractor import extract_skills
            resume_skills = extract_skills(resume_skills)

    # Resolve jobs.csv path dynamically
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    jobs_path = os.path.join(BASE_DIR, "../data/jobs.csv")
    if not os.path.exists(jobs_path):
        jobs_path = os.path.join(BASE_DIR, "data/jobs.csv")

    if not os.path.exists(jobs_path):
        return []

    jobs = pd.read_csv(jobs_path)

    # Coerce experience to integer
    try:
        experience = int(experience)
    except (ValueError, TypeError):
        experience = 0

    recommendations = []

    for _, job in jobs.iterrows():

        job_skills = [
            skill.strip().lower()
            for skill in str(job["skills"]).split(",")
            if skill.strip()
        ]

        candidate_skills = [
            skill.strip().lower()
            for skill in resume_skills
        ]

        # Skill matching
        matched_skills = set(candidate_skills) & set(job_skills)

        if len(job_skills) > 0:
            skill_score = (
                len(matched_skills) /
                len(job_skills)
            ) * 100
        else:
            skill_score = 0

        # Experience matching
        try:
            exp_min = int(job["experience_min"])
            exp_max = int(job["experience_max"])
            if exp_min <= experience <= exp_max:
                experience_score = 100
            else:
                experience_score = 40
        except (ValueError, KeyError, TypeError):
            experience_score = 50

        # Location matching
        if preferred_location:
            if preferred_location.lower() in str(job.get("location", "")).lower():
                location_score = 100
            else:
                location_score = 50
        else:
            location_score = 50

        # Final score calculation
        final_score = (
            skill_score * 0.50
            + experience_score * 0.20
            + location_score * 0.10
            + 20
        )

        salary_min = job.get("salary_min_lpa", "N/A")
        salary_max = job.get("salary_max_lpa", "N/A")

        recommendations.append({
            "job_title": job["job_title"],
            "company": job["company"],
            "location": job["location"],
            "salary": f"₹{salary_min}–₹{salary_max} LPA",
            "match_score": round(final_score, 2),
            "matched_skills": ", ".join(sorted(matched_skills)) if matched_skills else "None"
        })

    recommendations.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    return recommendations[:10]