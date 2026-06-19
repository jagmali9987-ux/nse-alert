import requests
import time
import json
import os
import io
import threading
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from pypdf import PdfReader
from groq import Groq

# ============================================================
# CONFIG
# ============================================================

WATCHLIST = ["360ONE",
"ABB",
"APLAPOLLO",
"AUBANK",
"ADANIENSOL",
"ADANIENT",
"ADANIGREEN",
"ADANIPORTS",
"ADANIPOWER",
"ATGL",
"ABCAPITAL",
"ALKEM",
"AMBUJACEM",
"APOLLOHOSP",
"AUROPHARMA",
"BSE",
"BAJAJFINSV",
"BAJAJHLDNG",
"BANKINDIA",
"BDL",
"BEL",
"BHARATFORG",
"BHEL",
"BPCL",
"BHARTIARTL",
"GROWW",
"BIOCON",
"BOSCHLTD",
"BRITANNIA",
"CGPOWER",
"CANBK",
"CIPLA",
"COCHINSHIP",
"COFORGE",
"COLPAL",
"CONCOR",
"COROMANDEL",
"CUMMINSIND",
"DLF",
"DIVISLAB",
"DRREDDY",
"EICHERMOT",
"NYKAA",
"FORTIS",
"GAIL",
"GVT&D",
"GMRAIRPORT",
"GLENMARK",
"GODFRYPHLP",
"GODREJPROP",
"GRASIM",
"HDFCAMC",
"HDFCLIFE",
"HEROMOTOCO",
"HINDPETRO",
"HINDZINC",
"POWERINDIA",
"HUDCO",
"HYUNDAI",
"ICICIGI",
"ICICIAMC",
"IDFCFIRSTB",
"ITC",
"IOC",
"IRCTC",
"IRFC",
"IREDA",
"INDUSTOWER",
"INDUSINDBK",
"NAUKRI",
"JSWENERGY",
"JIOFIN",
"JUBLFOOD",
"KALYANKJIL",
"LGEINDIA",
"LICHSGFIN",
"LT",
"LAURUSLABS",
"LENSKART",
"LODHA",
"LUPIN",
"MANKIND",
"MFSL",
"MAZDOCK",
"MOTILALOFS",
"MCX",
"MUTHOOTFIN",
"NHPC",
"NTPC",
"NATIONALUM",
"NESTLEIND",
"OBEROIRLTY",
"ONGC",
"OIL",
"PAYTM",
"OFSS",
"POLICYBZR",
"PATANJALI",
"PHOENIXLTD",
"PIDILITIND",
"PFC",
"POWERGRID",
"PRESTIGE",
"PNB",
"RECLTD",
"RVNL",
"RELIANCE",
"SBILIFE",
"SRF",
"MOTHERSON",
"SHRIRAMFIN",
"ENRIN",
"SIEMENS",
"SUNPHARMA",
"TATACAP",
"TATACOMM",
"TATACONSUM",
"TATAELXSI",
"TATAINVEST",
"TMCV",
"TMPV",
"TATAPOWER",
"TITAN",
"TORNTPHARM",
"TRENT",
"TIINDIA",
"ULTRACEMCO",
"VBL",
"VAML",
"VEDL",
"VOGL",
"IDEA",
"ZYDUSLIFE",
"APOLLOTYRE",
"BALKRISIND",
"CEATLTD",
"ESCORTS",
"ARE&M",
"UNOMINDA",
"ASHOKA",
"IRB",
"PNCINFRA",
"NCC",
"BIRLACORPN",
"HEIDELBERG",
"JKCEMENT",
"RAMCOCEM",
"SAGCEM",
"STARCEMENT",
"JKLAKSHMI",
"DALBHARAT",
"CERA",
"KAJARIACER",
"KNRCON",
"JKIL",
"NBCC",
"AHLUCONT",
"CEMPRO",
"DBL",
"TTKPRESTIG",
"BAJAJELEC",
"SYMPHONY",
"MAYURUNIQ",
"CENTURYPLY",
"GABRIEL",
"VGUARD",
"CYIENT",
"FSL",
"MASTEK",
"INTELLECT",
"SONATSOFTW",
"KPIL",
"KEC",
"DOLLAR",
"DCBBANK",
"SOUTHBANK",
"J&KBANK",
"CUB",
"KTKBANK",
"KARURVYSYA",
"HGINFRA",
"KKCL",
"GREENLAM",
"ABFRL",
"GALAXYSURF",
"ENDURANCE",
"ZFCVINDIA",
"GREENPLY",
"AARTIIND",
"FINCABLES",
"MMFL",
"NILKAMAL",
"ATUL",
"NOCIL",
"FINPIPE",
"FINEORG",
"NAVINFLUOR",
"ARVINDFASN",
"AMBER",
"NEOGEN",
"LEMONTREE",
"CROMPTON",
"ORIENTELEC",
"VINATIORGA",
"PVRINOX",
"VMART",
"SUDARSCHEM",
"INDIAMART",
"UBL",
"BSOFT",
"BERGEPAINT",
"KANSAINER",
"CRAFTSMAN",
"RALLIS",
"SHARDACROP",
"AFFLE",
"GOCOLORS",
"SANSERA",
"GREENPANEL",
"MAPMYINDIA",
"ZYDUSWELL",
"POONAWALLA",
"STYLAMIND",
"RATEGAIN",
"BANDHANBNK",
"LATENTVIEW",
"VIPIND",
"SAFARI",
"EMAMILTD",
"CHALET",
"EMIL",
"METROBRAND",
"VENUSPIPES",
"BAYERCROP",
"SUMICHEM",
"DHANUKA",
"PARKHOTELS",
"SENCO",
"MEDANTA",
"JLHL",
"RAINBOW",
"NH",
"KIMS",
"ROSSARI",
"TBOTEK",
"JSL",
"APTUS",
"LLOYDSME",
"MASFIN",
"ARTEMISMED",
"INDRAMEDCO",
"PGEL",
"BECTORFOOD",
"MOIL",
"PROTEAN",
"UNIMECH",
"LTTS",
"HAPPSTMNDS",
"SURAJEST",
"BANSALWIRE",
"ABLBL",
"IXIGO",
"KFINTECH",
"CAMS",
"IMFA",
"CRIZAC",
"CARYSIL",
"DEVYANI",
"SAPPHIRE",
"RBA",
"HINDCOPPER",
"JUBLINGREA",
"AFCONS",
"TDPOWERSYS",
"EXCELSOFT",
"SKFINDUS",
"SKFINDIA",
"VIYASH",
"EMMVEE",
"VIKRAMSOLR",
"AMAGI",
"HCG",
"ASTRAMICRO",
"CELLO"]

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
EMAIL_TO       = os.environ.get("EMAIL_TO", "")
GROQ_API_KEY   = os.environ.get("GROQ_API_KEY", "")

