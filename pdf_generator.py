import re
from io import BytesIO
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    Image,
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable
)

# ---------------------------------------------------------
# Color Palette
# ---------------------------------------------------------
C_DARK = HexColor("#0F172A")          # Deep Navy/Charcoal
C_NAVY = HexColor("#1E293B")
C_BLUE = HexColor("#2563EB")          # Accent Blue
C_LIGHT_BLUE = HexColor("#EFF6FF")
C_BORDER_BLUE = HexColor("#BFDBFE")
C_SUCCESS = HexColor("#059669")       # Emerald Green
C_SUCCESS_BG = HexColor("#ECFDF5")
C_SUCCESS_BORDER = HexColor("#A7F3D0")
C_DANGER = HexColor("#DC2626")        # Crimson Red
C_DANGER_BG = HexColor("#FEF2F2")
C_DANGER_BORDER = HexColor("#FECACA")
C_WARNING = HexColor("#D97706")       # Amber
C_WARNING_BG = HexColor("#FFFBEB")
C_WARNING_BORDER = HexColor("#FDE68A")
C_LIGHT = HexColor("#F8FAFC")         # Crisp Off-white
C_TEXT = HexColor("#1E293B")
C_MUTED = HexColor("#64748B")
C_BORDER = HexColor("#E2E8F0")

# ---------------------------------------------------------
# Typography Styles
# ---------------------------------------------------------
styles = getSampleStyleSheet()

style_title = ParagraphStyle(
    "ReportTitle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=13,
    leading=15,
    textColor=colors.white
)

style_subtitle = ParagraphStyle(
    "ReportSubtitle",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8,
    leading=10,
    textColor=HexColor("#94A3B8")
)

style_meta_right = ParagraphStyle(
    "MetaRight",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=7,
    leading=9.5,
    alignment=TA_RIGHT,
    textColor=HexColor("#CBD5E1")
)

style_section_hdr = ParagraphStyle(
    "SectionHeader",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=9,
    leading=11,
    textColor=C_DARK,
    spaceAfter=3
)

style_body = ParagraphStyle(
    "Body",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=7.5,
    leading=10,
    textColor=C_TEXT
)

style_body_bold = ParagraphStyle(
    "BodyBold",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=7.5,
    leading=10,
    textColor=C_DARK
)

style_muted = ParagraphStyle(
    "Muted",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=6.5,
    leading=8.5,
    textColor=C_MUTED
)

style_card_title = ParagraphStyle(
    "CardTitle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=7.5,
    leading=9,
    alignment=TA_CENTER,
    textColor=C_MUTED
)

style_card_val = ParagraphStyle(
    "CardValue",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=15,
    leading=17,
    alignment=TA_CENTER
)

style_card_sub = ParagraphStyle(
    "CardSub",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=6.5,
    leading=8,
    alignment=TA_CENTER,
    textColor=C_MUTED
)

style_badge = ParagraphStyle(
    "Badge",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=7,
    leading=8,
    alignment=TA_CENTER
)

