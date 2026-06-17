import requests
import smtplib
import time
import json
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# ============================================================
#  CONFIG — edit these or set as Railway environment variables
# ============================================================

WATCHLIST = [
    "BLUESTARCO",
    "MARICO",
    "COFORGE",
    "VOLTAS",
    "HAVELLS",
    # Add more NSE symbols here
]

EMAIL_SENDER   = os.environ.get("EMAIL_SENDER", "")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")
EMAIL_TO       = os.environ.get("EMAIL_TO", "")

POLL_INTERVAL  = 3   # seconds between each NSE check
SEEN_FILE      = "seen_announcements.json"

# ============================================================
#  NSE SESSION SETUP
#  NSE blocks plain requests — needs a browser-like session
# ============================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.nseindia.com/",
}

session = requests.Session()
session.headers.update(HEADERS)


def refresh_nse_cookies():
    """Visit NSE homepage to get valid cookies before API calls."""
    try:
        session.get("https://www.nseindia.com", timeout=10)
        session.get("https://www.nseindia.com/companies-listing/corporate-filings-announcements", timeout=10)
        print(f"[{now()}] NSE cookies refreshed.")
    except Exception as e:
        print(f"[{now()}] Cookie refresh failed: {e}")


def now():
    return datetime.now().strftime("%H:%M:%S")


# ============================================================
#  LOAD / SAVE SEEN ANNOUNCEMENTS  (avoids duplicate emails)
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
#  FETCH NSE ANNOUNCEMENTS
# ============================================================

def fetch_announcements():
    url = "https://www.nseindia.com/api/corporate-announcements?index=equities"
    try:
        resp = session.get(url, timeout=8)

        # --- DEBUG LINE: shows exactly what NSE sent back ---
        print(f"[{now()}] DEBUG status={resp.status_code} "
              f"content-type={resp.headers.get('Content-Type')} "
              f"body={resp.text[:300]!r}")
        # ------------------------------------------------------

        if resp.status_code == 401 or resp.status_code == 403:
            print(f"[{now()}] Session expired — refreshing cookies.")
            refresh_nse_cookies()
            return []
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.JSONDecodeError:
        print(f"[{now()}] Bad JSON — refreshing cookies.")
        refresh_nse_cookies()
        return []
    except Exception as e:
        print(f"[{now()}] Fetch error: {e}")
        return []


# ============================================================
#  SEND EMAIL ALERT
# ============================================================

def send_email(announcement):
    symbol   = announcement.get("symbol", "N/A")
    subject  = announcement.get("subject", "No Subject")
    an_date  = announcement.get("exchdisstime", "")
    pdf_link = announcement.get("attchmntFile", "")

    if pdf_link and not pdf_link.startswith("http"):
        pdf_link = f"https://nsearchives.nseindia.com/{pdf_link}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"NSE Alert: {symbol} — {subject}"
    msg["From"]    = EMAIL_SENDER
    msg["To"]      = EMAIL_TO

    body_html = f"""
    <html><body style="font-family:Arial,sans-serif;padding:20px;">
      <h2 style="color:#1a1a2e;">📢 NSE Announcement Alert</h2>
      <table style="border-collapse:collapse;width:100%;">
        <tr><td style="padding:8px;font-weight:bold;width:140px;">Company</td>
            <td style="padding:8px;">{symbol}</td></tr>
        <tr style="background:#f5f5f5;"><td style="padding:8px;font-weight:bold;">Subject</td>
            <td style="padding:8px;">{subject}</td></tr>
        <tr><td style="padding:8px;font-weight:bold;">Time</td>
            <td style="padding:8px;">{an_date}</td></tr>
        <tr style="background:#f5f5f5;"><td style="padding:8px;font-weight:bold;">PDF</td>
            <td style="padding:8px;">
              {"<a href='" + pdf_link + "' style='color:#0066cc;'>Click to open PDF</a>" if pdf_link else "No PDF attached"}
            </td></tr>
      </table>
    </body></html>
    """

    msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_TO, msg.as_string())
        print(f"[{now()}] EMAIL SENT — {symbol}: {subject}")
    except Exception as e:
        print(f"[{now()}] Email failed: {e}")


# ============================================================
#  MAIN LOOP
# ============================================================

def main():
    print("=" * 55)
    print("  NSE Announcement Alert — Started")
    print(f"  Watching: {', '.join(WATCHLIST)}")
    print(f"  Polling every {POLL_INTERVAL} seconds")
    print("=" * 55)

    refresh_nse_cookies()
    seen = load_seen()

    # Seed seen on first run so we don't get flooded with old announcements
    if not seen:
        print(f"[{now()}] First run — seeding existing announcements (no emails)...")
        data = fetch_announcements()
        for item in data:
            seen.add(item.get("an_seq_num", ""))
        save_seen(seen)
        print(f"[{now()}] Seeded {len(seen)} existing announcements. Now watching for NEW ones.")

    cookie_refresh_counter = 0

    while True:
        try:
            data = fetch_announcements()

            for item in data:
                seq_id = item.get("an_seq_num", "")
                symbol = item.get("symbol", "").upper()

                if seq_id in seen:
                    continue

                # New announcement found
                seen.add(seq_id)

                if symbol in [s.upper() for s in WATCHLIST]:
                    has_pdf = bool(item.get("attchmntFile", ""))
                    print(f"[{now()}] NEW: {symbol} — {item.get('subject', '')} | PDF: {has_pdf}")
                    send_email(item)
                else:
                    print(f"[{now()}] Skipped (not in watchlist): {symbol}")

            save_seen(seen)

            # Refresh cookies every 10 minutes to stay alive
            cookie_refresh_counter += 1
            if cookie_refresh_counter >= (600 // POLL_INTERVAL):
                refresh_nse_cookies()
                cookie_refresh_counter = 0

            time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            print("\nStopped by user.")
            break
        except Exception as e:
            print(f"[{now()}] Unexpected error: {e}. Retrying in 10s.")
            time.sleep(10)


if __name__ == "__main__":
    main()