POLL_INTERVAL  = 15          # seconds
SEEN_FILE      = "seen_announcements.json"
MAX_SEEN       = 5000
GROQ_MODEL     = "llama-3.3-70b-versatile"
WATCHLIST_SET  = set(s.upper() for s in WATCHLIST)

# ============================================================
# GROQ CLIENT
# ============================================================

GROQ_CLIENT = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# ============================================================
# NSE SESSION
# ============================================================

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer":    "https://www.nseindia.com/",
    "Accept":     "application/json, text/plain, */*",
}

session = requests.Session()
session.headers.update(HEADERS)

def now():
    return datetime.now().strftime("%H:%M:%S")

def log(msg):
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
            pass

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
        log(f"Cookie refresh error: {e}")

def fetch_announcements():
    url = "https://www.nseindia.com/api/corporate-announcements?index=equities"
    try:
        resp = session.get(url, timeout=10)
        if resp.status_code in (401, 403):
            log(f"NSE {resp.status_code} — refreshing cookies and retrying.")
            refresh_nse_cookies()
            resp = session.get(url, timeout=10)
        if resp.status_code != 200:
            log(f"NSE unexpected status {resp.status_code}")
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

def save_seen(seen):
    try:
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
        log(f"PDF download error: {e}")
        return ""

# ============================================================
# AI SUMMARY (GROQ)
# ============================================================

