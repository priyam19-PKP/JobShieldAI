import re
import urllib.parse
from html.parser import HTMLParser
import requests

class SimpleHTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.ignore_tags = {"script", "style", "noscript", "nav", "footer", "header", "svg"}
        self.current_tag = None

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag.lower()

    def handle_endtag(self, tag):
        if self.current_tag == tag.lower():
            self.current_tag = None

    def handle_data(self, data):
        if self.current_tag not in self.ignore_tags:
            cleaned = data.strip()
            if cleaned:
                self.text_parts.append(cleaned)

    def get_text(self):
        return "\n".join(self.text_parts)


def fetch_job_from_url(url: str) -> str:
    """
    Fetches web content from a given URL and extracts clean readable text.
    Handles redirects, timeouts, and standard headers.
    """
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # Parse and validate domain
    parsed = urllib.parse.urlparse(url)
    if not parsed.netloc:
        raise ValueError("Invalid URL format. Please provide a valid web address (e.g., https://example.com/job).")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }

    try:
        response = requests.get(url, headers=headers, timeout=8, verify=False)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise TimeoutError("The request timed out while attempting to connect to the provided URL.")
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to access URL: {str(e)}")

    content_type = response.headers.get("Content-Type", "")
    if "text/html" not in content_type and "text/plain" not in content_type:
        raise ValueError("The provided link does not point to a web page (HTML).")

    # Extract text from HTML
    parser = SimpleHTMLTextExtractor()
    parser.feed(response.text)
    extracted = parser.get_text()

    # Filter out excessive blank lines and common cookies/boilerplate
    lines = [line.strip() for line in extracted.split("\n") if line.strip()]
    cleaned_text = "\n".join(lines)

    if len(cleaned_text) < 50:
        raise ValueError("Insufficient readable job text found at this link. The site may require login or JavaScript rendering.")

    return cleaned_text[:5000]  # Cap at 5000 chars for optimal NLP processing
