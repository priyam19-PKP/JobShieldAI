import re
import html

SCAM_RULES = [
    {
        "id": "fee",
        "terms": ["registration fee", "processing fee", "security deposit", "application fee", "refundable deposit"],
        "name": "Upfront Payment or Deposit Required",
        "icon": "💰",
        "category": "Financial Fraud",
        "severity": "CRITICAL",
        "explanation": "Legitimate employers never demand advance fees, processing charges, or deposits for interviews, testing, or equipment."
    },
    {
        "id": "whatsapp",
        "terms": ["whatsapp", "telegram", "signal chat", "wire chat"],
        "name": "Unverified Chat App Communication",
        "icon": "📱",
        "category": "Communication Channel",
        "severity": "HIGH",
        "explanation": "Official recruitment processes use corporate email domains and scheduled video/office interviews, not anonymous messaging platforms."
    },
    {
        "id": "public_email",
        "terms": ["@gmail.com", "@yahoo.com", "@hotmail.com", "@outlook.com"],
        "name": "Personal Webmail Recruiter Address",
        "icon": "📧",
        "category": "Identity Verification",
        "severity": "HIGH",
        "explanation": "Recruiters representing corporate entities should use corporate domain emails, not personal public webmail accounts."
    },
    {
        "id": "suspicious_domain",
        "terms": [".xyz", ".online", ".top", ".club", ".work", ".site", ".info"],
        "name": "Suspicious / Cheap Web Domain",
        "icon": "🌐",
        "category": "Domain Authenticity",
        "severity": "HIGH",
        "explanation": "Disposable or low-cost top-level domains (.xyz, .online, .top) are heavily associated with phishing and transient scam infrastructure."
    },
    {
        "id": "urgency",
        "terms": ["urgent hiring", "urgent opening", "apply immediately", "immediate start", "limited slots"],
        "name": "Artificial Urgency & Time Pressure",
        "icon": "⚡",
        "category": "Social Engineering",
        "severity": "MEDIUM",
        "explanation": "Scammers leverage false urgency to pressure victims into making hasty decisions without verifying employer credentials."
    },
    {
        "id": "immediate_joining",
        "terms": ["immediate joining", "instant onboarding", "start today", "join tomorrow"],
        "name": "Unrealistic Immediate Joining Promise",
        "icon": "🚨",
        "category": "Hiring Procedure",
        "severity": "MEDIUM",
        "explanation": "Legitimate positions typically require structured interviews, background checks, and offer processing rather than instant hiring."
    },
    {
        "id": "no_interview",
        "terms": ["no interview", "without interview", "direct selection", "no screening"],
        "name": "No Formal Screening or Interview",
        "icon": "❌",
        "category": "Hiring Procedure",
        "severity": "HIGH",
        "explanation": "Skipping skill evaluation or interviews is a hallmark of phantom job offers designed to quickly funnel victims toward payment."
    },
    {
        "id": "free_equipment",
        "terms": ["free laptop", "free macbook", "free iphone", "home office allowance check"],
        "name": "Unrealistic Free Equipment / Check Offer",
        "icon": "💻",
        "category": "Advance-Fee / Fake Check",
        "severity": "HIGH",
        "explanation": "Commonly linked to fake check scams where the victim is sent a fraudulent check to purchase hardware from a specific 'vendor'."
    },
    {
        "id": "unrealistic_salary",
        "terms": ["earn $", "per week", "daily payout", "weekly payout", "quick cash", "$100/hr", "$90/hr"],
        "name": "Disproportionate Salary Claim",
        "icon": "💸",
        "category": "Compensation Anomaly",
        "severity": "MEDIUM",
        "explanation": "Exaggerated compensation for entry-level or minimal-skill tasks is used as clickbait to lure job seekers into fraud."
    },
    {
        "id": "banking",
        "terms": ["bank details", "bank account", "credit card", "debit card", "routing number", "crypto wallet"],
        "name": "Premature Financial Credential Request",
        "icon": "🏦",
        "category": "Credential Harvesting",
        "severity": "CRITICAL",
        "explanation": "Banking details should only be collected through official secure HR payroll portals after a formal contract is executed."
    }
]


def extract_context_sentence(text: str, term: str) -> str:
    """Extracts the sentence or surrounding context containing the matched term."""
    sentences = re.split(r'[.\n!?;]+', text)
    term_lower = term.lower()
    for s in sentences:
        if term_lower in s.lower():
            cleaned = s.strip()
            if len(cleaned) > 160:
                # Truncate overly long sentences while centering on the term
                idx = cleaned.lower().find(term_lower)
                start = max(0, idx - 40)
                end = min(len(cleaned), idx + len(term) + 60)
                return f"...{cleaned[start:end].strip()}..."
            return cleaned
    return f"Found '{term}' in posting"


def detect_scam_details(text: str):
    """
    Detects scam patterns and extracts exact supporting quote evidence from the job text.
    Returns a list of structured finding dictionaries.
    """
    findings = []
    text_lower = text.lower()

    for rule in SCAM_RULES:
        for term in rule["terms"]:
            if term in text_lower:
                quote = extract_context_sentence(text, term)
                findings.append({
                    "id": rule["id"],
                    "rule": rule["name"],
                    "icon": rule["icon"],
                    "category": rule["category"],
                    "severity": rule["severity"],
                    "matched_term": term,
                    "quote": quote,
                    "explanation": rule["explanation"]
                })
                break  # Record each rule once

    return findings


def detect_scam_signs(text: str):
    """
    Backward-compatible scam signs detector.
    Returns list of strings with icons, rule names, and quoted evidence.
    """
    details = detect_scam_details(text)
    if not details:
        return ["✅ No obvious scam indicators detected"]

    warnings = []
    for d in details:
        warnings.append(f"{d['icon']} {d['rule']} (Evidence: \"{d['quote']}\")")
    return warnings


def highlight_evidence_in_text(text: str, findings: list) -> str:
    """
    Generates HTML markup of the job description with all detected scam terms highlighted.
    Escapes HTML first for safety.
    """
    escaped_text = html.escape(text)

    # Collect unique terms to highlight
    terms_to_highlight = set()
    for f in findings:
        terms_to_highlight.add(f["matched_term"])

    # Highlight longer phrases first to prevent partial nested replacements
    sorted_terms = sorted(terms_to_highlight, key=len, reverse=True)

    for term in sorted_terms:
        escaped_term = html.escape(term)
        # Case-insensitive replacement preserving original casing
        pattern = re.compile(re.escape(escaped_term), re.IGNORECASE)
        escaped_text = pattern.sub(
            lambda m: f'<mark class="scam-highlight" title="Suspicious Indicator: {m.group(0)}">{m.group(0)}</mark>',
            escaped_text
        )

    # Convert line breaks to <br/>
    return escaped_text.replace("\n", "<br/>")
