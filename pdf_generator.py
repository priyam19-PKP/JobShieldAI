from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from pathlib import Path

from reportlab.platypus import (
    Image,
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable
)

# -----------------------------
# Color Theme
# -----------------------------

PRIMARY = HexColor("#1E3A8A")
BLUE = HexColor("#2563EB")
SUCCESS = HexColor("#22C55E")
WARNING = HexColor("#F59E0B")
DANGER = HexColor("#EF4444")
LIGHT = HexColor("#F8FAFC")
TEXT = HexColor("#1F2937")
BORDER = HexColor("#CBD5E1")

# -----------------------------
# Styles
# -----------------------------

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "Title",
    parent=styles["Heading1"],
    alignment=TA_CENTER,
    fontName="Helvetica-Bold",
    fontSize=22,
    textColor=colors.white,
    spaceAfter=8,
)

heading_style = ParagraphStyle(
    "Heading",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=15,
    textColor=PRIMARY,
    spaceAfter=10,
)

normal_style = ParagraphStyle(
    "Normal",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=10,
    leading=18,
    textColor=TEXT,
)

small_style = ParagraphStyle(
    "Small",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=8,
    leading=12,
    alignment=TA_CENTER,
    textColor=colors.grey,
)

# -----------------------------
# Helper Functions
# -----------------------------

def section_heading(title):
    return Paragraph(f"<b>{title}</b>", heading_style)


def divider():
    return HRFlowable(
        width="100%",
        thickness=0.6,
        color=BORDER,
    )


def kpi_card(title, value, bg_color):
    card = Table(
        [[
            Paragraph(
                f"<para align='center'>"
                f"<font color='white'><b>{title}</b></font><br/><br/>"
                f"<font color='white' size='16'><b>{value}</b></font>"
                f"</para>",
                normal_style
            )
        ]],
        colWidths=[170]
    )

    card.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg_color),
        ("TOPPADDING", (0, 0), (-1, -1), 15),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 15),
        ("BOX", (0, 0), (-1, -1), 1, bg_color),
    ]))

    return card
def add_page_number(canvas, doc):
    canvas.saveState()

    canvas.setFont("Helvetica", 9)

    page_num = canvas.getPageNumber()

    canvas.drawRightString(
        560,
        18,
        f"Page {page_num}"
    )

    canvas.restoreState()


# -----------------------------
# Main Function
# -----------------------------

