# ============================================================
#  CONFIG — add this line to your existing env vars section
# ============================================================
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")


# ============================================================
#  SEND EMAIL ALERT  — replaces the old smtplib send_email()
# ============================================================

def send_email(announcement, summary):
    symbol   = announcement.get("symbol", "N/A")
    subject  = announcement.get("subject") or announcement.get("attchmntText", "No Subject")
    an_date  = announcement.get("an_dt") or announcement.get("exchdisstime", "")
    pdf_link = announcement.get("attchmntFile", "")

    if pdf_link and not pdf_link.startswith("http"):
        pdf_link = f"https://nsearchives.nseindia.com/{pdf_link}"

    summary_html = summary.replace("\n", "<br>")

    body_html = f"""
    <html><body style="font-family:Arial,sans-serif;padding:20px;">
      <h2 style="color:#1a1a2e;">NSE Announcement Alert</h2>
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
      <hr>
      <h3 style="color:#1a1a2e;">AI Summary</h3>
      <p>{summary_html}</p>
    </body></html>
    """

    if not RESEND_API_KEY:
        print(f"[{now()}] RESEND_API_KEY not set — skipping email.")
        return

    try:
        resp = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from":    "onboarding@resend.dev",
                "to":      [EMAIL_TO],
                "subject": f"NSE Alert: {symbol} — {subject}",
                "html":    body_html,
            },
            timeout=15,
        )
        resp.raise_for_status()
        print(f"[{now()}] EMAIL SENT — {symbol}: {subject}")
    except Exception as e:
        print(f"[{now()}] Email failed: {e}")


# ============================================================
#  GEMINI SUMMARY — replaces old summarize_with_gemini()
#  Now reads fresh key from env + retries once on 429
# ============================================================

def summarize_with_gemini(pdf_text):
    if not pdf_text:
        return "(Could not extract text from PDF to summarize.)"

    # Always read fresh from env so rotating keys works instantly
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return "(GEMINI_API_KEY not set — skipping summary.)"

    prompt = (
        "Summarize this NSE corporate announcement PDF in exactly 2-3 bullet points. "
        "Each bullet must be ONE short sentence, under 15 words. "
        "Keep every number, date, and amount exactly as written in the source, do not round or drop any. "
        "No preamble, no headings, no extra commentary, just the bullets starting with '-'. "
        "Focus only on the single most material fact per bullet (the decision, the amount, the date, the outcome).\n\n"
        f"{pdf_text}"
    )

    url  = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={api_key}"
    body = {"contents": [{"parts": [{"text": prompt}]}]}

    for attempt in range(2):   # try twice — once normally, once after 30s wait
        try:
            resp = requests.post(url, json=body, timeout=30)

            if resp.status_code == 429:
                if attempt == 0:
                    print(f"[{now()}] Gemini 429 — waiting 30s then retrying...")
                    time.sleep(30)
                    continue
                else:
                    print(f"[{now()}] Gemini 429 again — sending email without summary.")
                    return "(AI summary unavailable — rate limit reached.)"

            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()

        except Exception as e:
            print(f"[{now()}] Gemini error (attempt {attempt+1}): {e}")
            if attempt == 0:
                time.sleep(5)

    return "(Summary unavailable — Gemini error after retry.)"
