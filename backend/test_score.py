import os
from resume_parser import extract_text_from_pdf
from skill_extractor import extract_skills
from resume_scorer import calculate_resume_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
possible_paths = [
    os.path.join(BASE_DIR, "../uploads/resume.pdf"),
    os.path.join(BASE_DIR, "../uploads/uploaded_resume.pdf"),
    os.path.join(BASE_DIR, "uploads/25MCA043  Resume.pdf"),
]
pdf_path = next((p for p in possible_paths if os.path.exists(p)), None)

if pdf_path:
    # Extract resume text
    text = extract_text_from_pdf(pdf_path)

    # Extract skills
    skills = extract_skills(text)

    # Convert resume text to lowercase
    text_lower = text.lower()

    # Check education
    education = any(
        word in text_lower
        for word in [
            "b.tech",
            "b.e",
            "bachelor",
            "m.tech",
            "m.e",
            "master"
        ]
    )

    # Check experience
    experience = any(
        word in text_lower
        for word in [
            "experience",
            "internship",
            "worked"
        ]
    )

    # Check projects
    projects = "project" in text_lower

    # Check certifications
    certifications = any(
        word in text_lower
        for word in [
            "certification",
            "certificate"
        ]
    )

    # Calculate score
    score = calculate_resume_score(
        skills,
        education,
        experience,
        projects,
        certifications
    )

    print("\n========== RESUME ANALYSIS ==========")
    print("\nDetected Skills:")
    for skill in skills:
        print("✓", skill)

    print("\nEducation:", education)
    print("Experience:", experience)
    print("Projects:", projects)
    print("Certifications:", certifications)

    print("\n=====================================")
    print("RESUME SCORE:", score, "/ 100")
    print("=====================================")
else:
    print("No test PDF found!")