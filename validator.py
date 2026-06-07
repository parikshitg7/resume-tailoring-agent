from typing import Dict, Any


# =====================================================
# HELPERS
# =====================================================

def safe_string(value):
    if value is None:
        return ""

    return str(value).strip()


def trim_bullets(bullets, max_count=4):

    if not bullets:
        return []

    cleaned = []

    for bullet in bullets[:max_count]:

        bullet = safe_string(bullet)

        if bullet:
            cleaned.append(bullet)

    return cleaned


# =====================================================
# VALIDATION NODE
# =====================================================

def validate_resume_node(state: dict) -> Dict[str, Any]:

    print("\n--- NODE: VALIDATING RESUME DATA ---")

    resume_data = state.get("structured_resume_data", {})

    # =================================================
    # SUMMARY
    # =================================================

    summary = safe_string(
        resume_data.get("summary", "")
    )

    if len(summary) > 500:
        summary = summary[:500]

    resume_data["summary"] = summary

    # =================================================
    # SKILLS
    # =================================================

    skills = resume_data.get("skills", [])

    validated_skills = []

    for skill_group in skills:

        category = safe_string(
            skill_group.get("category", "")
        )

        skill_items = skill_group.get(
            "skills",
            []
        )

        if not category:
            continue

        cleaned_items = []

        for item in skill_items:

            item = safe_string(item)

            if item:
                cleaned_items.append(item)

        if cleaned_items:

            validated_skills.append({
                "category": category,
                "skills": cleaned_items
            })

    resume_data["skills"] = validated_skills

    # =================================================
    # PROJECTS
    # =================================================

    projects = resume_data.get("projects", [])

    validated_projects = []

    for project in projects[:2]:

        title = safe_string(
            project.get("title", "")
        )

        if not title:
            continue

        validated_projects.append({
            "title": title,
            "tech_stack": safe_string(
                project.get("tech_stack", "")
            ),
            "bullets": trim_bullets(
                project.get("bullets", []),
                4
            )
        })

    resume_data["projects"] = validated_projects

    # =================================================
    # EXPERIENCE
    # =================================================

    experience = resume_data.get(
        "experience",
        []
    )

    validated_experience = []

    for exp in experience:

        title = safe_string(
            exp.get("job_title", "")
        )

        company = safe_string(
            exp.get("company", "")
        )

        if not title and not company:
            continue

        validated_experience.append({
            "job_title": title,
            "company": company,
            "duration": safe_string(
                exp.get("duration", "")
            ),
            "bullets": trim_bullets(
                exp.get("bullets", []),
                4
            )
        })

    resume_data["experience"] = validated_experience

    # =================================================
    # CERTIFICATIONS
    # =================================================

    certifications = resume_data.get(
        "certifications",
        []
    )

    resume_data["certifications"] = [
        safe_string(cert)
        for cert in certifications
        if safe_string(cert)
    ]

    # =================================================
    # ACHIEVEMENTS
    # =================================================

    achievements = resume_data.get(
        "achievements",
        []
    )

    resume_data["achievements"] = [
        safe_string(item)
        for item in achievements
        if safe_string(item)
    ]

    # =================================================
    # EDUCATION
    # =================================================

    education = resume_data.get(
        "education",
        []
    )

    validated_education = []

    for edu in education:

        degree = safe_string(
            edu.get("degree", "")
        )

        university = safe_string(
            edu.get("university", "")
        )

        if not degree and not university:
            continue

        validated_education.append({
            "degree": degree,
            "university": university,
            "location": safe_string(
                edu.get("location", "")
            ),
            "duration": safe_string(
                edu.get("duration", "")
            ),
            "score": safe_string(
                edu.get("score", "")
            )
        })

    resume_data["education"] = validated_education

    # =================================================
    # PERSONAL INFO
    # =================================================

    personal = resume_data.get(
        "personal_info",
        {}
    )

    resume_data["personal_info"] = {
        "name": safe_string(personal.get("name", "")),
        "email": safe_string(personal.get("email", "")),
        "phone": safe_string(personal.get("phone", "")),
        "linkedin": safe_string(personal.get("linkedin", "")),
        "github": safe_string(personal.get("github", "")),
        "location": safe_string(personal.get("location", ""))
    }

    print("--- VALIDATION COMPLETE ---")

    return {
        "structured_resume_data": resume_data
    }