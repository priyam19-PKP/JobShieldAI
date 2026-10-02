import re
import urllib.parse

def extract_domain_from_url(url: str) -> str:
    """Extracts root/base domain from a URL or web string."""
    if not url or url == "Not Found":
        return ""
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    try:
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc.lower()
        # Remove port if present
        netloc = netloc.split(":")[0]
        # Remove www.
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc
    except Exception:
        return ""


def extract_domain_from_email(email: str) -> str:
    """Extracts domain from an email address."""
    if not email or email == "Not Found" or "@" not in email:
        return ""
    parts = email.split("@")
    return parts[-1].strip().lower()


def verify_domain_consistency(info: dict) -> dict:
    """
    Cross-references recruiter email domain against company website domain.
    Distinguishes verified corporate matches from free webmail and domain discrepancies.
    """
    email = info.get("Email", "Not Found")
    website = info.get("Website", "Not Found")

    email_domain = extract_domain_from_email(email)
    web_domain = extract_domain_from_url(website)

    free_webmails = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", "proton.me", "protonmail.com"}

    if email_domain in free_webmails:
        return {
            "status": "FREE_WEBMAIL",
            "badge": "🚨 HIGH RISK • FREE WEBMAIL",
            "color": "#EF4444",
            "bg": "rgba(239, 68, 68, 0.12)",
            "border": "rgba(239, 68, 68, 0.35)",
            "summary": f"Recruiter is using a public consumer email (@{email_domain}) rather than an authenticated corporate domain.",
            "email_domain": email_domain,
            "web_domain": web_domain
        }

    if email_domain and web_domain:
        # Check if email domain matches or is a subdomain of website domain (or vice versa)
        if email_domain == web_domain or email_domain.endswith("." + web_domain) or web_domain.endswith("." + email_domain):
            return {
                "status": "MATCH",
                "badge": "✅ VERIFIED DOMAIN MATCH",
                "color": "#10B981",
                "bg": "rgba(16, 185, 129, 0.12)",
                "border": "rgba(16, 185, 129, 0.35)",
                "summary": f"Recruiter email domain (@{email_domain}) aligns directly with the official company web portal ({web_domain}).",
                "email_domain": email_domain,
                "web_domain": web_domain
            }
        else:
            return {
                "status": "MISMATCH",
                "badge": "⚠️ DOMAIN DISCREPANCY",
                "color": "#F59E0B",
                "bg": "rgba(245, 158, 11, 0.12)",
                "border": "rgba(245, 158, 11, 0.35)",
                "summary": f"Email domain (@{email_domain}) differs from the stated employer website domain ({web_domain}). Potential masquerading.",
                "email_domain": email_domain,
                "web_domain": web_domain
            }

    return {
        "status": "INCOMPLETE",
        "badge": "⚪ UNVERIFIABLE DOMAIN",
        "color": "#94A3B8",
        "bg": "rgba(148, 163, 184, 0.1)",
        "border": "rgba(148, 163, 184, 0.2)",
        "summary": "Email address or official company URL was not specified in the posting text.",
        "email_domain": email_domain or "Not Specified",
        "web_domain": web_domain or "Not Specified"
    }


def calculate_profile_completeness(info: dict) -> dict:
    """Calculates metadata presence and completeness percentage."""
    total_fields = len(info)
    found_fields = sum(1 for v in info.values() if v != "Not Found")
    pct = round((found_fields / total_fields) * 100)

    if pct >= 70:
        level = "High Completeness"
        color = "#10B981"
    elif pct >= 40:
        level = "Moderate Completeness"
        color = "#F59E0B"
    else:
        level = "Sparse Information"
        color = "#EF4444"

    return {
        "found": found_fields,
        "total": total_fields,
        "percentage": pct,
        "level": level,
        "color": color
    }


def extract_job_info(text: str) -> dict:
    """Extracts job posting metadata using regex patterns."""
    company = "Not Found"
    position = "Not Found"
    location = "Not Found"
    salary = "Not Found"
    experience = "Not Found"
    email = "Not Found"
    website = "Not Found"

    company_match = re.search(r"Company[:\-]?\s*(.*)", text, re.IGNORECASE)
    if company_match:
        company = company_match.group(1).strip()

    position_match = re.search(r"(Position|Job Title|Role)[:\-]?\s*(.*)", text, re.IGNORECASE)
    if position_match:
        position = position_match.group(2).strip()

    location_match = re.search(r"Location[:\-]?\s*(.*)", text, re.IGNORECASE)
    if location_match:
        location = location_match.group(1).strip()

    salary_match = re.search(r"(Salary|Compensation|Pay)[:\-]?\s*(.*)", text, re.IGNORECASE)
    if salary_match:
        salary = salary_match.group(2).strip()

    exp_match = re.search(r'(\d+\+?\s*(years|year|yrs|yr))', text, re.IGNORECASE)
    if exp_match:
        experience = exp_match.group()

    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email_match:
        email = email_match.group()

    website_match = re.search(r'https?://[^\s,]+|www\.[^\s,]+', text)
    if website_match:
        website = website_match.group().rstrip('.')

    return {
        "Company": company,
        "Position": position,
        "Location": location,
        "Salary": salary,
        "Experience": experience,
        "Email": email,
        "Website": website
    }
