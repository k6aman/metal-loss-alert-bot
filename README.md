# Metal Loss AI Alert Bot

A small Python bot that checks metal loss for each department in jewellery manufacturing. When a department's loss goes over the limit, it uses Google Gemini to write a short plain-English summary and sends it as an email alert. GitHub Actions runs it once a day.

> **Dummy data only.** No real company data is used in this project.

## Problem

In jewellery manufacturing, some gold or silver is lost at every step (casting, filing, polishing, setting). A small rise in loss % costs real money. It is easy to miss when you only look at reports now and then. This bot checks every day and sends an alert only when a department crosses the limit.

## How it works

```
Google Sheet (dummy production data, published as CSV)
        │
        ▼
Python + pandas ── calculate loss % per department
        │
        ▼
Loss > 2% ? ── no ──► "All OK" in the run summary
        │ yes
        ▼
Google Gemini (free tier) ── short plain-English summary
        │
        ▼
Email alert (Gmail SMTP)

Scheduled daily by GitHub Actions (runs in the cloud, not on my PC)
```

## Tools (all free)

| Tool | Use |
|---|---|
| Python 3.12 + pandas | Read the data and calculate loss % |
| Google Sheets (published as CSV) | Dummy production data, no login needed |
| Google Gemini API (free tier, Google AI Studio) | AI summary of the alert |
| Gmail SMTP (App Password) | Send the alert email |
| GitHub Actions | Run the bot every day on a schedule |

## Data

Dummy production data: 30 days (1–30 Sep 2026) × 7 departments = 210 rows.

| Column | Meaning |
|---|---|
| `date` | Production date |
| `department` | Casting, Filing, Assembly, Diamond Setting, Final Polish, Polish Repair, Plating |
| `metal_type` | 18K Gold, 14K Gold or Silver 925 |
| `issue_weight_g` | Metal given to the department (grams) |
| `return_weight_g` | Metal returned by the department (grams) |

Loss % = (issue − return) ÷ issue × 100. Five rows are set above the 2% limit on purpose so the bot has alerts to send.

- Generator: [`data/generate_dummy_data.py`](data/generate_dummy_data.py) (fixed seed, so it makes the same data every time)
- Local copy: [`data/dummy_metal_loss.csv`](data/dummy_metal_loss.csv)
- Published Google Sheet (CSV, read-only, no login needed): [dummy_metal_loss.csv](https://docs.google.com/spreadsheets/d/e/2PACX-1vQoY_WG5HV6JIMJINpsUofVehYBL2upPPFu6T_aVVLmdbvjD7_SESpfcyuiPl6hfGgCRfglvwXUUkWF/pub?output=csv)

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Check loss % per department (prints a table and lists departments over 2%):

```bash
python -m bot.loss_check                     # latest day, from the Google Sheet
python -m bot.loss_check --date 2026-09-29   # a chosen day
python -m bot.loss_check --local             # use the local CSV (offline)
```

The 2% limit and the Sheet link are set in [`bot/config.py`](bot/config.py).

### AI summary (Google Gemini)

1. Get a free API key from [Google AI Studio](https://aistudio.google.com/apikey) (no card needed).
2. Copy [`.env.example`](.env.example) to `.env` and paste the key as `GEMINI_API_KEY`. `.env` is never committed.
3. Run:

```bash
python -m bot.ai_summary --date 2026-09-29   # a day with a department over 2%
python -m bot.ai_summary --local             # latest day, local CSV
```

Gemini gets the loss table and writes a 4–6 line summary: which departments crossed the limit, by how much, and one thing to check. If the main model is busy, it tries a lighter backup model and retries a few times. If the key is missing or every try fails, the bot prints a simple fallback summary instead of crashing. If no department is over the limit, Gemini is not called. The model names and retry settings are set in [`bot/config.py`](bot/config.py).

### Email alert + full run

1. Turn on [2-Step Verification](https://myaccount.google.com/signinoptions/twosv) for the Gmail account that sends the alert.
2. Create an [App Password](https://myaccount.google.com/apppasswords) (16 letters). It is used instead of the normal Gmail password.
3. Add to `.env`: `GMAIL_USER`, `GMAIL_APP_PASSWORD` and `ALERT_TO` (see [`.env.example`](.env.example)).
4. Run the full bot:

```bash
python -m bot.main                           # latest day, from the Google Sheet
python -m bot.main --date 2026-09-29         # a day with a department over 2%
python -m bot.main --date 2026-09-29 --dry-run   # save the email to out/alert_preview.html, do not send
```

Flow: loss check → if any department is over 2% → Gemini summary → HTML email with the summary and the loss table (departments over the limit in red). If every department is within the limit, it prints "All departments within limit" and sends nothing. Email uses Python's built-in `smtplib`, so there is nothing extra to install.

## Status

- [x] Step 1: Repo setup (README, .gitignore, requirements.txt)
- [x] Step 2: Dummy production data in Google Sheets
- [x] Step 3: Calculate loss % per department and flag > 2%
- [x] Step 4: Gemini summary
- [x] Step 5: Email alert + `main.py`
- [ ] Step 6: Daily run with GitHub Actions
- [ ] Step 7: Final README, screenshots, pin on profile
