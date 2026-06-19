import requests
import time
import json
import os
import io
import sys
import threading
import traceback
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

POLL_INTERVAL  = 15  # seconds — gentler on NSE than 5s
SEEN_FILE      = "seen_announcements.json"
MAX_SEEN       = 5000  # cap so the seen-set doesn't grow forever

GROQ_MODEL     = "llama-3.3-70b-versatile"  # current as of mid-2026; llama3-70b-8192 is deprecated

WATCHLIST_SET  = set(s.upper() for s in WATCHLIST)

# ============================================================
# GROQ CLIENT (INIT ONCE)
# ============================================================

GROQ_CLIENT = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

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

def log(msg):
    # flush=True so logs show up immediately in containerized/non-TTY environments
    print(f"[{now()}] {msg}", flush=True)

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

        def log_message(self, format, *args):
            pass  # silence default access logs

    server = HTTPServer(("0.0.0.0", port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    log(f"Healthcheck server listening on :{port}")

# ============================================================
# NSE HELPERS
# ============================================================

def refresh_nse_cookies():
    try:
        session.get("https://www.nseindia.com", timeout=10)
        log("NSE cookies refreshed.")
    except Exception as e:
        log(f"Cookie error: {e}")

def fetch_announcements():
    url = "https://www.nseindia.com/api/corporate-announcements?index=equities"
    try:
        resp = session.get(url, timeout=10)
        if resp.status_code in (401, 403):
            log(f"NSE returned {resp.status_code}, refreshing cookies.")
            refresh_nse_cookies()
            return []
        if resp.status_code != 200:
            log(f"NSE returned unexpected status {resp.status_code}")
            return []
        return resp.json()
    except Exception as e:
        log(f"Fetch error: {e}")
        return []

# ============================================================
# STORAGE
# ============================================================

def load_seen():
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r") as f:
                return set(json.load(f))
        except Exception as e:
            log(f"Failed to load seen file, starting fresh: {e}")
            return set()
    return set()

def save_seen(seen):
    try:
        # cap size: keep most recent MAX_SEEN entries (sets are unordered,
        # so this is a simple soft cap, not strict LRU)
        trimmed = seen
        if len(trimmed) > MAX_SEEN:
            trimmed = set(list(trimmed)[-MAX_SEEN:])
        with open(SEEN_FILE, "w") as f:
            json.dump(list(trimmed), f)
        return trimmed
    except Exception as e:
        log(f"Failed to save seen file: {e}")
        return seen

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
        log(f"PDF error: {e}")
        return ""

# ============================================================
# AI SUMMARY (GROQ)
# ============================================================

def summarize_with_groq(pdf_text):
    if not pdf_text:
        return "(No text to summarize)"

    if not GROQ_CLIENT:
        return "(No GROQ_API_KEY set)"

    prompt = (
        "Summarize in 2-3 bullet points. "
        "Each bullet under 15 words. Keep numbers exact.\n\n"
        + pdf_text
    )

    try:
        chat = GROQ_CLIENT.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        return chat.choices[0].message.content.strip()

    except Exception as e:
        log(f"Groq error: {e}")
        return "(Summary failed)"

# ============================================================
# EMAIL
# ============================================================

def send_email(item, summary):
    if not RESEND_API_KEY or not EMAIL_TO:
        log("Email config missing, skipping send.")
        return

    symbol = item.get("symbol", "")
    subject = item.get("subject", "")
    pdf = item.get("attchmntFile", "")

    if pdf and not pdf.startswith("http"):
        pdf = f"https://nsearchives.nseindia.com/{pdf}"

    summary_html = summary.replace("\n", "<br>")

    html = f"""
    <html><body>
    <h2>{symbol}</h2>
    <p>{subject}</p>
    <p>{summary_html}</p>
    <a href="{pdf}">Open PDF</a>
    </body></html>
    """

    try:
        resp = requests.post(
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
            timeout=10,
        )
        if resp.status_code >= 300:
            log(f"Email send failed ({resp.status_code}): {resp.text[:200]}")
        else:
            log(f"Email sent: {symbol}")
    except Exception as e:
        log(f"Email error: {e}")

# ============================================================
# MAIN LOOP
# ============================================================

def main():
    start_healthcheck_server()
    refresh_nse_cookies()

    seen = load_seen()
    log(f"Loaded {len(seen)} previously seen announcements.")
    log(f"Watching: {sorted(WATCHLIST_SET)}")

    while True:
        try:
            data = fetch_announcements()

            for item in data:
                seq = item.get("an_seq_num")
                if seq is None:
                    continue  # skip items without a stable id instead of polluting `seen`

                if seq in seen:
                    continue
                seen.add(seq)

                symbol = item.get("symbol", "").upper()

                if symbol in WATCHLIST_SET:
                    log(f"NEW: {symbol} - {item.get('subject', '')[:80]}")

                    pdf = item.get("attchmntFile", "")
                    text = download_pdf_text(pdf) if pdf else ""

                    summary = summarize_with_groq(text)

                    send_email(item, summary)

            seen = save_seen(seen)

        except Exception:
            # Top-level guard: log the full traceback instead of letting the
            # process die silently and the container exit.
            log("Unhandled error in main loop:")
            traceback.print_exc()

        time.sleep(POLL_INTERVAL)

# ============================================================

if __name__ == "__main__":
    main()
