import requests
import time
import json
import os
import io
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from pypdf import PdfReader
from groq import Groq

# ============================================================
# CONFIG
# ============================================================

WATCHLIST = ["RELIANCE", "TCS", "INFY"]  # keep small for testing

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
EMAIL_TO       = os.environ.get("EMAIL_TO", "")
GROQ_API_KEY   = os.environ.get("GROQ_API_KEY", "")

POLL_INTERVAL  = 5
SEEN_FILE      = "seen_announcements.json"

WATCHLIST_SET  = set(s.upper() for s in WATCHLIST)

# ============================================================
# GROQ CLIENT (INIT ONCE)
# ============================================================

GROQ_CLIENT = Groq(api_key=GROQ_API_KEY)

# ============================================================
# NSE SESSION
# ============================================================

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.nseindia.com/",
}

session = requests.Session()
session.headers.update(HEADERS)

def now():
    return datetime.now().strftime("%H:%M:%S")

# ============================================================
# HEALTH SERVER
# ============================================================

def start_healthcheck_server():
    port = int(os.environ.get("PORT", 8080))

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

    server = HTTPServer(("0.0.0.0", port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

# ============================================================
# NSE HELPERS
# ============================================================

def refresh_nse_cookies():
    try:
        session.get("https://www.nseindia.com", timeout=10)
        print(f"[{now()}] NSE cookies refreshed.")
    except Exception as e:
        print(f"[{now()}] Cookie error: {e}")

def fetch_announcements():
    url = "https://www.nseindia.com/api/corporate-announcements?index=equities"
    try:
        resp = session.get(url, timeout=10)
        if resp.status_code in (401, 403):
            refresh_nse_cookies()
            return []
        return resp.json()
    except:
        return []

# ============================================================
# STORAGE
# ============================================================

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

# ============================================================
# PDF TEXT
# ============================================================

def download_pdf_text(pdf_url):
    try:
        if not pdf_url.startswith("http"):
            pdf_url = f"https://nsearchives.nseindia.com/{pdf_url}"

        resp = session.get(pdf_url, timeout=20)
        reader = PdfReader(io.BytesIO(resp.content))

        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
            if len(text) > 10000:
                break

        return text[:10000]

    except Exception as e:
        print(f"[{now()}] PDF error: {e}")
        return ""

# ============================================================
# AI SUMMARY (GROQ)
# ============================================================

def summarize_with_groq(pdf_text):
    if not pdf_text:
        return "(No text to summarize)"

    if not GROQ_API_KEY:
        return "(No GROQ_API_KEY set)"

    prompt = (
        "Summarize in 2-3 bullet points. "
        "Each bullet under 15 words. Keep numbers exact.\n\n"
        + pdf_text
    )

    try:
        chat = GROQ_CLIENT.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        return chat.choices[0].message.content.strip()

    except Exception as e:
        print(f"[{now()}] Groq error: {e}")
        return "(Summary failed)"

# ============================================================
# EMAIL
# ============================================================

def send_email(item, summary):
    if not RESEND_API_KEY or not EMAIL_TO:
        print("Email config missing")
        return

    symbol = item.get("symbol", "")
    subject = item.get("subject", "")
    pdf = item.get("attchmntFile", "")

    if pdf and not pdf.startswith("http"):
        pdf = f"https://nsearchives.nseindia.com/{pdf}"

    html = f"""
    <html><body>
    <h2>{symbol}</h2>
    <p>{subject}</p>
    <p>{summary.replace("\\n", "<br>")}</p>
    <a href="{pdf}">Open PDF</a>
    </body></html>
    """

    try:
        requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": "onboarding@resend.dev",
                "to": [EMAIL_TO],
                "subject": f"NSE Alert: {symbol}",
                "html": html,
            },
        )
        print(f"[{now()}] Email sent: {symbol}")
    except Exception as e:
        print(f"Email error: {e}")

# ============================================================
# MAIN LOOP
# ============================================================

def main():
    start_healthcheck_server()
    refresh_nse_cookies()

    seen = load_seen()

    while True:
        data = fetch_announcements()

        for item in data:
            seq = item.get("an_seq_num")
            symbol = item.get("symbol", "").upper()

            if seq in seen:
                continue
            seen.add(seq)

            if symbol in WATCHLIST_SET:
                print(f"[{now()}] NEW: {symbol}")

                pdf = item.get("attchmntFile", "")
                text = download_pdf_text(pdf) if pdf else ""

                summary = summarize_with_groq(text)

                send_email(item, summary)

        save_seen(seen)
        time.sleep(POLL_INTERVAL)

# ============================================================

if __name__ == "__main__":
    main()