def summarize_with_groq(pdf_text, subject=""):
    if not GROQ_CLIENT:
        return "(No GROQ_API_KEY set — skipping summary)"

    # If no PDF text, try to summarise just the subject line
    content = pdf_text if pdf_text else f"Announcement subject: {subject}"
    if not content.strip():
        return "(Nothing to summarise)"

    prompt = (
        "You are a financial analyst assistant. "
        "Read the following NSE corporate announcement and give a concise summary "
        "in 2-3 bullet points. Each bullet must be under 20 words. "
        "Preserve all numbers exactly as they appear.\n\n"
        + content
    )

    try:
        chat = GROQ_CLIENT.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300,
        )
        return chat.choices[0].message.content.strip()
    except Exception as e:
        log(f"Groq error: {e}")
        return "(AI summary failed)"

# ============================================================
# EMAIL — rich HTML
# ============================================================

def build_html(item, summary, pdf_url):
    symbol  = item.get("symbol", "N/A")
    subject = item.get("subject", "N/A")
    seq     = item.get("an_seq_num", "")
    cat     = item.get("desc", item.get("category", ""))
    ts      = item.get("exchdisstime", item.get("sort_date", ""))

    # format summary bullets into styled list
    lines = [l.strip() for l in summary.splitlines() if l.strip()]
    bullets_html = "".join(
        f'<li style="margin-bottom:6px;">{l.lstrip("-•* ")}</li>'
        for l in lines
    )

    pdf_link = (
        f'<a href="{pdf_url}" style="display:inline-block;margin-top:12px;'
        f'padding:8px 18px;background:#1a56db;color:#fff;border-radius:5px;'
        f'text-decoration:none;font-size:14px;">📄 Open Filing PDF</a>'
        if pdf_url else ""
    )

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:Arial,sans-serif;background:#f4f6f9;padding:24px;margin:0;">
  <div style="max-width:600px;margin:auto;background:#fff;border-radius:10px;
              box-shadow:0 2px 8px rgba(0,0,0,.1);overflow:hidden;">

    <!-- Header -->
    <div style="background:#1a56db;padding:20px 24px;">
      <h1 style="margin:0;color:#fff;font-size:22px;">📢 NSE Alert: {symbol}</h1>
      <p style="margin:4px 0 0;color:#c7d9ff;font-size:13px;">{ts}</p>
    </div>

    <!-- Body -->
    <div style="padding:24px;">

      <table style="width:100%;border-collapse:collapse;margin-bottom:18px;font-size:14px;">
        <tr>
          <td style="padding:6px 10px;background:#f0f4ff;font-weight:bold;width:130px;
                     border:1px solid #dde3f0;">Symbol</td>
          <td style="padding:6px 10px;border:1px solid #dde3f0;font-weight:bold;
                     color:#1a56db;">{symbol}</td>
        </tr>
        <tr>
          <td style="padding:6px 10px;background:#f0f4ff;font-weight:bold;
                     border:1px solid #dde3f0;">Category</td>
          <td style="padding:6px 10px;border:1px solid #dde3f0;">{cat}</td>
        </tr>
        <tr>
          <td style="padding:6px 10px;background:#f0f4ff;font-weight:bold;
                     border:1px solid #dde3f0;">Subject</td>
          <td style="padding:6px 10px;border:1px solid #dde3f0;">{subject}</td>
        </tr>
        <tr>
          <td style="padding:6px 10px;background:#f0f4ff;font-weight:bold;
                     border:1px solid #dde3f0;">Seq #</td>
          <td style="padding:6px 10px;border:1px solid #dde3f0;color:#888;">{seq}</td>
        </tr>
      </table>

      <h3 style="margin:0 0 10px;font-size:15px;color:#333;">🤖 AI Summary</h3>
      <ul style="background:#f8f9fc;border-left:4px solid #1a56db;padding:14px 14px 14px 30px;
                 margin:0;border-radius:0 6px 6px 0;font-size:14px;color:#333;line-height:1.6;">
        {bullets_html}
      </ul>

      {pdf_link}

    </div>

    <!-- Footer -->
    <div style="background:#f0f4ff;padding:12px 24px;font-size:12px;color:#888;text-align:center;">
      NSE Announcement Watcher • Auto-generated alert
    </div>

  </div>
