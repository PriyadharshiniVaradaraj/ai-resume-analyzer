import os
from resume_parser import extract_text_from_pdf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
possible_paths = [
    os.path.join(BASE_DIR, "../uploads/resume.pdf"),
    os.path.join(BASE_DIR, "../uploads/uploaded_resume.pdf"),
    os.path.join(BASE_DIR, "uploads/25MCA043  Resume.pdf"),
]
pdf_path = next((p for p in possible_paths if os.path.exists(p)), None)

if pdf_path:
    text = extract_text_from_pdf(pdf_path)
    print("========== RESUME TEXT ==========")
    print(text[:1000])
else:
    print("No test PDF found!")