import requests
import smtplib
import json
import os
import io
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from pypdf import PdfReader

EMAIL_SENDER     = os.environ.get("EMAIL_SENDER", "")
EMAIL_PASSWORD   = os.environ.get("EMAIL_PASSWORD", "")
EMAIL_TO         = os.environ.get("EMAIL_TO", "")
GEMINI_API_KEY   = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL     = "gemini-2.5-flash"

SEARCH_TERM = "SARVESHWAR"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Referer": "https://www.nseindia.com/",
}

session = requests.Session()
session.headers.update(HEADERS)


def now():
    return datetime.now().strftime("%H:%M:%S")


def refresh_nse_cookies():
    session.get("https://www.nseindia.com", timeout=10)
    session.get("https://www.nseindia.com/companies-listing/corporate-filings-announcements", timeout=10)
    print(f"[{now()}] NSE cookies refreshed.")


def fetch_announcements():
    url = "https://www.nseindia.com/api/corporate-announcements?index=equities"
    resp = session.get(url, timeout=8)
    resp.raise_for_status()
    return resp.json()


def find_match(data, term):
    matches = []
    for item in data:
        blob = json.dumps(item).upper()
        if term.upper() in blob:
            matches.append(item)
    return matches


def download_pdf_text(pdf_url, max_chars=15000):
    """Download the PDF and extract its text content."""
    try:
        resp = session.get(pdf_url, timeout=20)
        resp.raise_for_status()
        reader = PdfReader(io.BytesIO(resp.content))
        text = ""
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
            if len(text) >= max_chars:
                break
        return text[:max_chars].strip()
    except Exception as e:
        print(f"[{now()}] PDF download/extract failed: {e}")
        return ""


def summarize_with_gemini(pdf_text):
    """Send extracted PDF text to Gemini for a short summary."""
    if not pdf_text:
        return "(Could not extract text from PDF to summarize.)"
    if not GEMINI_API_KEY:
        return "(GEMINI_API_KEY not set — skipping summary.)"

    prompt = (
        "Summarize this NSE corporate announcement PDF in exactly 2-3 bullet points. "
        "Each bullet must be ONE short sentence, under 15 words. "
        "Keep every number, date, and amount exactly as written in the source, do not round or drop any. "
        "No preamble, no headings, no extra commentary, just the bullets starting with '-'. "
        "Focus only on the single most material fact per bullet (the decision, the amount, the date, the outcome).\n\n"
        f"{pdf_text}"
    )

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    body = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        resp = requests.post(url, json=body, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"[{now()}] Gemini summarization failed: {e}")
        return f"(Summary unavailable — Gemini error: {e})"


def send_raw_email(item, summary):
    pretty = json.dumps(item, indent=2)

    pdf_link = item.get("attchmntFile", "")
    text_blob = item.get("attchmntText") or item.get("subject") or "See full details below."
    date_field = item.get("an_dt") or item.get("exchdisstime") or ""

    summary_html = summary.replace("\n", "<br>")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"NSE Alert (manual fetch): {SEARCH_TERM}"
    msg["From"]    = EMAIL_SENDER
    msg["To"]      = EMAIL_TO

    body_html = f"""
    <html><body style="font-family:Arial,sans-serif;padding:20px;">
      <h2 style="color:#1a1a2e;">NSE Announcement — {SEARCH_TERM}</h2>
      <p><b>Date/time:</b> {date_field}</p>
      <p><b>Details:</b> {text_blob}</p>
      <p><b>PDF:</b> {"<a href='" + pdf_link + "'>Open PDF</a>" if pdf_link else "No PDF found"}</p>
      <hr>
      <h3 style="color:#1a1a2e;">AI Summary (Gemini)</h3>
      <p>{summary_html}</p>
      <hr>
      <p style="font-size:12px;color:#666;">Raw fields received from NSE (for debugging):</p>
      <pre style="background:#f5f5f5;padding:10px;font-size:11px;">{pretty}</pre>
    </body></html>
    """
    msg.attach(MIMEText(body_html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_TO, msg.as_string())
    print(f"[{now()}] Email sent for {SEARCH_TERM}.")


def main():
    refresh_nse_cookies()
    data = fetch_announcements()
    print(f"[{now()}] Fetched {len(data)} announcements.")

    matches = find_match(data, SEARCH_TERM)
    if not matches:
        print(f"[{now()}] No match found for '{SEARCH_TERM}' in current feed.")
        return

    item = matches[0]
    print(f"[{now()}] Found {len(matches)} match(es). Full raw record below:\n")
    print(json.dumps(item, indent=2))

    pdf_link = item.get("attchmntFile", "")
    pdf_text = download_pdf_text(pdf_link) if pdf_link else ""
    print(f"[{now()}] Extracted {len(pdf_text)} chars from PDF.")

    summary = summarize_with_gemini(pdf_text)
    print(f"[{now()}] Summary:\n{summary}")

    send_raw_email(item, summary)


if __name__ == "__main__":
    main()