</body>
</html>
"""

def send_email(item, summary):
    if not RESEND_API_KEY or not EMAIL_TO:
        log("Email config missing — skipping.")
        return

    symbol  = item.get("symbol", "UNKNOWN")
    subject = item.get("subject", "")
    pdf     = item.get("attchmntFile", "")
    if pdf and not pdf.startswith("http"):
        pdf = f"https://nsearchives.nseindia.com/{pdf}"

    html = build_html(item, summary, pdf)
    email_subject = f"NSE 📢 {symbol}: {subject[:60]}{'…' if len(subject) > 60 else ''}"

    try:
        resp = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type":  "application/json",
            },
            json={
                "from":    "onboarding@resend.dev",
                "to":      [EMAIL_TO],
                "subject": email_subject,
                "html":    html,
            },
            timeout=10,
        )
        if resp.status_code >= 300:
            log(f"Email FAILED ({resp.status_code}): {resp.text[:200]}")
        else:
            log(f"✅ Email sent → {symbol}: {subject[:60]}")
    except Exception as e:
        log(f"Email error: {e}")

# ============================================================
# STARTUP TEST EMAIL
# ============================================================

def send_test_email():
    if not RESEND_API_KEY or not EMAIL_TO:
        log("Skipping startup test email — RESEND_API_KEY or EMAIL_TO not set.")
        return
    try:
        resp = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type":  "application/json",
            },
            json={
                "from":    "onboarding@resend.dev",
                "to":      [EMAIL_TO],
                "subject": "NSE Watcher started ✅",
                "html":    "<p>Watcher is running. You will receive alerts for watchlist matches.</p>",
            },
            timeout=10,
        )
        if resp.status_code >= 300:
            log(f"Startup test email FAILED ({resp.status_code}): {resp.text[:300]}")
        else:
            log("Startup test email sent ✅")
    except Exception as e:
        log(f"Startup test email error: {e}")

# ============================================================
# FORCE-SEND TEST — grabs the very first announcement from NSE
# and sends a real alert email so you can verify the full flow
# Set env var FORCE_TEST_EMAIL=1 to trigger on startup
# ============================================================

def force_test_announcement_email():
    log("FORCE_TEST_EMAIL=1 detected — fetching live announcement to test full email flow...")
    data = fetch_announcements()
    if not data:
        log("No announcements returned from NSE for force-test.")
        return

    # pick the first announcement that has a PDF, otherwise just use first
    item = next((x for x in data if x.get("attchmntFile")), data[0])
    symbol  = item.get("symbol", "TEST")
    subject = item.get("subject", "")
    pdf     = item.get("attchmntFile", "")

    log(f"Force-test using: {symbol} | {subject[:60]}")

    text    = download_pdf_text(pdf) if pdf else ""
    summary = summarize_with_groq(text, subject)

    log(f"AI Summary:\n{summary}")
    send_email(item, summary)

# ============================================================
# MAIN LOOP
# ============================================================

def main():
    start_healthcheck_server()
    refresh_nse_cookies()
    send_test_email()

    # Optional: force a real announcement email at startup to verify pipeline
    if os.environ.get("FORCE_TEST_EMAIL", "").strip() == "1":
        force_test_announcement_email()

    seen = load_seen()
    log(f"Loaded {len(seen)} previously seen announcement IDs.")

    poll_count = 0

    while True:
        try:
            poll_count += 1
            data = fetch_announcements()
            log(f"Poll #{poll_count}: {len(data)} announcements from NSE.")

            # Log first 3 raw items each poll for visibility
            for item in data[:3]:
                log(
                    f"  → {item.get('symbol','?')} | seq={item.get('an_seq_num','?')} "
                    f"| {item.get('subject','')[:50]}"
                )

            new_count = 0
            for item in data:
                seq = (
                    item.get("an_seq_num")
                    or item.get("symbol", "") + "|" + item.get("attchmntFile", "")
                )
                
                if seq in seen:
                    continue
                
                seen.add(seq)
                new_count += 1

                symbol = item.get("symbol", "").upper()

                if symbol in WATCHLIST_SET:
                    log(f"MATCH FOUND: {symbol}")
                    log(f"NEW: {symbol}")

                pdf     = item.get("attchmntFile", "")
                text    = download_pdf_text(pdf) if pdf else ""
                summary = summarize_with_groq(text, item.get("subject", ""))

                log(f"   Summary: {summary[:120]}")
                send_email(item, summary)

            if new_count:
                log(f"  {new_count} new announcement(s) processed this poll.")

            seen = save_seen(seen)

        except Exception:
            log("Unhandled error in main loop:")
            traceback.print_exc()

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
