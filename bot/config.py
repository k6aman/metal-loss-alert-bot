"""Settings for the bot. Change values here, not inside the code."""

from pathlib import Path

# Published Google Sheet (CSV, read-only, no login needed)
SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vQoY_WG5HV6JIMJINpsUofVehYBL2upPPFu6T_aVVLmdbvjD7_SESpfcyuiPl6hfGgCRfglvwXUUkWF"
    "/pub?output=csv"
)

# Local copy of the same data, used with --local (works offline)
LOCAL_CSV = Path(__file__).parent.parent / "data" / "dummy_metal_loss.csv"

# A department is flagged when its loss % is above this limit
LOSS_LIMIT_PCT = 2.0

# Gemini model for the AI summary (free tier, Google AI Studio)
# Tried in order; the lite model is a backup when the main one is busy.
# "-latest" aliases always point to the current free models.
GEMINI_MODELS = ["gemini-flash-latest", "gemini-flash-lite-latest"]
GEMINI_TRIES = 3          # rounds over GEMINI_MODELS before using the fallback summary
GEMINI_RETRY_WAIT_S = 10  # seconds to wait between rounds

# Email alert (Gmail SMTP). Login details come from .env: GMAIL_USER, GMAIL_APP_PASSWORD, ALERT_TO
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465           # SSL
PREVIEW_HTML = Path(__file__).parent.parent / "out" / "alert_preview.html"  # written by --dry-run
