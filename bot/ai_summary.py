"""Write a short plain-English summary of the flagged departments with Google Gemini.

The API key is read from the GEMINI_API_KEY environment variable (or the .env file).
If the key is missing or the API call fails, a simple fallback summary is used,
so the bot never crashes because of the AI step.

Run:
    python -m bot.ai_summary                     # latest day, from the Google Sheet
    python -m bot.ai_summary --date 2026-09-29   # a chosen day
    python -m bot.ai_summary --local             # use data/dummy_metal_loss.csv
"""

import argparse
import os
import time

from dotenv import load_dotenv

from bot import config
from bot.loss_check import department_loss, flagged, load_data

PROMPT = """You are a production analyst at a jewellery manufacturing company.
Metal loss % per department for {day} is below. The limit is {limit}%.

{table}

Write a short summary (4-6 lines, plain English, no markdown) for the production manager:
- which departments crossed the limit and by how much,
- how much metal was lost in grams,
- one practical thing to check in each flagged department.
Do not invent numbers that are not in the table."""


def fallback_summary(day, over):
    """Plain summary without AI, used when Gemini is not available."""
    lines = [f"{len(over)} department(s) crossed the {config.LOSS_LIMIT_PCT}% loss limit on {day.date()}:"]
    for row in over.itertuples():
        lines.append(
            f"- {row.department}: {row.loss_pct:.2f}% "
            f"({row.loss_pct - config.LOSS_LIMIT_PCT:.2f} points over, {row.loss_g:.2f} g lost)"
        )
    lines.append("Please check the issue/return records and scrap collection in these departments.")
    return "\n".join(lines)


def ai_summary(day, result):
    """Return (summary text, source). Source is 'gemini (<model>)', 'fallback' or 'none'."""
    over = flagged(result)
    if over.empty:
        return f"All OK - no department crossed the {config.LOSS_LIMIT_PCT}% limit on {day.date()}.", "none"

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not set - using fallback summary.")
        return fallback_summary(day, over), "fallback"

    table = result[["department", "issue_g", "return_g", "loss_g", "loss_pct"]].to_string(
        index=False, float_format=lambda x: f"{x:.2f}"
    )
    prompt = PROMPT.format(day=day.date(), limit=config.LOSS_LIMIT_PCT, table=table)

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    # free tier is sometimes busy (503) -> try each model, a few rounds, before giving up
    for attempt in range(1, config.GEMINI_TRIES + 1):
        for model in config.GEMINI_MODELS:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    # plain text only, no tools -> turn off function calling (also hides an SDK warning)
                    config=types.GenerateContentConfig(
                        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
                    ),
                )
                text = (response.text or "").strip()
                if not text:
                    raise ValueError("empty response")
                return text, f"gemini ({model})"
            except Exception as err:  # any API problem -> next model/round, then fallback, never crash
                print(f"Gemini call failed, {model}, round {attempt}/{config.GEMINI_TRIES} ({str(err)[:60]})")
        if attempt < config.GEMINI_TRIES:
            time.sleep(config.GEMINI_RETRY_WAIT_S)

    print("Using fallback summary.")
    return fallback_summary(day, over), "fallback"


def main():
    parser = argparse.ArgumentParser(description="AI summary of departments over the loss limit.")
    parser.add_argument("--date", help="Day to check (YYYY-MM-DD). Default: latest day.")
    parser.add_argument("--local", action="store_true", help="Use the local CSV file.")
    args = parser.parse_args()

    df = load_data(local=args.local)
    day, result = department_loss(df, args.date)
    text, source = ai_summary(day, result)

    print(f"\nSummary for {day.date()} (source: {source})\n")
    print(text)


if __name__ == "__main__":
    main()
