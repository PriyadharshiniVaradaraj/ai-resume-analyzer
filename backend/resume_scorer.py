def calculate_resume_score(
    skills,
    education,
    experience,
    projects,
    certifications
):

    # Skills: maximum 40 marks
    skill_score = min(len(skills) / 10 * 40, 40)

    # Education: 15 marks
    education_score = 15 if education else 0

    # Experience: 20 marks
    experience_score = 20 if experience else 0

    # Projects: 15 marks
    project_score = 15 if projects else 0

    # Certifications: 10 marks
    certification_score = 10 if certifications else 0

    total_score = (
        skill_score
        + education_score
        + experience_score
        + project_score
        + certification_score
    )

    return round(total_score, 2)