def md_to_reportlab(text):
    """Clean markdown artifacts and convert to ReportLab XML format."""
    if not text:
        return ""
    text = re.sub(r'#{1,4}\s*(.*)', r'<b><font color="#1E3A8A">\1</font></b>', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
    text = re.sub(r'^\s*[-*]\s+', '&bull; ', text, flags=re.MULTILINE)
    text = text.replace('\n', '<br/>')
    text = re.sub(r'(<br/>\s*){3,}', '<br/><br/>', text)
    return text

def add_page_decorations(canvas, doc):
    """Draw professional page borders, header line, and footer numbering."""
    canvas.saveState()
    canvas.setStrokeColor(C_BORDER)
    canvas.setLineWidth(0.6)
    canvas.line(24, 26, 571, 26)
    
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(C_MUTED)
    canvas.drawString(24, 16, "JobShieldAI • Autonomous Cyber Fraud Defense Platform")
    canvas.drawRightString(571, 16, f"Page {doc.page} of 1 • Official Forensic Audit Document")
    canvas.restoreState()

# ---------------------------------------------------------
# Main PDF Generator Function
# ---------------------------------------------------------
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
        pagesize=(595.27, 842.89),
        leftMargin=24,
        rightMargin=24,
        topMargin=18,
        bottomMargin=28,
    )

    story = []
    is_real = "Real" in result
    report_id = f"JSA-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    timestamp_str = datetime.now().strftime("%d %b %Y, %I:%M %p")

    # =========================================================
    # 1. HEADER BANNER
    # =========================================================
    logo_path = Path(__file__).parent / "logo.png"
    if logo_path.exists():
        logo_img = Image(str(logo_path), width=36, height=36)
    else:
        logo_img = Paragraph("<font size='22'>🛡️</font>", style_title)

    title_block = Paragraph(
        "<b><font size='13' color='white'>JobShield<font color='#60A5FA'>AI</font> FORENSIC AUDIT REPORT</font></b><br/>"
        "<font size='7.5' color='#94A3B8'>Autonomous Recruitment Fraud Defense & Threat Intelligence</font>",
        style_title
    )

    meta_block = Paragraph(
        f"<b>AUDIT ID:</b> {report_id}<br/>"
        f"<b>DATE:</b> {timestamp_str}<br/>"
        f"<b>CLASSIFICATION:</b> RESTRICTED / FORENSIC",
        style_meta_right
    )

    header_table = Table(
        [[logo_img, title_block, meta_block]],
        colWidths=[42, 335, 170]
    )
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_DARK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))

    # =========================================================
    # 2. HERO SECURITY VERDICT BANNER
    # =========================================================
    if is_real:
        v_title = "✔ VERIFIED LEGITIMATE JOB • LOW SECURITY RISK"
        v_sub = "Supervised ML classifier and 10 deterministic scam guardrails identified no significant indicators of fraudulent recruitment."
        v_bg = C_SUCCESS_BG
        v_border = C_SUCCESS
        v_text_color = "#065F46"
        badge_text = "PASSED"
        badge_bg = C_SUCCESS
    else:
        v_title = "✖ CRITICAL THREAT DETECTED • HIGH RISK RECRUITMENT FRAUD"
        v_sub = "This posting exhibits high-probability patterns of recruitment fraud, advance-fee scamming, or credential harvesting."
        v_bg = C_DANGER_BG
        v_border = C_DANGER
        v_text_color = "#991B1B"
        badge_text = "FLAGGED"
        badge_bg = C_DANGER

    verdict_content = Paragraph(
        f"<b><font size='10' color='{v_text_color}'>{v_title}</font></b><br/>"
        f"<font size='7.5' color='#475569'>{v_sub}</font>",
        style_body
    )

    badge_table = Table(
        [[Paragraph(f"<para align='center'><font color='white'><b>{badge_text}</b></font></para>", style_badge)]],
        colWidths=[65]
    )
    badge_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), badge_bg),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    verdict_table = Table(
        [[verdict_content, badge_table]],
        colWidths=[460, 75]
    )
    verdict_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), v_bg),
        ("LINEBEFORE", (0, 0), (0, -1), 4, v_border),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.5, C_BORDER),
    ]))
    story.append(verdict_table)
    story.append(Spacer(1, 8))

    # =========================================================
    # 3. 3-KPI METRIC CARDS
    # =========================================================
    pred_color = C_SUCCESS if is_real else C_DANGER
    pred_text = "REAL JOB" if is_real else "FAKE JOB"

    if risk_level.upper() == "LOW":
        risk_color = C_SUCCESS
    elif risk_level.upper() == "MEDIUM":
        risk_color = C_WARNING
    else:
        risk_color = C_DANGER

    def make_kpi(title, value, val_color, subtext, top_color):
        t = Table(
            [
                [Paragraph(title, style_card_title)],
                [Paragraph(f"<font color='{val_color}'>{value}</font>", style_card_val)],
                [Paragraph(subtext, style_card_sub)],
            ],
            colWidths=[174]
        )
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), C_LIGHT),
            ("BOX", (0, 0), (-1, -1), 0.5, C_BORDER),
            ("LINEABOVE", (0, 0), (-1, 0), 2.5, top_color),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))
        return t

    card1 = make_kpi("CLASSIFICATION VERDICT", pred_text, pred_color.hexval(), "XGBoost Classifier Model", pred_color)
    card2 = make_kpi("MODEL CONFIDENCE", f"{confidence:.1f}%", C_BLUE.hexval(), "Class Probability Metric", C_BLUE)
    card3 = make_kpi("THREAT RISK INDEX", f"{risk_score}/100", risk_color.hexval(), f"{risk_level} Risk Category", risk_color)

    cards_row = Table([[card1, card2, card3]], colWidths=[180, 180, 180])
    cards_row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(cards_row)
    story.append(Spacer(1, 10))

    # =========================================================
    # 4. TWO-COLUMN: ENTITY INTELLIGENCE & SCAM GUARDRAILS
    # =========================================================
    email_val = info.get("Email", "Not Found")
    is_suspicious_email = any(d in email_val.lower() for d in ["@gmail.com", "@yahoo.com", "@hotmail.com"])
    trust_label = "Free Webmail (High Risk)" if is_suspicious_email else "Corporate / Verified Domain"
    trust_color = "#DC2626" if is_suspicious_email else "#059669"

    job_rows = [
        [Paragraph("<b>Company</b>", style_body), Paragraph(info.get("Company", "Not Specified"), style_body)],
        [Paragraph("<b>Position</b>", style_body), Paragraph(info.get("Position", "Not Specified"), style_body)],
        [Paragraph("<b>Location</b>", style_body), Paragraph(info.get("Location", "Not Specified"), style_body)],
        [Paragraph("<b>Salary</b>", style_body), Paragraph(info.get("Salary", "Not Specified"), style_body)],
        [Paragraph("<b>Experience</b>", style_body), Paragraph(info.get("Experience", "Not Specified"), style_body)],
        [Paragraph("<b>Email</b>", style_body), Paragraph(info.get("Email", "Not Specified"), style_body)],
        [Paragraph("<b>Domain Trust</b>", style_body), Paragraph(f"<font color='{trust_color}'><b>{trust_label}</b></font>", style_body)],
    ]

    table_entities = Table(job_rows, colWidths=[70, 192])
    table_entities.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), C_LIGHT),
        ("BACKGROUND", (1, 0), (1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, C_BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))

    left_block = [
        Paragraph("📋 <b>Extracted Job Metadata & Domain Trust</b>", style_section_hdr),
        table_entities
    ]

    # Right Column: Scam Guardrail Findings Table with Quotes
    scam_rows = []
    for item in warnings[:7]:
        if item.startswith("✅"):
            stat = "SAFE"
            bg = C_SUCCESS
            clean_text = item.replace("✅", "").strip()
        else:
            stat = "ALERT"
            bg = C_DANGER
            clean_text = item

        b_tab = Table([[Paragraph(f"<para align='center'><font color='white'><b>{stat}</b></font></para>", style_badge)]], colWidths=[42])
        b_tab.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), bg),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        scam_rows.append([b_tab, Paragraph(clean_text, style_body)])

    table_scam = Table(scam_rows, colWidths=[48, 214])
    table_scam.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, C_BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("BACKGROUND", (1, 0), (1, -1), colors.white),
    ]))

    right_block = [
        Paragraph("🚨 <b>Heuristic Threat Guardrails & Evidence</b>", style_section_hdr),
        table_scam
    ]

    col_split = Table(
        [[left_block, right_block]],
        colWidths=[268, 272]
    )
    col_split.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(col_split)
    story.append(Spacer(1, 10))

    # =========================================================
    # 5. AI FORENSIC SECURITY ANALYSIS
    # =========================================================
    story.append(Paragraph("🧠 <b>AI Forensic Security Analysis (LLaMA 3.2 Intelligence)</b>", style_section_hdr))

    formatted_ai = md_to_reportlab(explanation)
    ai_content = Paragraph(formatted_ai, style_body)

    ai_table = Table([[ai_content]], colWidths=[540])
    ai_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.5, C_BORDER_BLUE),
        ("LINEBEFORE", (0, 0), (0, -1), 3.5, C_BLUE),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
    ]))
    story.append(ai_table)
    story.append(Spacer(1, 8))

    # =========================================================
    # 6. CANDIDATE ACTION PROTOCOL
    # =========================================================
    if is_real:
        action_text = (
            "&bull; <b>Verify Listing:</b> Confirm opening directly on the organization's official careers portal.<br/>"
            "&bull; <b>Email Domain Check:</b> Ensure all communications originate from the verified corporate web domain.<br/>"
            "&bull; <b>Zero Fee Rule:</b> Legitimate employers never charge fees for testing, onboarding, or work equipment."
        )
        act_bg = C_SUCCESS_BG
        act_border = C_SUCCESS
    else:
        action_text = (
            "&bull; <b>DO NOT Transfer Funds:</b> Legitimate employers never request deposits or fees for interviews/laptops.<br/>"
            "&bull; <b>Protect Credentials:</b> Do not submit bank details, government IDs, or SSNs without verified contracts.<br/>"
            "&bull; <b>Cease Messaging Apps:</b> Refuse interviews conducted exclusively over WhatsApp, Telegram, or SMS."
        )
        act_bg = C_DANGER_BG
        act_border = C_DANGER

    action_content = Paragraph(action_text, style_body)
    action_table = Table(
        [[Paragraph("<b>Candidate Protective Protocol:</b>", style_body_bold), action_content]],
        colWidths=[120, 420]
    )
    action_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), act_bg),
        ("BOX", (0, 0), (-1, -1), 0.5, act_border),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(action_table)
    story.append(Spacer(1, 8))

    # =========================================================
    # 7. AUDIT SIGNATURE & DISCLAIMER
    # =========================================================
    sign_block = Paragraph(
        "<b>SYSTEM AUDIT SIGNATURE</b><br/>"
        "Platform: <b>JobShieldAI v1.0</b> • Engine: <b>XGBoost + LLaMA 3.2</b><br/>"
        "Principal Developer: <b>Priyam Prajapati</b> • Department of AIML, Viva Institute of Technology",
        style_body
    )
    disclaimer_block = Paragraph(
        "<b>LIMITATION & UNCERTAINTY NOTICE:</b> This assessment is generated via statistical NLP machine learning and local AI inference. "
        "A 'Legitimate' result does not guarantee employer bona fides. Candidates must independently verify employers before disclosing personal data.",
        style_muted
    )

    footer_table = Table(
        [[sign_block, disclaimer_block]],
        colWidths=[270, 270]
    )
    footer_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(footer_table)

    # Build PDF with custom canvas decorations
    doc.build(
        story,
        onFirstPage=add_page_decorations,
        onLaterPages=add_page_decorations,
    )

    pdf = buffer.getvalue()
    buffer.close()
    return pdf
