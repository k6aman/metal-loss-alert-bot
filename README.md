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

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Create a `.env` file for secrets. It is never committed. The keys are added in later steps.

## Status

- [x] Step 1: Repo setup (README, .gitignore, requirements.txt)
- [ ] Step 2: Dummy production data in Google Sheets
- [ ] Step 3: Calculate loss % per department and flag > 2%
- [ ] Step 4: Gemini summary
- [ ] Step 5: Email alert + `main.py`
- [ ] Step 6: Daily run with GitHub Actions
- [ ] Step 7: Final README, screenshots, pin on profile
