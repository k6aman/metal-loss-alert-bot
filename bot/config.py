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
