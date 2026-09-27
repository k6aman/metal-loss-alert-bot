"""Generate dummy metal loss data for the alert bot.

30 days x 7 departments. Each row has the metal issued to a department and
the metal returned by it. Loss % = (issue - return) / issue * 100.
A few rows are set above 2% on purpose so the bot has alerts to send.

Run:  python data/generate_dummy_data.py
Output: data/dummy_metal_loss.csv
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 42  # same seed = same data every run
START_DATE = date(2026, 9, 1)
DAYS = 30
OUTPUT = Path(__file__).parent / "dummy_metal_loss.csv"

# Department: (min issue g, max issue g, min normal loss %, max normal loss %)
DEPARTMENTS = {
    "Casting": (800, 1500, 0.5, 1.5),
    "Filing": (600, 1200, 0.8, 1.6),
    "Assembly": (400, 900, 0.2, 0.8),
    "Diamond Setting": (300, 700, 0.1, 0.5),
    "Final Polish": (500, 1000, 0.6, 1.5),
    "Polish Repair": (100, 300, 0.3, 1.0),
    "Plating": (300, 800, 0.05, 0.3),
}

METAL_TYPES = ["18K Gold", "14K Gold", "Silver 925"]

# (day number, department): loss % -- deliberate spikes above the 2% limit
SPIKES = {
    (5, "Casting"): 2.6,
    (12, "Filing"): 2.3,
    (18, "Final Polish"): 3.1,
    (23, "Casting"): 2.2,
    (29, "Polish Repair"): 2.8,
}


def main():
    random.seed(SEED)
    rows = []
    for day in range(DAYS):
        current = START_DATE + timedelta(days=day)
        for dept, (min_issue, max_issue, min_loss, max_loss) in DEPARTMENTS.items():
            issue = round(random.uniform(min_issue, max_issue), 3)
            loss_pct = SPIKES.get((day + 1, dept), random.uniform(min_loss, max_loss))
            returned = round(issue * (1 - loss_pct / 100), 3)
            rows.append({
                "date": current.isoformat(),
                "department": dept,
                "metal_type": random.choice(METAL_TYPES),
                "issue_weight_g": issue,
                "return_weight_g": returned,
            })

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUTPUT}")


if __name__ == "__main__":
    main()
