"""Build and send the metal loss alert email with Gmail SMTP.

Login details are read from the environment (or the .env file):
    GMAIL_USER          Gmail address that sends the alert
    GMAIL_APP_PASSWORD  16-letter App Password (needs 2-Step Verification)
    ALERT_TO            who gets the alert (several addresses: separate with commas)

Uses Python's built-in smtplib and email modules, so nothing extra to install.
"""

import html
import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

from bot import config

ROW_STYLE = "padding:6px 10px;border:1px solid #ddd;"


def subject(day):
    return f"⚠ Metal loss alert – {day.date()}"


def html_table(result):
    """All departments for the day; the ones over the limit are shown in red."""
    head = "".join(
        f'<th style="{ROW_STYLE}background:#f2f2f2;text-align:left;">{h}</th>'
        for h in ["Department", "Issue (g)", "Return (g)", "Loss (g)", "Loss %"]
    )
    rows = []
    for row in result.itertuples():
        colour = "color:#c00;font-weight:bold;" if row.over_limit else ""
        cells = [
            html.escape(row.department),
            f"{row.issue_g:.2f}",
            f"{row.return_g:.2f}",
            f"{row.loss_g:.2f}",
            f"{row.loss_pct:.2f}%",
        ]
        rows.append("<tr>" + "".join(f'<td style="{ROW_STYLE}{colour}">{c}</td>' for c in cells) + "</tr>")
    return f'<table style="border-collapse:collapse;font-size:14px;"><tr>{head}</tr>{"".join(rows)}</table>'


def build_email(day, result, summary, source):
    """Return an EmailMessage with a plain-text part and an HTML part."""
    over = result[result["over_limit"]]
    footer = f"Limit: {config.LOSS_LIMIT_PCT}% · Summary: {source} · Dummy data, sent by Metal Loss AI Alert Bot"

    text = (
        f"Metal loss alert for {day.date()}\n"
        f"{len(over)} department(s) over the {config.LOSS_LIMIT_PCT}% limit.\n\n"
        f"{summary}\n\n"
        f"{result[['department', 'issue_g', 'return_g', 'loss_g', 'loss_pct']].to_string(index=False, float_format=lambda x: f'{x:.2f}')}\n\n"
        f"{footer}\n"
    )

    body = f"""\
<html><body style="font-family:Arial,sans-serif;color:#222;">
<h2 style="color:#c00;margin-bottom:4px;">Metal loss alert – {day.date()}</h2>
<p style="margin-top:0;">{len(over)} department(s) over the {config.LOSS_LIMIT_PCT}% limit.</p>
<p style="background:#fff4e5;border-left:4px solid #f0a000;padding:10px;">{html.escape(summary).replace(chr(10), "<br>")}</p>
{html_table(result)}
<p style="font-size:12px;color:#777;">{html.escape(footer)}</p>
</body></html>"""

    msg = EmailMessage()
    msg["Subject"] = subject(day)
    msg.set_content(text)
    msg.add_alternative(body, subtype="html")
    return msg


def send_email(msg):
    """Send the message with Gmail SMTP. Raises an error if a login detail is missing."""
    load_dotenv()
    user = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_APP_PASSWORD")
    to = os.getenv("ALERT_TO") or user
    missing = [name for name, value in [("GMAIL_USER", user), ("GMAIL_APP_PASSWORD", password)] if not value]
    if missing:
        raise RuntimeError(f"Email not sent - missing in .env: {', '.join(missing)}")

    msg["From"] = user
    msg["To"] = to
    with smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT) as smtp:
        smtp.login(user, password.replace(" ", ""))  # App Password is often copied with spaces
        smtp.send_message(msg)
    return to
