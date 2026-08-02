import streamlit as st
from predict import predict_job
from ollama_ai import explain_prediction
from extractor import extract_job_info
from scam_detector import detect_scam_signs
from risk_score import calculate_risk_score
from pdf_generator import generate_pdf
from pathlib import Path



# -------------------------
# Page Configuration
# -------------------------

st.set_page_config(
    page_title="JobShieldAI",
    page_icon="🛡️",
    layout="wide"
)
logo_path = Path(__file__).parent / "logo.png"


# Load Custom CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -------------------------
# Sidebar
# -------------------------

with st.sidebar:

    # Logo
    st.image("logo.png", width=150)

    st.markdown("""
    <div style="text-align:center;margin-top:-12px;margin-bottom:15px;">
        <p style="
            color:#94A3B8;
            font-size:15px;
            margin:0;
        ">
        AI-Powered Fake Job Detection
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### 🚀 Features")

    features = [
        "🤖 Machine Learning",
        "🧠 Ollama AI",
        "🚨 Scam Detection",
        "📊 Risk Analysis",
        "📋 Job Information",
        "📄 PDF Report"
    ]

    for feature in features:
        st.markdown(
            f"""
            <div style="
                background:#23304A;
                padding:10px 15px;
                border-radius:10px;
                margin-bottom:8px;
                color:white;
                font-size:15px;
            ">
                {feature}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    st.markdown("### 👨‍💻 Developer")

    st.markdown(
        """
    <div style="
    background:#23304A;
    padding:18px;
    border-radius:15px;
    text-align:center;
    color:white;
    ">

    <h3 style="margin:0;">Priyam Prajapati</h3>

    <p style="margin-top:10px;">
    🎓 AIML Department
    </p>

    <p>
    🏫 Viva Institute of Technology
    </p>

    </div>
    """,
        unsafe_allow_html=True,
    )

# -------------------------
# Main Page
# -------------------------

# =========================
# Modern Header
# =========================

col1, col2 = st.columns([1, 5], vertical_alignment="center")

with col1:
    st.image("logo.png", width=110)

with col2:
    st.title("JobShieldAI")
    st.caption("AI-Powered Fake Job Detection using Machine Learning + Local AI")
st.success("🟢 System Status : Secure • Local AI Ready • Model Loaded Successfully")
st.markdown("---")



st.write("### 📄 Paste the Job Description")

job_description = st.text_area(
    "",
    height=250,
    placeholder="Paste the complete job description here..."
)
# -------------------------
# Analyze Button
# -------------------------

analyze = st.button(
    "🚀 Analyze Job Security",
    use_container_width=True,
    type="primary"
)

if analyze:

    if job_description.strip() == "":
        st.warning("Please enter a job description.")
        st.stop()

    # ML Prediction
    result, confidence = predict_job(job_description)
    confidence = float(confidence)

    # AI Explanation
    with st.spinner("🤖 AI is analyzing the job..."):
        explanation = explain_prediction(job_description, result)

    # Extract Information
    info = extract_job_info(job_description)

    # Scam Detection
    warnings = detect_scam_signs(job_description)

    # Risk Score
    risk_score, risk_level = calculate_risk_score(result, warnings)

    # -------------------------
    # Generate PDF Report
    # -------------------------

    pdf = generate_pdf(
        result,
        confidence,
        risk_score,
        risk_level,
        info,
        warnings,
        explanation
    )

    st.success("✅ Analysis Completed!")

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    # -------------------------
    # Prediction Card
    # -------------------------

    with col1:

        if "Real" in result:
            color = "#22c55e"
            icon = "✅"
            status = "REAL JOB"
        else:
            color = "#ef4444"
            icon = "❌"
            status = "FAKE JOB"

        st.markdown(f"""
        <div style="
            background:white;
padding:28px;
border-radius:18px;
text-align:center;
border-left:6px solid {color};
box-shadow:0 8px 20px rgba(0,0,0,0.10);
        ">
            <h1 style="margin-bottom:8px;">{icon}</h1>
<h2 style="margin:0;color:{color};">{status}</h2>
<p style="color:#64748B;">Prediction Result</p>
        </div>
        """, unsafe_allow_html=True)

    # -------------------------
    # Confidence Card
    # -------------------------

    with col2:

        st.markdown(f"""
        <div style="
            background:white;
padding:28px;
border-radius:18px;
text-align:center;
border-left:6px solid #2563EB;
box-shadow:0 8px 20px rgba(0,0,0,.10);
        ">
            <h1>📊</h1>
<h2 style="margin:0;color:#2563EB;">{confidence:.2f}%</h2>
<p style="color:#64748B;">Model Confidence</p>
        </div>
        """, unsafe_allow_html=True)
        st.progress(confidence / 100)

        st.caption(f"Model Confidence: {confidence:.2f}%")

    # -------------------------
    # Risk Card
    # -------------------------

    with col3:

        if risk_level == "LOW":
            risk_color = "#22c55e"
            risk_icon = "🟢"
        elif risk_level == "MEDIUM":
            risk_color = "#f59e0b"
            risk_icon = "🟠"
        else:
            risk_color = "#ef4444"
            risk_icon = "🔴"

        st.markdown(f"""
        <div style="
            background:white;
padding:28px;
border-radius:18px;
text-align:center;
border-left:6px solid {risk_color};
box-shadow:0 8px 20px rgba(0,0,0,.10);
        ">
            <h1>{risk_icon}</h1>
<h2 style="margin:0;color:{risk_color};">{risk_score}/100</h2>
<p style="color:#64748B;">{risk_level} RISK</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📈 Risk Meter")

    st.progress(risk_score / 100)

    if risk_level == "LOW":
        st.success("🟢 Low Risk Job")

    elif risk_level == "MEDIUM":
        st.warning("🟠 Medium Risk Job")

    else:
        st.error("🔴 High Risk Job")

    # Job Information

    # -------------------------
    # Job Information
    # -------------------------

    st.markdown("📋 Job Information")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(f"""
        <div style="
        background:#1E293B;
        padding:18px;
        border-radius:15px;
        margin-bottom:15px;
        border-left:5px solid #2563EB;
        ">
        <b>🏢 Company</b><br>
        {info["Company"]}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="
        background:#1E293B;
        padding:18px;
        border-radius:15px;
        margin-bottom:15px;
        border-left:5px solid #2563EB;
        ">
        <b>💼 Position</b><br>
        {info["Position"]}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="
        background:#1E293B;
        padding:18px;
        border-radius:15px;
        margin-bottom:15px;
        border-left:5px solid #2563EB;
        ">
        <b>📍 Location</b><br>
        {info["Location"]}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="
        background:#1E293B;
        padding:18px;
        border-radius:15px;
        margin-bottom:15px;
        border-left:5px solid #2563EB;
        ">
        <b>💰 Salary</b><br>
        {info["Salary"]}
        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown(f"""
        <div style="
        background:#1E293B;
        padding:18px;
        border-radius:15px;
        margin-bottom:15px;
        border-left:5px solid #06B6D4;
        ">
        <b>🧑 Experience</b><br>
        {info["Experience"]}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="
        background:#1E293B;
        padding:18px;
        border-radius:15px;
        margin-bottom:15px;
        border-left:5px solid #06B6D4;
        ">
        <b>📧 Email</b><br>
        {info["Email"]}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="
        background:#1E293B;
        padding:18px;
        border-radius:15px;
        margin-bottom:15px;
        border-left:5px solid #06B6D4;
        ">
        <b>🌐 Website</b><br>
        {info["Website"]}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Scam Detection

    # -------------------------
    # Scam Detection
    # -------------------------

    st.markdown("🚨 Scam Detection")

    for item in warnings:

        if item.startswith("✅"):

            st.markdown(f"""
            <div style="
            background:#DCFCE7;
            color:#166534;
            padding:15px;
            border-radius:12px;
            margin-bottom:10px;
            border-left:5px solid #22C55E;
            ">
            {item}
            </div>
            """, unsafe_allow_html=True)

        else:

            st.markdown(f"""
            <div style="
            background:#FEF3C7;
            color:#92400E;
            padding:15px;
            border-radius:12px;
            margin-bottom:10px;
            border-left:5px solid #F59E0B;
            ">
            {item}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # AI Explanation

    # -------------------------
    # AI Explanation
    # -------------------------

    st.markdown("🤖 AI Security Analysis")
    st.markdown("""
    <div style="
    background:#1E293B;
    padding:20px;
    border-radius:15px;
    border-left:5px solid #2563EB;
    ">
    <h3 style="color:#60A5FA;">🧠 AI Assessment</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(explanation)

    st.caption("⚠️ This analysis is AI-assisted. Always verify job offers independently.")

    st.markdown("---")

    st.markdown("---")

    # -------------------------
    # Download PDF Report
    # -------------------------

    # ===========================
    # PDF Report
    # ===========================

    st.markdown("""
    <div style="
    background:linear-gradient(135deg,#1E3A8A,#2563EB);
    padding:22px;
    border-radius:18px;
    color:white;
    margin-bottom:20px;
    box-shadow:0 8px 25px rgba(37,99,235,.30);
    ">

    <h2 style="margin-bottom:10px;">
    📄 Security Report
    </h2>

    <p style="font-size:16px;">
    Download a detailed PDF containing:
    </p>

    ✅ ML Prediction<br>
    📊 Confidence Score<br>
    🎯 Risk Score<br>
    🚨 Scam Detection<br>
    🤖 AI Explanation<br>
    📋 Job Information

    </div>
    """, unsafe_allow_html=True)

    st.download_button(
        label="⬇ Download JobShieldAI Report",
        data=pdf,
        file_name="JobShieldAI_Report.pdf",
        mime="application/pdf",
        use_container_width=True,
        type="primary"
    )

    st.markdown("---")

    # Original Job Description

    with st.expander("📄 View Original Job Description"):
        st.write(job_description)
        st.markdown("---")

        st.markdown("""
        <div style="
        text-align:center;
        color:#94A3B8;
        padding:15px;
        font-size:14px;
        ">
        🛡️ <b>JobShieldAI</b><br>
        Developed by <b>Priyam Prajapati</b><br>
        Department of Artificial Intelligence & Machine Learning<br>
        Viva Institute of Technology
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <hr>

        <div style="text-align:center;color:#94A3B8;padding:20px;">

        🛡️ JobShieldAI • AI Powered Fake Job Detection

        <br><br>

        Developed by <b>Priyam Prajapati</b>

        </div>
        """, unsafe_allow_html=True)