def generate_pdf(
    result,
    confidence,
    risk_score,
    risk_level,
    info,
    warnings,
    explanation,
):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=(595, 842),
        leftMargin=25,
        rightMargin=25,
        topMargin=25,
        bottomMargin=25,
    )

    story = []
    # ==========================================
    # HEADER
    # ==========================================

    logo_path = Path(__file__).parent / "logo.png"
    report_id = f"JSA-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    logo = Image(str(logo_path), width=55, height=55)

    title = Paragraph(
        "<font size='22'><b>JobShieldAI</b></font><br/>"
        "<font size='10'>AI-Powered Fake Job Detection System</font>",
        title_style,
    )

    header = Table(
        [[logo, title]],
        colWidths=[70, 470]
    )

    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PRIMARY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 15),
        ("RIGHTPADDING", (0, 0), (-1, -1), 15),
        ("TOPPADDING", (0, 0), (-1, -1), 15),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 15),
    ]))

    # ==========================================
    # REPORT DETAILS
    # ==========================================

    report_info = [
        ["📄 Report ID", report_id],
        ["📅 Generated", datetime.now().strftime("%d %b %Y %I:%M %p")]
    ]

    info_table = Table(report_info, colWidths=[150, 390])

    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), BLUE),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
        ("BACKGROUND", (1, 0), (1, -1), LIGHT),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(info_table)

    story.append(Spacer(1, 18))

    # ==========================================
    # KPI CARDS
    # ==========================================

    prediction_color = SUCCESS if "Real" in result else DANGER

    if risk_level.upper() == "LOW":
        risk_color = SUCCESS
    elif risk_level.upper() == "MEDIUM":
        risk_color = WARNING
    else:
        risk_color = DANGER

    prediction_card = kpi_card(
        "Prediction",
        result,
        prediction_color
    )

    confidence_card = kpi_card(
        "Confidence",
        f"{confidence:.2f}%",
        BLUE
    )

    risk_card = kpi_card(
        "Risk Score",
        f"{risk_score}/100",
        risk_color
    )

    cards = Table(
        [[prediction_card, confidence_card, risk_card]],
        colWidths=[175, 175, 175]
    )

    cards.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))

    story.append(cards)
    story.append(Spacer(1, 18))

    if "Real" in result:
        verdict_text = "🟢 SAFE JOB"
        verdict_color = SUCCESS
    elif risk_level.upper() == "MEDIUM":
        verdict_text = "🟠 SUSPICIOUS JOB"
        verdict_color = WARNING
    else:
        verdict_text = "🔴 FAKE JOB"
        verdict_color = DANGER

    banner = Table(
        [[Paragraph(
            f"<para align='center'><font size='18' color='white'><b>{verdict_text}</b></font></para>",
            normal_style
        )]],
        colWidths=[540]
    )

    banner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), verdict_color),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))

    story.append(banner)

    story.append(Spacer(1, 20))

    story.append(divider())

    story.append(Spacer(1, 15))

    # ==========================================
    # JOB INFORMATION
    # ==========================================

    story.append(section_heading("📋 Job Information"))

    job_data = [
        ["Company", info.get("Company", "Not Found")],
        ["Position", info.get("Position", "Not Found")],
        ["Location", info.get("Location", "Not Found")],
        ["Salary", info.get("Salary", "Not Found")],
        ["Experience", info.get("Experience", "Not Found")],
        ["Email", info.get("Email", "Not Found")],
        ["Website", info.get("Website", "Not Found")],
    ]

    job_table = Table(
        job_data,
        colWidths=[150, 390]
    )

    job_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), PRIMARY),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
        ("BACKGROUND", (1, 0), (1, -1), LIGHT),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    story.append(job_table)

    story.append(Spacer(1, 20))
    # ==========================================
    # SCAM DETECTION
    # ==========================================

    story.append(section_heading("🚨 Scam Detection"))

    scam_rows = [["Status", "Finding"]]

    for item in warnings:
        if item.startswith("✅"):
            status = "SAFE"
        else:
            status = "WARNING"

        scam_rows.append([status, item])

    scam_table = Table(scam_rows, colWidths=[90, 450])

    style = [
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (1, 1), (-1, -1), LIGHT),
    ]

    for row in range(1, len(scam_rows)):
        if scam_rows[row][0] == "SAFE":
            style.append(("BACKGROUND", (0, row), (0, row), SUCCESS))
            style.append(("TEXTCOLOR", (0, row), (0, row), colors.white))
        else:
            style.append(("BACKGROUND", (0, row), (0, row), WARNING))
            style.append(("TEXTCOLOR", (0, row), (0, row), colors.white))

    scam_table.setStyle(TableStyle(style))

    story.append(scam_table)
    story.append(Spacer(1, 18))

    # ==========================================
    # AI SECURITY ANALYSIS
    # ==========================================

    story.append(section_heading("🤖 AI Security Analysis"))

    ai_box = Table(
        [[Paragraph(explanation.replace("\n", "<br/>"), normal_style)]],
        colWidths=[540]
    )

    ai_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
        ("BOX", (0, 0), (-1, -1), 1, BLUE),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))

    story.append(ai_box)

    story.append(Spacer(1, 20))

    story.append(divider())

    story.append(Spacer(1, 10))

    # ==========================================
    # DISCLAIMER
    # ==========================================
    disclaimer = Paragraph(
        "<b>Disclaimer</b><br/><br/>"
        "This report is generated using Machine Learning and Local AI. "
        "The prediction is intended to assist users in identifying potentially fraudulent job postings. "
        "Always verify recruiter identities, company websites, email domains, interview procedures, "
        "and never share sensitive personal or financial information without proper verification.",
        normal_style,
    )

    story.append(disclaimer)

    story.append(Spacer(1, 20))

    # ==========================================
    # FOOTER
    # ==========================================

    footer = Paragraph(
        "JobShieldAI • AI Powered Fake Job Detection<br/>"
        "Developed by <b>Priyam Prajapati</b><br/>"
        "Department of Artificial Intelligence & Machine Learning<br/>"
        "Viva Institute of Technology",
        small_style,
    )

    story.append(footer)

    # ==========================================
    # BUILD PDF
    # ==========================================

    doc.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )

    pdf = buffer.getvalue()
    buffer.close()

    return pdf