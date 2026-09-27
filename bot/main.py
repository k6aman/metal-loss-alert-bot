"""Run the full bot: loss check -> AI summary -> email alert.

If no department is over the limit, nothing is sent and it prints "All departments within limit".

Run:
    python -m bot.main                        # latest day, from the Google Sheet
    python -m bot.main --date 2026-09-29      # a chosen day
    python -m bot.main --local                # use data/dummy_metal_loss.csv
    python -m bot.main --dry-run              # build the email but save it as HTML instead of sending
"""

import argparse

from bot import config
from bot.ai_summary import ai_summary
from bot.loss_check import department_loss, flagged, load_data
from bot.send_email import build_email, send_email


def run(day=None, local=False, dry_run=False):
    df = load_data(local=local)
    day, result = department_loss(df, day)
    over = flagged(result)

    print(f"Metal loss check for {day.date()} (limit {config.LOSS_LIMIT_PCT}%)")
    if over.empty:
        print("All departments within limit - no email sent.")
        return

    print(f"{len(over)} department(s) over the limit: {', '.join(over['department'])}")
    summary, source = ai_summary(day, result)
    print(f"\nSummary (source: {source})\n{summary}\n")

    msg = build_email(day, result, summary, source)
    if dry_run:
        config.PREVIEW_HTML.parent.mkdir(exist_ok=True)
        config.PREVIEW_HTML.write_text(msg.get_body(("html",)).get_content(), encoding="utf-8")
        print(f"Dry run - email not sent. Preview saved to {config.PREVIEW_HTML}")
        return

    to = send_email(msg)
    print(f"Alert email sent to {to}")


def main():
    parser = argparse.ArgumentParser(description="Metal loss check + AI summary + email alert.")
    parser.add_argument("--date", help="Day to check (YYYY-MM-DD). Default: latest day.")
    parser.add_argument("--local", action="store_true", help="Use the local CSV file.")
    parser.add_argument("--dry-run", action="store_true", help="Save the email as HTML instead of sending it.")
    args = parser.parse_args()
    try:
        run(args.date, args.local, args.dry_run)
    except RuntimeError as err:  # missing Gmail details -> clear message, exit code 1 (fails the Actions run)
        raise SystemExit(str(err))


if __name__ == "__main__":
    main()
