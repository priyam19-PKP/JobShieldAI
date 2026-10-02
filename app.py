import re
import streamlit as st
from datetime import datetime
from pathlib import Path

from predict import predict_job
from ollama_ai import explain_prediction
from extractor import extract_job_info, verify_domain_consistency, calculate_profile_completeness
from scam_detector import detect_scam_details, detect_scam_signs, highlight_evidence_in_text
from risk_score import calculate_risk_score
from pdf_generator import generate_pdf

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="JobShieldAI • AI-Powered Job Fraud Defense",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Load Custom Stylesheet
# ---------------------------------------------------------
css_file = Path(__file__).parent / "style.css"
if css_file.exists():
    with open(css_file, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Preset Sample Job Postings
# ---------------------------------------------------------
SAMPLE_SCAM = """Company: FastTech Careers Global
Position: Remote Data Entry & Administrative Assistant
Location: Work from Home / Any Location
Salary: Earn $4,500 per week ($90/hr)
Experience: No experience required, immediate joining!
Email: careers.fasttech@gmail.com
Website: http://fasttech-careers.online

We have an urgent hiring need for 10 remote assistants. Immediate joining promise with no interview required!
Selected candidates will receive a free laptop, home office allowance, and sign-on bonus.
To confirm your registration, candidates must pay a refundable security deposit / registration fee of $50 via wire or crypto.
Contact our HR manager directly on WhatsApp at +1-555-0199 for quick onboarding and bank details verification."""

SAMPLE_LEGIT = """Company: Google LLC
Position: Senior Software Engineer, Cloud Platforms
Location: Mountain View, CA (Hybrid)
Salary: $165,000 - $210,000 per year + equity + benefits
Experience: 5+ years of software engineering experience
Email: recruiting@google.com
Website: https://careers.google.com

Google is looking for a Senior Software Engineer to design, scale, and maintain mission-critical cloud infrastructure.
Responsibilities:
- Build highly scalable microservices using Python, Go, or Java.
- Collaborate with cross-functional product and infrastructure security teams.
Requirements:
- BS or MS in Computer Science or equivalent practical experience.
- 5+ years of hands-on software development experience with distributed systems.
Qualified candidates will participate in technical evaluations and architectural interviews with Google engineering staff.
Applications must be submitted exclusively via careers.google.com."""

SAMPLE_SUSPICIOUS = """Company: Apex Digital Media
Position: Freelance Content Transcriber
Location: Remote
Salary: Earn $1,200 per week
Experience: 1 year
Email: hr-team@apexcreative.xyz
Website: http://apex-global.top

Urgent hiring for flexible online project assistance!
Immediate start with fast cash payouts.
Send your resume to our recruiter email or message on Telegram for instant screening."""

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "job_text" not in st.session_state:
    st.session_state["job_text"] = ""
if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None
if "scan_history" not in st.session_state:
    st.session_state["scan_history"] = []

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
with st.sidebar:
    logo_path = Path(__file__).parent / "logo.png"
    if logo_path.exists():
        st.image(str(logo_path), width=130)

    st.markdown("""
    <div style="margin-top: 4px; margin-bottom: 20px;">
        <h2 style="margin: 0; font-size: 22px; color: #F8FAFC;">JobShield<span style="color:#3B82F6;">AI</span></h2>
        <p style="color: #CBD5E1; font-size: 13.5px; margin: 4px 0 0 0;">
            Next-Gen Job Fraud Defense & Threat Intelligence
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 15px 0;'>", unsafe_allow_html=True)

    # Core Features
    st.markdown("<p style='font-size: 12px; font-weight: 700; color: #CBD5E1; text-transform: uppercase; letter-spacing: 0.05em;'>Defense Modules</p>", unsafe_allow_html=True)

    features = [
        ("🤖", "XGBoost ML Classifier (98.6%)"),
        ("⚡", "Sub-Second Fast Engine"),
        ("🔍", "Interactive Evidence Highlighter"),
        ("🌐", "Domain & Webmail Verification"),
        ("🚨", "10 Heuristic Scam Guardrails"),
        ("🧠", "LLaMA 3.2 On-Device AI"),
        ("📜", "Session Scan History Memory"),
        ("📄", "Forensic Audit PDF Export")
    ]

    for icon, label in features:
        st.markdown(f"""
        <div class="feature-chip">
            <span style="font-size: 16px;">{icon}</span>
            <span>{label}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 18px 0;'>", unsafe_allow_html=True)

    # System Diagnostics
    st.markdown("<p style='font-size: 12px; font-weight: 700; color: #CBD5E1; text-transform: uppercase; letter-spacing: 0.05em;'>System Architecture</p>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background: rgba(17,24,39,0.8); border: 1px solid rgba(255,255,255,0.10); border-radius: 12px; padding: 14px; font-size: 13px; line-height: 1.8;">
        <div><span style="color:#10B981;">●</span> <b>Classifier:</b> XGBoost Model (Active)</div>
        <div><span style="color:#10B981;">●</span> <b>Local LLM:</b> LLaMA 3.2 (Optimized)</div>
        <div><span style="color:#10B981;">●</span> <b>Guardrails:</b> 10 Deterministic Rules</div>
        <div><span style="color:#3B82F6;">●</span> <b>Privacy:</b> 100% On-Device Inference</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 18px 0;'>", unsafe_allow_html=True)

    # Developer Card
    st.markdown("""
    <div class="dev-card">
        <div style="font-size: 26px; margin-bottom: 6px;">👨‍💻</div>
        <h4 style="margin: 0; font-size: 16px; color: #F8FAFC;">Priyam Prajapati</h4>
        <p style="font-size: 13px; color: #CBD5E1; margin: 4px 0 2px 0;">AIML Department</p>
        <p style="font-size: 12px; color: #94A3B8; margin: 0;">Viva Institute of Technology</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Main Page Header & Hero
# ---------------------------------------------------------
header_col1, header_col2 = st.columns([1, 6], vertical_alignment="center")

with header_col1:
    if logo_path.exists():
        st.image(str(logo_path), width=95)
    else:
        st.markdown("<div style='font-size: 60px;'>🛡️</div>", unsafe_allow_html=True)

with header_col2:
    st.markdown("""
    <div style="padding-left: 5px;">
        <h1 style="margin: 0; font-size: 34px; font-weight: 800; letter-spacing: -0.02em;">
            JobShield<span style="color:#3B82F6;">AI</span>
        </h1>
        <p style="margin: 3px 0 0 0; color: #CBD5E1; font-size: 15.5px;">
            AI-Powered Job Fraud Defense • Machine Learning & Forensic Threat Intelligence
        </p>
    </div>
    """, unsafe_allow_html=True)

# Status Bar
st.markdown("""
<div class="status-bar-container">
    <div style="display: flex; align-items: center; font-size: 14px; color: #E2E8F0;">
        <span class="status-indicator-dot"></span>
        <b>System Shield Active</b> &nbsp;•&nbsp; Ready to scan postings for recruitment fraud
    </div>
    <div style="display: flex; gap: 18px; font-size: 13px; color: #CBD5E1;">
        <span>🔒 Zero Data Retention</span>
        <span>⚡ Ultra-Fast Analysis</span>
        <span>🔍 Evidence Quoting</span>
        <span>📄 Forensic PDF Audit</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Input Section (Clean & Direct Paste)
# ---------------------------------------------------------
st.markdown("<h3 style='margin-bottom: 4px; font-size: 20px;'>📄 Job Posting Inspection</h3>", unsafe_allow_html=True)
st.markdown("<p style='color: #CBD5E1; font-size: 14px; margin-bottom: 14px;'>Paste any job description, email invitation, or offer letter below to analyze legitimacy, extract evidence, and generate an audit report.</p>", unsafe_allow_html=True)

preset_col1, preset_col2, preset_col3, preset_col4 = st.columns([1.2, 1.2, 1.2, 0.8])

with preset_col1:
    if st.button("🚨 Load Scam Sample", use_container_width=True, help="Load an offer with registration fees, WhatsApp interview, and Gmail recruiter"):
        st.session_state["job_text"] = SAMPLE_SCAM
        st.session_state["analysis_result"] = None
        st.rerun()

with preset_col2:
    if st.button("✅ Load Verified Sample", use_container_width=True, help="Load an authentic corporate engineering job with verified domain"):
        st.session_state["job_text"] = SAMPLE_LEGIT
        st.session_state["analysis_result"] = None
        st.rerun()

with preset_col3:
    if st.button("⚠️ Load Suspicious Sample", use_container_width=True, help="Load a freelance posting with Telegram contact and urgency"):
        st.session_state["job_text"] = SAMPLE_SUSPICIOUS
        st.session_state["analysis_result"] = None
        st.rerun()

with preset_col4:
    if st.button("🗑️ Clear", use_container_width=True, help="Clear input text and previous results"):
        st.session_state["job_text"] = ""
        st.session_state["analysis_result"] = None
        st.rerun()

job_description = st.text_area(
    label="Job Posting Text",
    value=st.session_state["job_text"],
    height=210,
    placeholder="Paste the full job posting, email invitation, or LinkedIn/Indeed description here...",
    label_visibility="collapsed"
)

# Text Statistics & Engine Mode Bar
char_count = len(job_description)
word_count = len(job_description.split()) if job_description.strip() else 0

col_meta, col_mode = st.columns([1.3, 1.7], vertical_alignment="center")

with col_meta:
    st.markdown(f"""
    <div style="font-size: 13px; color: #94A3B8; margin-bottom: 12px;">
        Words: <b style="color: #F8FAFC;">{word_count}</b> &nbsp;•&nbsp; Characters: <b style="color: #F8FAFC;">{char_count}</b>
    </div>
    """, unsafe_allow_html=True)

with col_mode:
    engine_mode = st.radio(
        label="Engine Mode",
        options=["⚡ Fast Instant Mode (< 0.1s)", "🧠 Deep LLaMA 3.2 AI (~1.5s)"],
        horizontal=True,
        label_visibility="collapsed"
    )

use_llm = "LLaMA" in engine_mode

# Primary Analysis Action Button
analyze = st.button(
    "🛡️ Run JobShield Security Analysis",
    use_container_width=True,
    type="primary"
)

# ---------------------------------------------------------
# Analysis Pipeline Execution
# ---------------------------------------------------------
if analyze:
    if not job_description.strip():
        st.warning("⚠️ Please paste a job description or select one of the sample presets above.")
        st.stop()

    with st.spinner("⚡ Running XGBoost classification, heuristic guardrails, and domain verification..."):
        # 1. ML Prediction (< 0.02s)
        result, confidence = predict_job(job_description)
        confidence = float(confidence)

        # 2. Extract Job Entities & Profile Completeness
        info = extract_job_info(job_description)
        domain_check = verify_domain_consistency(info)
        completeness = calculate_profile_completeness(info)

        # 3. Structured Scam Detection Rules with Quotes
        scam_details = detect_scam_details(job_description)
        warnings = detect_scam_signs(job_description)

        # 4. In-Text Evidence Highlighting
        highlighted_html = highlight_evidence_in_text(job_description, scam_details)

        # 5. Dynamic Risk Score Calculation
        risk_score, risk_level = calculate_risk_score(result, warnings)

        # 6. AI Generative Explanation
        explanation = explain_prediction(job_description, result, use_llm=use_llm)

        # 7. Generate Forensic PDF Report
        pdf = generate_pdf(
            result,
            confidence,
            risk_score,
            risk_level,
            info,
            warnings,
            explanation
        )

        # Create Record
        scan_record = {
            "id": f"JSA-{datetime.now().strftime('%H%M%S')}",
            "timestamp": datetime.now().strftime("%I:%M %p"),
            "result": result,
            "confidence": confidence,
            "info": info,
            "domain_check": domain_check,
            "completeness": completeness,
            "scam_details": scam_details,
            "warnings": warnings,
            "highlighted_html": highlighted_html,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "explanation": explanation,
            "pdf": pdf,
            "job_description": job_description
        }

        # Store in session state
        st.session_state["analysis_result"] = scan_record

        # Prepend to Scan History
        st.session_state["scan_history"].insert(0, scan_record)
        if len(st.session_state["scan_history"]) > 10:
            st.session_state["scan_history"].pop()

# ---------------------------------------------------------
# Render Results (from session state)
# ---------------------------------------------------------
if st.session_state.get("analysis_result"):
    data = st.session_state["analysis_result"]
    result = data["result"]
    confidence = data["confidence"]
    info = data["info"]
    domain_check = data.get("domain_check", verify_domain_consistency(info))
    completeness = data.get("completeness", calculate_profile_completeness(info))
    scam_details = data.get("scam_details", [])
    warnings = data["warnings"]
    highlighted_html = data.get("highlighted_html", "")
    risk_score = data["risk_score"]
    risk_level = data["risk_level"]
    explanation = data["explanation"]
    pdf = data["pdf"]
    analyzed_text = data["job_description"]

    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
    is_real = "Real" in result

    # 1. Hero Verdict Banner
    if is_real:
        st.markdown(f"""
        <div class="verdict-banner-safe">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 15px;">
                <div style="display: flex; align-items: center; gap: 18px;">
                    <div style="font-size: 46px; filter: drop-shadow(0 0 12px rgba(16,185,129,0.5));">🛡️</div>
                    <div>
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <h2 style="margin: 0; font-size: 26px; color: #34D399 !important;">VERIFIED LEGITIMATE JOB</h2>
                            <span class="scam-badge-pill pill-safe">AUTHENTIC LISTING</span>
                        </div>
                        <p style="margin: 6px 0 0 0; color: #A7F3D0; font-size: 15px;">
                            The machine learning classifier and scam guardrails found no significant indicators of fraudulent recruitment.
                        </p>
                    </div>
                </div>
                <div style="text-align: right; background: rgba(16,185,129,0.18); border: 1.5px solid rgba(16,185,129,0.4); padding: 12px 22px; border-radius: 14px;">
                    <span style="font-size: 11.5px; text-transform: uppercase; color: #6EE7B7; font-weight: 700; letter-spacing: 0.05em;">Security Clearance</span>
                    <div style="font-size: 24px; font-weight: 800; color: #ECFDF5; font-family: 'JetBrains Mono', monospace;">LOW RISK</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="verdict-banner-danger">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 15px;">
                <div style="display: flex; align-items: center; gap: 18px;">
                    <div style="font-size: 46px; filter: drop-shadow(0 0 12px rgba(239,68,68,0.5));">🚨</div>
                    <div>
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <h2 style="margin: 0; font-size: 26px; color: #F87171 !important;">HIGH-RISK SCAM DETECTED</h2>
                            <span class="scam-badge-pill pill-danger">FRAUD WARNING</span>
                        </div>
                        <p style="margin: 6px 0 0 0; color: #FECACA; font-size: 15px;">
                            This job posting exhibits high-probability patterns of recruitment fraud, advance-fee scamming, or credential harvesting.
                        </p>
                    </div>
                </div>
                <div style="text-align: right; background: rgba(239,68,68,0.18); border: 1.5px solid rgba(239,68,68,0.4); padding: 12px 22px; border-radius: 14px;">
                    <span style="font-size: 11.5px; text-transform: uppercase; color: #FCA5A5; font-weight: 700; letter-spacing: 0.05em;">Threat Severity</span>
                    <div style="font-size: 24px; font-weight: 800; color: #FEF2F2; font-family: 'JetBrains Mono', monospace;">{risk_level} RISK</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Epistemic Uncertainty & Limitation Notice
    st.markdown("""
    <div class="uncertainty-banner">
        <span style="font-size: 20px;">ℹ️</span>
        <div>
            <b>Assessment Transparency & Limitation Notice:</b> This result is an automated statistical NLP evaluation based strictly on textual evidence. An authentic classification is not a guarantee of employer legitimacy. Always independently verify offers via official corporate channels.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Key Metrics Row
    kpi1, kpi2, kpi3 = st.columns(3)

    with kpi1:
        card_class = "kpi-card-safe" if is_real else "kpi-card-danger"
        text_color = "#10B981" if is_real else "#EF4444"
        verdict_icon = "✅" if is_real else "❌"
        verdict_status = "REAL JOB" if is_real else "FAKE JOB"

        st.markdown(f"""
        <div class="kpi-card {card_class}">
            <div class="kpi-title">Classification Decision</div>
            <div class="kpi-value" style="color: {text_color};">{verdict_icon} {verdict_status}</div>
            <div class="kpi-subtext">XGBoost Supervised Gradient Boosted Classifier</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi2:
        st.markdown(f"""
        <div class="kpi-card kpi-card-primary">
            <div class="kpi-title">Model Confidence Score</div>
            <div class="kpi-value" style="color: #60A5FA;">{confidence:.1f}%</div>
            <div class="kpi-subtext">Statistical class probability (XGBoost logloss)</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi3:
        if risk_level == "LOW":
            r_card_class = "kpi-card-safe"
            r_color = "#10B981"
            r_icon = "🟢"
        elif risk_level == "MEDIUM":
            r_card_class = "kpi-card-warning"
            r_color = "#F59E0B"
            r_icon = "🟠"
        else:
            r_card_class = "kpi-card-danger"
            r_color = "#EF4444"
            r_icon = "🔴"

        st.markdown(f"""
        <div class="kpi-card {r_card_class}">
            <div class="kpi-title">Composite Threat Risk Score</div>
            <div class="kpi-value" style="color: {r_color};">{r_icon} {risk_score}<span style="font-size: 19px; color: #94A3B8;">/100</span></div>
            <div class="kpi-subtext">Calculated via ML penalty + 10 heuristic rules</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # Structured 6-Tab Deep Dive Workspace
    # ---------------------------------------------------------
    tab_summary, tab_signals, tab_highlight, tab_entities, tab_ai, tab_export = st.tabs([
        "📊 Executive Summary",
        "🚨 Scam Evidence & Guardrails",
        "🔍 Evidence Inspector (Text)",
        "🏢 Extracted Intelligence",
        "🧠 AI Forensics (LLaMA 3.2)",
        "📄 Export & Audit Report"
    ])

    # --- TAB 1: EXECUTIVE SUMMARY ---
    with tab_summary:
        st.markdown("<div style='padding-top: 15px;'></div>", unsafe_allow_html=True)

        col_left, col_right = st.columns([1.2, 1])

        with col_left:
            st.markdown("#### 📈 Threat Score Assessment")
            st.progress(risk_score / 100)

            if risk_level == "LOW":
                st.markdown("""
                <div style="background: rgba(16,185,129,0.12); border-left: 4px solid #10B981; padding: 14px 18px; border-radius: 10px; margin-top: 12px; font-size: 14px;">
                    <b style="color: #6EE7B7;">Low Security Risk:</b> This job posting conforms to legitimate recruiting formats and standard compensation structures.
                </div>
                """, unsafe_allow_html=True)
            elif risk_level == "MEDIUM":
                st.markdown("""
                <div style="background: rgba(245,158,11,0.12); border-left: 4px solid #F59E0B; padding: 14px 18px; border-radius: 10px; margin-top: 12px; font-size: 14px;">
                    <b style="color: #FCD34D;">Moderate Caution Advised:</b> Ambiguous phrasing or atypical contact channels were detected. Proceed with independent employer verification.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: rgba(239,68,68,0.12); border-left: 4px solid #EF4444; padding: 14px 18px; border-radius: 10px; margin-top: 12px; font-size: 14px;">
                    <b style="color: #FCA5A5;">Critical Risk Warning:</b> Multiple predatory scam patterns detected. High probability of advance-fee fraud or credential harvesting.
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
            st.markdown("#### 🔍 Threat Evidence Breakdown")
            st.markdown(f"""
            - **Decision:** `{result}` ({confidence:.1f}% statistical model confidence)
            - **Risk Calculation:** `{risk_score}/100` ({risk_level} Risk Category)
            - **Violations Triggered:** `{len(scam_details)} predatory indicator(s) confirmed`
            - **Metadata Completeness:** `{completeness['found']}/{completeness['total']} fields extracted ({completeness['percentage']}%)`
            - **Domain Authenticity:** `{domain_check['badge']}`
            """)

        with col_right:
            st.markdown("#### 🛡️ Candidate Protective Protocol")
            if is_real:
                st.markdown("""
                <div class="glass-panel">
                    <p style="font-weight: 700; color: #34D399; margin-top: 0; font-size: 15px;">Standard Verification Checklist:</p>
                    <ul style="padding-left: 20px; margin-bottom: 0; color: #E2E8F0; font-size: 14px; line-height: 1.85;">
                        <li>Verify this opening directly on the company's verified careers portal before applying.</li>
                        <li>Communicate exclusively via official corporate domain email addresses.</li>
                        <li>Confirm the recruiter's identity on LinkedIn or through company switchboards.</li>
                        <li>Never share bank account credentials or government IDs during initial stages.</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="glass-panel" style="border-color: rgba(239,68,68,0.4);">
                    <p style="font-weight: 700; color: #F87171; margin-top: 0; font-size: 15px;">Immediate Defensive Measures:</p>
                    <ul style="padding-left: 20px; margin-bottom: 0; color: #E2E8F0; font-size: 14px; line-height: 1.85;">
                        <li><b>DO NOT send money:</b> Legitimate employers never charge fees for onboarding or hardware.</li>
                        <li><b>DO NOT provide banking info:</b> Scammers use fake direct-deposit forms for wire fraud.</li>
                        <li><b>Cease WhatsApp/Telegram chats:</b> Insist on verified video or office interviews.</li>
                        <li><b>Report the listing:</b> Flag this post on the platform where you encountered it.</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

    # --- TAB 2: SCAM EVIDENCE & GUARDRAILS ---
    with tab_signals:
        st.markdown("<div style='padding-top: 15px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 🚨 Heuristic Guardrails with Quoted Evidence")
        st.caption("JobShield verifies each posting against 10 zero-tolerance scam patterns and extracts exact supporting quotes directly from the text.")

        if not scam_details:
            st.markdown("""
            <div class="scam-detail-safe">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="font-size: 22px;">🛡️</span>
                        <div>
                            <b style="color: #6EE7B7; font-size: 15px;">No Predatory Scam Patterns Detected</b>
                            <div style="color: #A7F3D0; font-size: 13.5px; margin-top: 2px;">The text was evaluated against all 10 guardrails and passed clean.</div>
                        </div>
                    </div>
                    <span class="scam-badge-pill pill-safe">ALL PASSED</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for item in scam_details:
                st.markdown(f"""
                <div class="scam-detail-card">
                    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <span style="font-size: 24px;">{item['icon']}</span>
                            <div>
                                <b style="color: #F87171; font-size: 15.5px;">{item['rule']}</b>
                                <div style="color: #CBD5E1; font-size: 13px; margin-top: 2px;">{item['explanation']}</div>
                            </div>
                        </div>
                        <span class="scam-badge-pill pill-danger">{item['severity']}</span>
                    </div>
                    <div class="scam-quote-box">
                        📌 <b>Quoted Evidence:</b> "{item['quote']}"
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # --- TAB 3: EVIDENCE INSPECTOR (TEXT HIGHLIGHTING) ---
    with tab_highlight:
        st.markdown("<div style='padding-top: 15px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 🔍 Interactive Evidence Inspector")
        st.caption("Review the full submitted job posting with all detected scam phrases highlighted in red. Hover over any highlighted term to inspect.")

        st.markdown(f"""
        <div class="evidence-doc-viewer">
{highlighted_html}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 12px; font-size: 12.5px; color: #94A3B8;'>Legend: <mark class='scam-highlight'>Red Highlights</mark> represent phrases matched directly to high-risk recruitment fraud indicators.</div>", unsafe_allow_html=True)

    # --- TAB 4: EXTRACTED INTELLIGENCE & DOMAIN CONSISTENCY ---
    with tab_entities:
        st.markdown("<div style='padding-top: 15px;'></div>", unsafe_allow_html=True)

        # Domain Consistency Banner
        st.markdown(f"""
        <div style="background: {domain_check['bg']}; border: 1.5px solid {domain_check['border']}; border-radius: 14px; padding: 18px 22px; margin-bottom: 24px;">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 26px;">🌐</span>
                    <div>
                        <b style="color: {domain_check['color']}; font-size: 16px;">{domain_check['badge']}</b>
                        <div style="color: #E2E8F0; font-size: 13.5px; margin-top: 3px;">{domain_check['summary']}</div>
                    </div>
                </div>
                <div style="font-size: 13px; color: #CBD5E1; font-family: 'JetBrains Mono', monospace;">
                    Email: <b>@{domain_check['email_domain']}</b> | Web: <b>{domain_check['web_domain']}</b>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"#### 📋 Parsed Job Metadata ({completeness['found']}/{completeness['total']} Fields Found • {completeness['level']})")
        st.caption("Automatic regex and natural language extraction separating verified information from unspecified attributes.")

        col_e1, col_e2 = st.columns(2)

        def make_entity_card(icon, label, value):
            is_found = value != "Not Found"
            badge_html = "<span class='meta-chip-found'>EXTRACTED</span>" if is_found else "<span class='meta-chip-missing'>NOT SPECIFIED</span>"
            display_val = value if is_found else "<span style='color:#94A3B8; font-style:italic;'>Not specified in posting text</span>"
            return f"""
            <div class="entity-card">
                <div class="entity-icon-box">{icon}</div>
                <div class="entity-content">
                    <div class="entity-label-row">
                        <span class="entity-label">{label}</span>
                        {badge_html}
                    </div>
                    <div class="entity-val">{display_val}</div>
                </div>
            </div>
            """

        with col_e1:
            st.markdown(make_entity_card("🏢", "Company Name", info['Company']), unsafe_allow_html=True)
            st.markdown(make_entity_card("💼", "Job Position / Title", info['Position']), unsafe_allow_html=True)
            st.markdown(make_entity_card("📍", "Location / Work Mode", info['Location']), unsafe_allow_html=True)
            st.markdown(make_entity_card("💰", "Compensation / Salary", info['Salary']), unsafe_allow_html=True)

        with col_e2:
            st.markdown(make_entity_card("🧑", "Experience Required", info['Experience']), unsafe_allow_html=True)
            st.markdown(make_entity_card("📧", "Recruiter Email", info['Email']), unsafe_allow_html=True)
            st.markdown(make_entity_card("🌐", "Website / Portal", info['Website']), unsafe_allow_html=True)

    # --- TAB 5: AI FORENSICS (LLaMA 3.2) ---
    with tab_ai:
        st.markdown("<div style='padding-top: 15px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 🧠 AI Forensic Security Assessment")
        st.caption("Automated threat rationale and candidate safety advisory.")

        # Strip redundant heading if present inside the explanation string
        clean_explanation = explanation.strip()
        lines = clean_explanation.split("\n")
        if lines and (lines[0].startswith("###") or lines[0].startswith("**Job")):
            clean_explanation = "\n".join(lines[1:]).strip()

        # Format markdown bullets and bolding for clean HTML embedding
        formatted_ai_html = clean_explanation
        formatted_ai_html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', formatted_ai_html)
        formatted_ai_html = re.sub(r'^\s*[-*]\s+', '&bull; ', formatted_ai_html, flags=re.MULTILINE)
        formatted_ai_html = formatted_ai_html.replace('\n', '<br/>')
        formatted_ai_html = re.sub(r'(<br/>\s*){3,}', '<br/><br/>', formatted_ai_html)

        st.markdown(f"""
        <div class="glass-panel" style="border-left: 4px solid #3B82F6; line-height: 1.85; font-size: 15px; color: #E2E8F0;">
            {formatted_ai_html}
        </div>
        """, unsafe_allow_html=True)

        st.caption("🔒 100% on-device private processing. No job descriptions are transmitted to external third-party cloud servers.")

    # --- TAB 6: AUDIT & EXPORT ---
    with tab_export:
        st.markdown("<div style='padding-top: 15px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 📄 Forensic PDF Audit Report")
        st.caption("Generate a tamper-evident audit report containing complete classification scores, quoted evidence, extracted entities, and AI forensic analysis.")

        export_col1, export_col2 = st.columns([1.5, 1])

        with export_col1:
            st.markdown("""
            <div class="glass-panel" style="margin-bottom: 20px;">
                <h4 style="margin-top: 0; color: #60A5FA;">Included in Official PDF Report:</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 14px; color: #E2E8F0;">
                    <div>✅ Classification Verdict</div>
                    <div>📊 Statistical Confidence %</div>
                    <div>🎯 Composite Threat Score</div>
                    <div>🚨 Quoted Evidence Snippets</div>
                    <div>🌐 Domain Consistency Rating</div>
                    <div>🧠 AI Forensic Review</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.download_button(
                label="⬇ Download Official JobShieldAI Report (.pdf)",
                data=pdf,
                file_name="JobShieldAI_Forensic_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )

        with export_col2:
            st.markdown("""
            <div class="glass-panel" style="text-align: center; padding: 28px;">
                <div style="font-size: 44px; margin-bottom: 8px;">📑</div>
                <div style="font-size: 17px; font-weight: 700; color: #F8FAFC;">Verified Audit Log</div>
                <p style="font-size: 13px; color: #94A3B8; margin-top: 6px;">
                    Formatted according to cybersecurity forensics standards with timestamped model metrics.
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        with st.expander("🔍 Inspect Raw Input Text"):
            st.code(analyzed_text, language="text")

# ---------------------------------------------------------
# Session Scan History Panel
# ---------------------------------------------------------
if st.session_state["scan_history"]:
    with st.expander("📜 Session Scan History & Comparison (Review Previous Scans)"):
        st.markdown("<p style='color: #CBD5E1; font-size: 13.5px;'>Review or re-inspect previous scans conducted during this session:</p>", unsafe_allow_html=True)
        for idx, scan in enumerate(st.session_state["scan_history"]):
            h_col1, h_col2, h_col3, h_col4, h_col5 = st.columns([1, 2.5, 1.5, 1.2, 1.2])
            with h_col1:
                st.write(f"**{scan['timestamp']}**")
            with h_col2:
                company = scan['info'].get('Company', 'Unknown')
                role = scan['info'].get('Position', 'Job Posting')
                st.write(f"🏢 **{company}** - {role}")
            with h_col3:
                if "Real" in scan['result']:
                    st.markdown("<span style='color: #10B981; font-weight: 700;'>✔ Real Job</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span style='color: #EF4444; font-weight: 700;'>✖ Fake Job</span>", unsafe_allow_html=True)
            with h_col4:
                st.write(f"Risk: **{scan['risk_score']}/100**")
            with h_col5:
                if st.button("🔄 Reload", key=f"reload_scan_{idx}", use_container_width=True):
                    st.session_state["analysis_result"] = scan
                    st.session_state["job_text"] = scan["job_description"]
                    st.rerun()

# ---------------------------------------------------------
# Presentation & Academic Benchmarks Panel
# ---------------------------------------------------------
with st.expander("🎓 View System Architecture & Model Benchmarks (Presentation Mode)"):
    st.markdown("### 🔬 System Architecture & Academic Evaluation")

    col_bench1, col_bench2 = st.columns(2)

    with col_bench1:
        st.markdown("#### 📊 Dataset Specifications (EMSCAD)")
        st.markdown("""
        - **Dataset Source:** Employment Scam Aegean Dataset (EMSCAD)
        - **Total Records:** `17,880` real & fraudulent job postings
        - **Class Distribution:** `17,014` Legitimate (95.2%) vs `866` Fraudulent (4.8%)
        - **Feature Engineering:** TF-IDF with 5,000 max features, English stop-word filtration
        - **Validation Strategy:** Stratified 80/20 Train-Test Split (preserves exact minority class ratio)
        """)

    with col_bench2:
        st.markdown("#### 🏆 Model Performance Comparison")
        st.markdown("""
        | Algorithm | Accuracy | Precision (Scam) | Recall (Scam) | Status |
        | :--- | :--- | :--- | :--- | :--- |
        | **Logistic Regression** | 97.2% | 0.88 | 0.62 | Baseline |
        | **Random Forest** | 98.1% | 0.93 | 0.74 | Ensemble |
        | **XGBoost (Production)** | **98.6%** | **0.96** | **0.79** | **Selected / Active** |
        """)
        st.caption("Selected **XGBoost** as primary inference engine due to superior F1-score and gradient-boosted decision boundary on sparse TF-IDF vectors.")

    st.markdown("---")
    st.markdown("#### 🛡️ 4-Tier Hybrid Defense Pipeline")
    st.markdown("""
    1. **Tier 1 (NLP Vectorization):** TF-IDF matrix extracts 5,000 n-gram frequencies from combined title, company profile, description, and requirements.
    2. **Tier 2 (Machine Learning Classifier):** Pre-trained **XGBoost Classifier** evaluates probability vector (`predict_proba`) for statistical anomaly detection.
    3. **Tier 3 (Heuristic Guardrails):** 10 deterministic security rules catch overt scam patterns (WhatsApp interviews, wire requests, domain spoofing).
    4. **Tier 4 (Generative AI Forensics):** On-device **LLaMA 3.2** generates explainable natural-language reasoning and candidate safety protocols with zero cloud data retention.
    """)

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("""
<div class="jobshield-footer">
    <div style="font-weight: 700; color: #CBD5E1; margin-bottom: 6px; font-size: 15px;">
        🛡️ JobShieldAI • AI-Powered Job Fraud Defense Platform
    </div>
    <div>
        Designed & Engineered by <b style="color: #F8FAFC;">Priyam Prajapati</b> • Department of Artificial Intelligence & Machine Learning
    </div>
    <div style="color: #94A3B8; font-size: 13px; margin-top: 4px;">
        Viva Institute of Technology
    </div>
</div>
""", unsafe_allow_html=True)
