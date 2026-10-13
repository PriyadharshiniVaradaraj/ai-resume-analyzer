def find_skill_gap(user_skills, job_skills):

    # Convert everything to lowercase
    user_skills = [skill.lower().strip() for skill in user_skills]
    job_skills = [skill.lower().strip() for skill in job_skills]

    # Find skills that the user already has
    matching_skills = []

    for skill in job_skills:
        if skill in user_skills:
            matching_skills.append(skill)

    # Find skills that are missing
    missing_skills = []

    for skill in job_skills:
        if skill not in user_skills:
            missing_skills.append(skill)

    return matching_skills, missing_skills