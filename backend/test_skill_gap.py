import os
from resume_parser import extract_text_from_pdf
from skill_extractor import extract_skills
from skill_gap import find_skill_gap

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
possible_paths = [
    os.path.join(BASE_DIR, "../uploads/resume.pdf"),
    os.path.join(BASE_DIR, "../uploads/uploaded_resume.pdf"),
    os.path.join(BASE_DIR, "uploads/25MCA043  Resume.pdf"),
]
pdf_path = next((p for p in possible_paths if os.path.exists(p)), None)

if pdf_path:
    # Extract resume text
    resume_text = extract_text_from_pdf(pdf_path)

    # Extract user's skills
    user_skills = extract_skills(resume_text)

    # Example job skills
    job_skills = [
        "python",
        "sql",
        "machine learning",
        "tensorflow",
        "docker",
        "aws"
    ]

    # Find skill gap
    matching_skills, missing_skills = find_skill_gap(
        user_skills,
        job_skills
    )

    print("\n========== SKILL GAP ANALYSIS ==========\n")
    print("Your Skills:")
    for skill in matching_skills:
        print("✓", skill)

    print("\nSkills You Need:")
    for skill in missing_skills:
        print("✗", skill)

    print("\n========================================")
else:
    print("No test PDF found!")