import re


def extract_job_info(text):

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

    position_match = re.search(r"(Position|Job Title)[:\-]?\s*(.*)", text, re.IGNORECASE)
    if position_match:
        position = position_match.group(2).strip()

    location_match = re.search(r"Location[:\-]?\s*(.*)", text, re.IGNORECASE)
    if location_match:
        location = location_match.group(1).strip()

    salary_match = re.search(r"Salary[:\-]?\s*(.*)", text, re.IGNORECASE)
    if salary_match:
        salary = salary_match.group(1).strip()

    exp_match = re.search(r'(\d+\+?\s*(years|year))', text, re.IGNORECASE)
    if exp_match:
        experience = exp_match.group()

    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email_match:
        email = email_match.group()

    website_match = re.search(r'https?://[^\s]+|www\.[^\s]+', text)
    if website_match:
        website = website_match.group()

    return {
        "Company": company,
        "Position": position,
        "Location": location,
        "Salary": salary,
        "Experience": experience,
        "Email": email,
        "Website": website
    }