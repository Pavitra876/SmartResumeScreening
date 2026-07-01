"""
reports/pdf_report.py
Generates a downloadable PDF report of the ATS analysis results.
"""

from fpdf import FPDF
from datetime import date


class ResumeReport(FPDF):
    def header(self):
        self.set_fill_color(15, 23, 41)
        self.rect(0, 0, 210, 22, "F")
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(248, 250, 252)
        self.set_xy(10, 6)
        self.cell(0, 10, "Smart Resume Screening - Analysis Report", ln=False)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 10, f"Generated on {date.today()} · Page {self.page_no()}", align="C")


def _section_title(pdf, title):
    pdf.set_fill_color(16, 185, 129)
    pdf.rect(10, pdf.get_y(), 4, 7, "F")
    pdf.set_x(17)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(15, 23, 41)
    pdf.cell(0, 7, title, ln=True)
    pdf.ln(2)


def _skill_chips(pdf, skills, color_rgb):
    pdf.set_font("Helvetica", "", 10)
    x_start = 12
    x = x_start
    y = pdf.get_y()
    chip_height = 7
    chip_padding_x = 4

    for skill in skills:
        chip_width = pdf.get_string_width(skill) + chip_padding_x * 2
        if x + chip_width > 195:
            x = x_start
            y += chip_height + 2
        r, g, b = color_rgb
        pdf.set_fill_color(r, g, b)
        pdf.set_draw_color(r, g, b)
        pdf.set_text_color(15, 23, 41)
        pdf.set_xy(x, y)
        pdf.cell(chip_width, chip_height, skill, border=1, fill=True, align="C")
        x += chip_width + 3

    pdf.ln(chip_height + 6)


def generate_report(user_name, resume_name, role_name, ats_score,
                    matched_skills, missing_skills, verdict, roadmap):
    pdf = ResumeReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_margins(10, 28, 10)

    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(15, 23, 41)
    pdf.cell(0, 10, user_name, ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 6, f"Resume: {resume_name}  ·  Target Role: {role_name}", ln=True)
    pdf.ln(4)

    score_color = (16, 185, 129) if ats_score >= 60 else (245, 158, 11) if ats_score >= 35 else (239, 68, 68)
    pdf.set_fill_color(*score_color)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 28)
    pdf.cell(50, 18, f"{ats_score:.0f}%", fill=True, align="C")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 116, 139)
    pdf.set_x(65)
    pdf.cell(0, 18, "ATS SCORE", ln=True)
    pdf.ln(6)

    _section_title(pdf, "Overall Assessment")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(30, 41, 59)
    pdf.multi_cell(0, 6, verdict)
    pdf.ln(4)

    _section_title(pdf, f"Matched Skills ({len(matched_skills)})")
    if matched_skills:
        _skill_chips(pdf, matched_skills, (209, 250, 229))
    else:
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 6, "No matching skills found.", ln=True)
    pdf.ln(2)

    _section_title(pdf, f"Skill Gap ({len(missing_skills)} missing)")
    if missing_skills:
        _skill_chips(pdf, missing_skills, (254, 243, 199))
    else:
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 6, "No skill gaps - great fit!", ln=True)
    pdf.ln(2)

    if roadmap:
        _section_title(pdf, "Career Roadmap - Priority Skills to Learn")
        for i, item in enumerate(roadmap, 1):
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(15, 23, 41)
            pdf.cell(0, 7, f"{i}. {item['skill']}", ln=True)
            if item.get("resources"):
                for title, url in item["resources"]:
                    pdf.set_font("Helvetica", "", 9)
                    pdf.set_text_color(100, 116, 139)
                    pdf.set_x(16)
                    pdf.cell(0, 5, f"-> {title}", ln=True)
                    pdf.set_text_color(16, 185, 129)
                    pdf.set_x(16)
                    pdf.cell(0, 5, url, ln=True)
            pdf.ln(2)

    return bytes(pdf.output())