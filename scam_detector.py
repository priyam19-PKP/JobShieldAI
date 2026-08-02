import re


def detect_scam_signs(text):

    text = text.lower()

    warnings = []

    if "registration fee" in text or "processing fee" in text or "security deposit" in text:
        warnings.append("💰 Registration fee requested")

    if "whatsapp" in text:
        warnings.append("📱 WhatsApp interview/contact detected")

    if "@gmail.com" in text:
        warnings.append("📧 Gmail recruiter email used")

    if ".xyz" in text or ".online" in text or ".top" in text:
        warnings.append("🌐 Suspicious website domain")

    if "urgent hiring" in text:
        warnings.append("⚡ Urgent hiring pressure")

    if "immediate joining" in text:
        warnings.append("🚨 Immediate joining promise")

    if "no interview" in text:
        warnings.append("❌ No interview required")

    if "free laptop" in text:
        warnings.append("💻 Unrealistic free laptop offer")

    if "earn" in text and "per week" in text:
        warnings.append("💸 Unrealistic salary claim")

    if "bank details" in text:
        warnings.append("🏦 Requests bank details")

    if len(warnings) == 0:
        warnings.append("✅ No obvious scam indicators detected")

    return warnings