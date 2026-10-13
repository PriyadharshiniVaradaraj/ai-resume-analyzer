import re


SKILLS = [
    "python",
    "java",
    "c++",
    "sql",
    "machine learning",
    "deep learning",
    "tensorflow",
    "pytorch",
    "power bi",
    "excel",
    "aws",
    "azure",
    "docker",
    "kubernetes",
    "linux",
    "html",
    "css",
    "javascript",
    "react",
    "node.js",
    "git",
    "github",
    "nlp",
    "statistics",
    "data analysis",
    "tableau",
    "mongodb",
    "mysql"
]


def extract_skills(text):

    text = text.lower()

    detected_skills = []

    for skill in SKILLS:

        if skill in text:
            detected_skills.append(skill)

    return detected_skills